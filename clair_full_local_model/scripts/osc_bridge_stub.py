#!/usr/bin/env python3
"""OSC bridge stub for driving a VRM model.

This script sends simple Joy/Angry/Sorrow/Fun values over OSC to
demonstrate how the PAD values might be mapped to animation
parameters in a VRM avatar (e.g. in VSeeFace).  It reads the OSC
host and port from the environment variables `OSC_HOST` and
`OSC_PORT` (see `.env.example`).

The values are generated using sine waves so that you can see the
avatar cycle through different emotions.  Replace this logic with
real PAD‑to‑blendshape mapping to control the avatar based on
Clair's actual mood.
"""

import math
import os
import time
from dotenv import load_dotenv
from pythonosc.udp_client import SimpleUDPClient


def main():
    load_dotenv()
    host = os.getenv("OSC_HOST", "127.0.0.1")
    port = int(os.getenv("OSC_PORT", "9000"))
    client = SimpleUDPClient(host, port)
    print(f"Sending OSC messages to {host}:{port}. Press Ctrl+C to stop.")
    t = 0
    try:
        while True:
            # Generate cyclic values between 0 and 1
            joy = 0.5 * (math.sin(t * 0.1) + 1.0)
            sorrow = 0.5 * (math.sin(t * 0.1 + math.pi) + 1.0)
            angry = 0.5 * (math.sin(t * 0.1 + math.pi / 2) + 1.0)
            fun = 0.5 * (math.sin(t * 0.1 - math.pi / 2) + 1.0)
            # Send OSC messages to common blendshape names
            client.send_message("/avatar/parameters/Joy", joy)
            client.send_message("/avatar/parameters/Angry", angry)
            client.send_message("/avatar/parameters/Sorrow", sorrow)
            client.send_message("/avatar/parameters/Fun", fun)
            # Print for visibility
            print(f"t={t:04d} joy={joy:.2f} angry={angry:.2f} sorrow={sorrow:.2f} fun={fun:.2f}")
            t += 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping OSC bridge.")


if __name__ == "__main__":
    main()