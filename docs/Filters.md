# Filters

Clair ships with a word-replacement filter pipeline.

## Levels

- **twitch** – strict profanity filter suitable for streaming.
- **pg13** – family-friendly with mild cursing removed.
- **enabled** – default dictionary for casual use.
- **adult** – minimal filtering.
- **dev0** – filter disabled for local testing.

The replacement tables for each level live in `scripts/filter_system.py`.

## Conversational Tone Limits

During dialogue the emotion orchestrator clamps valence, arousal and
dominance to ±0.6.  Downstream speech and animation systems reference the
clamped values so Clair's vocal delivery and facial expressions remain
within everyday intensity.
