# HomeAISystem-DEV

Local-first VTuber companion (Clair) with:

- Local LLM (llama.cpp via `llama-cpp-python`)
- Unity-driven in-world UI and subtitles
- TTS/STT hooks
- OSC bridge for expressions, idle motion, lip-sync
- Logging & diagnostics
- Tiered memory system with long-term persistence

## Quick Start (10 steps)

1. Clone repo.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   ```

   On Linux or Mac:


   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and fill in paths or keys.
5. Run `./dl_models.ps1` to download sample models **or** drop your own
   GGUF, STT and TTS models into `LLM-BASE/`, `voice/`, etc.
6. Open `unity_project/` in **Unity Hub** (Unity 2022 LTS).
7. Via *Package Manager* install **UniVRM** and **OscJack**.
8. Drag your avatar `.vrm` into `Assets/CharacterModels/`, your room model
   into `Assets/RoomModels/`, and open `Assets/Scenes/Main.unity`.
9. Start the Python side: `python -m scripts.voice_loop_stub` (optional
   settings server: `python -m scripts.settings_server`).
10. Press **Play** in Unity; Clair faces the camera, roams if enabled, and
    responds using STT/TTS out of the box.

See `docs/EXTERNAL_DEPENDENCIES.txt` for optional audio/vision setup
details.


### Environment configuration

The `.env` file controls runtime behaviour:



### Unity VRM setup

A starter Unity project lives in `unity_project/` with scripts for
`PADReceiver`, `LookAtCamera` and `RoamController`. It also contains
empty `Assets/CharacterModels/` and `Assets/RoomModels/` folders for
avatars and room prefabs. See [`docs/UnitySetupManual.md`](docs/UnitySetupManual.md)
for a beginner-friendly, step-by-step manual covering Unity
installation, importing a VRM, installing **UniVRM** and **OscJack**, attaching the
scripts, and connecting to the Python runtime.

## Notes

- Do **not** commit `.env`.
- Large models/assets are intentionally excluded.
- A starter Unity project lives in `unity_project/` with a `PADReceiver` script
  for driving VRM avatars via OSC.
- Content filter levels are outlined in [docs/Filters.md](docs/Filters.md).

## Development mode

During development the application runs with `DEV_MODE` enabled by default. This
skips the cinematic disclaimer and relaxes certain safety restrictions so that
features can be tested quickly. To simulate the end-user experience, set
`DEV_MODE=false` in your `.env`.

