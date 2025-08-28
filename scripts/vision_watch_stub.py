#!/usr/bin/env python3
"""Vision watcher for Clair.

Capture frames from the default camera using OpenCV and perform basic
scene change and face detection.  This is intentionally lightweight and
serves as a starting point for integrating richer computer-vision logic.

Set ``VISION_WATCH_ENABLED=false`` in the ``.env`` file to disable this
feature.
"""

import os
import time
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    if os.getenv("VISION_WATCH_ENABLED", "true").lower() != "true":
        print("Vision watcher is disabled via environment variable.")
        return

    import cv2
    import numpy as np

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Vision: Could not open camera.")
        return

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    prev_gray: np.ndarray | None = None

    print("Vision watcher started. Press Ctrl+C to stop.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Vision: Failed to grab frame.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 0:
                print(f"Vision: Detected {len(faces)} face(s).")
            elif prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                if diff.mean() > 10:
                    print("Vision: Scene changed.")
            prev_gray = gray

            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Vision watcher stopped.")


if __name__ == "__main__":
    main()
