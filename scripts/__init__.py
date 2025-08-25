"""Package marker for the scripts module.

This file makes the ``scripts`` directory a proper Python package so that
relative imports (e.g. ``from . import llm_adapter``) work correctly when
modules are executed directly or via the ``-m`` switch.
The file itself is intentionally empty.
"""
