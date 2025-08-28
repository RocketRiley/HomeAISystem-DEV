from __future__ import annotations

"""Track fast affect and slow mood using tag-aware persistence."""

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from emotion.tag_persistence import TagRule, effective_tau, floors, load_table, weight

CONFIG_PATH = Path("config/emotion.json")


def _load_config() -> Dict[str, any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            return {}
    return {}


@dataclass
class EmotionEvent:
    pad_delta: Dict[str, float]
    intensity: float
    tags: List[str]
    timestamp: float
    tau_eff: float
    weight: float


@dataclass
class EmotionState:
    pad_fast: Dict[str, float] = field(default_factory=lambda: {"P": 0.0, "A": 0.0, "D": 0.0})
    events: List[EmotionEvent] = field(default_factory=list)
    last_display: Dict[str, float] = field(default_factory=lambda: {"P": 0.0, "A": 0.0, "D": 0.0})
    last_display_ts: float = field(default_factory=time.time)
    last_switch_ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        cfg = _load_config().get("emotion", {})
        self.alpha = cfg.get("alpha_blend", 0.5)
        self.hysteresis = cfg.get("hysteresis", {}).get("seconds", 3)
        self.evi_threshold = cfg.get("evi", {}).get("threshold", 0.15)
        table_cfg = cfg.get("tag_persistence", {})
        self.tag_table = load_table(table_cfg)

    # Fast affect
    def update_fast(self, delta: Dict[str, float], lam: float = 0.1) -> None:
        for k in self.pad_fast:
            self.pad_fast[k] = max(-1.0, min(1.0, self.pad_fast[k] * (1 - lam) + delta.get(k, 0.0)))

    # Events -> mood
    def add_event(
        self,
        pad_delta: Dict[str, float],
        tags: List[str],
        intensity: float = 1.0,
        repetition: float = 1.0,
        relationship: float = 1.0,
    ) -> None:
        now = time.time()
        rule = self.tag_table.get(tags[0], TagRule(24.0, 1.0))
        tau = effective_tau(rule, intensity, repetition, relationship)
        w = weight(rule, intensity)
        self.events.append(
            EmotionEvent(pad_delta=pad_delta, intensity=intensity, tags=tags, timestamp=now, tau_eff=tau * 3600, weight=w)
        )

    def _decayed_events(self) -> List[EmotionEvent]:
        now = time.time()
        out = []
        for e in self.events:
            decay = math.exp(-(now - e.timestamp) / e.tau_eff)
            if decay > 0.01:
                out.append(EmotionEvent(e.pad_delta, e.intensity, e.tags, e.timestamp, e.tau_eff, e.weight * decay))
        self.events = out
        return out

    def mood(self) -> Dict[str, float]:
        mood = {"P": 0.0, "A": 0.0, "D": 0.0}
        for e in self._decayed_events():
            for k in mood:
                mood[k] += e.pad_delta.get(k, 0.0) * e.weight
        for k in mood:
            mood[k] = max(-1.0, min(1.0, mood[k]))
        # apply floors if any
        fl = floors([t for e in self.events for t in e.tags], self.tag_table)
        if fl[0] is not None:
            mood["P"] = max(mood["P"], fl[0])
        return mood

    def displayed(self) -> Dict[str, float]:
        m = self.mood()
        disp = {k: (1 - self.alpha) * self.pad_fast[k] + self.alpha * m[k] for k in m}
        # hysteresis gating
        now = time.time()
        evi = self.evi(disp, now)
        if evi > self.evi_threshold:
            self.last_display_ts = now
        if now - self.last_display_ts < self.hysteresis:
            return self.last_display
        self.last_display = disp
        return disp

    def evi(self, current: Optional[Dict[str, float]] = None, ts: Optional[float] = None) -> float:
        if current is None:
            current = self.last_display
        if ts is None:
            ts = time.time()
        dt = ts - self.last_display_ts
        if dt <= 0:
            return 0.0
        diff = sum((current[k] - self.last_display.get(k, 0.0)) ** 2 for k in current)
        return math.sqrt(diff) / dt

    def top_tag(self, positive: bool = True) -> Optional[str]:
        agg: Dict[str, float] = {}
        for e in self.events:
            val = e.pad_delta.get("P", 0.0)
            if not positive:
                val = -val
            agg[e.tags[0]] = agg.get(e.tags[0], 0.0) + val * e.weight
        if not agg:
            return None
        tag, value = max(agg.items(), key=lambda kv: kv[1])
        if value <= 0:
            return None
        return tag

__all__ = ["EmotionState", "EmotionEvent"]
