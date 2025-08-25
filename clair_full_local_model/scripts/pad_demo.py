#!/usr/bin/env python3
"""A simple demonstration of the PAD (Pleasure–Arousal–Dominance) system.

This script loads the emotion definitions from the emotion pack and
spikes a few emotions to show how their PAD projections blend over
time.  It also uses the TTS mapping in `emotion_pack/config.json` to
compute example speech parameters (rate, pitch, energy, pause).

Run this script from the root of the `clair_local_model` directory:

    python scripts/pad_demo.py

The output shows the time in seconds, the current PAD values and the
resulting TTS settings.
"""

import json
import math
import os
import time
from pathlib import Path


def load_emotion_pack():
    """Load emotions and configuration from the emotion_pack folder."""
    base = Path(__file__).resolve().parent.parent / "emotion_pack"
    with open(base / "emotions.json", "r", encoding="utf-8") as f:
        emotions_data = json.load(f)
    with open(base / "config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    # Convert emotions list into dict keyed by name for easier access
    emo_dict = {}
    for item in emotions_data["emotions"]:
        emo_dict[item["name"]] = {
            "pad": item["pad"],
            "half_life_s": item["half_life_s"]
        }
    return emo_dict, config


def decay(value, hl, dt):
    """Exponential decay based on half‑life hl (seconds)."""
    if hl <= 0:
        return value
    return value * math.exp(-math.log(2) * dt / hl)


def compute_pad(active_emotions, emo_defs):
    """Compute the blended PAD values from active emotions.

    `active_emotions` is a dict of emotion name → intensity (0..1).
    Returns a dict with P, A and D in the range [-1, +1].
    """
    total = sum(active_emotions.values()) or 1e-9
    P = sum(active_emotions[name] * emo_defs[name]["pad"]["P"] for name in active_emotions) / total
    A = sum(active_emotions[name] * emo_defs[name]["pad"]["A"] for name in active_emotions) / total
    D = sum(active_emotions[name] * emo_defs[name]["pad"]["D"] for name in active_emotions) / total
    return {"P": P, "A": A, "D": D}


def tts_params(pad, mapping):
    """Compute TTS parameters from PAD values and mapping config."""
    rate_base = mapping["rate_base"]
    pitch_base = mapping["pitch_base"]
    energy_base = mapping["energy_base"]
    pause_base = mapping["pause_base"]
    rate = rate_base + mapping["kA"] * pad["A"]
    pitch = pitch_base + mapping["kP"] * (pad["P"] + 0.3 * pad["D"])
    energy = energy_base + mapping["kE"] * (pad["A"] + 0.2 * pad["D"])
    pause = max(0.0, pause_base - mapping["kS"] * pad["A"])
    return {"rate": round(rate, 3), "pitch": round(pitch, 3), "energy": round(energy, 3), "pause": round(pause, 3)}


def main():
    emotions, config = load_emotion_pack()
    mapping = config["tts_mapping"]
    # Active emotion intensities
    active = {name: 0.0 for name in emotions.keys()}
    # Spike a couple of emotions at t=0
    active["excitement"] = 0.8
    active["curiosity"] = 0.4
    print("Demonstrating PAD and TTS mappings over 20 seconds.\n")
    for t in range(21):
        # Compute PAD and TTS parameters
        pad = compute_pad(active, emotions)
        tts = tts_params(pad, mapping)
        print(f"t={t:02d}s -> PAD={pad}  TTS={tts}")
        # Decay emotions each second
        time.sleep(1)
        for name in list(active.keys()):
            active[name] = decay(active[name], emotions[name]["half_life_s"], 1)

    print("\nDemo complete. You can modify this script to trigger different emotions and observe their effects.")


if __name__ == "__main__":
    main()