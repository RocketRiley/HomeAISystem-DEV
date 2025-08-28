#!/usr/bin/env bash
set -e
# Run from repository root
cd "$(dirname "$0")/.."
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m scripts.preinstall
