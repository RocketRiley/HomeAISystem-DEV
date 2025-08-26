from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional
import time


@dataclass
class MemoryPacket:
    timestamp: float
    text: str
    participants: List[str]
    tags: List[str]
    salience: float = 0.5
    expiry: Optional[float] = None

    @classmethod
    def create(
        cls,
        text: str,
        participants: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        salience: float = 0.5,
        expiry: Optional[float] = None,
    ) -> "MemoryPacket":
        return cls(time.time(), text, participants or [], tags or [], salience, expiry)

    def to_dict(self) -> dict:
        return asdict(self)
