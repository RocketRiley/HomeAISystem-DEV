#!/usr/bin/env python3
"""Local calendar integration stub for Clair.

This module provides a basic interface to a calendar stored in a
JSON file.  It can load events, list events for a specific date,
and find the next upcoming event relative to the current time.  It
serves as a placeholder for a real calendar service (e.g. Google
Calendar, Nextcloud or CalDAV).  To use it, create a file
``config/calendar_events.json`` containing an array of events with
``start``, ``end``, ``title`` and optional ``description`` and
``location`` fields.  See the example in that file.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class CalendarIntegration:
    """Load and query events from a JSON calendar file."""

    def __init__(self, path: Any) -> None:
        self.path = Path(path)
        self.events: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.events = json.load(f)
            except Exception:
                self.events = []
        else:
            self.events = []

    def list_events_on(self, date: str) -> List[Dict[str, Any]]:
        """Return all events starting on the given date (YYYY-MM-DD)."""
        results = []
        for event in self.events:
            start = event.get("start")
            if start and start.startswith(date):
                results.append(event)
        return results

    def get_next_event(self, now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Return the next event occurring after ``now``.

        Parameters
        ----------
        now: datetime, optional
            The reference time.  If not provided, the current UTC
            time is used.

        Returns
        -------
        dict or None
            The event with the earliest start time after ``now``, or
            ``None`` if there are no upcoming events.
        """
        if now is None:
            now = datetime.utcnow()
        upcoming: List[Dict[str, Any]] = []
        for event in self.events:
            start_str = event.get("start")
            if not start_str:
                continue
            try:
                start_dt = datetime.fromisoformat(start_str)
            except Exception:
                continue
            if start_dt >= now:
                upcoming.append((start_dt, event))
        if not upcoming:
            return None
        upcoming.sort(key=lambda x: x[0])
        return upcoming[0][1]


__all__ = ["CalendarIntegration"]