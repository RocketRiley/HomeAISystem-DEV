# HomeAISystem-DEV

Local-first VTuber companion (Clair) with:

- Local LLM (llama.cpp via `llama-cpp-python`)
- Unity-driven in-world UI and subtitles
- TTS/STT hooks
- OSC bridge for expressions, idle motion, lip-sync
- Logging & diagnostics
- Tiered memory system with long-term persistence



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

Clair persists information across five tiers, each stored under
`MEMORY_ROOT`:

| Tier       | Purpose                    | Directory              |
|------------|----------------------------|------------------------|
| Active     | in-RAM working context     | *(memory only)*        |
| Short-term | 24-hour session log        | `config/short_term/`   |
| Mid-term   | time-limited project notes | `config/mid_term/`     |
| Long-term  | curated facts              | `config/long_term/`    |
| Archive    | compressed history         | `config/archive/`      |

A background consolidator promotes or archives items so the system can run
for years without unbounded growth. See [`docs/Memory.md`](docs/Memory.md)
for details.
=======


