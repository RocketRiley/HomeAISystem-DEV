#!/usr/bin/env python3
"""Simple music player stub for Clair.

This module provides a very lightweight interface for playing music
via YouTube.  When `play_music` is called with a query string, it
opens the default web browser to a YouTube search page for that
query.  If the query appears to be a URL (starts with ``http``), it
will open the URL directly instead.  In an offline or headless
environment, the function simply prints what it would do.

This is intended as a placeholder; in a full implementation you
might integrate with a dedicated music player, use a YouTube API,
or call ``yt-dlp`` to download and play audio.
"""
from __future__ import annotations

import webbrowser
def play_music(query: str) -> None:
    """Play music based on a search query or URL.

    If ``query`` looks like a URL (starts with ``http``), it will be
    opened directly in the default web browser.  Otherwise, the
    function constructs a YouTube search URL for the query.  In
    environments where a GUI browser is not available, the URL
    opening may fail silently.  The function always prints a message
    indicating what it is doing.

    Parameters
    ----------
    query: str
        The search terms or full URL to play.

    Returns
    -------
    None
    """
    if not query:
        print("Clair: No music query provided.")
        return
    # Determine if the query is already a URL
    if query.lower().startswith("http"):
        url = query
    else:
        # Encode spaces as + for YouTube search
        search_terms = query.strip().replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={search_terms}"
    print(f"Clair: Opening music for '{query}'... (URL: {url})")
    try:
        webbrowser.open(url)
    except Exception:
        # In a non‑GUI environment this will do nothing
        pass


__all__ = ["play_music"]
