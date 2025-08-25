#!/usr/bin/env python3
"""Personal calendar manager for Clair and users.

This module provides a simple API for maintaining two separate calendars:
one for Clair herself (``clair``) and one for the primary user
(``user``).  Calendars are stored as JSON lists of event dictionaries
in the ``config/clair_calendar.json`` and ``config/user_calendar.json``
files, respectively.  Each event contains an ``id`` (a string), a
``title``, a ``date`` in ISO format (YYYY‑MM‑DD), ``start`` and
``end`` times (HH:MM), and an optional ``description``.

Functions are provided to list events on a date, add new events, and
retrieve the next upcoming event.  If the calendar files do not
exist they will be created on demand.

Note: This is a very lightweight manager intended for local use.
There is no collision detection, timezone handling, or recurring
event support.  All times are treated as naive local times.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class PersonalCalendar:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        # Calendar files for Clair and the user
        self.files = {
            "clair": base_path / "clair_calendar.json",
            "user": base_path / "user_calendar.json",
        }
        # Ensure files exist
        for f in self.files.values():
            if not f.exists():
                with open(f, "w", encoding="utf-8") as fh:
                    json.dump([], fh)

    def _load(self, who: str) -> List[Dict[str, Any]]:
        path = self.files[who]
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return []

    def _save(self, who: str, events: List[Dict[str, Any]]) -> None:
        path = self.files[who]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(events, fh, indent=2)

    def list_events(self, who: str, date: str) -> List[Dict[str, Any]]:
        """Return all events for a given calendar and date (YYYY‑MM‑DD)."""
        events = self._load(who)
        return [e for e in events if e.get("date") == date]

    def add_event(self, who: str, date: str, start: str, end: str, title: str, description: str = "") -> str:
        """Add an event to the specified calendar and return its new id.

        Args:
            who: "clair" or "user"
            date: event date in ISO format (YYYY‑MM‑DD)
            start: start time (HH:MM)
            end: end time (HH:MM)
            title: summary/title of the event
            description: optional extra details

        Returns:
            The id of the newly created event as a string.
        """
        events = self._load(who)
        # Generate a simple numeric id
        next_id = str((max([int(e.get("id", "0")) for e in events]) + 1) if events else 1)
        event = {
            "id": next_id,
            "date": date,
            "start": start,
            "end": end,
            "title": title,
            "description": description,
        }
        events.append(event)
        # Sort events by date/time for convenience
        events.sort(key=lambda e: (e.get("date"), e.get("start")))
        self._save(who, events)
        return next_id

    def get_next_event(self, who: Optional[str] = None, now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Return the next upcoming event after ``now`` for one or both calendars.

        Args:
            who: "clair", "user", or None (both).  If None, the next event
                across both calendars is returned.
            now: a datetime instance representing the current time.

        Returns:
            The event dictionary, or None if no future events exist.
        """
        now = now or datetime.utcnow()
        candidates: List[Dict[str, Any]] = []
        cals = [who] if who else ["clair", "user"]
        for cal in cals:
            for e in self._load(cal):
                date_str = e.get("date")
                start_str = e.get("start")
                if not date_str or not start_str:
                    continue
                try:
                    dt = datetime.fromisoformat(f"{date_str}T{start_str}:00")
                except Exception:
                    continue
                if dt >= now:
                    # attach calendar owner for context
                    evt = {**e, "who": cal}
                    candidates.append(evt)
        if not candidates:
            return None
        return min(candidates, key=lambda e: (e.get("date"), e.get("start")))


if __name__ == "__main__":
    # Quick manual test
    base = Path(__file__).resolve().parent.parent / "config"
    pc = PersonalCalendar(base)
    eid = pc.add_event("clair", "2025-08-26", "10:00", "11:00", "Test event", "demo description")
    print("Added event", eid)
    print("Events on 2025-08-26:", pc.list_events("clair", "2025-08-26"))
    print("Next event:", pc.get_next_event())