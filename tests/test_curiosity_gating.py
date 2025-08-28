import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts.curiosity_engine import CuriosityEngine, CuriosityContext, EmotionState, MemoryPeek


def _base_ctx(**kwargs):
    default = dict(
        user_text="hi",
        persona_name="Clair",
        mode="enabled",
        dlc_warm_nights=False,
        emotion=EmotionState(0.0, 0.0, 0.0, [], 0.0),
        memory=MemoryPeek([], {}, []),
        turns_since_user_question=2,
        user_tokens_in_last_turn=1,
        now_ts=time.time(),
        last_probe_ts=0.0,
        probes_so_far=0,
        persona_constraints={},
        safety_filter_level="enabled",
        user_led_adult_topic=False,
        active_goal=None,
        emotion_effects=None,
    )
    default.update(kwargs)
    return CuriosityContext(**default)


def test_curiosity_suppressed_by_gravity():
    engine = CuriosityEngine()
    engine._rng.seed(0)
    effects = {"bundle": {"curiosity": 0.8}, "stance": {"gravity": 0.6}, "curiosity": {"suppress_if": True}}
    ctx = _base_ctx(emotion_effects=effects)
    assert engine.maybe_ask(ctx) is None


def test_curiosity_allows_question():
    engine = CuriosityEngine()
    engine._rng.seed(0)
    engine._rng.random = lambda: 0.0
    effects = {"bundle": {"curiosity": 0.8}, "stance": {"gravity": 0.2}}
    ctx = _base_ctx(emotion_effects=effects)
    assert engine.maybe_ask(ctx) is not None
