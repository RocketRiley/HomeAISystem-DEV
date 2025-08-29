from __future__ import annotations

"""Fallback sentiment guard using a small HuggingFace model.

The primary system may use a full LLM to infer user sentiment.  When
that is not available this module loads ``distilroberta-base-go-emotions``
and maps its emotion labels to a simple positive/negative score.  The
result is fed into the :class:`emotion.orchestrator.EmotionOrchestrator`
to influence valence (pleasure) adjustments.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

try:  # pragma: no cover - transformers is optional
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None  # type: ignore

from emotion.orchestrator import EmotionOrchestrator, PAD

# Labels grouped by valence.  These are a coarse mapping of the
# GoEmotions taxonomy.
_POSITIVE: set[str] = {
    "admiration",
    "amusement",
    "approval",
    "caring",
    "curiosity",
    "desire",
    "excitement",
    "gratitude",
    "joy",
    "love",
    "optimism",
    "pride",
    "relief",
}

_NEGATIVE: set[str] = {
    "anger",
    "annoyance",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "fear",
    "grief",
    "nervousness",
    "remorse",
    "sadness",
}


@dataclass
class EmotionGuard:
    """Compute valence using a tiny sentiment classifier."""

    model_name: str = "bhadresh-savani/distilroberta-base-go-emotions"

    def __post_init__(self) -> None:  # pragma: no cover - model load
        self._clf = None
        if pipeline is not None:
            try:
                self._clf = pipeline(
                    "text-classification", model=self.model_name, top_k=None
                )
            except Exception:
                self._clf = None
        self._orchestrator = EmotionOrchestrator()

    # ------------------------------------------------------------------
    def _score(self, text: str) -> float:
        """Return a valence score in ``[-1, 1]``."""
        if self._clf is None:
            return 0.0
        results: List[Dict[str, Any]] = self._clf(text)[0]
        pos = sum(r["score"] for r in results if r["label"] in _POSITIVE)
        neg = sum(r["score"] for r in results if r["label"] in _NEGATIVE)
        return max(-1.0, min(1.0, pos - neg))

    def analyse(self, text: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Analyse ``text`` and return orchestrator effects.

        ``context`` may contain existing affect tags which will be
        forwarded to the orchestrator.  The computed valence drives the
        pleasure component of the PAD model.
        """

        context = context or {}
        val = self._score(text)
        pad = PAD(pleasure=val, arousal=0.0, dominance=0.0)
        appraisal = self._orchestrator.appraise(text, context)
        bundle = self._orchestrator.bundle(appraisal, pad, None, None)
        stance = self._orchestrator.stance(bundle, pad, None, None)
        return self._orchestrator.effects(bundle, stance, pad, appraisal.get("tags", []))


__all__ = ["EmotionGuard"]
