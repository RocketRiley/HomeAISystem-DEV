"""HTTP server exposing `.env` settings for Unity.

Run with:
    python -m scripts.settings_server

Endpoints:
    GET /config  -> returns current settings as JSON
    POST /config -> accepts JSON body of key/value pairs to update
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

from .config_api import load_config, update_config


class _Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes = b"", content: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path.rstrip("/") == "/config":
            body = json.dumps(load_config()).encode("utf-8")
            self._send(200, body)
        else:
            self._send(404, b"{}")

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path.rstrip("/") != "/config":
            self._send(404, b"{}")
            return
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        try:
            changes: Dict[str, str] = json.loads(data.decode("utf-8"))
            update_config(changes)
        except Exception:
            self._send(400, b"{}")
            return
        self._send(204)


def main() -> None:
    port = int(os.getenv("SETTINGS_PORT", "8765"))
    HTTPServer(("", port), _Handler).serve_forever()


if __name__ == "__main__":  # pragma: no cover
    main()
