#!/usr/bin/env python3
"""Simple log manager for Clair.

This module provides a LogManager class that appends entries to a
log file.  Each entry is expected to be a dictionary that can be
serialised to JSON.  The manager will create the log file and
its directory if they do not already exist.  Logs are stored in
``config/logs.jsonl`` by default (one JSON object per line).

The logging system is intended to help developers trace user
interactions, assistant replies and other events for debugging
purposes.  It is lightweight and does not block on errors.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class LogManager:
    """A simple manager that writes JSON log entries to a file."""

    def __init__(self, log_file: str | Path):
        self.log_file = Path(log_file)
        # Ensure parent directory exists
        if not self.log_file.parent.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, entry: Dict[str, Any]) -> None:
        """Append a dictionary as a JSON line to the log file.

        Parameters
        ----------
        entry: Dict[str, Any]
            The data to log.  A timestamp will be added if not present.
        """
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")
        except Exception:
            # Silently ignore logging errors
            pass
