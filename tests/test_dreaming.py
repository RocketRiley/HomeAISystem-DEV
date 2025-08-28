from __future__ import annotations

import json
from pathlib import Path

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from brain import dreaming


def test_run_nightly_writes_journal(tmp_path, monkeypatch):
    cfg = {
        "dreams": {
            "enabled": True,
            "max_minutes": 1,
            "max_tokens": 50,
            "store_full": True,
            "share_morning_one_liner": True,
        }
    }
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))
    log_path = tmp_path / "dream.log"
    monkeypatch.setattr(dreaming, "CONFIG_PATH", cfg_path)
    monkeypatch.setattr(dreaming, "LOG_PATH", log_path)

    calls = []

    def fake_filter(self, text):
        calls.append(text)
        return text

    monkeypatch.setattr(dreaming.FilterPipeline, "filter_text", fake_filter, raising=False)

    def fake_generate(prompt, history=None, human_mode=False):
        return "A sunny field of code and friends."  # short

    monkeypatch.setattr(dreaming, "generate_response", fake_generate)
    dm = dreaming.DreamManager(lambda: dreaming.Mood(valence=-0.5))
    result = dm.run_nightly(None)
    assert result["ran"] is True
    assert log_path.exists()
    assert calls, "filter should be invoked"
    summary = dm.recall_last_dream()
    assert summary is not None
    before = result["mood_before"]["valence"]
    after = result["mood_after"]["valence"]
    assert after > before
    assert "plan" in result
