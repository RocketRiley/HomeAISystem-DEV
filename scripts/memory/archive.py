from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterable, List

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
