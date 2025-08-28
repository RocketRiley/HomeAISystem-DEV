from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import time
import re
import random

# ---------- Public config knobs ----------
DEFAULT_COOLDOWN_SEC = 75            # minimum time between curiosity prompts
MAX_PER_SESSION      = 6             # absolute cap per app run
MIN_USER_TOKENS      = 6             # don't probe if user already wrote a lot
MIN_TURN_GAP         = 1             # at least this many user turns since last probe
MIN_EMOTION_MAG      = 0.35          # ask more when emotions are a bit strong
FOLLOWUP_CHANCE      = 0.45          # base probability (modulated by signals)

# Filter gates by mode
ALLOWED_TOPICS = {
    "family": {"school", "study", "hobbies", "chores", "meals", "sleep", "sports", "friends", "music", "pets"},
    "enabled": "any",                 # safe, general curiosity
    "adult": "any_but_no_initiation", # can follow user's lead on adult topics but never initiate
}

# “Topic extractors”—super light heuristics (replace with NER/memory graph later)
TOPIC_PATTERNS = {
    "work": r"\b(work|office|shift|project|deadline|meeting)\b",
    "school": r"\b(class|school|homework|assignment|exam|study)\b",
    "hobbies": r"\b(game|music|guitar|draw|gym|run|cook|bake|art|blender)\b",
    "health": r"\b(sleep|tired|sick|workout|diet)\b",
    "social": r"\b(friend|date|party|family|mom|dad|sister|brother)\b",
    "sports": r"\b(soccer|basketball|football|hockey|tennis|gym)\b",
    "media": r"\b(movie|show|anime|book|song|album|podcast|stream)\b",
}

# ---------- Data plumbing ----------
@dataclass
class MemoryPeek:
    known_topics: List[str]
    missing_slots: Dict[str, bool]
    last_followups: List[str]

@dataclass
class EmotionState:
    valence: float
    arousal: float
    dominance: float
    top_labels: List[str]

@dataclass
class CuriosityContext:
    user_text: str
    persona_name: str
    mode: str
    dlc_warm_nights: bool
    emotion: EmotionState
    memory: MemoryPeek
    turns_since_user_question: int
    user_tokens_in_last_turn: int
    now_ts: float
    last_probe_ts: float
    probes_so_far: int
    persona_constraints: Dict[str, Any]
    safety_filter_level: str
    user_led_adult_topic: bool
    active_goal: Optional[str]


class CuriosityEngine:
    def __init__(self) -> None:
        self._rng = random.Random()

    # ---------- Public entry point ----------
    def maybe_ask(self, ctx: CuriosityContext) -> Optional[str]:
        """Return a curiosity question or None."""
        if not self._cooldown_ok(ctx):
            return None
        if ctx.probes_so_far >= MAX_PER_SESSION:
            return None
        if ctx.active_goal:
            return None
        if ctx.user_tokens_in_last_turn >= MIN_USER_TOKENS:
            return None
        if ctx.turns_since_user_question < MIN_TURN_GAP:
            return None

        topics_seen = self._extract_topics(ctx.user_text)
        if not self._topics_allowed(ctx, topics_seen):
            return None

        score = self._score_interest(ctx, topics_seen)
        if self._rng.random() > score:
            return None

        question = self._craft_question(ctx, topics_seen)
        return question.strip() if question else None

    # ---------- Signal mixing ----------
    def _score_interest(self, ctx: CuriosityContext, topics_seen: List[str]) -> float:
        score = FOLLOWUP_CHANCE
        emo_mag = (abs(ctx.emotion.valence) + ctx.emotion.arousal) / 2.0
        if emo_mag > MIN_EMOTION_MAG:
            score += 0.15
        if topics_seen and self._has_open_memory_slot(ctx, topics_seen):
            score += 0.15
        if ctx.mode == "family":
            score -= 0.10
        return max(0.05, min(0.95, score))

    def _cooldown_ok(self, ctx: CuriosityContext) -> bool:
        if ctx.last_probe_ts <= 0:
            return True
        return (ctx.now_ts - ctx.last_probe_ts) >= DEFAULT_COOLDOWN_SEC

    # ---------- Topic & memory helpers ----------
    def _extract_topics(self, text: str) -> List[str]:
        text = text.lower()
        hits = []
        for name, pat in TOPIC_PATTERNS.items():
            if re.search(pat, text):
                hits.append(name)
        return hits

    def _has_open_memory_slot(self, ctx: CuriosityContext, topics: List[str]) -> bool:
        needs = ctx.memory.missing_slots
        if not needs:
            return False
        topic_to_slot = {
            "media": "fav_show_or_song",
            "hobbies": "fav_hobby",
            "work": "role",
            "school": "major_or_grade",
            "social": "close_friend",
            "sports": "fav_team",
            "health": "sleep_pattern",
        }
        for t in topics:
            slot = topic_to_slot.get(t)
            if slot and needs.get(slot, False):
                return True
        return False

    def _topics_allowed(self, ctx: CuriosityContext, topics: List[str]) -> bool:
        if ctx.mode == "family":
            allowed = ALLOWED_TOPICS["family"]
            return any(t in allowed for t in topics) or not topics
        if ctx.mode == "adult":
            if ctx.user_led_adult_topic:
                return True
            return True
        return True

    # ---------- Question generation ----------
    def _craft_question(self, ctx: CuriosityContext, topics: List[str]) -> Optional[str]:
        base_templates = [
            "Noticed that. Want to tell me a bit more about it?",
            "Curious—what’s your take on it lately?",
            "What do you enjoy most about that?",
            "Should we make a tiny plan around it?",
        ]
        topic_templates = {
            "work": ["How’s work feeling today?", "Any projects you’re excited about?"],
            "school": ["What class is grabbing you lately?", "Anything due soon I can help track?"],
            "hobbies": ["What have you been making or playing lately?", "Want me to queue something you like?"],
            "health": ["Did you sleep okay?", "Want a gentle nudge for water or a stretch?"],
            "social": ["Seen any friends recently?", "Anyone I should remember to ask you about?"],
            "sports": ["Catching any games this week?", "Who are you rooting for these days?"],
            "media": ["What are you watching or listening to right now?", "Want me to remember a favorite?"],
        }
        if ctx.mode == "family":
            topic_templates = {k: [re.sub(r"\?$", "?", t) for t in v] for k, v in topic_templates.items()}
        candidates: List[str] = []
        for t in topics:
            candidates.extend(topic_templates.get(t, []))
        if not candidates:
            candidates = base_templates
        candidates = [c for c in candidates if c not in (ctx.memory.last_followups or [])]
        if not candidates:
            return None
        q = self._rng.choice(candidates)
        if ctx.persona_constraints.get("no_ai_self_ref", True):
            q = re.sub(r"\bas an ai\b", "", q, flags=re.I)
        return q


__all__ = [
    "CuriosityEngine",
    "CuriosityContext",
    "EmotionState",
    "MemoryPeek",
]

