from __future__ import annotations

"""Sentiment guard utility.

This module provides a lightweight sentiment classifier that can be used
as a fallback when no large language model (LLM) is available.  It relies
on the ``distilroberta-base-go-emotions`` model from HuggingFace and maps
its emotion tags to positive or negative valence scores.  The resulting
scores can be fed into the :class:`emotion.orchestrator.EmotionOrchestrator`
so that the agent's pleasure (valence) is nudged accordingly.
"""

from dataclasses import dataclass
from typing import Tuple

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover - transformers optional
    pipeline = None  # type: ignore

from emotion.orchestrator import EmotionOrchestrator, PAD

# Positive and negative label groups for GoEmotions
POSITIVE_LABELS = {
    "admiration",
    "amusement",
    "approval",
    "caring",
    "desire",
    "excitement",
    "gratitude",
    "joy",
    "love",
    "optimism",
    "pride",
    "relief",
    "surprise",
}

NEGATIVE_LABELS = {
    "anger",
    "annoyance",
    "confusion",
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
    """Small sentiment helper with optional LLM override."""

    llm: object | None = None
    model_name: str = "bhadresh-savani/distilroberta-base-go-emotions"

    def __post_init__(self) -> None:
        if self.llm is None and pipeline is not None:
            # Load lightweight sentiment classifier
            self.classifier = pipeline(
                "text-classification", model=self.model_name, top_k=None
            )
        else:  # pragma: no cover - requires external LLM
            self.classifier = None

    def classify(self, text: str) -> Tuple[float, float]:
        """Return ``(positive, negative)`` scores for ``text``.

        When an LLM is supplied this method should defer to it; otherwise the
        local model is used.  Scores are normalised to ``0..1``.
        """

        if self.llm is not None:  # pragma: no cover - placeholder
            raise NotImplementedError("LLM-based sentiment not implemented")

        if self.classifier is None:
            return 0.0, 0.0

        outputs = self.classifier(text)[0]
        pos = sum(o["score"] for o in outputs if o["label"].lower() in POSITIVE_LABELS)
        neg = sum(o["score"] for o in outputs if o["label"].lower() in NEGATIVE_LABELS)
        return pos, neg

    def adjust_pad(self, text: str, orchestrator: EmotionOrchestrator, pad: PAD) -> PAD:
        """Classify ``text`` and use scores to adjust ``pad`` via the orchestrator."""

        pos, neg = self.classify(text)
        return orchestrator.apply_sentiment(pad, pos, neg)
