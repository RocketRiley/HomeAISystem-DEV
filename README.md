# HomeAISystem-DEV

Local-first VTuber companion (Clair) with:
- Local LLM (llama.cpp via `llama-cpp-python`)
- GUI launcher + chat window
- TTS/STT hooks
- VSeeFace (OSC) bridge for expressions, idle motion, lip-sync
- Logging & diagnostics

## Quick Start
1. Clone repo
2. `python -m venv .venv && .\.venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and edit settings
5. `.\dl_models.ps1` to fetch local-only models (or place assets in `LLM-BASE/`, `vrm/`, `voice/`)
6. Run: `python -m scripts.ui_launcher`

## Notes
- Do **not** commit `.env`.
- Large models/assets are intentionally excluded.
