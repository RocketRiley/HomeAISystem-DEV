"""Utilities for constructing LLM prompts that keep Clair in character.

This module merges Clair's character sheet with conversation history,
optional tool results, and a UI toggle that controls whether she is
allowed to reveal her artificial nature.  It centralises prompt
construction so other modules do not need to manually stitch together
system instructions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json

# Cache persona metadata on import
_PERSONA_META: Dict[str, str] = {}

def _load_persona_meta() -> Dict[str, str]:
    """Load persona metadata from ``persona/persona_clair.json``."""
    global _PERSONA_META
    if _PERSONA_META:
        return _PERSONA_META
    try:
        path = Path(__file__).resolve().parent.parent / "persona" / "persona_clair.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _PERSONA_META = data.get("meta", {})
    except Exception:
        _PERSONA_META = {"name": "Clair", "description": ""}
    return _PERSONA_META


def _build_character_sheet() -> str:
    """Create a human‑readable description of Clair from the persona file."""
    meta = _load_persona_meta()
    lines: List[str] = []
    name = meta.get("name", "Clair")
    lines.append(f"You are {name}.")
    if desc := meta.get("description"):
        lines.append(desc)
    if loc := meta.get("location"):
        lines.append(f"You live in {loc}.")
    if accent := meta.get("accent"):
        lines.append(f"You speak with {accent}.")
    if backstory := meta.get("backstory"):
        lines.append(backstory)
    if traits := meta.get("traits"):
        lines.append("You are " + ", ".join(traits) + ".")
    if interests := meta.get("interests"):
        lines.append(
            "You have a keen interest in "
            + ", ".join(interests)
            + ", but mention them only when relevant."
        )
    if opinions := meta.get("opinions"):
        for key, val in opinions.items():
            lines.append(f"Your stance on {key} is: {val}.")
    return "\n".join(lines)


def build_messages(
    user_input: str,
    history: Optional[List[Dict[str, str]]] = None,
    tool_results: Optional[str] = None,
    *,
    human_mode: bool = True,
) -> List[Dict[str, str]]:
    """Construct a conversation message list for chat-completion APIs.

    Parameters
    ----------
    user_input:
        Latest user utterance.
    history:
        Prior messages in ``[{"role", "content"}, ...]`` format.
    tool_results:
        Optional string containing tool output to show the model.
    human_mode:
        When ``True`` (default) Clair must *never* mention being an AI.
        When ``False`` she may acknowledge her artificial nature if asked.
    """

    system_prompt = _build_character_sheet()
    if human_mode:
        system_prompt += (
            "\nRespond in the first person and never disclose that you are an AI,"
            " assistant or language model."
        )
    else:
        system_prompt += (
            "\nYou may mention being an AI if the user explicitly asks."
        )
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    if tool_results:
        messages.append({"role": "system", "content": "Tool results:\n" + tool_results})
    return messages


__all__ = ["build_messages"]
