"""WebSocket bridge for emotion, transcript and UI events.

This module exposes a small WebSocket server used to communicate between the
Python backend and the Unity front end.  It provides three logical channels:

- ``emotion``: Broadcasts avatar emotion parameters.
- ``transcript``: Sends transcript strings from the speech system.
- ``ui``: Receives UI events such as button clicks or settings changes.

The server groups clients by the request path (``/emotion``, ``/transcript`` or
``/ui``).  Utility functions are provided to publish messages to the
corresponding channel from other Python modules.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Set

import websockets
from websockets.server import WebSocketServerProtocol

# Known channels and their subscribers
CHANNELS = ("emotion", "transcript", "ui")
_clients: Dict[str, Set[WebSocketServerProtocol]] = {c: set() for c in CHANNELS}
# Queue for UI events coming from the Unity client
_ui_events: asyncio.Queue[dict] = asyncio.Queue()


async def _handler(ws: WebSocketServerProtocol, path: str) -> None:
    """WebSocket connection handler."""
    channel = path.strip("/")
    if channel not in _clients:
        await ws.close()
        return
    _clients[channel].add(ws)
    try:
        async for message in ws:
            if channel == "ui":
                try:
                    data = json.loads(message)
                except Exception:
                    continue
                await _ui_events.put(data)
    finally:
        _clients[channel].discard(ws)


async def _broadcast(channel: str, payload: Any) -> None:
    """Send ``payload`` to all clients subscribed to ``channel``."""
    if channel not in _clients:
        return
    message = json.dumps(payload)
    dead: Set[WebSocketServerProtocol] = set()
    for ws in _clients[channel]:
        try:
            await ws.send(message)
        except Exception:
            dead.add(ws)
    for ws in dead:
        _clients[channel].discard(ws)


def publish(channel: str, payload: Any) -> None:
    """Schedule ``payload`` to be sent to subscribers of ``channel``."""
    asyncio.get_event_loop().create_task(_broadcast(channel, payload))


def send_emotion(p: float, a: float, d: float) -> None:
    """Convert PAD values to four common emotion parameters and broadcast."""
    joy = max(0.0, min(1.0, (p + a) / 2))
    angry = max(0.0, min(1.0, (a - p) / 2))
    sorrow = max(0.0, min(1.0, (-p - a) / 2))
    fun = max(0.0, min(1.0, (p - a) / 2))
    publish("emotion", {"Joy": joy, "Angry": angry, "Sorrow": sorrow, "Fun": fun})


def send_transcript(text: str) -> None:
    """Broadcast a transcript string to all listeners."""
    publish("transcript", {"text": text})


async def get_ui_event() -> dict:
    """Return the next UI event sent by the client."""
    return await _ui_events.get()


async def start(host: str = "0.0.0.0", port: int = 8765):
    """Start the WebSocket server and return the server object."""
    return await websockets.serve(_handler, host, port)


async def _run_forever(host: str, port: int) -> None:
    async with websockets.serve(_handler, host, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":  # pragma: no cover - manual execution
    asyncio.run(_run_forever("0.0.0.0", 8765))


__all__ = [
    "start",
    "publish",
    "send_emotion",
    "send_transcript",
    "get_ui_event",
]
