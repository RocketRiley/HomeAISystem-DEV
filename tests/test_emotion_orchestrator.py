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


def test_apply_sentiment_adjusts_valence():
    ebo = EmotionOrchestrator()
    pad = PAD(pleasure=0.0, arousal=0.0, dominance=0.0)
    pad_pos = ebo.apply_sentiment(pad, positive=0.8, negative=0.2)
    assert abs(pad_pos.pleasure - 0.6) < 1e-6
    pad_neg = ebo.apply_sentiment(pad, positive=0.1, negative=0.7)
    assert abs(pad_neg.pleasure + 0.6) < 1e-6
