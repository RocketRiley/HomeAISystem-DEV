#!/usr/bin/env python3
"""Show a status board with tasks, calendar, mood and filters.

This script provides a quick textual dashboard of Clair's current
state.  It lists upcoming tasks (due in the next three days), the
next calendar event, a simple mood indicator based on the last few
logged events, the active content filter level (from the environment)
and the relationship metrics for the primary user (assumed "riley").
You can run it at any time to see how Clair is doing and what she
thinks you should pay attention to.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from memory_manager import MemoryManager  # type: ignore
from tasks_manager import TaskManager  # type: ignore
from calendar_integration_stub import CalendarIntegration  # type: ignore
from personal_calendar_manager import PersonalCalendar  # type: ignore
from contact_manager import ContactManager  # type: ignore


def simple_mood(memory_manager: MemoryManager) -> str:
    """Derive a coarse mood label from recent memory events.

    This function looks at the last 10 events and counts positive and
    negative keywords.  It's a placeholder for a real mood estimator.
    """
    positive_words = {"great", "fun", "success", "happy", "good"}
    negative_words = {"bad", "tired", "sad", "problem", "frustrated"}
    events = memory_manager.get_last_events(10)
    pos = neg = 0
    for e in events:
        text = e.get("text", "").lower()
        for w in positive_words:
            if w in text:
                pos += 1
        for w in negative_words:
            if w in text:
                neg += 1
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def main() -> None:
    # Paths
    base = Path(__file__).resolve().parent.parent
    tasks_path = base / "config" / "tasks.json"
    calendar_path = base / "config" / "calendar_events.json"
    contacts_path = base / "config" / "contacts.json"
    user_id = "default"
    # Load managers
    mm = MemoryManager(user_id)
    tm = TaskManager(tasks_path)
    cal = CalendarIntegration(calendar_path)
    # Personal calendars (Clair and user)
    personal = PersonalCalendar(base / "config")
    cm = ContactManager(contacts_path)
    # Active filter
    filter_level = os.getenv("FILTER_LEVEL", "enabled").lower()
    # Upcoming tasks (within next 3 days)
    now = datetime.utcnow()
    horizon = now + timedelta(days=3)
    upcoming_tasks = []
    for t in tm.list_tasks(False):
        due_str = t.get("due")
        if not due_str:
            continue
        try:
            due_dt = datetime.fromisoformat(due_str)
        except Exception:
            continue
        if now <= due_dt <= horizon:
            upcoming_tasks.append(t)
    upcoming_tasks.sort(key=lambda t: t.get("due"))
    # Next calendar event: combine personal (clair & user) with external
    next_external = cal.get_next_event(now)
    next_personal = personal.get_next_event(None, now)
    def parse_time(evt):
        if not evt:
            return datetime.max
        if "date" in evt:
            # personal event
            return datetime.fromisoformat(f"{evt['date']}T{evt['start']}:00")
        return datetime.fromisoformat(evt.get("start"))
    next_event = None
    if next_external or next_personal:
        candidates = []
        if next_external:
            candidates.append((parse_time(next_external), next_external, "external"))
        if next_personal:
            candidates.append((parse_time(next_personal), next_personal, next_personal.get("who")))
        candidates.sort(key=lambda x: x[0])
        next_event = candidates[0]
    # Mood
    mood = simple_mood(mm)
    # Contact feelings
    contact = cm.get("riley")
    feelings = contact.get("feelings", {}) if contact else {}
    # Print status
    print("=== Clair Status Board ===")
    print(f"Filter level: {filter_level}")
    print(f"Mood (simple): {mood}")
    if next_event:
        _, evt, owner = next_event
        if owner == "external":
            title = evt.get("title", "(no title)")
            start = evt.get("start")
            print(f"Next event: {start} – {title}")
        else:
            title = evt.get("title", "(no title)")
            date = evt.get("date")
            start = evt.get("start")
            # Distinguish Clair vs user calendar
            who = "my" if owner == "clair" else "your"
            print(f"Next event: {date} {start} – {title} ({who} calendar)")
    else:
        print("Next event: none")
    print("Upcoming tasks (next 3 days):")
    if not upcoming_tasks:
        print("  none")
    else:
        for t in upcoming_tasks:
            print(f"  {t['due']} – {t['description']} (id: {t['id']})")
    if contact:
        print(f"Relationship with {contact['id']}: valence={feelings.get('valence',0.0):.2f}, trust={feelings.get('trust',0.0):.2f}, familiarity={feelings.get('familiarity',0.0):.2f}")
    else:
        print("No contact record for user.")


if __name__ == "__main__":
    main()