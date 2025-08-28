from __future__ import annotations

"""Helpers for tag-aware emotion persistence."""

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

# Default tag table; values can be overridden by config
_DEFAULT_TABLE: Dict[str, Dict[str, float]] = {
    "abuse": {"tau_hours": 96.0, "weight": 1.4, "floor_P": -0.2},
    "trust_breach": {"tau_hours": 60.0, "weight": 1.3},
    "grief": {"tau_hours": 72.0, "weight": 1.2},
    "bonding": {"tau_hours": 60.0, "weight": 1.2},
    "humor": {"tau_hours": 8.0, "weight": 0.9},
    "minor_slight": {"tau_hours": 4.0, "weight": 0.8},
}

@dataclass
class TagRule:
    tau_hours: float
    weight: float
    floor_P: float | None = None


def load_table(overrides: Dict[str, Dict[str, float]] | None = None) -> Dict[str, TagRule]:
    """Merge overrides into the default tag table."""
    table = {k: TagRule(**v) for k, v in _DEFAULT_TABLE.items()}
    if overrides:
        for tag, vals in overrides.items():
            base = table.get(tag, TagRule(24.0, 1.0))
            table[tag] = TagRule(
                tau_hours=vals.get("tau_hours", base.tau_hours),
                weight=vals.get("weight", base.weight),
                floor_P=vals.get("floor", {}).get("P", base.floor_P) if isinstance(vals.get("floor"), dict) else base.floor_P,
            )
    return table


def effective_tau(rule: TagRule, intensity: float, repetition: float, relationship: float) -> float:
    """Return the effective half-life (hours) for an event."""
    return rule.tau_hours * intensity * repetition * relationship


def weight(rule: TagRule, intensity: float) -> float:
    return rule.weight * intensity


def floors(tags: Iterable[str], table: Dict[str, TagRule]) -> Tuple[float | None, float | None, float | None]:
    P = A = D = None
    for t in tags:
        r = table.get(t)
        if r and r.floor_P is not None:
            P = P if P is not None else r.floor_P
            P = max(P, r.floor_P)
    return P, A, D

__all__ = ["TagRule", "load_table", "effective_tau", "weight", "floors"]
