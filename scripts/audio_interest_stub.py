#!/usr/bin/env python3
"""Simulated audio interest trigger for Clair.

This stub mimics audio analysis by periodically generating events such
as the user repeatedly calling Clair's name or interesting sounds
captured by a microphone.  In a real system you would integrate
wake‑word detection, speaker diarisation and sound classification.
"""

import random
import time

def main():
    names = ["clair", "assistant", "buddy"]
    sounds = ["doorbell", "phone ringing", "kitchen timer", "alarm"]
    print("Starting simulated audio interest monitor. Press Ctrl+C to stop.")
    count = 0
    try:
        while True:
            time.sleep(6)
            # Alternate between name calls and interesting sounds
            if count % 2 == 0:
                name = random.choice(names)
                print(f"Audio: Heard '{name}' called repeatedly – getting user's attention.\n")
            else:
                sound = random.choice(sounds)
                print(f"Audio: Detected sound '{sound}' – potential event to handle.\n")
            count += 1
    except KeyboardInterrupt:
        print("Audio interest monitor stopped.")


if __name__ == "__main__":
    main()