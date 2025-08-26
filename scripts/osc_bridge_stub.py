"""Send PAD emotion values to VSeeFace over OSC."""
from __future__ import annotations

import os
from typing import Optional

try:  # pragma: no cover - optional dependency
    from pythonosc.udp_client import SimpleUDPClient
except Exception:  # pragma: no cover
    SimpleUDPClient = None  # type: ignore

client: Optional[SimpleUDPClient] = None


def _client() -> Optional[SimpleUDPClient]:
    """Return a cached OSC client if python-osc is available."""
    global client
    if SimpleUDPClient is None:
        return None
    if client is None:
        host = os.getenv("OSC_HOST", "127.0.0.1")
        port = int(os.getenv("OSC_PORT", "9000"))
        client = SimpleUDPClient(host, port)
    return client


def send_pad(p: float, a: float, d: float) -> None:
    """Map Pleasure‑Arousal‑Dominance values to VSeeFace blendshapes."""
    c = _client()
    if c is None:
        return
    # Basic mapping from PAD to four common emotions
    joy = max(0.0, min(1.0, (p + a) / 2))
    angry = max(0.0, min(1.0, (a - p) / 2))
    sorrow = max(0.0, min(1.0, (-p + -a) / 2))
    fun = max(0.0, min(1.0, (p - a) / 2))
    c.send_message("/avatar/parameters/Joy", joy)
    c.send_message("/avatar/parameters/Angry", angry)
    c.send_message("/avatar/parameters/Sorrow", sorrow)
    c.send_message("/avatar/parameters/Fun", fun)


__all__ = ["send_pad"]
