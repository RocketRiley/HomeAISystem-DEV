#!/usr/bin/env python3
"""Experimental planning agent powered by DSPy.

This module demonstrates how Clair can generate and store routines using
Stanford's DSPy library.  It filters each step through the existing content
policy and stores the resulting plan in the mid-term memory so the system can
refine or recall it later.
"""
from __future__ import annotations

import os
from typing import List

try:  # pragma: no cover - optional dependency
    import dspy  # type: ignore
except Exception:  # pragma: no cover
    dspy = None  # type: ignore

from .memory_manager import MemoryManager
from .filter_system import FilterPipeline


class DSPyLearningAgent:
    """Generate filtered plans and save them to memory."""

    def __init__(self) -> None:
        self.memory = MemoryManager(user_id=os.getenv("USER_ID", "default"))
        self.filter = FilterPipeline(os.getenv("FILTER_LEVEL", "enabled"))
        model_name = os.getenv("DSPY_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
        if dspy is not None:
            dspy.settings.configure(lm=model_name)
            self.planner = dspy.ChainOfThought()
        else:  # pragma: no cover - dsp y not installed
            self.planner = None

    def plan(self, goal: str) -> List[str]:
        """Return a list of steps for ``goal`` after filtering and storage."""
        if self.planner is None:
            return [goal]
        result = self.planner(goal)
        steps = [s.strip() for s in result.split("\n") if s.strip()]
        cleaned: List[str] = []
        for step in steps:
            filtered = self.filter.filter_text(step)
            cleaned.append(filtered)
            self.memory.add_event(filtered, tags=["plan"])
        return cleaned


if __name__ == "__main__":
    agent = DSPyLearningAgent()
    target = "help the user stay organised for the week"
    for line in agent.plan(target):
        print("-", line)
