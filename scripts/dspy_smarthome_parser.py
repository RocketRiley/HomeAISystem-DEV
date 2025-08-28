#!/usr/bin/env python3
"""DSPy routine to parse natural language smart home commands."""
from __future__ import annotations

import json
import os
from typing import Optional, Dict

try:  # pragma: no cover - optional dependency
    import dspy  # type: ignore
except Exception:  # pragma: no cover
    dspy = None  # type: ignore


class SmartHomeSignature(dspy.Signature):  # type: ignore
    """Parse ``utterance`` into a JSON command."""
    utterance = dspy.InputField()  # type: ignore
    json_cmd = dspy.OutputField(desc="JSON with keys device, action, value")  # type: ignore


class SmartHomeCommandParser:
    """Use DSPy to convert text into structured smart home commands."""

    def __init__(self) -> None:
        if dspy is None:  # pragma: no cover
            self.parser = None
            return
        model_name = os.getenv("DSPY_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
        dspy.settings.configure(lm=model_name)
        self.parser = dspy.Predict(SmartHomeSignature)

    def parse(self, utterance: str) -> Optional[Dict[str, str]]:
        if not self.parser:
            return None
        result = self.parser(utterance)
        try:
            data = json.loads(result.json_cmd)
            if {"device", "action"} <= data.keys():
                return data
        except Exception:
            pass
        return None


if __name__ == "__main__":  # pragma: no cover
    parser = SmartHomeCommandParser()
    print(parser.parse("turn the living room lights to blue"))
