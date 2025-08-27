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


def main() -> None:
    show_env()
    check_paths()
    check_osc()


if __name__ == "__main__":
    main()
