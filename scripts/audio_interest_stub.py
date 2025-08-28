#!/usr/bin/env python3
"""Audio interest monitor for Clair.

Record microphone input using ``sounddevice`` and trigger events when
volume or configured keywords exceed thresholds.  Keyword detection is
performed with the optional ``SpeechRecognition`` package.

Set ``AUDIO_INTEREST_ENABLED=false`` in the ``.env`` file to disable this
feature.
"""

import os
import queue
from typing import List
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    if os.getenv("AUDIO_INTEREST_ENABLED", "true").lower() != "true":
        print("Audio interest monitor is disabled via environment variable.")
        return

    import numpy as np
    import sounddevice as sd

    try:  # Keyword detection is optional
        import speech_recognition as sr
    except Exception:  # pragma: no cover - handled gracefully
        sr = None

    volume_threshold = float(os.getenv("AUDIO_VOLUME_THRESHOLD", "0.02"))
    keywords: List[str] = [
        k.strip().lower() for k in os.getenv("AUDIO_KEYWORDS", "clair,assistant,buddy").split(",")
    ]
    sample_rate = 16_000
    recognizer = sr.Recognizer() if sr else None
    if recognizer is None:
        print("Keyword detection disabled (SpeechRecognition not installed).")

    q: queue.Queue[np.ndarray] = queue.Queue()

    def callback(indata, frames, time, status) -> None:  # noqa: D401
        """Receive audio blocks from sounddevice."""
        if status:
            print(status)
        q.put(indata.copy())

    with sd.InputStream(channels=1, samplerate=sample_rate, callback=callback):
        print("Audio interest monitor started. Press Ctrl+C to stop.")
        try:
            while True:
                data = q.get()
                volume = float(np.linalg.norm(data) / len(data))
                if volume > volume_threshold:
                    print("Audio: Volume threshold exceeded.")
                    if recognizer:
                        data_int16 = np.int16(data * 32767)
                        audio = sr.AudioData(data_int16.tobytes(), sample_rate, 2)
                        try:
                            text = recognizer.recognize_google(audio).lower()
                            for kw in keywords:
                                if kw in text:
                                    print(f"Audio: Keyword '{kw}' detected.")
                                    break
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            print("Audio: Speech recognition service unavailable.")
        except KeyboardInterrupt:
            pass
    print("Audio interest monitor stopped.")


if __name__ == "__main__":
    main()
