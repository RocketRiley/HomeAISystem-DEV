"""Simple camera monitoring that reports basic face detections."""

from __future__ import annotations

import threading

try:  # pragma: no cover - optional dependency
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore


def _run() -> None:
    if cv2 is None:
        print("[Vision] OpenCV not available; vision monitor disabled.")
        return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Vision] Camera not accessible.")
        return
    classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = classifier.detectMultiScale(gray, 1.3, 5)
        if len(faces):
            print("[Vision] face detected")
        if cv2.waitKey(1) == 27:  # ESC to quit when running standalone
            break
    cap.release()


def start_vision_monitor() -> None:
    """Launch the vision monitor in a background thread."""
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
