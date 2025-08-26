"""Map emotional PAD values to language model generation styles."""

from __future__ import annotations

from typing import Dict

# Five simple micro-styles used as building blocks
_MICRO_STYLES = {
    "calm": {"temperature": 0.5, "top_p": 0.7, "interjection": ""},
    "curious": {"temperature": 0.8, "top_p": 0.9, "interjection": "Hmm,"},
    "joyful": {"temperature": 0.9, "top_p": 0.95, "interjection": "Hey!"},
    "melancholy": {"temperature": 0.6, "top_p": 0.8, "interjection": ""},
    "angry": {"temperature": 1.0, "top_p": 0.9, "interjection": "Listen,"},
}


def _style_weights_from_pad(pad: Dict[str, float]) -> Dict[str, float]:
    """Roughly map PAD coordinates to micro-style weights."""
    P, A = pad.get("P", 0.0), pad.get("A", 0.0)
    weights = {
        "joyful": max(0.0, P),
        "melancholy": max(0.0, -P),
        "angry": max(0.0, A - P),
        "calm": max(0.0, -A),
        "curious": max(0.0, min(1.0, (A + P) / 2)),
    }
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def _blend_styles(weights: Dict[str, float]) -> Dict[str, float]:
    temperature = sum(_MICRO_STYLES[k]["temperature"] * w for k, w in weights.items())
    top_p = sum(_MICRO_STYLES[k]["top_p"] * w for k, w in weights.items())
    # For interjection choose the style with highest weight
    primary = max(weights.items(), key=lambda kv: kv[1])[0]
    interjection = _MICRO_STYLES[primary]["interjection"]
    return {"temperature": temperature, "top_p": top_p, "interjection": interjection}


def style_from_pad(pad: Dict[str, float]) -> Dict[str, float]:
    """Public helper to obtain style parameters from PAD."""
    weights = _style_weights_from_pad(pad)
    return _blend_styles(weights)


__all__ = ["style_from_pad"]
