from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).resolve().parents[1] / 'scripts'))
from emotion_state import EmotionState


def test_abuse_decays_slowly():
    es = EmotionState()
    es.add_event({"P": -0.5, "A": 0.0, "D": -0.2}, ["abuse"], intensity=1.0)
    es.add_event({"P": -0.5}, ["humor"], intensity=1.0)
    # after 12h, humor should decay much more
    for e in es.events:
        e.timestamp -= 12 * 3600
    mood = es.mood()
    assert mood["P"] <= -0.2  # negative mood persists


def test_evi_gates_output():
    es = EmotionState()
    es.displayed()  # initialise
    es.update_fast({"P": 1.0})
    first = es.displayed()
    es.update_fast({"P": -1.0})
    second = es.displayed()
    assert second == first  # gated due to high EVI


def test_repetition_increases_tau():
    es = EmotionState()
    es.add_event({"P": -0.1}, ["minor_slight"], intensity=1.0, repetition=1.0)
    tau1 = es.events[0].tau_eff
    es.add_event({"P": -0.1}, ["minor_slight"], intensity=1.0, repetition=2.0)
    tau2 = es.events[1].tau_eff
    assert tau2 > tau1
