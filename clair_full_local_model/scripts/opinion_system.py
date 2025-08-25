#!/usr/bin/env python3
"""Opinion management for Clair.

This module defines a simple opinion store and update mechanism that
mirrors how a human might revise their beliefs or preferences over
time.  Each opinion has a *stance* (in the range [-1, 1]), a
*confidence* (in the range [0, 1]) and an evidence log explaining
previous updates.  Opinions can be of type ``belief`` (factual,
reasoned claims), ``preference`` (subjective tastes) or ``value``
(hard constraints).  Value opinions change very slowly and cannot be
flipped by user input.

The :class:`OpinionManager` loads and saves opinions from a JSON
file.  It exposes methods to list, retrieve and update them.  The
update algorithm follows the description in the system design:

    • The stance change ``Δs`` is proportional to the evidence
      strength, the trust assigned to the source, and the remaining
      uncertainty (1‑confidence).  A constant ``k`` controls the
      maximum update size.  Value opinions cap the update step at
      ``±0.05`` to avoid violating core principles.

    • The confidence increase is controlled by ``c_gain`` times the
      evidence strength, trust and remaining uncertainty.  Confidence
      approaches 1 as more consistent evidence accumulates.

    • Each call to :meth:`update` appends an entry to the opinion's
      ``evidence_log`` containing the timestamp and parameters of the
      update.  This allows the assistant to explain why a stance has
      shifted when asked.

See ``config/opinions.json`` for an example opinion store.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class OpinionManager:
    """Manages loading, storing and updating opinions about topics.

    Parameters
    ----------
    path: Path or str
        The path to the JSON file where opinions are persisted.  If
        the file does not exist, it will be created on first save.
    """

    def __init__(self, path: Any) -> None:
        self.path = Path(path)
        self.opinions: Dict[str, Dict[str, Any]] = {}
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    def load(self) -> None:
        """Load opinions from the JSON file.  If the file is missing
        or malformed, the manager starts with an empty dictionary.
        """
        try:
            if self.path.exists():
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Convert list of opinions into dict keyed by topic
                self.opinions = {op["topic"]: op for op in data if "topic" in op}
            else:
                self.opinions = {}
        except Exception:
            # On any load error, start with an empty set of opinions
            self.opinions = {}

    def save(self) -> None:
        """Persist the current opinions to disk as JSON.  Opinions
        will be written as a list of dicts; the order of opinions is
        undefined.
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(list(self.opinions.values()), f, indent=2)
        except Exception:
            # Swallow errors silently; in a real application you may
            # want to log exceptions
            pass

    # ------------------------------------------------------------------
    # Querying opinions
    def list_topics(self) -> List[str]:
        """Return a sorted list of all known opinion topics."""
        return sorted(self.opinions.keys())

    def get(self, topic: str) -> Optional[Dict[str, Any]]:
        """Return the opinion dict for the given topic, or ``None`` if
        no opinion is recorded."""
        return self.opinions.get(topic)

    # ------------------------------------------------------------------
    # Updating opinions
    def update(
        self,
        topic: str,
        evidence_strength: float,
        trust: float,
        direction: float,
        reason: str = "",
        source: str = "user",
    ) -> Dict[str, Any]:
        """Update an opinion on ``topic`` using a single piece of evidence.

        Parameters
        ----------
        topic: str
            The subject of the opinion to update (e.g. "standing desks").
            If this topic does not yet exist, a new opinion of type
            ``belief`` will be created with zero stance and confidence.

        evidence_strength: float
            A measure of how compelling the new evidence is, between 0
            (weak) and 1 (strong).  Larger values drive bigger stance
            changes and increases in confidence.

        trust: float
            The trust assigned to the source of evidence, between 0
            (unreliable) and 1 (fully trusted).  Evidence from highly
            trusted sources produces larger updates.

        direction: float
            The direction of the evidence: positive values support the
            current topic stance, negative values oppose it.  Values
            should be in [-1, 1]; for example, +1 means strong
            supporting evidence, -0.5 means moderate opposing evidence.

        reason: str, optional
            A free‑text explanation or citation for the evidence.  This
            will be stored in the opinion's ``evidence_log``.

        source: str, optional
            A tag identifying who or what provided the evidence (e.g.
            ``"riley"``, ``"study"``).  Useful for auditing changes.

        Returns
        -------
        dict
            The updated opinion dictionary.

        Notes
        -----
        The update algorithm uses two constants, ``k`` and ``c_gain``,
        controlling how stance and confidence evolve.  Value opinions
        (core principles) are protected: their maximum stance change
        per update is capped at ±0.05 to prevent flips.  Beliefs and
        preferences can change freely, though very strong evidence is
        required to move them far.
        """
        # Normalise input ranges
        evidence_strength = max(0.0, min(1.0, evidence_strength))
        trust = max(0.0, min(1.0, trust))
        direction = max(-1.0, min(1.0, direction))

        # Ensure an opinion exists
        if topic not in self.opinions:
            self.opinions[topic] = {
                "topic": topic,
                "type": "belief",
                "stance": 0.0,
                "confidence": 0.0,
                "evidence_log": [],
                "guardrails": []
            }
        opinion = self.opinions[topic]

        # Determine maximum allowed stance change
        max_delta = 0.05 if opinion.get("type") == "value" else 1.0

        # Retrieve current values
        current_stance = float(opinion.get("stance", 0.0))
        current_conf = float(opinion.get("confidence", 0.0))

        # Compute update step
        k = 0.5  # control magnitude of stance adjustment
        c_gain = 0.3  # control how quickly confidence increases
        delta = k * evidence_strength * trust * (1.0 - current_conf) * direction
        # Cap delta to respect guardrails on values
        if abs(delta) > max_delta:
            delta = max_delta if delta > 0 else -max_delta

        # Apply update and clamp to [-1, 1]
        new_stance = max(-1.0, min(1.0, current_stance + delta))
        new_confidence = max(0.0, min(1.0, current_conf + c_gain * evidence_strength * trust * (1.0 - current_conf)))

        # Update opinion
        opinion["stance"] = new_stance
        opinion["confidence"] = new_confidence

        # Log update event
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "evidence_strength": evidence_strength,
            "trust": trust,
            "direction": direction,
            "reason": reason,
            "source": source,
            "new_stance": new_stance,
            "new_confidence": new_confidence
        }
        opinion.setdefault("evidence_log", []).append(event)

        # Save updated state to disk
        self.opinions[topic] = opinion
        self.save()
        return opinion


__all__ = ["OpinionManager"]