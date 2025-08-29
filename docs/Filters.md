# Filters

Clair ships with a word-replacement filter pipeline.

## Levels

- **twitch** – strict profanity filter suitable for streaming.
- **pg13** – family-friendly with mild cursing removed.
- **enabled** – default dictionary for casual use.
- **adult** – minimal filtering.
- **dev0** – filter disabled for local testing.

The replacement tables for each level live in `scripts/filter_system.py`.

## Optional Sentiment Model

For deployments that require additional emotional safeguards, an optional
sentiment classifier can be enabled.  The fallback model is
[`distilroberta-base-go-emotions`](https://huggingface.co/bhadresh-savani/distilroberta-base-go-emotions),
which is released under the permissive MIT license.  When installed the
classifier maps text to positive or negative scores and nudges the agent's
valence accordingly.  This optional component is intended to help meet
content guidelines for North American markets.
