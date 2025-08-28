from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterable, List
from datetime import datetime, timedelta

from .types import MemoryPacket


class ArchiveMemory:
    """Tier‑5 archival storage using compressed JSONL."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def store(self, packets: Iterable[MemoryPacket]) -> None:
        mode = "ab" if self.path.exists() else "wb"
        with gzip.open(self.path, mode) as f:
            for p in packets:
                line = json.dumps(p.to_dict()).encode("utf-8") + b"\n"
                f.write(line)

    def fetch_by_tags(self, tags: List[str]) -> List[MemoryPacket]:
        if not self.path.exists():
            return []
        result: List[MemoryPacket] = []
        with gzip.open(self.path, "rb") as f:
            for line in f:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if set(tags).issubset(set(data.get("tags", []))):
                        result.append(MemoryPacket(**data))
                except Exception:
                    continue
        return result

    def purge_old_memories(self, age_threshold_days: int, salience_threshold: float) -> None:
        """Remove memories older than ``age_threshold_days`` with salience below ``salience_threshold``."""
        if not self.path.exists():
            return
        cutoff = datetime.utcnow() - timedelta(days=age_threshold_days)
        tmp_path = self.path.with_suffix(".tmp")
        with gzip.open(self.path, "rb") as src, gzip.open(tmp_path, "wb") as dst:
            for line in src:
                try:
                    data = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                ts = datetime.utcfromtimestamp(data.get("timestamp", 0))
                sal = float(data.get("salience", 0.0))
                if ts < cutoff and sal < salience_threshold:
                    continue
                dst.write(line)
        tmp_path.replace(self.path)
