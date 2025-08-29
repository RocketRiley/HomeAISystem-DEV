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
