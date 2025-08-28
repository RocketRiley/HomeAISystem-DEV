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
2. Run the setup script to create a virtual environment, install
   dependencies, download sample models, create `.env`, and set up
   Unity asset folders:

   ```powershell
   scripts\setup.ps1
   ```

   On Linux or Mac:

   ```bash
   bash scripts/setup.sh
   ```

3. Review `.env` and fill in any paths or keys.
4. Open `unity_project/` in **Unity Hub** (Unity 2022 LTS).
5. Via *Package Manager* install **UniVRM** and **OscJack**.
6. Drag your avatar `.vrm` into `Assets/CharacterModels/`.
7. Drag your room model into `Assets/RoomModels/` and open
   `Assets/Scenes/Main.unity`.
8. Start the Python voice loop: `python -m scripts.voice_loop_stub`.
9. Optionally start `python -m scripts.settings_server` for runtime
   configuration.
10. Press **Play** in Unity; Clair faces the camera, roams if enabled,
    and responds using STT/TTS out of the box.

See `docs/EXTERNAL_DEPENDENCIES.txt` for required audio/vision setup
details.

For smart home integration instructions see
[`docs/SmartHome_Setup.md`](docs/SmartHome_Setup.md).

### Troubleshooting

If Clair fails to respond:

- Run `python -m scripts.diagnostics` to print resolved model paths and
  test OSC port connectivity.
- Verify the `WHISPER_MODEL_PATH`, `PIPER_MODEL_PATH`, and
  `LLAMA_MODEL_PATH` files exist.
- Confirm your microphone and speakers are selectable in the OS audio
  settings.

### Environment configuration

The `.env` file controls runtime behaviour:

- `LLAMA_MODEL_PATH` - path to a local GGUF model
- `LLAMA_N_CTX`, `LLAMA_MAX_TOKENS` - local context window and reply length
- `OPENAI_API_KEY` - enables online LLM calls when `ONLINE_MODE=true`
- `OPENAI_MAX_TOKENS` - max tokens per reply when using OpenAI
- `WAKE_WORD_MODEL`, `WHISPER_MODEL_PATH`, `PIPER_MODEL_PATH` - paths to the
  wake-word, STT and TTS models required for voice interaction
- `STT_ENGINE`, `TTS_ENGINE` - choose between bundled speech engines
- `LLM_CONTINUE_ON_TRUNCATION` - auto-continue if a reply is cut off
- `MQTT_HOST`, `MQTT_PORT`, `MQTT_USER`, `MQTT_PASS` - Home Assistant MQTT
  broker details
- `MEMORY_ROOT` - where per-user memories are stored (defaults to `config/`)
- `FILTER_LEVEL` - content policy level applied to all generated text
- `DSPY_MODEL` - model name used by the optional DSPy planning agent

### Learning routines

The repository includes an experimental planner powered by
[DSPy](https://github.com/stanfordnlp/dspy) that generates human-like routines
and stores them in memory. Try it with:

```bash
python -m scripts.dspy_learning
```

Set `DSPY_MODEL` in your `.env` to pick the language model backend.

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

## Memory directories

Memory data lives under `MEMORY_ROOT` (defaults to `config/`) and each tier has
its own folder:

```text
config/
|-- short_term/
|-- mid_term/
|-- long_term/
`-- archive/
```

### All Memory Tiers

Clair organizes knowledge into five tiers rooted at `MEMORY_ROOT`:

| Tier       | Purpose                       | Directory            |
|------------|-------------------------------|----------------------|
| Active     | in-RAM working context        | *(memory only)*      |
| Short-term | 24-hour session log           | `config/short_term/` |
| Mid-term   | time-limited project notes    | `config/mid_term/`   |
| Long-term  | curated facts and preferences | `config/long_term/`  |
| Archive    | compressed history            | `config/archive/`    |

A background consolidator periodically promotes important items and prunes
old ones to keep storage bounded. See
[`docs/Memory.md`](docs/Memory.md) for details.
