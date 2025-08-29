#!/usr/bin/env python3
"""Life lesson management for Clair.

This module bridges experiential "life lessons" with the existing
:class:`OpinionManager`.  Lessons are stored as high‑confidence opinions
that can evolve with new evidence but never override the global content
filters.  Each lesson is treated as an opinion of type ``lesson`` and
is always passed through the active :class:`FilterPipeline` before
storage so unsafe text is never recorded.

The design follows the "additive" rule from the safety spec: lessons can
shape behaviour but cannot bypass or soften the filter pipeline or other
core guardrails.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .opinion_system import OpinionManager
from .filter_system import FilterPipeline


class LifeLessonManager:
    """Stores and updates high‑level life lessons.

    Parameters
    ----------
    path:
        Location of the JSON file where lessons are stored.
    filter_level:
        Content‑filter level to apply when recording lessons.
    """

    def __init__(self, path: Any, filter_level: str = "enabled") -> None:
        self.path = Path(path)
        self.opinions = OpinionManager(self.path)
        self.filter = FilterPipeline(filter_level)

    # ------------------------------------------------------------------
    def add_lesson(
        self,
        text: str,
        evidence_strength: float = 1.0,
        trust: float = 1.0,
        source: str = "experience",
    ) -> Dict[str, Any]:
        """Record a new life lesson or reinforce an existing one.

        ``text`` is filtered before storage.  The lesson is stored with
        high positive stance and confidence reflecting that it is a
        distilled principle.  Repeated calls strengthen the opinion via
        :meth:`OpinionManager.update`.
        """

        clean = self.filter.filter_text(text)
        # Ensure the lesson exists as an opinion of type "lesson".
        if clean not in self.opinions.opinions:
            self.opinions.opinions[clean] = {
                "topic": clean,
                "type": "lesson",
                "stance": 1.0,
                # Start slightly below absolute certainty so lessons
                # remain revisable with new evidence.
                "confidence": min(0.9, evidence_strength * trust),
                "evidence_log": [],
            }
            self.opinions.save()
            return self.opinions.opinions[clean]
        # Reinforce existing lesson.
        return self.opinions.update(
            clean,
            evidence_strength,
            trust,
            1.0,
            reason="lesson reinforcement",
            source=source,
        )

    # ------------------------------------------------------------------
    def revise_lesson(
        self,
        text: str,
        evidence_strength: float,
        direction: float,
        source: str = "user",
    ) -> Dict[str, Any]:
        """Revise a stored lesson using new evidence.

        ``direction`` should be positive to strengthen the lesson or
        negative to weaken it.  The update still flows through the
        :class:`OpinionManager` to keep guardrails intact.
        """

        clean = self.filter.filter_text(text)
        return self.opinions.update(
            clean,
            evidence_strength,
            trust=1.0,
            direction=direction,
            reason="lesson update",
            source=source,
        )

    # ------------------------------------------------------------------
    def list_lessons(self) -> List[Dict[str, Any]]:
        """Return all recorded lessons."""
        return [
            op for op in self.opinions.opinions.values() if op.get("type") == "lesson"
        ]


__all__ = ["LifeLessonManager"]
