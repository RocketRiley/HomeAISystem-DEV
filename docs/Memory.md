# Memory

Clair stores conversations and events across five tiers.

## Tiers

1. **Active** – recent utterances kept in RAM.
2. **Short-term** – 24-hour session log at `config/short_term/<user>.json`.
3. **Mid-term** – time-limited notes in `config/mid_term/<user>.db`.
4. **Long-term** – curated knowledge graph at `config/long_term/<user>.json`.
5. **Archive** – compressed backup in `config/archive/<user>.jsonl.gz`.

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

