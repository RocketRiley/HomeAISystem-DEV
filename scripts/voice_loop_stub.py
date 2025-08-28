#!/usr/bin/env python3
"""Simple voice loop integrating wake word, STT and TTS.

This script demonstrates how you could wire together a wake‑word
detector, streaming speech‑to‑text (STT) and text‑to‑speech (TTS)
engine to drive Clair completely hands‑free.  It builds on top of
the existing ``speech_loop_stub.py`` by replacing keyboard input and
console output with real audio pipelines.

**Wake word**:  The example references the `openWakeWord` project, a
Python library that can run a custom wake‑word model offline.  See
<https://github.com/dylansden/openWakeWord> for installation and
model download instructions.  You must provide a `.tflite` model and
set the `WAKE_WORD_MODEL` environment variable or modify the
``openWakeWord.WakeWordEngine`` initialiser.

**STT**:  We recommend the `faster‑whisper` library for streaming
speech recognition.  It runs Whisper models on your CPU or GPU.  See
<https://github.com/guillaumekln/faster-whisper> for installation and
usage.  Alternative placeholders for Vosk or a remote service are
provided and can be selected via the ``STT_ENGINE`` environment
variable.

**TTS**:  For speech synthesis, you can use the `piper` project
(<https://github.com/rhasspy/piper>), Coqui `XTTS`, Suno `Bark`, or
`DiffSinger` for singing voices.  These engines, along with a generic
server option, can be chosen through the ``TTS_ENGINE`` environment
variable.  Here we define simple placeholders; integrate them with
real engines for production use.

To run this script you need to install the above packages and place
the corresponding models in the ``models/`` directory or update
paths accordingly.  Without these dependencies installed, the
placeholders will print debug messages instead of performing real
recognition or synthesis.

This example is non‑blocking: it listens for audio in the background
and only enters the conversation loop after the wake word is heard.
Upon detecting silence or the `sleep` command it will return to a
listening state.
"""

import os
import threading
import time
from pathlib import Path
from typing import Optional

from osc_bridge_stub import send_mouth_open, send_pad

try:
    from smarthome_bridge import SmartHomeBridge  # type: ignore
    from dspy_smarthome_parser import SmartHomeCommandParser  # type: ignore
except Exception:  # pragma: no cover - optional dependencies
    SmartHomeBridge = None  # type: ignore
    SmartHomeCommandParser = None  # type: ignore

try:
    import sounddevice as sd  # type: ignore
except Exception:
    sd = None

try:
    from faster_whisper import WhisperModel  # type: ignore
except Exception:
    WhisperModel = None

try:
    from openWakeWord import WakeWordEngine  # type: ignore
except Exception:
    WakeWordEngine = None


class DummyWakeWord:
    """Fallback wake word engine that never fires."""
    def __init__(self, *args, **kwargs):
        self.threshold = 0.8

    def start(self, callback):
        # No wake word detection; call callback periodically for demo
        def loop():
            while True:
                time.sleep(9999)  # effectively disabled
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        return t

    def stop(self):
        pass


class WhisperSTT:
    """Simple microphone recorder backed by faster‑whisper."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        if WhisperModel is None or sd is None:
            raise RuntimeError("faster-whisper or sounddevice not available")
        model_name = model_path or os.getenv("WHISPER_MODEL", "small")
        self.model = WhisperModel(model_name)

    def listen(self) -> str:
        samplerate = 16000
        duration = float(os.getenv("STT_WINDOW", "5"))
        if sd is None:
            return input("(Say something) > ")
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()
        audio = recording.flatten()
        segments, _ = self.model.transcribe(audio, sampling_rate=samplerate)
        return "".join(seg.text for seg in segments).strip()


class DummySTT:
    """Fallback STT that prompts via stdin."""

    def listen(self) -> str:
        return input("(Say something) > ")


class VoskSTT(DummySTT):
    """Placeholder for a Vosk-based recogniser."""
    pass


class ServerSTT(DummySTT):
    """Placeholder for remote STT service."""
    pass


class PiperTTS:
    """Simple wrapper around piper CLI for offline TTS.

    You need to install piper and provide a voice model.  The
    environment variable ``PIPER_VOICE`` can be used to point to the
    voice file (e.g. `en_US/libri_stretch_low.flite`).  See the
    piper documentation for available voices.  This wrapper
    synthesises the audio into a temp file and plays it back using
    sounddevice.  Modify it to suit your audio output preferences.
    """
    def __init__(self, voice: Optional[str] = None):
        self.voice = voice or os.getenv("PIPER_VOICE")
        self.rate = float(os.getenv("PIPER_RATE", "1.0"))
        if not self.voice:
            print("[TTS] Warning: PIPER_VOICE is not set; speech will not run.")

    def speak(self, text: str) -> None:
        if not self.voice:
            print(f"[TTS] (simulated): {text}")
            return
        # Write text to file and call piper
        tmp_path = Path("/tmp/piper_out.wav")
        cmd = ["piper", "--model", self.voice, "--output_file", str(tmp_path), "--text", text]
        # Adjust speech rate by stretching the audio using sox (optional)
        try:
            import subprocess
            subprocess.run(cmd, check=True)
            # Play file via sounddevice
            if sd is not None:
                import soundfile as sf  # type: ignore
                data, sr = sf.read(tmp_path)
                sd.play(data, sr)
                sd.wait()
            else:
                print(f"[TTS] File synthesised at {tmp_path}, but sounddevice is unavailable.")
        except Exception as e:
            print(f"[TTS] Error during synthesis: {e}")


class XTTS:
    """Placeholder for Coqui XTTS engine."""

    def speak(self, text: str) -> None:
        print(f"[TTS XTTS] {text}")


class BarkTTS:
    """Placeholder for Suno Bark engine."""

    def speak(self, text: str) -> None:
        print(f"[TTS Bark] {text}")


class DiffSingerTTS:
    """Placeholder for DiffSinger engine."""

    def speak(self, text: str) -> None:
        print(f"[TTS DiffSinger] {text}")


class ServerTTS:
    """Placeholder for external TTS service."""

    def speak(self, text: str) -> None:
        print(f"[TTS Server] {text}")


def select_stt():
    """Select STT engine based on environment variable."""
    engine = os.getenv("STT_ENGINE", "whisper").lower()
    if engine == "whisper":
        try:
            return WhisperSTT()
        except Exception:
            return DummySTT()
    if engine == "vosk":
        return VoskSTT()
    if engine == "server":
        return ServerSTT()
    return DummySTT()


def select_tts():
    """Select TTS engine based on environment variable."""
    engine = os.getenv("TTS_ENGINE", "piper").lower()
    if engine == "piper":
        return PiperTTS()
    if engine == "xtts":
        return XTTS()
    if engine == "bark":
        return BarkTTS()
    if engine == "diffsinger":
        return DiffSingerTTS()
    if engine == "server":
        return ServerTTS()
    return PiperTTS()


def main() -> None:
    """Run a voice conversation loop with wake word, STT and TTS.

    This function starts the wake word detection engine, waits for
    activation, then records audio until a pause is detected,
    transcribes it via STT, passes it into the core response logic
    (delegated to ``speech_loop_stub``), and speaks the reply with
    TTS.  For brevity and clarity, this demo uses placeholders
    instead of actual audio streaming.  To integrate properly, you
    should adapt the STT listen loop to your microphone and call
    ``OpinionManager``, ``FilterPipeline`` and other classes as in
    ``speech_loop_stub.py``.
    """
    # Select wake word engine
    if WakeWordEngine is not None:
        model_path = os.getenv("WAKE_WORD_MODEL")
        if model_path:
            ww_engine = WakeWordEngine(models=[model_path])
        else:
            print("[WakeWord] Set WAKE_WORD_MODEL to the path of your .tflite wake word model.")
            ww_engine = DummyWakeWord()
    else:
        ww_engine = DummyWakeWord()
    # Select STT/TTS engines
    stt = select_stt()
    tts = select_tts()

    # Optional smart home helpers
    bridge = SmartHomeBridge() if SmartHomeBridge else None
    parser = SmartHomeCommandParser() if SmartHomeCommandParser else None
    print("Voice loop ready. Say the wake word to begin.")
    # Start wake word detection
    def on_wake():
        print("Wake word detected. Listening…")
        # Listen for a phrase
        text = stt.listen()
        if not text:
            return
        # Attempt smart home parsing first
        handled = False
        if parser and bridge:
            cmd = parser.parse(text)
            if cmd:
                bridge.publish_command(cmd["device"], cmd["action"], cmd.get("value"))
                reply = f"Okay, {cmd['action'].replace('_', ' ')} {cmd['device'].replace('_', ' ')}."
                handled = True
        if not handled:
            # Here you would call into your conversation logic. For demo we just echo.
            reply = f"You said: {text}"
        # Send neutral PAD and mouth-open signals for basic lip-sync
        send_pad(0.0, 0.0, 0.0)
        send_mouth_open(1.0)
        tts.speak(reply)
        send_mouth_open(0.0)

    try:
        ww_engine.start(on_wake)
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping…")
        ww_engine.stop()


if __name__ == "__main__":
    main()
