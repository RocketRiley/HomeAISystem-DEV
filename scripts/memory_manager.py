#!/usr/bin/env python3
"""Backwards compatible wrapper for the new tiered memory system."""

from __future__ import annotations

from .memory import MemoryCoordinator, MemoryPacket  # type: ignore


class MemoryManager(MemoryCoordinator):
    """Alias of :class:`MemoryCoordinator` for legacy imports."""

    pass


__all__ = ["MemoryManager", "MemoryPacket"]
