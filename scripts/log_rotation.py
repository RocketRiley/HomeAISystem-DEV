#!/usr/bin/env python3
"""Utility for rotating log files and pruning old archives.

This module checks JSONL log files under ``logs/`` (e.g. ``stt.jsonl`` and
``llm.jsonl``) and rotates them either when the file grows beyond a size
threshold or when a new day begins.  Rotated logs are compressed to
``.gz`` archives and older archives are deleted after a retention period.

Environment variables
---------------------
``LOG_ROTATION_SIZE_MB``  Size threshold in megabytes (default: 5).
``LOG_RETENTION_DAYS``    Number of days to keep archived logs (default: 30).
``LOG_DIR``               Base directory for logs (default: ``logs``).
"""
from __future__ import annotations

import gzip
import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


def rotate_logs(log_files: Iterable[Path], size_threshold: int, retention_days: int) -> None:
    """Rotate and prune the given log files.

    Parameters
    ----------
    log_files:
        Iterable of log file paths to examine.
    size_threshold:
        Maximum allowed size in bytes before rotation occurs.
    retention_days:
        Age in days after which archived logs are removed.
    """
    now = datetime.utcnow()
    today = now.date()

    for path in log_files:
        if not path.exists():
            continue
        stat = path.stat()
        file_date = datetime.utcfromtimestamp(stat.st_mtime).date()
        if stat.st_size >= size_threshold or file_date < today:
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            rotated = path.with_name(f"{path.stem}-{timestamp}{path.suffix}")
            path.rename(rotated)
            # Compress rotated file
            with open(rotated, "rb") as src, gzip.open(f"{rotated}.gz", "wb") as dst:
                shutil.copyfileobj(src, dst)
            rotated.unlink()

    # Prune old archives
    cutoff = now - timedelta(days=retention_days)
    log_dir = Path(log_files[0]).parent if log_files else Path(os.getenv("LOG_DIR", "logs"))
    for archive in log_dir.glob("*.gz"):
        mtime = datetime.utcfromtimestamp(archive.stat().st_mtime)
        if mtime < cutoff:
            archive.unlink(missing_ok=True)


def rotate_logs_periodically(
    interval_seconds: int = 24 * 60 * 60,
    log_files: Iterable[Path] | None = None,
    size_mb: int | None = None,
    retention_days: int | None = None,
) -> threading.Thread:
    """Start a background thread that periodically rotates logs."""
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    default_files = [log_dir / "stt.jsonl", log_dir / "llm.jsonl"]
    files = list(log_files) if log_files else default_files
    size_threshold = int((size_mb or int(os.getenv("LOG_ROTATION_SIZE_MB", "5"))) * 1024 * 1024)
    retention = retention_days or int(os.getenv("LOG_RETENTION_DAYS", "30"))

    def loop() -> None:
        while True:
            try:
                rotate_logs(files, size_threshold, retention)
            except Exception:
                pass
            time.sleep(interval_seconds)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t


def main() -> None:
    """Run a single rotation pass using default settings."""
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    log_files = [log_dir / "stt.jsonl", log_dir / "llm.jsonl"]
    size_threshold = int(os.getenv("LOG_ROTATION_SIZE_MB", "5")) * 1024 * 1024
    retention_days = int(os.getenv("LOG_RETENTION_DAYS", "30"))
    rotate_logs(log_files, size_threshold, retention_days)


if __name__ == "__main__":
    main()
