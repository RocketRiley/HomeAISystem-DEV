"""Periodic health checker exposing a `/healthz` endpoint."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

try:  # pragma: no cover - optional dependency
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

STATUS: Dict[str, object] = {"services": {}, "memory": {}}


def _check_tcp(host: str, port: int, timeout: float = 1.0) -> bool:
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _restart(env_var: str) -> None:
    cmd = os.getenv(env_var)
    if not cmd:
        return
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception:
        pass


def _memory() -> Dict[str, float]:
    if psutil is not None:
        proc = psutil.Process(os.getpid())
        rss = proc.memory_info().rss / (1024 * 1024)
        total = psutil.virtual_memory().total / (1024 * 1024)
        return {"rss_mb": round(rss, 2), "system_mb": round(total, 2)}
    try:
        import resource  # type: ignore

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if os.name == "posix":
            rss = rss / 1024
        return {"rss_mb": round(rss, 2)}
    except Exception:  # pragma: no cover
        return {}


def _run(interval: float) -> None:
    while True:
        services: Dict[str, bool] = {}
        host = os.getenv("STT_HOST", "127.0.0.1")
        port = int(os.getenv("STT_PORT", "9001"))
        ok = _check_tcp(host, port)
        services["stt"] = ok
        if not ok:
            _restart("STT_RESTART_CMD")

        host = os.getenv("TTS_HOST", "127.0.0.1")
        port = int(os.getenv("TTS_PORT", "9002"))
        ok = _check_tcp(host, port)
        services["tts"] = ok
        if not ok:
            _restart("TTS_RESTART_CMD")

        host = os.getenv("MQTT_HOST", "127.0.0.1")
        port = int(os.getenv("MQTT_PORT", "1883"))
        ok = _check_tcp(host, port)
        services["mqtt"] = ok
        if not ok:
            _restart("MQTT_RESTART_CMD")

        host = os.getenv("OSC_HOST", "127.0.0.1")
        port = int(os.getenv("OSC_PORT", "9000"))
        ok = _check_tcp(host, port)
        services["osc"] = ok
        if not ok:
            _restart("OSC_RESTART_CMD")

        STATUS["services"] = services
        STATUS["memory"] = _memory()
        time.sleep(interval)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path.rstrip("/") == "/healthz":
            body = json.dumps(STATUS).encode("utf-8")
            code = 200 if all(STATUS["services"].values()) else 503
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


def main() -> None:
    interval = float(os.getenv("HEALTH_INTERVAL", "30"))
    port = int(os.getenv("HEALTH_PORT", "8080"))
    thread = threading.Thread(target=_run, args=(interval,), daemon=True)
    thread.start()
    HTTPServer(("", port), _Handler).serve_forever()


if __name__ == "__main__":  # pragma: no cover
    main()
