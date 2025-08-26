from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

from .types import MemoryPacket


class LongTermMemory:
    """Tier‑4 knowledge store persisted as JSON."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.entries: List[Dict] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = []

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def reinforce(self, packet: MemoryPacket) -> None:
        """Add or update a memory with increased salience."""
        for entry in self.entries:
            if entry.get("text") == packet.text:
                entry["salience"] = min(1.0, entry.get("salience", 0.5) + 0.1)
                self._save()
                return
        self.entries.append(packet.to_dict())
        self._save()

    def decay(self, threshold: float = 0.2) -> List[MemoryPacket]:
        """Decay salience and return memories that fell below threshold."""
        archived: List[MemoryPacket] = []
        kept: List[Dict] = []
        for entry in self.entries:
            entry["salience"] = entry.get("salience", 0.5) * 0.99
            if entry["salience"] < threshold:
                archived.append(MemoryPacket(**entry))
            else:
                kept.append(entry)
        self.entries = kept
        self._save()
        return archived

    def query(self, text: str) -> List[Dict]:
        return [e for e in self.entries if text.lower() in e.get("text", "").lower()]
