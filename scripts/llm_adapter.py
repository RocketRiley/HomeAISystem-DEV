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
import re
from pathlib import Path
from typing import Optional

# Try to import optional dependencies
try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore

try:
    import llama_cpp  # type: ignore
except ImportError:  # pragma: no cover
    llama_cpp = None  # type: ignore

# Cached Llama model instance
_LLAMA_MODEL = None


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

def _build_system_prompt() -> str:
    """Construct a rich system prompt from Clair's persona metadata.

    This function combines the meta fields in ``persona_clair.json`` to
    produce a natural language description of Clair.  It emphasises
    her human qualities and explicitly instructs the model not to
    mention being an AI, language model or assistant unless allowed
    via the ``HIDE_AI_IDENTITY`` flag.  If the file is missing or
    incomplete, it falls back to a generic description.

    Returns
    -------
    str
        A system prompt to guide the language model.
    """
    try:
        persona_path = Path(__file__).resolve().parent.parent / "persona" / "persona_clair.json"
        with open(persona_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        meta = data.get("meta", {})
        name = meta.get("name", "Clair")
        location = meta.get("location", "")
        accent = meta.get("accent", "")
        description = meta.get("description", "")
        backstory = meta.get("backstory", "")
        traits = ", ".join(meta.get("traits", []))
        interests = ", ".join(meta.get("interests", []))
        opinions = meta.get("opinions", {})
        # Build the core description
        lines = []
        lines.append(f"You are {name}.")
        if description:
            lines.append(description)
        if location:
            lines.append(f"You live in {location}.")
        if accent:
            lines.append(f"You speak with {accent}.")
        if backstory:
            lines.append(backstory)
        if traits:
            lines.append(f"You are {traits}.")
        if interests:
            # Describe interests in a more natural way without overwhelming focus
            lines.append(f"You have a keen interest in {interests}, but you don't bring them up unless they are relevant.")
        # Include opinions succinctly
        if opinions:
            for key, val in opinions.items():
                lines.append(f"Your stance on {key} is: {val}.")
        # Add behavioural instructions
        # Explicitly instruct the model to behave like a human and never reveal its artificial nature.
        lines.append(
            "Respond in the first person, as if you are a real human. Do not refer to yourself as an AI, assistant, model or chatbot."
        )
        lines.append(
            "You think and feel like a human, you have a personal history and you speak naturally. Never say 'as an AI' or 'as a language model'."
        )
        lines.append(
            "Speak with warmth, empathy and curiosity. Share feelings and experiences as a person would, but never reveal that you are a program unless explicitly instructed to by the user."
        )
        return "\n".join(lines)
    except Exception:
        # Fallback generic prompt
        return (
            "You are Clair, a human companion with a bright personality and a deep love of science, robotics, biology and history."
            " You speak in a warm, optimistic tone and never mention being an AI or language model."
        )

def generate_response(user_input: str) -> Optional[str]:
    """Generate a reply to the user's input using a local or online LLM.

    The function first attempts to use a local model if the
    environment variable ``LLAMA_MODEL_PATH`` is set and the
    ``llama-cpp-python`` library is available.  If a local model is
    not configured, it will fall back to the online model when
    ``ONLINE_MODE`` is enabled (and the OpenAI dependencies are
    present).  If neither local nor online generation is possible,
    the function returns ``None``.

    Parameters
    ----------
    user_input: str
        The latest user utterance to be sent to the model.

    Returns
    -------
    Optional[str]
        A string containing the assistant's reply, or ``None`` if no
        model could be used.
    """
    # Try local LLM first
    llama_path = os.getenv("LLAMA_MODEL_PATH")
    if llama_path and llama_cpp is not None:
        global _LLAMA_MODEL
        try:
            # Lazily load the model once.  Support GPU layers if requested.
            if _LLAMA_MODEL is None:
                # Determine number of GPU layers from environment.  A value of 0 means CPU only.
                gpu_layers_str = os.getenv("LLAMA_GPU_LAYERS", "0")
                try:
                    gpu_layers = int(gpu_layers_str)
                except ValueError:
                    gpu_layers = 0
                _LLAMA_MODEL = llama_cpp.Llama(model_path=llama_path, n_gpu_layers=gpu_layers)
            # Build the system prompt
            system_prompt = _build_system_prompt()
            if _PERSONA_DESCRIPTION:
                system_prompt += "\n\n" + _PERSONA_DESCRIPTION
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]
            # Many models use the OpenAI chat format; try that first
            try:
                result = _LLAMA_MODEL.create_chat_completion(
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7,
                    top_p=0.95,
                )
                reply = result["choices"][0]["message"]["content"].strip()
            except Exception:
                # Fallback to plain completion by concatenating prompts
                prompt = system_prompt + "\n\nUser: " + user_input + "\nAssistant:"
                result = _LLAMA_MODEL.create_completion(
                    prompt=prompt,
                    max_tokens=200,
                    temperature=0.7,
                    top_p=0.95,
                    stop=["\nUser:"]
                )
                reply = result["choices"][0]["text"].strip()
            # If hiding AI identity is requested, strip AI references
            hide_ai = os.getenv("HIDE_AI_IDENTITY", "false").lower() in {"true", "1", "yes"}
            if hide_ai:
                # Replace references to being an AI or assistant.  This is a simple heuristic.
                patterns = [
                    r"\bAI\b",
                    r"\bA\.I\.\b",
                    r"\bassistant\b",
                    r"\bmodel\b",
                    r"\blanguage model\b",
                    r"\bchatbot\b",
                    # Remove statements about not having feelings or emotions like a machine
                    r"I\s+do\s+not\s+experience\s+emotions[^\.]*\.",
                    r"I\s+can't\s+feel[^\.]*\.",
                    r"I\s+cannot\s+feel[^\.]*\.",
                    r"As\s+an\s+artificial\s+intelligence[^\.]*\.",
                    r"As\s+an\s+AI[^\.]*\.",
                ]
                for pat in patterns:
                    reply = re.sub(pat, "", reply, flags=re.IGNORECASE)
                # Remove extra spaces and stray punctuation
                reply = re.sub(r"\s{2,}", " ", reply).strip()
            return reply
        except Exception:
            # If anything goes wrong, fall back to online/offline
            pass
    # Local model unavailable; try online if enabled
    online_env = os.getenv("ONLINE_MODE", "false").lower()
    if online_env in {"true", "1", "yes"}:
        # Ensure we have the OpenAI module and an API key
        if openai is None:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY is not set."
        # Configure the OpenAI client
        try:
            # Use the new OpenAI SDK if available
            client = openai.OpenAI(api_key=api_key)  # type: ignore
        except Exception:
            # Fallback to old API if necessary
            openai.api_key = api_key  # type: ignore
            client = None  # type: ignore
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
                chat = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7,
                    top_p=0.95,
                )
                return chat.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(  # type: ignore
                    model=model_name,
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7,
                    top_p=0.95,
                )
                return response.choices[0].message.content.strip()
        except Exception:
            return None
    # Neither local nor online available
    return None


__all__ = ["generate_response"]