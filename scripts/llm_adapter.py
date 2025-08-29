#!/usr/bin/env python3
"""Adapter for generating responses via a local or online LLM."""
from __future__ import annotations

import os
import re
from typing import Dict, List, Optional

from .prompt_manager import build_messages
from .dialogue_regulator import normalize_reply

try:  # pragma: no cover - optional
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore

try:  # pragma: no cover - optional
    import llama_cpp  # type: ignore
except ImportError:  # pragma: no cover
    llama_cpp = None  # type: ignore

try:  # pragma: no cover - optional
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover
    tiktoken = None  # type: ignore

_LLAMMA_MODEL = None  # type: ignore


def _verbose_log(msg: str) -> None:
    if os.getenv("LLM_VERBOSE", "false").lower() in {"true", "1", "yes"}:
        print(msg)


def _strip_ai_mentions(text: str) -> str:
    patterns = [
        r"\bAI\b",
        r"\bA\.I\.\b",
        r"\bassistant\b",
        r"\bmodel\b",
        r"\blanguage model\b",
        r"\bchatbot\b",
        r"As an artificial intelligence[^\.]*\.",
        r"As an AI[^\.]*\.",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()


def generate_response(
    user_input: str,
    history: Optional[List[Dict[str, str]]] = None,
    *,
    tool_results: Optional[str] = None,
    human_mode: bool = True,
    style: Optional[Dict[str, float]] = None,
    emotion: Optional[Dict[str, float]] = None,
) -> Optional[str]:
    """Generate a reply to the user's input using a local or online LLM."""
    messages = build_messages(
        user_input, history=history, tool_results=tool_results, human_mode=human_mode
    )
    temp = style.get("temperature", 0.7) if style else 0.7
    top_p = style.get("top_p", 0.95) if style else 0.95

    llama_path = os.getenv("LLAMA_MODEL_PATH")
    max_tokens_local = int(os.getenv("LLAMA_MAX_TOKENS", "512"))
    cont = os.getenv("LLM_CONTINUE_ON_TRUNCATION", "true").lower() in {"1", "true", "yes"}
    if llama_path and llama_cpp is not None:
        global _LLAMMA_MODEL  # type: ignore
        try:
            if _LLAMMA_MODEL is None:  # type: ignore
                gpu_layers = int(os.getenv("LLAMA_GPU_LAYERS", "0") or 0)
                n_ctx = int(os.getenv("LLAMA_N_CTX", "4096") or 4096)
                _LLAMMA_MODEL = llama_cpp.Llama(
                    model_path=llama_path, n_gpu_layers=gpu_layers, n_ctx=n_ctx
                )
            else:
                n_ctx = _LLAMMA_MODEL.n_ctx  # type: ignore
            # Dynamically compute available tokens so replies are not cut off.
            prompt_text = "".join(m["content"] for m in messages)
            prompt_tokens = len(_LLAMMA_MODEL.tokenize(prompt_text.encode()))  # type: ignore
            available = n_ctx - prompt_tokens - 8
            max_tokens_local = min(max_tokens_local, max(0, available))
            reply_parts = []
            while True:
                result = _LLAMMA_MODEL.create_chat_completion(  # type: ignore
                    messages=messages,
                    max_tokens=max_tokens_local,
                    temperature=temp,
                    top_p=top_p,
                    stop=["<|im_end|>"],
                )
                part = result["choices"][0]["message"]["content"].strip()
                finish = result["choices"][0].get("finish_reason")
                _verbose_log(f"llama finish_reason={finish}")
                reply_parts.append(part)
                if finish != "length" or not cont:
                    break
                messages.append({"role": "assistant", "content": part})
                messages.append({"role": "user", "content": ""})
                prompt_text = "".join(m["content"] for m in messages)
                prompt_tokens = len(_LLAMMA_MODEL.tokenize(prompt_text.encode()))  # type: ignore
                available = n_ctx - prompt_tokens - 8
                max_tokens_local = min(int(os.getenv("LLAMA_MAX_TOKENS", "512")), max(0, available))
            reply = " ".join(reply_parts).strip()
        except Exception:
            return None
    else:
        online_env = os.getenv("ONLINE_MODE", "false").lower()
        if online_env not in {"true", "1", "yes"} or openai is None:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY is not set."
        try:
            client = openai.OpenAI(api_key=api_key)  # type: ignore
        except Exception:
            openai.api_key = api_key  # type: ignore
            client = None  # type: ignore
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        max_tokens_online = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
        n_ctx_online = int(os.getenv("OPENAI_N_CTX", "8192"))
        prompt_text = "".join(m["content"] for m in messages)
        cont = os.getenv("LLM_CONTINUE_ON_TRUNCATION", "true").lower() in {"1", "true", "yes"}
        if tiktoken is not None:
            try:
                enc = tiktoken.encoding_for_model(model_name)
                prompt_tokens = len(enc.encode(prompt_text))
            except Exception:
                prompt_tokens = len(prompt_text.split())
        else:
            prompt_tokens = len(prompt_text.split())
        available = n_ctx_online - prompt_tokens - 8
        max_tokens_online = min(max_tokens_online, max(0, available))
        try:
            reply_parts = []
            while True:
                if client:
                    chat = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=max_tokens_online,
                        temperature=temp,
                        top_p=top_p,
                        stop=["<|im_end|>"],
                    )
                    finish = chat.choices[0].finish_reason
                    part = chat.choices[0].message.content.strip()
                else:
                    response = openai.ChatCompletion.create(  # type: ignore
                        model=model_name,
                        messages=messages,
                        max_tokens=max_tokens_online,
                        temperature=temp,
                        top_p=top_p,
                        stop=["<|im_end|>"],
                    )
                    finish = response.choices[0].finish_reason
                    part = response.choices[0].message.content.strip()
                _verbose_log(f"openai finish_reason={finish}")
                reply_parts.append(part)
                if finish != "length" or not cont:
                    break
                messages.append({"role": "assistant", "content": part})
                messages.append({"role": "user", "content": ""})
                prompt_text = "".join(m["content"] for m in messages)
                if tiktoken is not None:
                    try:
                        enc = tiktoken.encoding_for_model(model_name)
                        prompt_tokens = len(enc.encode(prompt_text))
                    except Exception:
                        prompt_tokens = len(prompt_text.split())
                else:
                    prompt_tokens = len(prompt_text.split())
                available = n_ctx_online - prompt_tokens - 8
                max_tokens_online = min(int(os.getenv("OPENAI_MAX_TOKENS", "512")), max(0, available))
            reply = " ".join(reply_parts).strip()
        except Exception:
            return None

    if human_mode:
        reply = _strip_ai_mentions(reply)
    if style and style.get("interjection"):
        reply = f"{style['interjection']} {reply}".strip()
    return normalize_reply(reply, emotion or {})


__all__ = ["generate_response"]
