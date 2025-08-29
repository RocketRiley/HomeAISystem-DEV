from __future__ import annotations

"""Nightly dream cycle that performs a private monologue and logs it."""

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, Optional

from scripts.filter_system import FilterPipeline
from scripts.llm_adapter import generate_response
from scripts.log_manager import LogManager
from .self_care_planner import make_plan
from scripts.emotion_state import EmotionState

CONFIG_PATH = Path("config/emotional_hygiene.json")
LOG_PATH = Path("logs/dream_log.jsonl")


def _load_config() -> Dict[str, any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


@dataclass
class Mood:
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0


class DreamManager:
    """Create nightly dreams and store short summaries."""

    def __init__(
        self,
        mood_getter: Optional[Callable[[], Mood]] = None,
        emotion_state: Optional[EmotionState] = None,
 codex/resolve-conflict-in-readme.md-74x7dq
        wake_check: Optional[Callable[[], bool]] = None,
    ) -> None:
        self.mood_getter = mood_getter or (lambda: Mood())
        self.emotion_state = emotion_state
        self.wake_check = wake_check or (lambda: False)
=======
    ) -> None:
        self.mood_getter = mood_getter or (lambda: Mood())
        self.emotion_state = emotion_state
 main
        self.log = LogManager(LOG_PATH)
        cfg = _load_config().get("dreams", {})
        self.enabled = cfg.get("enabled", True)
        self.max_minutes = cfg.get("max_minutes", 6)
        self.max_tokens = cfg.get("max_tokens", 1500)
        self.store_full = cfg.get("store_full", False)
        self.share_one_liner = cfg.get("share_morning_one_liner", True)
 codex/resolve-conflict-in-readme.md-74x7dq
        self.sleep_hours = cfg.get("sleep_hours", 8)
        self.check_interval = cfg.get("check_interval_minutes", 10) * 60
=======
 main
        self.filter = FilterPipeline(os.getenv("FILTER_LEVEL", "enabled"))

    def run_nightly(self, daily_summary: Optional[str] = None) -> Dict[str, any]:
        if not self.enabled:
            return {"ran": False, "reason": "disabled"}
        mood_before = self.mood_getter()
        plan = None
        if mood_before.valence < 0:
            plan = make_plan("sleep", "self")
            seed = plan.get("prompt", "Take a gentle breath and dream of warmth.")
            reason = "negative mood"
        else:
            if daily_summary:
                seed = (
                    "Dream about the day's events: "
                    + daily_summary[:200]
                    + " and end hopeful."
                )
            else:
                tag = self.emotion_state.top_tag(True) if self.emotion_state else None
                if tag:
                    seed = f"Begin a short whimsical adventure about {tag} that ends hopeful."
                else:
                    seed = "Begin a short whimsical adventure that ends hopeful."
            reason = "neutral/positive mood"
        prompt = (
            "You are Clair. In a private dream, speak first-person, kind and safe.\n" + seed
        )
        start = time.time()
        text = generate_response(prompt, history=None, human_mode=False) or ""
        elapsed = time.time() - start
        if len(text.split()) > self.max_tokens:
            text = " ".join(text.split()[: self.max_tokens])
        summary = text.strip().split("\n", 1)[0][:200]
        summary = self.filter.filter_text(summary)
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "summary": summary,
        }
        if self.store_full:
            entry["full"] = self.filter.filter_text(text.strip())
        self.log.log(entry)
        delta = 0.05 if mood_before.valence >= 0 else 0.1
        mood_after = Mood(
            valence=min(1.0, mood_before.valence + delta),
            arousal=mood_before.arousal,
            dominance=mood_before.dominance,
        )
        result = {
            "ran": True,
            "reason": reason,
            "mood_before": mood_before.__dict__,
            "mood_after": mood_after.__dict__,
            "dream_title": summary,
            "journal_id": entry["ts"],
        }
        if plan:
            result["plan"] = plan
 codex/resolve-conflict-in-readme.md-74x7dq
        self._sleep_until_wake()
        return result

    def _sleep_until_wake(self) -> None:
        cycles = int(self.sleep_hours * 3600 / self.check_interval)
        for _ in range(max(1, cycles)):
            if self.wake_check():
                break
            time.sleep(self.check_interval)

=======
        return result

 main
    def recall_last_dream(self, hours: int = 12) -> Optional[str]:
        if not LOG_PATH.exists():
            return None
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
        for line in reversed(lines):
            try:
                data = json.loads(line)
            except Exception:
                continue
            ts = datetime.fromisoformat(data.get("ts"))
            if ts >= cutoff:
                return data.get("summary")
        return None

__all__ = ["DreamManager", "Mood"]
