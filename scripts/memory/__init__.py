from __future__ import annotations

import time
import os
from pathlib import Path
from typing import List, Optional

from .types import MemoryPacket
from .active import ActiveMemory
from .short_term import ShortTermMemory
from .mid_term import MidTermMemory
from .long_term import LongTermMemory
from .archive import ArchiveMemory

# Determine the root directory for memory storage.  Handlers can override the
# default ``config`` path via the ``MEMORY_ROOT`` environment variable.
BASE_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
CONFIG_DIR = Path(os.getenv("MEMORY_ROOT", BASE_CONFIG_DIR))


class MemoryCoordinator:
    """High level interface coordinating all memory tiers."""

    def __init__(self, user_id: str = "default") -> None:
        self.user_id = user_id
        self.active = ActiveMemory()
        # Ensure tier directories exist and are namespaced per user
        (CONFIG_DIR / "short_term").mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "mid_term").mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "long_term").mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "archive").mkdir(parents=True, exist_ok=True)
        self.short = ShortTermMemory(CONFIG_DIR / "short_term" / f"{user_id}.json")
        self.mid = MidTermMemory(CONFIG_DIR / "mid_term" / f"{user_id}.db")
        self.long = LongTermMemory(CONFIG_DIR / "long_term" / f"{user_id}.json")
        self.archive = ArchiveMemory(CONFIG_DIR / "archive" / f"{user_id}.jsonl.gz")

    # Compatibility methods -------------------------------------------------
    def add_event(
        self,
        text: str,
        participants: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        salience: float = 0.5,
        expiry: Optional[float] = None,
    ) -> None:
        packet = MemoryPacket.create(text, participants, tags, salience, expiry)
        self.add_packet(packet)

    # Core API --------------------------------------------------------------
    def add_packet(self, packet: MemoryPacket) -> None:
        self.active.push(packet)
        self.short.add(packet)
        if packet.expiry:
            self.mid.add(packet, packet.expiry)
        if packet.salience >= 0.8:
            self.long.reinforce(packet)

    def get_last_events(self, n: int = 10) -> List[dict]:
        recent = self.short.get_recent(24)
        return [p.to_dict() for p in recent[-n:]]

    def summarise_day(self, date: str) -> str:
        packets = [p for p in self.short.entries if time.strftime("%Y-%m-%d", time.localtime(p.timestamp)) == date]
        if not packets:
            return f"No events recorded for {date}."
        participants = sorted({p for e in packets for p in e.participants})
        tags = sorted({t for e in packets for t in e.tags})
        texts = [e.text for e in packets]
        summary_parts: List[str] = []
        char_count = 0
        for t in texts:
            for s in t.split('. '):
                s_clean = s.strip()
                if s_clean:
                    summary_parts.append(s_clean)
                    char_count += len(s_clean)
                    if len(summary_parts) >= 3 or char_count > 200:
                        break
            if len(summary_parts) >= 3 or char_count > 200:
                break
        summary_text = '. '.join(summary_parts) + ('...' if summary_parts else '')
        participant_str = ', '.join(participants) if participants else 'none'
        tag_str = ', '.join(tags) if tags else 'none'
        return f"Summary of {date}: participants: {participant_str}; tags: {tag_str}. {summary_text}"

    def consolidate(self) -> None:
        # Move old short-term entries
        old_packets = self.short.prune()
        for p in old_packets:
            if p.salience >= 0.8:
                self.long.reinforce(p)
            else:
                self.archive.store([p])
        # Expire mid-term
        expired = self.mid.sweep()
        if expired:
            self.archive.store(expired)
        # Decay long-term
        demoted = self.long.decay()
        if demoted:
            self.archive.store(demoted)

    # Search ---------------------------------------------------------------
    def search(self, query: str) -> List[dict]:
        results = []
        for p in self.short.entries:
            if query.lower() in p.text.lower():
                results.append(p.to_dict())
        results.extend(self.long.query(query))
        return results


__all__ = ["MemoryCoordinator", "MemoryPacket"]
