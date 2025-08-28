import json
from pathlib import Path

from emotion.orchestrator import EmotionOrchestrator, PAD


def test_prosody_mapping(tmp_path):
    ebo = EmotionOrchestrator()
    bundle = {"melancholy": 0.7}
    stance = {"gravity": 0.5, "warmth": 0.0, "enthusiasm": 0.0}
    pad = PAD(pleasure=0.0, arousal=0.0, dominance=0.0)
    effects = ebo.effects(bundle, stance, pad, [])
    prosody = effects["prosody"]
    # Values scaled by weight 0.7
    assert abs(prosody["rate"] + 0.07) < 1e-6
    assert abs(prosody["pitch"] + 0.035) < 1e-6
    assert abs(prosody["pause_ms"] - 84.0) < 1e-6
