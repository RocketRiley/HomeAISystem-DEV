#!/usr/bin/env python3
"""Generate daily memory roll‑ups for Clair.

This script loads the episodic memory from ``config/memory.json`` and
prints a summary for a specified date (default: yesterday).  It
leverages the ``MemoryManager`` class from ``memory_manager.py`` to
collate events, participants and tags into a single digest.  In a
full integration you might schedule this script via cron or call it
from inside your application at midnight to produce a daily recap
and perhaps feed it back into Clair's long‑term memory or send it to
the user.

Usage:

    python scripts/daily_rollup.py          # summarise yesterday
    python scripts/daily_rollup.py 2025-08-25  # summarise 25th Aug 2025
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from memory_manager import MemoryManager  # type: ignore


def main(date_str: str) -> None:
    mem_path = Path(__file__).resolve().parent.parent / "config" / "memory.json"
    mm = MemoryManager(mem_path)
    summary = mm.summarise_day(date_str)
    print(summary)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        # Default to yesterday in local timezone
        today = datetime.utcnow().date()
        date_str = (today - timedelta(days=1)).isoformat()
    main(date_str)