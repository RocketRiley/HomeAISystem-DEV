from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

from .types import MemoryPacket


class ShortTermMemory:
    """Tier‑2 session log persisted per user."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.entries: List[MemoryPacket] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.entries = [MemoryPacket(**e) for e in data]
            except Exception:
                self.entries = []

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in self.entries], f, indent=2)
        except Exception:
            pass

    def add(self, packet: MemoryPacket) -> None:
        self.entries.append(packet)
        self._save()

    def get_recent(self, hours: int = 24) -> List[MemoryPacket]:
        cutoff = time.time() - hours * 3600
        return [p for p in self.entries if p.timestamp >= cutoff]

    def prune(self) -> List[MemoryPacket]:
        """Remove entries older than 24h and return them."""
        cutoff = time.time() - 24 * 3600
        old = [p for p in self.entries if p.timestamp < cutoff]
        if old:
            self.entries = [p for p in self.entries if p.timestamp >= cutoff]
            self._save()
        return old
