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
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Set


class LogManager:
    """A simple manager that writes JSON log entries to a file.

    Optionally, log entries are broadcast over a WebSocket so that other
    components (e.g. the in‑game diagnostics HUD) can display them in
    real time.  The WebSocket server runs in a background thread and
    accepts JSON messages for each log entry.
    """

    def __init__(self, log_file: str | Path, ws_port: Optional[int] = 8765):
        self.log_file = Path(log_file)
        if not self.log_file.parent.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self._ws_port = ws_port
        self._ws_clients: Set[Any] = set()
        self._ws_loop: Optional[asyncio.AbstractEventLoop] = None

        if ws_port is not None:
            try:
                import websockets  # type: ignore

                self._ws_module = websockets
                self._ws_loop = asyncio.new_event_loop()
                thread = threading.Thread(target=self._run_ws_server, daemon=True)
                thread.start()
            except Exception:
                # If websockets fail to start, disable broadcasting silently
                self._ws_port = None

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
            pass

        if self._ws_port is not None and self._ws_loop is not None:
            try:
                message = json.dumps(entry, ensure_ascii=False)
                asyncio.run_coroutine_threadsafe(
                    self._broadcast(message), self._ws_loop
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # WebSocket support
    def _run_ws_server(self) -> None:
        if self._ws_loop is None:
            return
        asyncio.set_event_loop(self._ws_loop)
        server = self._ws_module.serve(self._ws_handler, "0.0.0.0", self._ws_port)
        self._ws_loop.run_until_complete(server)
        self._ws_loop.run_forever()

    async def _ws_handler(self, websocket, _path) -> None:
        self._ws_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._ws_clients.discard(websocket)

    async def _broadcast(self, message: str) -> None:
        if not self._ws_clients:
            return
        await asyncio.gather(
            *[client.send(message) for client in list(self._ws_clients)],
            return_exceptions=True,
        )
