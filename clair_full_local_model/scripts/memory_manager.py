#!/usr/bin/env python3
"""Simple episodic memory manager for Clair.

This module provides a lightweight mechanism for logging events and
summarising them over time.  Each event entry captures a timestamp,
the text of the interaction, a list of participants (e.g. user IDs),
and a set of tags describing the nature of the event (e.g.
"science", "reminder", "emotion").  The memory is persisted to
``config/memory.json``.  A :class:`MemoryManager` instance can append
events, return recent history, and summarise events by day.

The summarisation here is intentionally simplistic: it groups all
messages from a day and returns the first few sentences along with a
list of unique participants and tags.  In a production system you
would likely replace this with a proper summarisation model and
embedding retrieval.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryManager:
    """Manage the assistant's episodic memory.

    Parameters
    ----------
    path: str or Path
        Path to a JSON file used for persisting the memory log.
    """
    def __init__(self, path: Any) -> None:
        self.path = Path(path)
        self.memory: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except Exception:
                self.memory = []
        else:
            self.memory = []

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception:
            pass

    def add_event(self, text: str, participants: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> None:
        """Append a new event to the memory log.

        Parameters
        ----------
        text: str
            A description of what occurred (e.g. a transcript snippet,
            comment, summary).
        participants: list of str, optional
            Identifiers of people involved in the event.  Could be
            Twitch usernames, local user names, or contact IDs.
        tags: list of str, optional
            Keywords describing the event (e.g. ["science", "daily_log"]).
        """
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "text": text,
            "participants": participants or [],
            "tags": tags or []
        }
        self.memory.append(entry)
        self._save()

    def get_last_events(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return the most recent ``n`` events."""
        return self.memory[-n:]

    def summarise_day(self, date: str) -> str:
        """Return a simple summary of all events that occurred on a given date.

        Parameters
        ----------
        date: str
            Date in ISO format (YYYY-MM-DD).  Only events whose
            timestamps begin with this date will be summarised.

        Returns
        -------
        str
            A human‑readable summary including a list of participants
            and a brief concatenation of the first few sentences.
        """
        # Filter events by date
        events = [e for e in self.memory if e.get("timestamp", "").startswith(date)]
        if not events:
            return f"No events recorded for {date}."
        # Gather unique participants and tags
        participants = sorted({p for e in events for p in e.get("participants", [])})
        tags = sorted({t for e in events for t in e.get("tags", [])})
        # Concatenate first sentences
        texts = [e.get("text", "") for e in events]
        # Take the first 3 sentences or up to 200 characters as a crude summary
        summary_parts: List[str] = []
        char_count = 0
        for t in texts:
            sentences = t.split(". ")
            for s in sentences:
                s_clean = s.strip()
                if s_clean:
                    summary_parts.append(s_clean)
                    char_count += len(s_clean)
                    if len(summary_parts) >= 3 or char_count > 200:
                        break
            if len(summary_parts) >= 3 or char_count > 200:
                break
        summary_text = ". ".join(summary_parts) + ("..." if len(summary_parts) > 0 else "")
        participant_str = ", ".join(participants) if participants else "none"
        tag_str = ", ".join(tags) if tags else "none"
        return f"Summary of {date}: participants: {participant_str}; tags: {tag_str}. {summary_text}"


__all__ = ["MemoryManager"]