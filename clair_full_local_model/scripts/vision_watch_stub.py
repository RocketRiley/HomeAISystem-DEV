#!/usr/bin/env python3
"""Simulated vision watcher for Clair.

This stub pretends to monitor a TV or display visible in the camera
feed.  It periodically prints a message indicating that a show or
video has been detected.  In a real system, you would integrate
computer vision or OCR here to understand what is on screen and
trigger appropriate behaviour.  Use this as a starting point for
developing your own vision integration.
"""

import random
import time

def main():
    shows = [
        "Nature documentary",
        "Science show",
        "Cooking demonstration",
        "Historical film",
        "Space exploration stream",
        "Robotics competition"
    ]
    print("Starting simulated vision watcher. Press Ctrl+C to stop.")
    try:
        while True:
            show = random.choice(shows)
            print(f"Vision: Detected a TV show on screen → {show}")
            print("You might want to comment or summarize this for the user.\n")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Vision watcher stopped.")


if __name__ == "__main__":
    main()