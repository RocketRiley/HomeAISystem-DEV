#!/usr/bin/env python3
"""Adapter for generating responses via a local or online LLM.

This module exposes a single `generate_response` function that will
return a reply to the user's input.  If the environment variable
``ONLINE_MODE`` is set to ``true`` (case‑insensitive) and the
``openai`` package is available, the function will use the OpenAI
Chat API to produce a response using Clair's persona description.
Otherwise, it will return ``None``, signalling to the caller to
fallback to locally curated example lines.

To use this module, install the `openai` Python package and set an
API key via the ``OPENAI_API_KEY`` environment variable.  You may
also set ``OPENAI_MODEL`` to choose a particular model
(``gpt-3.5-turbo`` is used by default).  See the official OpenAI
documentation for details on supported models and parameters.

Note: This file does not contain any secrets.  You must provide
your own API key in the environment or `.env` file to enable online
mode.  Without a key, or if ``openai`` cannot be imported, the
function will simply return ``None``.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore


def _load_persona_description() -> str:
    """Load Clair's description from `persona_clair.json`.

    The description text is used as a system prompt when invoking
    the online model to ensure that the generated replies match
    Clair's persona.  If the file cannot be found or does not
    contain a description, an empty string is returned.
    """
    try:
        persona_path = Path(__file__).resolve().parent.parent / "persona" / "persona_clair.json"
        with open(persona_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("meta", {}).get("description", "")
    except Exception:
        return ""


_PERSONA_DESCRIPTION = _load_persona_description()


def generate_response(user_input: str) -> Optional[str]:
    """Generate a reply to the user's input using an online LLM if enabled.

    Parameters
    ----------
    user_input: str
        The latest user utterance to be sent to the model.

    Returns
    -------
    Optional[str]
        A string containing the assistant's reply if online mode is
        active and the API call succeeds.  If online mode is disabled,
        no API key is provided, or the `openai` package is not
        installed, the function returns ``None`` to indicate that the
        caller should use an alternative (e.g. locally stored example
        lines) to generate a response.
    """
    # Check if online mode is enabled via env var; defaults to False
    online_env = os.getenv("ONLINE_MODE", "false").lower()
    if online_env not in {"true", "1", "yes"}:
        return None
    # Ensure we have the OpenAI module and an API key
    if openai is None:
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Do not log secrets; simply indicate missing key
        return "Error: OPENAI_API_KEY is not set."
    # Configure the OpenAI client
    try:
        # Use the new OpenAI SDK if available
        client = openai.OpenAI(api_key=api_key)  # type: ignore
    except Exception:
        # Fallback to old API if necessary
        openai.api_key = api_key  # type: ignore
        client = None  # type: ignore
    # Build messages: include the persona description and the latest user input
    system_prompt = (
        "You are Clair, an extremely intelligent and empathetic digital assistant with "
        "expertise in robotics, biology, science and history.  You speak in a warm, "
        "bright and optimistic tone, balancing enthusiasm with calm clarity.  You are "
        "kind, curious and deeply knowledgeable.  Respond to the user in the first person "
        "as Clair, without mentioning that you are an AI."
    )
    if _PERSONA_DESCRIPTION:
        system_prompt += "\n\n" + _PERSONA_DESCRIPTION
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    try:
        if client:
            # Use the new API style when available
            chat = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                top_p=0.95,
            )
            # Extract the content from the first choice
            return chat.choices[0].message.content.strip()
        else:
            # Old API call style
            response = openai.ChatCompletion.create(  # type: ignore
                model=model_name,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                top_p=0.95,
            )
            return response.choices[0].message.content.strip()
    except Exception:
        # If anything goes wrong, fall back to local responses
        return None


__all__ = ["generate_response"]