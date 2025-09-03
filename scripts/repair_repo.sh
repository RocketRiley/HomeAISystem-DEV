#!/usr/bin/env bash
set -euo pipefail

# Remove residual Codex merge markers from text files
find . -type f \
  \( -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.json" -o -name "*.cs" -o -name "*.unity" \) \
  ! -path "./.git/*" \
  -print0 | xargs -0 sed -i '/codex\/resolve-conflict-in-readme.md/d;/^=======$/d;/^ main$/d'

# Restore requirements.txt if present
if [ -f requirements.txt ]; then
  cat <<'REQ' > requirements.txt
# Python dependencies for the Clair Local Model demo scripts
#
# These packages are sufficient to run the provided example scripts.
# You may install additional libraries such as openWakeWord, faster-whisper
# or Piper/XTTS for full STT/TTS integration; those are optional and
# not included here because they may require platform-specific builds.

python-osc>=1.7.4
websockets>=10.4
python-dotenv>=0.21.0
# Optional sensory and voice frameworks
opencv-python>=4.8.0
sounddevice>=0.4.5
numpy>=1.24
faster-whisper>=0.8.0
piper-tts>=0.3.0
openwakeword>=0.7.0
paho-mqtt>=1.6.1
# Open-source LLM support (requires a local .gguf model)
llama-cpp-python>=0.2.0
openai>=1.0.0  # required only for online mode; safe to omit if running offline
# Experimental learning framework
dspy>=3.0.2
# Build utility for creating standalone installer
pyinstaller>=6.0
REQ
fi

# Install dependencies
pip install -r requirements.txt
