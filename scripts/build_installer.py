"""Build a standalone installer executable using PyInstaller."""
from __future__ import annotations

import PyInstaller.__main__
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    script = project_root / "scripts" / "installer_entry.py"
    PyInstaller.__main__.run([
        str(script),
        "--onefile",
        "--name", "HomeAISetup",
        "--distpath", str(project_root / "dist"),
    ])


if __name__ == "__main__":
    main()
