from __future__ import annotations

"""Emotion Bundle Orchestrator (EBO).

This module computes a weighted bundle of affects for a given turn and
produces cross‑system "effects" that downstream modules can consume.  It
is intentionally lightweight: the appraisal logic is heuristic based and
all cross‑system mappings are data driven via ``config/affect_effects.json``.

Subscribers are expected to call ``effects`` each turn and adapt their
behaviour according to the returned knobs.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

PAD_LIMIT = 0.6


@dataclass
class PAD:
    pleasure: float
    arousal: float
    dominance: float


def clamp_pad(pad: PAD, limit: float = PAD_LIMIT) -> PAD:
    """Clamp PAD components to ``±limit`` and return a new instance."""

    return PAD(
        pleasure=max(-limit, min(limit, pad.pleasure)),
        arousal=max(-limit, min(limit, pad.arousal)),
        dominance=max(-limit, min(limit, pad.dominance)),
    )


class EmotionOrchestrator:
    """Compute affect bundles and broadcast cross‑system knobs."""

    def __init__(self, config_path: Path | None = None):
        base = Path(__file__).resolve().parent.parent
        if config_path is None:
            config_path = base / "config" / "affect_effects.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self.effects_cfg: Dict[str, Dict[str, Any]] = json.load(f)

    # ------------------------------------------------------------------
    # Appraisal → bundle → stance → effects
    # ------------------------------------------------------------------
    def appraise(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """A tiny appraisal stub.

        Currently this simply forwards tags from the context.  A real
        implementation could analyse ``request`` and ``context`` to infer
        richer signals.
        """

        return {"tags": context.get("tags", [])}

    def bundle(
        self,
        appraisal: Dict[str, Any],
        pad: PAD,
        traits: Dict[str, float] | None,
        relationship: Dict[str, float] | None,
    ) -> Dict[str, float]:
        """Build a small affect bundle.

        Heuristics: each tag maps to an affect with a default weight of
        ``0.7``.  This keeps the interface simple while still allowing
        tests to exercise cross‑system mappings.
        """

        bundle: Dict[str, float] = {}
        for tag in appraisal.get("tags", []):
            bundle[tag] = max(bundle.get(tag, 0.0), 0.7)
        return bundle

    def stance(
        self,
        bundle: Dict[str, float],
        pad: PAD,
        traits: Dict[str, float] | None,
        relationship: Dict[str, float] | None,
    ) -> Dict[str, float]:
        """Derive a conversational stance.

        The rules are deliberately straightforward: ``warmth`` follows the
        empathy/tenderness affects, ``gravity`` follows melancholy or low
        pleasure, and ``enthusiasm`` mirrors arousal.  Values are clipped to
        ``0..1`` for downstream consumers.
        """

        pad = clamp_pad(pad)

        def clamp(v: float) -> float:
            return max(0.0, min(1.0, v))

        warmth = max(bundle.get("empathy", 0.0), bundle.get("tenderness", 0.0))
        gravity = max(bundle.get("melancholy", 0.0), 1.0 - (pad.pleasure + 1) / 2)
        enthusiasm = (pad.arousal + 1) / 2
        return {
            "warmth": clamp(warmth),
            "gravity": clamp(gravity),
            "enthusiasm": clamp(enthusiasm),
        }

    def effects(
        self,
        bundle: Dict[str, float],
        stance: Dict[str, float],
        pad: PAD,
        tags: List[str],
    ) -> Dict[str, Any]:
        """Compute cross‑system knobs based on the affect bundle.

        For each domain in ``affect_effects.json`` the contributions of all
        matching affects are summed, scaled by the affect's weight.
        """

        pad = clamp_pad(pad)

        result: Dict[str, Any] = {
            "bundle": bundle,
            "stance": stance,
            "pad": {
                "pleasure": pad.pleasure,
                "arousal": pad.arousal,
                "dominance": pad.dominance,
            },
        }

        for domain, mapping in self.effects_cfg.items():
            domain_effect: Dict[str, Any] = {}
            for affect, effects in mapping.items():
                weight = bundle.get(affect, 0.0)
                if weight <= 0:
                    continue
                for key, value in effects.items():
                    # Numeric values are scaled by affect weight; other
                    # types (lists/booleans/strings) are copied as‑is.
                    if isinstance(value, (int, float)):
                        domain_effect[key] = domain_effect.get(key, 0.0) + value * weight
                    else:
                        domain_effect[key] = value
            if domain_effect:
                result[domain] = domain_effect
        return result


__all__ = ["EmotionOrchestrator", "PAD"]
