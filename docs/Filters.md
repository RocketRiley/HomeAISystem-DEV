# Filters

Clair ships with a word-replacement filter pipeline.

## Levels

- **twitch** – strict profanity filter suitable for streaming.
- **pg13** – family-friendly with mild cursing removed.
- **enabled** – default dictionary for casual use.
- **adult** – minimal filtering.
- **dev0** – filter disabled for local testing.

The replacement tables for each level live in `scripts/filter_system.py`.
 codex/resolve-conflict-in-readme.md-74x7dq
=======

 codex/add-sentiment-model-and-documentation
## Optional sentiment model

Deployments that cannot query a full LLM may enable a tiny sentiment
classifier to supply valence hints to the emotion system.  The
`distilroberta-base-go-emotions` model from HuggingFace is bundled as an
optional dependency and loaded by `scripts/emotion_guard.py`.  Its
outputs are mapped to positive or negative scores which the emotion
orchestrator uses for pleasure (valence) adjustments.

The model is distributed under the MIT license.  Verify that any use of
this optional component complies with its license and with North
American content regulations.
=======
## Conversational Tone Limits

During dialogue the emotion orchestrator clamps valence, arousal and
dominance to ±0.6.  Downstream speech and animation systems reference the
clamped values so Clair's vocal delivery and facial expressions remain
within everyday intensity.
 main
