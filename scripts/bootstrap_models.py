"""Download default model assets and update .env paths.

This script reads `config/models.json` for model URLs and target paths.
Missing files are downloaded, and the .env file is updated with matching
variables if they are unset. Intended to be bundled into a standalone
installer.
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.request
from typing import Dict

MODEL_ENV_VARS = {
    "llm": "LLAMA_MODEL_PATH",
    "stt": "WHISPER_MODEL_PATH",
    "tts": "PIPER_MODEL_PATH",
}

CONFIG_PATH = pathlib.Path("config/models.json")
ENV_PATH = pathlib.Path(".env")


def _load_config() -> Dict[str, Dict[str, str]]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _download(url: str, dest: pathlib.Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[skip] {dest} already exists")
        return
    print(f"[download] {url} -> {dest}")
    with urllib.request.urlopen(url) as response, dest.open("wb") as out:
        out.write(response.read())


def _update_env(var: str, value: str) -> None:
    if not ENV_PATH.exists():
        return
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.startswith(f"{var}="):
            if line.strip() == f"{var}=":
                lines[idx] = f"{var}={value}"
            break
    else:
        lines.append(f"{var}={value}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not CONFIG_PATH.exists():
        print("model config not found; nothing to do")
        return
    config = _load_config()
    for key, meta in config.items():
        url = meta.get("url")
        dest = pathlib.Path(meta.get("path", ""))
        if not url or not dest:
            continue
        _download(url, dest)
        env_var = MODEL_ENV_VARS.get(key)
        if env_var:
            _update_env(env_var, str(dest))
    print("bootstrap complete")


if __name__ == "__main__":
    main()
