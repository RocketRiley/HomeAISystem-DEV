from __future__ import annotations

"""Daytime emotional hygiene helpers."""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

from scripts.filter_system import FilterPipeline
from scripts.log_manager import LogManager
from .self_care_planner import make_plan
from scripts.emotion_state import EmotionState

CONFIG_PATH = Path("config/emotional_hygiene.json")
LOG_PATH = Path("logs/hygiene_log.jsonl")


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


class EmotionalHygiene:
    def __init__(
        self,
        mood_getter: Optional[Callable[[], Mood]] = None,
        emotion_state: Optional[EmotionState] = None,
    ) -> None:
        cfg = _load_config().get("hygiene", {})
        self.user_interval = cfg.get("user", {}).get("offer_min_interval_minutes", 60) * 60
        self.self_interval = cfg.get("ai", {}).get("self_check_interval_minutes", 10) * 60
        self.allow_home = cfg.get("allow_home_actions", False)
        self.mood_getter = mood_getter or (lambda: Mood())
        self.emotion_state = emotion_state
        self.filter = FilterPipeline(os.getenv("FILTER_LEVEL", "enabled"))
        self.log = LogManager(LOG_PATH)
        self._last_user_offer = 0.0
        self._last_self_check = 0.0

    # ------------------------------------------------------------------
    def maybe_cheer_user(self, signals: Dict[str, float]) -> bool:
        now = time.time()
        if now - self._last_user_offer < self.user_interval:
            return False
        if signals.get("sentiment", 0.0) >= 0:
            return False
        if self.emotion_state and self.emotion_state.evi() > self.emotion_state.evi_threshold:
            return False
        plan = make_plan("day", "user")
        offer = self.filter.filter_text(plan.get("prompt", "Take a deep breath together."))
        self.log.log({"event": "offer_user", "offer": offer})
        self._last_user_offer = now
        return True

    # ------------------------------------------------------------------
    def maybe_cheer_self(self) -> bool:
        now = time.time()
        if now - self._last_self_check < self.self_interval:
            return False
        mood = self.mood_getter()
        if mood.valence >= 0:
            return False
        if self.emotion_state and self.emotion_state.evi() > self.emotion_state.evi_threshold:
            return False
        plan = make_plan("day", "self")
        text = self.filter.filter_text(plan.get("prompt", "Recall a small good thing."))
        self.log.log({"event": "self_regulation", "text": text})
        self._last_self_check = now
        return True

__all__ = ["EmotionalHygiene", "Mood"]
