#!/usr/bin/env python3
"""Simple content filter pipeline for Clair.

This module implements a layered filtering system that transforms text
according to a selected censorship level.  The levels are applied in
descending order of strictness: ``twitch`` > ``pg13`` > ``enabled`` >
``adult`` > ``dev0``.  Each level defines a set of words or phrases
that should be replaced or removed to meet a particular moderation
policy.  For example, the ``twitch`` level enforces Twitch’s terms
of service, while ``pg13`` aims for movie‑rating‑equivalent
language.  The ``enabled`` level is a modest filter suitable for
general audiences, ``adult`` removes almost no terms (but may still
obscure a few explicit words), and ``dev0`` leaves the text
unchanged.

Note: this is a demonstration and not a comprehensive profanity
filter.  For production use you should employ a well‑maintained
filter list and incorporate locale‑specific nuances.
"""

from __future__ import annotations

import re
from typing import Dict


class FilterPipeline:
    """Applies content filters to text based on a current level."""

    # Define per‑level replacement dictionaries.  Keys are lowercase
    # substrings to match, values are the replacement text.  The
    # ``twitch`` list is the most restrictive; lower levels can be
    # subsets.  These lists are illustrative; feel free to expand or
    # modify them to match your own content policies.
    _REPLACEMENTS: Dict[str, Dict[str, str]] = {
        "twitch": {
            "fuck": "fudge",
            "shit": "poop",
            "damn": "darn",
            "bitch": "jerk",
            "asshole": "jerk",
            "bastard": "jerk",
            "sex": "hugs",
            "porn": "adult stuff",
            "alcohol": "juice",
            "drugs": "medicine",
            "kill": "defeat"
        },
        "pg13": {
            "fuck": "frick",
            "shit": "crap",
            "damn": "dang",
            "bitch": "jerk",
            "asshole": "jerk",
            "sex": "kissing",
            "porn": "explicit content",
            "kill": "beat"
        },
        "enabled": {
            "fuck": "fudge",
            "shit": "crap",
            "bitch": "jerk"
        },
        "adult": {
            # Adult filter performs minimal redactions; we obscure
            # expletives slightly to soften tone but leave meaning.
            "fuck": "f***",
            "shit": "s***",
            "bitch": "b***",
            "porn": "adult content",
            "asshole": "a**hole"
        },
        "dev0": {}
    }

    def __init__(self, level: str = "enabled") -> None:
        self.level = level.lower()
        if self.level not in self._REPLACEMENTS:
            raise ValueError(f"Unknown filter level: {level}")

    def set_level(self, level: str) -> None:
        """Change the active filter level.  Raises if the level is
        unknown."""
        lvl = level.lower()
        if lvl not in self._REPLACEMENTS:
            raise ValueError(f"Unknown filter level: {level}")
        self.level = lvl

    def filter_text(self, text: str) -> str:
        """Return a filtered version of ``text`` based on the current
        filter level.  Replacements are applied case‑insensitively
        using simple substring matching.  Only complete word matches
        are replaced (e.g. "shit" in "shitty" is not replaced)."""
        if not text or self.level == "dev0":
            return text
        replacements = self._REPLACEMENTS[self.level]
        # Build a regex pattern that matches any of the keys as a whole word
        if not replacements:
            return text
        pattern = re.compile(r"\b(" + "|".join(map(re.escape, replacements.keys())) + r")\b", re.IGNORECASE)

        def repl(match: re.Match) -> str:
            word = match.group(0)
            lower = word.lower()
            replacement = replacements.get(lower, word)
            # Preserve capitalisation for the first letter
            if word[0].isupper():
                return replacement.capitalize()
            return replacement

        return pattern.sub(repl, text)


__all__ = ["FilterPipeline"]