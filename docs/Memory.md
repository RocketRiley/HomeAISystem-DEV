# Memory

Clair stores conversations and events across five tiers.

## Tiers

1. **Active** – recent utterances kept in RAM.
codex/resolve-conflict-in-readme.md-154yk5
=======
 codex/resolve-conflict-in-readme.md-ookl8l
main
2. **Short-term** – 24-hour session log at `config/short_term/{user}.json`.
3. **Mid-term** – time-limited notes in `config/mid_term/{user}.db`.
4. **Long-term** – curated knowledge graph at `config/long_term/{user}.json`.
5. **Archive** – compressed backup in `config/archive/{user}.jsonl.gz`.
 codex/resolve-conflict-in-readme.md-154yk5
=======
=======
2. **Short-term** – 24-hour session log at `config/short_term/<user>.json`.
3. **Mid-term** – time-limited notes in `config/mid_term/<user>.db`.
4. **Long-term** – curated knowledge graph at `config/long_term/<user>.json`.
5. **Archive** – compressed backup in `config/archive/<user>.jsonl.gz`.
 main
 main

## Promotion and consolidation

A background consolidator promotes salient events and archives old data so the
system runs indefinitely:

```python
from scripts.memory import MemoryCoordinator
mc = MemoryCoordinator()
mc.add_event("Met Alice for coffee", participants=["Alice"], salience=0.9)
mc.consolidate()
```

In the example above a notable event is added and then consolidated, moving
expired or low-salience items into the archive.

 codex/resolve-conflict-in-readme.md-154yk5
=======
 codex/resolve-conflict-in-readme.md-ookl8l
 main
## Daily summarization and proactive recall

During consolidation, short‑term logs older than a day are combined into a
"daily newspaper" summary via the local LLM. If any future events are mentioned,
they are added to the personal calendar and a mid‑term reminder is scheduled
three days beforehand. The helper `check_proactive_events()` surfaces due
reminders and follow‑up questions about events from the previous day so Clair
can proactively bring them up with the user.
 codex/resolve-conflict-in-readme.md-154yk5
=======
=======
 main
 main
