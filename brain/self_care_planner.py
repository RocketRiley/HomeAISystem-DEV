from __future__ import annotations

"""Utilities to plan gentle self‑care or cheer‑up actions.

This module queries the local LLM to enumerate a handful of safe options
and picks the best candidate according to simple heuristics.  If the LLM
is unavailable or returns malformed output, a static fallback list is
used instead.  All returned prompts are passed through the project's
FilterPipeline before being surfaced.
"""

import json
import os
from typing import Dict, List, Literal

from scripts.filter_system import FilterPipeline
from scripts.llm_adapter import generate_response

# Fallback options used if the LLM fails
_FALLBACK: List[Dict[str, str]] = [
    {"name": "short_story", "prompt": "Tell a silly one minute story about a cat astronaut.", "why": "light humor"},
    {"name": "gratitude_list", "prompt": "List three small things to be grateful for today.", "why": "promotes optimism"},
    {"name": "tomorrow_plan", "prompt": "Outline a cozy plan for tomorrow morning.", "why": "creates gentle anticipation"},
]

def _filter(level: str, text: str) -> str:
    return FilterPipeline(level).filter_text(text)


def make_plan(context: Literal["sleep", "day"], audience: Literal["self", "user"]) -> Dict[str, str]:
    """Return a single cheer‑up plan.

    Parameters
    ----------
    context: Literal["sleep", "day"]
        When the plan will run.  "sleep" is used for private, nightly
        reflection, while "day" indicates daytime interaction.
    audience: Literal["self", "user"]
        Who the plan targets.  "self" means the AI, "user" is the
        human handler.
    """

    level = os.getenv("FILTER_LEVEL", "enabled")
    prompt = (
        f"You are Clare's motivation module. Within strict safety limits ({level}), list 6 "
        f"gentle ways to cheer {audience} up right now. Prefer short, wholesome options. "
        f"Return JSON with fields: name, prompt, why."
    )
    try:
        raw = generate_response(prompt, history=None, human_mode=False)
        if raw:
            data = json.loads(raw)
            if isinstance(data, list) and data:
                candidates = data
            else:
                candidates = _FALLBACK
        else:
            candidates = _FALLBACK
    except Exception:
        candidates = _FALLBACK

    best = None
    best_score = -1.0
    for cand in candidates:
        prompt_text = _filter(level, cand.get("prompt", ""))
        why_text = _filter(level, cand.get("why", ""))
        cand["prompt"], cand["why"] = prompt_text, why_text
        length_penalty = len(prompt_text) / 200.0
        score = 1.0 - length_penalty
        if "gratitude" in cand.get("name", ""):
            score += 0.1
        if score > best_score:
            best = cand
            best_score = score
    return best or _FALLBACK[0]

__all__ = ["make_plan"]
