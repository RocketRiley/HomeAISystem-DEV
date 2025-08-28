"""Simple configuration checker for Clair."""

from __future__ import annotations

import os
import socket
from pathlib import Path

SENSITIVE = {"OPENAI_API_KEY"}
PATH_VARS = [
    "LLAMA_MODEL_PATH",
    "WHISPER_MODEL_PATH",
    "PIPER_MODEL_PATH",
    "WAKE_WORD_MODEL",
]

def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def show_env() -> None:
    for key in SENSITIVE:
        print(f"{key}={_mask(os.getenv(key, ''))}")


def check_paths() -> None:
    for var in PATH_VARS:
        path = os.getenv(var, "")
        if path:
            exists = Path(path).exists()
            status = "ok" if exists else "missing"
            print(f"{var}={path} ({status})")
        else:
            print(f"{var}= (unset)")


def check_osc() -> None:
    host = os.getenv("OSC_HOST", "127.0.0.1")
    port = int(os.getenv("OSC_PORT", "9000"))
    sock = socket.socket()
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        print(f"OSC {host}:{port} reachable")
    except OSError:
        print(f"OSC {host}:{port} unreachable")
    finally:
        sock.close()


 codex/resolve-conflict-in-readme.md-g7qctv
=======
 codex/resolve-conflict-in-readme.md-esoix8
=======
 codex/resolve-conflict-in-readme.md-154yk5
=======
 codex/resolve-conflict-in-readme.md-ookl8l
=======
 codex/resolve-conflict-in-readme.md-5fi9ql
 main
 main
 main
 main
def check_mqtt() -> None:
    host = os.getenv("MQTT_HOST")
    port = int(os.getenv("MQTT_PORT", "1883"))
    if not host:
        print("MQTT_HOST not set")
        return
    sock = socket.socket()
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        print(f"MQTT {host}:{port} reachable")
    except OSError:
        print(f"MQTT {host}:{port} unreachable")
    finally:
        sock.close()


 codex/resolve-conflict-in-readme.md-g7qctv
=======
 codex/resolve-conflict-in-readme.md-esoix8
=======
 codex/resolve-conflict-in-readme.md-154yk5
=======
 codex/resolve-conflict-in-readme.md-ookl8l
=======
=======
 main
 main
 main
 main
 main
def main() -> None:
    show_env()
    check_paths()
    check_osc()
 codex/resolve-conflict-in-readme.md-g7qctv
    check_mqtt()
=======
 codex/resolve-conflict-in-readme.md-esoix8
    check_mqtt()
=======
 codex/resolve-conflict-in-readme.md-154yk5
    check_mqtt()
=======
 codex/resolve-conflict-in-readme.md-ookl8l
    check_mqtt()
=======
 codex/resolve-conflict-in-readme.md-5fi9ql
    check_mqtt()
=======
 main
 main
 main
 main
 main


if __name__ == "__main__":
    main()
