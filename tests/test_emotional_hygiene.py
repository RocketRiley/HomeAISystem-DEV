from __future__ import annotations

import json
from pathlib import Path

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from brain import emotional_hygiene as eh


def test_user_offer_respects_cooldown(tmp_path, monkeypatch):
    cfg = {
        "hygiene": {
            "user": {"offer_min_interval_minutes": 60},
            "ai": {"self_check_interval_minutes": 10},
            "allow_home_actions": False,
        }
    }
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))
    log_path = tmp_path / "hlog.jsonl"
    monkeypatch.setattr(eh, "CONFIG_PATH", cfg_path)
    monkeypatch.setattr(eh, "LOG_PATH", log_path)
    monkeypatch.setattr(eh, "make_plan", lambda c, a: {"prompt": "Tell a joke."})
    h = eh.EmotionalHygiene()
    h.user_interval = 9999
    assert h.maybe_cheer_user({"sentiment": -0.5}) is True
    assert h.maybe_cheer_user({"sentiment": -0.9}) is False


def test_self_regulation_triggers(tmp_path, monkeypatch):
    cfg = {
        "hygiene": {
            "user": {"offer_min_interval_minutes": 0},
            "ai": {"self_check_interval_minutes": 0},
            "allow_home_actions": False,
        }
    }
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))
    log_path = tmp_path / "hlog.jsonl"
    monkeypatch.setattr(eh, "CONFIG_PATH", cfg_path)
    monkeypatch.setattr(eh, "LOG_PATH", log_path)
    monkeypatch.setattr(eh, "make_plan", lambda c, a: {"prompt": "Smile"})
    h = eh.EmotionalHygiene(lambda: eh.Mood(valence=-0.6))
    h.self_interval = 9999
    assert h.maybe_cheer_self() is True
    assert h.maybe_cheer_self() is False
