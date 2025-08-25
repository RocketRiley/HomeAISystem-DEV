#!/usr/bin/env python3
"""Simple graphical launcher and settings panel for Clair.

This script provides a basic cross‑platform user interface using
``tkinter`` to configure and start Clair.  Users can toggle between
online and offline modes, enable or disable the self‑start (wake
word) behaviour, choose the content filter level, and launch the
conversational loop.  Settings are stored in a `.env` file so that
they persist across runs.  A Play Music button is also provided to
quickly open a YouTube search for a given query.

Usage:

    python scripts/ui_launcher.py

If you bundle this project with PyInstaller or another packager, you
may set this file as the entry point to create a standalone
application.  See the README for packaging instructions.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Dict

import tkinter as tk
from tkinter import ttk, messagebox

try:
    from dotenv import dotenv_values, set_key
except ImportError:
    # Fallback if python-dotenv is not installed: use dummy functions
    def dotenv_values(path: str) -> Dict[str, str]:
        return {}

    def set_key(path: str, key: str, value: str) -> None:
        # Append or replace a line in a simple .env file
        try:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"{key}={value}\n")
                return
            # Read existing lines
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    updated = True
                    break
            if not updated:
                lines.append(f"{key}={value}\n")
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass


CONFIG_FILE = Path(__file__).resolve().parent.parent / ".env"


class LauncherUI(tk.Tk):
    """A simple Tkinter window for configuring and launching Clair."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Clair Launcher")
        self.geometry("400x300")
        self.resizable(False, False)
        # Load existing config values
        self.config_vals = dotenv_values(str(CONFIG_FILE))
        # Build UI
        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}
        # Online mode checkbox
        self.online_var = tk.BooleanVar(value=self.config_vals.get("ONLINE_MODE", "false").lower() in ("true", "1", "yes"))
        online_cb = ttk.Checkbutton(self, text="Enable Online Mode", variable=self.online_var)
        online_cb.grid(row=0, column=0, sticky="w", **padding)
        # Self‑start checkbox
        self.self_start_var = tk.BooleanVar(value=self.config_vals.get("SELF_START", "true").lower() not in ("false", "0", "no"))
        self_start_cb = ttk.Checkbutton(self, text="Enable Self‑Start (proactive)", variable=self.self_start_var)
        self_start_cb.grid(row=1, column=0, sticky="w", **padding)
        # Filter level dropdown
        filter_levels = ["twitch", "pg13", "enabled", "adult", "dev0"]
        current_filter = self.config_vals.get("FILTER_LEVEL", "enabled").lower()
        if current_filter not in filter_levels:
            current_filter = "enabled"
        self.filter_var = tk.StringVar(value=current_filter)
        ttk.Label(self, text="Content filter level:").grid(row=2, column=0, sticky="w", **padding)
        filter_menu = ttk.OptionMenu(self, self.filter_var, current_filter, *filter_levels)
        filter_menu.grid(row=2, column=1, sticky="w", **padding)
        # API key entry (masked)
        ttk.Label(self, text="OpenAI API Key:").grid(row=3, column=0, sticky="w", **padding)
        self.api_key_entry = ttk.Entry(self, show="*", width=30)
        self.api_key_entry.insert(0, self.config_vals.get("OPENAI_API_KEY", ""))
        self.api_key_entry.grid(row=3, column=1, sticky="w", **padding)
        # Buttons
        save_btn = ttk.Button(self, text="Save Settings", command=self.save_settings)
        save_btn.grid(row=4, column=0, **padding)
        start_btn = ttk.Button(self, text="Start Chat", command=self.start_chat)
        start_btn.grid(row=4, column=1, **padding)
        music_btn = ttk.Button(self, text="Play Music", command=self.play_music_dialog)
        music_btn.grid(row=5, column=0, **padding)
        quit_btn = ttk.Button(self, text="Quit", command=self.quit)
        quit_btn.grid(row=5, column=1, **padding)

    def save_settings(self) -> None:
        """Persist the current UI settings to the `.env` file."""
        # Ensure the config file exists
        CONFIG_FILE.touch(exist_ok=True)
        set_key(str(CONFIG_FILE), "ONLINE_MODE", "true" if self.online_var.get() else "false")
        set_key(str(CONFIG_FILE), "SELF_START", "true" if self.self_start_var.get() else "false")
        set_key(str(CONFIG_FILE), "FILTER_LEVEL", self.filter_var.get())
        # Only write the API key if it's non‑empty
        api_key = self.api_key_entry.get().strip()
        if api_key:
            set_key(str(CONFIG_FILE), "OPENAI_API_KEY", api_key)
        messagebox.showinfo("Settings Saved", "Your settings have been saved to .env.")

    def start_chat(self) -> None:
        """Launch the speech loop in a separate thread/process."""
        # Save settings before launching
        self.save_settings()
        def run_chat() -> None:
            script_path = Path(__file__).resolve().parent / "speech_loop_stub.py"
            try:
                subprocess.run([sys.executable, str(script_path)])
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to start chat: {exc}")
        # Launch in a new thread to avoid blocking the UI
        threading.Thread(target=run_chat, daemon=True).start()

    def play_music_dialog(self) -> None:
        """Prompt the user for a music search term and open YouTube."""
        query = tk.simpledialog.askstring("Play Music", "Enter search terms or a YouTube URL:")
        if query:
            # Use the music_player module if available
            try:
                from .music_player import play_music  # type: ignore
            except Exception:
                try:
                    from music_player import play_music  # type: ignore
                except Exception:
                    play_music = None  # type: ignore
            if play_music:
                play_music(query)
            else:
                # Fallback: open a YouTube search in the default browser
                url = f"https://www.youtube.com/results?search_query={query.strip().replace(' ', '+')}"
                webbrowser.open(url)


def main() -> None:
    ui = LauncherUI()
    ui.mainloop()


if __name__ == "__main__":
    main()