# HomeAISystem-DEV

Local-first VTuber companion (Clair) with:

- Local LLM (llama.cpp via `llama-cpp-python`)
- GUI launcher + chat window
- TTS/STT hooks
- VSeeFace (OSC) bridge for expressions, idle motion, lip-sync
- Logging & diagnostics
- Tiered memory system with long-term persistence

## Quick Start

1. Clone repo
2. `python -m venv .venv && .\.venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and edit settings (see [Environment configuration](#environment-configuration))
5. `.\dl_models.ps1` to fetch local-only models (or place assets in `LLM-BASE/`,
   `vrm/`, `voice/`)
6. Run: `python -m scripts.ui_launcher`

See `docs/EXTERNAL_DEPENDENCIES.txt` for optional audio/vision and Unity setup steps.

### Environment configuration

The `.env` file controls runtime behaviour:

- `LLAMA_MODEL_PATH` – path to a local GGUF model
- `OPENAI_API_KEY` – enables online LLM calls when `ONLINE_MODE=true`
- `VSEEFACE_PATH` / `VSEEFACE_MODEL` – launch VSeeFace with a specific VRM
- `WAKE_MODEL_PATH`, `WHISPER_MODEL_PATH`, `PIPER_MODEL_PATH` – optional
  wake‑word, STT and TTS models
- `MEMORY_ROOT` – where per‑user memories are stored (defaults to `config/`)

### Unity VRM setup

A starter Unity project lives in `unity_project/` with a `PADReceiver` script
that listens for PAD values over OSC. See [`docs/UnitySetupManual.md`](docs/UnitySetupManual.md)
for a beginner‑friendly, step‑by‑step manual covering Unity installation,
importing a VRM, installing **UniVRM** and **OscJack**, attaching `PADReceiver`,
and connecting to the Python runtime.

## Notes

- Do **not** commit `.env`.
- Large models/assets are intentionally excluded.
- A starter Unity project lives in `unity_project/` with a `PADReceiver` script
  for driving VRM avatars via OSC.

## Development mode

During development the application runs with `DEV_MODE` enabled by default. This
skips the cinematic disclaimer and relaxes certain safety restrictions so that
features can be tested quickly. To simulate the end-user experience, set
`DEV_MODE=false` in your `.env` or toggle the checkbox in the launcher.

All memory files are stored under the directory defined by `MEMORY_ROOT`
(defaults to `config/`). Each handler receives its own subdirectory so data
is isolated per user.

### All Memory Tiers

Clair uses a five‑tier memory stack:

1. **Active** – the last few utterances, kept in RAM
2. **Short‑term** – a 24‑hour session log
3. **Mid‑term** – time‑limited project notes
4. **Long‑term** – a curated knowledge graph of important facts
5. **Archive** – compressed storage for everything else

A background consolidator promotes or archives items so the system can run
for years without unbounded growth.
