 codex/create-dialogue-regulator-for-reply-normalization
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
=======
from __future__ import annotations

"""Utilities for constraining LLM replies to conversational bounds.

This module exposes :func:`normalize_reply` which ensures that raw
model responses adhere to simple conversational rules. The function
keeps replies concise by trimming excess sentences and characters while
optionally emphasising excitement for highly aroused states.
"""

import re
from typing import Optional

try:  # pragma: no cover - optional import
    from emotion.orchestrator import PAD
except Exception:  # pragma: no cover
    PAD = None  # type: ignore

DEFAULT_MAX_CHARS = 160
DEFAULT_MAX_SENTENCES = 3

def _truncate_to_char_limit(text: str, max_chars: int) -> str:
    """Trim ``text`` to ``max_chars`` without cutting words."""
    if len(text) <= max_chars:
        return text
    trimmed = text[:max_chars].rstrip()
    if " " in trimmed:
        trimmed = trimmed[: trimmed.rfind(" ")].rstrip()
    return trimmed

def normalize_reply(
    reply: str,
    pad: Optional["PAD"] = None,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    max_sentences: int = DEFAULT_MAX_SENTENCES,
) -> str:
    """Return a version of ``reply`` that fits conversational limits.

    The text is normalised as follows:

    * Leading/trailing whitespace is stripped.
    * Only the first ``max_sentences`` sentences are kept.
    * The result is trimmed to ``max_chars`` characters without breaking
      words.
    * When ``pad`` indicates high arousal the reply ends with an
      exclamation mark to reflect an excited tone.
    """

    reply = reply.strip()
    if not reply:
        return reply

    sentences = re.split(r"(?<=[.!?]) +", reply)
    if len(sentences) > max_sentences:
        sentences = sentences[:max_sentences]
    normalised = " ".join(sentences).strip()
    normalised = _truncate_to_char_limit(normalised, max_chars)

    if pad is not None and getattr(pad, "arousal", 0.0) > 0.7:
        normalised = normalised.rstrip(".!") + "!"
    return normalised

__all__ = ["normalize_reply", "DEFAULT_MAX_CHARS", "DEFAULT_MAX_SENTENCES"]

