# HomeAISystem-DEV

Local-first VTuber companion (Clair) with:

- Local LLM (llama.cpp via `llama-cpp-python`)
- Unity-driven in-world UI and subtitles
- TTS/STT hooks
- OSC bridge for expressions, idle motion, lip-sync
- Logging & diagnostics
- Tiered memory system with long-term persistence
- Optional MQTT bridge to Home Assistant for smart home control

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
    settings server: `python -m scripts.settings_server`). This emits PAD
    emotion values and a basic lip-sync signal over OSC. In another shell, run
    `python -m scripts.health_monitor` to expose a `/healthz` endpoint for
    watchdog supervision.
10. Press **Play** in Unity; Clair faces the camera, roams if enabled, and
    responds using STT/TTS out of the box.

See `docs/EXTERNAL_DEPENDENCIES.txt` for optional audio/vision setup
details.

For smart home integration instructions see
[`docs/SmartHome_Setup.md`](docs/SmartHome_Setup.md).

### Log rotation

The assistant writes JSONL logs under `logs/`. `scripts/log_rotation.py` runs in
the background (started by `scripts.voice_loop_stub`) and rotates `stt.jsonl`,
`llm.jsonl` and similar files once per day or when they exceed a configurable
size. Archived logs are compressed and removed after 30 days by default.
Adjust `LOG_ROTATION_SIZE_MB` and `LOG_RETENTION_DAYS` to tweak these settings.

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

### Standalone build

To produce a bundled player with the Python runtime:

1. Open the Unity project in `unity_project/`.
2. Navigate to **File > Build Settings** and add `Assets/Scenes/Main.unity` to
   the *Scenes In Build* list, ensuring it is checked.
3. Run **Build > Standalone** from the Unity editor. This executes
   `Build/StandaloneBuild.cs`, which builds the game, copies `scripts/` and
   `assets/` into `Build/Data/`, and writes `run.bat` / `run.sh` wrappers that
   launch the Unity player and Python side by side.

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


## Memory directories

Memory data lives under `MEMORY_ROOT` (defaults to `config/`) and each tier has
its own folder:

