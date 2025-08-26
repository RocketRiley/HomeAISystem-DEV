"""Tier-1 active (working) memory implemented as a bounded queue."""

from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List

from .types import MemoryPacket


class ActiveMemory:
    """Hold the most recent memory packets for immediate context."""

    def __init__(self, maxlen: int = 20) -> None:
        self._buffer: Deque[MemoryPacket] = deque(maxlen=maxlen)

    def push(self, packet: MemoryPacket) -> None:
        """Add a packet to working memory."""
        self._buffer.append(packet)

    def snapshot(self) -> List[MemoryPacket]:
        """Return a list of packets currently in working memory."""
        return list(self._buffer)

    def __iter__(self) -> Iterable[MemoryPacket]:
        return iter(self._buffer)
