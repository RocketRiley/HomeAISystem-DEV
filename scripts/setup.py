"""Initial setup utility for Clair.

Installs Python dependencies from requirements.txt and creates a default
.env file if one does not exist. This allows new handlers to prepare the
runtime with a single command:

    python -m scripts.setup
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "requirements.txt"
ENV_EXAMPLE = ROOT / ".env.example"
ENV_FILE = ROOT / ".env"


def install_requirements() -> None:
    """Install pip dependencies listed in requirements.txt."""
    if not REQ_FILE.exists():
        print("requirements.txt not found; skipping dependency installation")
        return
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)]
    subprocess.check_call(cmd)


def ensure_env_file() -> None:
    """Copy .env.example to .env on first run."""
    if ENV_FILE.exists() or not ENV_EXAMPLE.exists():
        return
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    print("Created .env from .env.example; please review and edit it.")


def main() -> None:
    install_requirements()
    ensure_env_file()
    print("Setup complete.")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
