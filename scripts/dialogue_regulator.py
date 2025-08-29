"""Normalize LLM replies to respect simple dialogue limits."""
from __future__ import annotations

import json
import re
from pathlib import Path
from textwrap import TextWrapper
from typing import Dict

CONFIG_PATH = Path("config/emotion.json")

def _load_limits() -> Dict[str, int]:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            return data.get("dialogue", {})
        except Exception:
            return {}
    return {}


def normalize_reply(text: str, emotion: Dict) -> str:
    """Trim or split overly long replies based on config limits."""
    limits = _load_limits()
    max_sentences = int(limits.get("max_sentences", 3))
    avg_words = int(limits.get("avg_words_per_sentence", 15))

    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    wrapper = TextWrapper(width=avg_words * 8, break_long_words=False, replace_whitespace=False)
    normalized = []
    for raw in raw_sentences:
        for sent in wrapper.wrap(raw):
            words = sent.strip().split()
            while len(words) > avg_words:
                chunk = " ".join(words[:avg_words]).rstrip(",;:") + "."
                normalized.append(chunk)
                words = words[avg_words:]
            if words:
                tail = " ".join(words).rstrip(",;:")
                if not tail.endswith(('.', '!', '?')):
                    tail += '.'
                normalized.append(tail)
    normalized = [s for s in normalized if s]
    normalized = normalized[:max_sentences]
    return " ".join(normalized)

__all__ = ["normalize_reply"]
