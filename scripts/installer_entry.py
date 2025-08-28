"""Entry point for bundled installer executable.

When executed, this script downloads default models via `bootstrap_models`
and prints next-step instructions.
"""
from __future__ import annotations

from pathlib import Path
import os

from bootstrap_models import main as bootstrap_main


def main() -> None:
    print("Clair setup starting...")
    bootstrap_main()
    if Path(".env").exists():
        print("\nModel paths written to .env. Review the file if needed.")
    else:
        print("\nNo .env found. Create one based on .env.example and rerun.")
    print("Setup complete. You can now launch the voice loop with:\n")
    print("    python -m scripts.voice_loop_stub\n")


if __name__ == "__main__":
    main()
