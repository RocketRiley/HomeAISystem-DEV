"""Setup helper to install Python deps and download models."""
from __future__ import annotations

import shutil
import subprocess
import sys
import pathlib


def _pip_install(requirements: pathlib.Path) -> None:
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements)]
    print("[pip]", " ".join(cmd))
    subprocess.check_call(cmd)


def _ensure_env(env_example: pathlib.Path, env_path: pathlib.Path) -> None:
    if env_path.exists():
        return
    if env_example.exists():
        shutil.copy(env_example, env_path)
        print(f"[env] created {env_path} from example")


def _ensure_unity_dirs(root: pathlib.Path) -> None:
    """Create Unity asset placeholders so the project opens cleanly."""
    assets = root / "unity_project" / "Assets"
    for name, message in {
        "CharacterModels": "Drop VRM avatar files here.\n",
        "RoomModels": "Drop room prefabs or models here.\n",
    }.items():
        target = assets / name
        target.mkdir(parents=True, exist_ok=True)
        readme = target / "README.md"
        if not readme.exists():
            readme.write_text(message, encoding="utf-8")


def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    req = root / "requirements.txt"
    env_example = root / ".env.example"
    env_path = root / ".env"

    if req.exists():
        _pip_install(req)

    _ensure_env(env_example, env_path)
    _ensure_unity_dirs(root)

    try:
        from . import bootstrap_models
        bootstrap_models.main()
    except Exception as exc:  # pragma: no cover - best effort
        print("[warn] bootstrap failed:", exc)

    print("pre-install complete")


if __name__ == "__main__":
    main()
