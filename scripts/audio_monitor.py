"""Basic microphone monitor that reports when sound is detected."""

from __future__ import annotations

import threading

try:  # pragma: no cover - optional dependency
    import numpy as np  # type: ignore
    import sounddevice as sd  # type: ignore
except Exception:  # pragma: no cover
    sd = None  # type: ignore
    np = None  # type: ignore


THRESH = 0.01  # crude volume threshold


def _run() -> None:
    if sd is None or np is None:
        print("[Audio] sounddevice/numpy not available; audio monitor disabled.")
        return

    def callback(indata, frames, time, status):  # type: ignore
        if status:
            return
        volume = float(np.linalg.norm(indata) / frames)
        if volume > THRESH:
            print("[Audio] sound detected")

    try:
        with sd.InputStream(callback=callback):
            threading.Event().wait()  # run until process exits
    except Exception:
        print("[Audio] microphone not accessible")


def start_audio_monitor() -> None:
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
