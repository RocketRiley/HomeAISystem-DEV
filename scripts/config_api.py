"""Simple helpers to load and update `.env` settings.

Unity or other front ends can import this module or call it via
`scripts.settings_server` to modify runtime configuration without the
legacy Tkinter launcher.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

try:
    from dotenv import dotenv_values, set_key
except Exception:  # pragma: no cover - fallback if python-dotenv missing
    def dotenv_values(path: str) -> Dict[str, str]:  # type: ignore
        return {}

    def set_key(path: str, key: str, value: str) -> None:  # type: ignore
        line = f"{key}={value}\n"
        p = Path(path)
        if p.exists():
            lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
            for i, existing in enumerate(lines):
                if existing.startswith(f"{key}="):
                    lines[i] = line
                    p.write_text("".join(lines), encoding="utf-8")
                    return
            lines.append(line)
            p.write_text("".join(lines), encoding="utf-8")
        else:
            p.write_text(line, encoding="utf-8")


CONFIG_FILE = Path(__file__).resolve().parent.parent / ".env"


def load_config() -> Dict[str, str]:
    """Return current key/value pairs from the `.env` file."""
    return dotenv_values(str(CONFIG_FILE))


def update_config(changes: Dict[str, str]) -> None:
    """Persist the provided key/value pairs to the `.env` file."""
    for k, v in changes.items():
        set_key(str(CONFIG_FILE), k, v)
