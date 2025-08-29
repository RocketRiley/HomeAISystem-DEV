import json
from pathlib import Path
 codex/resolve-conflict-in-readme.md-74x7dq
=======
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
 main

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
 codex/resolve-conflict-in-readme.md-74x7dq
=======

def test_stance_clamps_extreme_pad_values():
    ebo = EmotionOrchestrator()
    pad_low = PAD(pleasure=2.0, arousal=-2.0, dominance=5.0)
    stance = ebo.stance({}, pad_low, None, None)
    assert all(0.0 <= v <= 1.0 for v in stance.values())
    assert stance["enthusiasm"] == 0.0
    pad_high = PAD(pleasure=-2.0, arousal=2.0, dominance=-5.0)
    stance_high = ebo.stance({}, pad_high, None, None)
    assert stance_high["enthusiasm"] == 1.0
 main
