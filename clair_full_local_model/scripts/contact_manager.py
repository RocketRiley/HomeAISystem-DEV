#!/usr/bin/env python3
"""Per‑person contact manager for Clair.

This module manages information about individual people that Clair
interacts with.  Each contact record stores identifiers (e.g.
Twitch usernames, local names), current relationship dimensions
(valence, trust, familiarity) and optional notes.  Relationship
values range from -1 (strongly negative) to +1 (strongly positive).

The :class:`ContactManager` provides methods to add contacts,
retrieve them, list all contacts, and update feelings toward a
person based on new evidence.  Updates are similar to the opinion
update mechanism but are applied to specific dimensions rather than
overall stance.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContactManager:
    """Stores contact profiles and manages relationship values."""

    def __init__(self, path: Any) -> None:
        self.path = Path(path)
        self.contacts: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Data is expected to be a list of contact dicts
                    self.contacts = {c.get("id"): c for c in data if c.get("id")}
            except Exception:
                self.contacts = {}
        else:
            self.contacts = {}

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(list(self.contacts.values()), f, indent=2)
        except Exception:
            pass

    def list_contacts(self) -> List[str]:
        return sorted(self.contacts.keys())

    def get(self, contact_id: str) -> Optional[Dict[str, Any]]:
        return self.contacts.get(contact_id)

    def add_contact(self, contact_id: str, names: Optional[List[str]] = None) -> None:
        if contact_id in self.contacts:
            return
        self.contacts[contact_id] = {
            "id": contact_id,
            "names": names or [contact_id],
            "feelings": {
                "valence": 0.0,
                "trust": 0.0,
                "familiarity": 0.0
            },
            "notes": [],
            "last_seen": None
        }
        self._save()

    def update_feeling(
        self,
        contact_id: str,
        dimension: str,
        evidence_strength: float,
        trust: float,
        direction: float,
        reason: str = ""
    ) -> None:
        """Adjust a specific relationship dimension for a contact.

        Parameters
        ----------
        contact_id: str
            The identifier of the person.
        dimension: str
            One of ``"valence"``, ``"trust"`` or ``"familiarity"``.
        evidence_strength: float
            How strong the new evidence is (0–1).
        trust: float
            Trust in the evidence source (0–1).
        direction: float
            Direction of update (-1 to +1).  Positive values increase
            the dimension; negative values decrease it.
        reason: str, optional
            A short note explaining why the update occurred.
        """
        if contact_id not in self.contacts:
            # Auto‑add unknown contacts
            self.add_contact(contact_id)
        if dimension not in ("valence", "trust", "familiarity"):
            raise ValueError(f"Unknown relationship dimension: {dimension}")
        c = self.contacts[contact_id]
        current = float(c["feelings"].get(dimension, 0.0))
        # Compute a delta similar to the opinion update (but simpler)
        k = 0.5
        # Normalise inputs
        evidence_strength = max(0.0, min(1.0, evidence_strength))
        trust = max(0.0, min(1.0, trust))
        direction = max(-1.0, min(1.0, direction))
        delta = k * evidence_strength * trust * direction * (1 - abs(current))
        new_value = max(-1.0, min(1.0, current + delta))
        c["feelings"][dimension] = new_value
        note = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "dimension": dimension,
            "evidence_strength": evidence_strength,
            "trust": trust,
            "direction": direction,
            "reason": reason,
            "new_value": new_value
        }
        c.setdefault("notes", []).append(note)
        c["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.contacts[contact_id] = c
        self._save()


__all__ = ["ContactManager"]