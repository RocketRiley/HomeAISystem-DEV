from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import List

from .types import MemoryPacket


class MidTermMemory:
    """Tier‑3 project buffer backed by SQLite."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mid_term (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    expiry REAL
                )
                """
            )
        conn.close()

    def add(self, packet: MemoryPacket, expiry: float) -> None:
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute(
                "INSERT INTO mid_term(data, expiry) VALUES (?, ?)",
                (json.dumps(packet.to_dict()), expiry),
            )
        conn.close()

    def fetch_active(self) -> List[MemoryPacket]:
        now = time.time()
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT data FROM mid_term WHERE expiry > ?", (now,))
        rows = [MemoryPacket(**json.loads(r[0])) for r in cur.fetchall()]
        conn.close()
        return rows

    def sweep(self) -> List[MemoryPacket]:
        """Remove expired rows and return them for archiving."""
        now = time.time()
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT id, data FROM mid_term WHERE expiry <= ?", (now,))
        rows = cur.fetchall()
        ids = [r[0] for r in rows]
        packets = [MemoryPacket(**json.loads(r[1])) for r in rows]
        if ids:
            conn.execute(
                "DELETE FROM mid_term WHERE id IN (" + ",".join("?" * len(ids)) + ")",
                ids,
            )
        conn.commit()
        conn.close()
        return packets
