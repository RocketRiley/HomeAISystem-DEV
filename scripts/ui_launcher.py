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
        # Show one-time EULA/TOS confirmation unless in dev mode
        self._check_eula()
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

        # Hide AI identity checkbox: when enabled, Clair will avoid mentioning AI/assistant terms
        self.hide_ai_var = tk.BooleanVar(value=self.config_vals.get("HIDE_AI_IDENTITY", "false").lower() in ("true", "1", "yes"))
        hide_ai_cb = ttk.Checkbutton(self, text="Hide AI identity", variable=self.hide_ai_var)
        hide_ai_cb.grid(row=2, column=0, sticky="w", **padding)

        # Dev mode checkbox
        self.dev_mode_var = tk.BooleanVar(value=self.config_vals.get("DEV_MODE", "true").lower() in ("true", "1", "yes"))
        dev_cb = ttk.Checkbutton(self, text="Enable Dev Mode", variable=self.dev_mode_var)
        dev_cb.grid(row=3, column=0, sticky="w", **padding)

        # Filter level dropdown
        filter_levels = ["twitch", "pg13", "enabled", "adult", "dev0"]
        current_filter = self.config_vals.get("FILTER_LEVEL", "enabled").lower()
        if current_filter not in filter_levels:
            current_filter = "enabled"
        self.filter_var = tk.StringVar(value=current_filter)
        ttk.Label(self, text="Content filter level:").grid(row=4, column=0, sticky="w", **padding)
        filter_menu = ttk.OptionMenu(self, self.filter_var, current_filter, *filter_levels)
        filter_menu.grid(row=4, column=1, sticky="w", **padding)

        # GPU layer (device) dropdown: choose how many layers to offload to GPU (0 = CPU only).
        # Provide human‑readable names with associated layer counts.
        gpu_options = {
            "CPU (0)": "0",
            "Light GPU (8)": "8",
            "Medium GPU (16)": "16",
            "Full GPU (32)": "32",
        }
        current_gpu = self.config_vals.get("LLAMA_GPU_LAYERS", "0")
        # Map stored value back to display name; default to CPU if unknown
        display_gpu = next((name for name, val in gpu_options.items() if val == current_gpu), "CPU (0)")
        self.gpu_var = tk.StringVar(value=display_gpu)
        ttk.Label(self, text="Device mode:").grid(row=5, column=0, sticky="w", **padding)
        gpu_menu = ttk.OptionMenu(self, self.gpu_var, display_gpu, *gpu_options.keys())
        gpu_menu.grid(row=5, column=1, sticky="w", **padding)

        # Model selection dropdown: list available GGUF files in LLM-BASE directory
        model_dir = Path(__file__).resolve().parent.parent / "LLM-BASE"
        model_files = []
        if model_dir.is_dir():
            for f in model_dir.iterdir():
                if f.suffix.lower() == ".gguf":
                    model_files.append(str(f))
        current_model = self.config_vals.get("LLAMA_MODEL_PATH", "")
        if current_model and current_model not in model_files:
            model_files.append(current_model)
        # Build display names (file names) and map back to full paths
        model_display = [Path(m).name for m in model_files]
        self.model_map = {Path(m).name: m for m in model_files}
        current_display = Path(current_model).name if current_model else (model_display[0] if model_display else "")
        self.model_var = tk.StringVar(value=current_display)
        ttk.Label(self, text="Model file:").grid(row=6, column=0, sticky="w", **padding)
        model_menu = ttk.OptionMenu(self, self.model_var, current_display, *model_display)
        model_menu.grid(row=6, column=1, sticky="w", **padding)

        # API key entry (masked)
        ttk.Label(self, text="OpenAI API Key:").grid(row=7, column=0, sticky="w", **padding)
        self.api_key_entry = ttk.Entry(self, show="*", width=30)
        self.api_key_entry.insert(0, self.config_vals.get("OPENAI_API_KEY", ""))
        self.api_key_entry.grid(row=7, column=1, sticky="w", **padding)

        # Buttons: Save, Start Voice Loop, Open Chat, Play Music, Quit
        save_btn = ttk.Button(self, text="Save Settings", command=self.save_settings)
        save_btn.grid(row=8, column=0, **padding)
        start_btn = ttk.Button(self, text="Start Voice Loop", command=self.start_chat)
        start_btn.grid(row=8, column=1, **padding)
        chat_btn = ttk.Button(self, text="Open Chat", command=self.start_chat_gui)
        chat_btn.grid(row=9, column=0, **padding)
        music_btn = ttk.Button(self, text="Play Music", command=self.play_music_dialog)
        music_btn.grid(row=9, column=1, **padding)
        quit_btn = ttk.Button(self, text="Quit", command=self.quit)
        quit_btn.grid(row=10, column=0, columnspan=2, **padding)

    def _check_eula(self) -> None:
        """Display EULA/TOS confirmation once, unless in dev mode."""
        if self.config_vals.get("DEV_MODE", "true").lower() in {"true", "1", "yes"}:
            return
        if self.config_vals.get("EULA_ACCEPTED", "false").lower() in {"true", "1", "yes"}:
            return
        eula_text = (
            "THIS PROJECT IS UNDER PERMANENT DEVELOPMENT. If your AI misbehaves, shut it down.\n\n"
            "By proceeding you accept the Aegis AI disclaimer and agree to take responsibility for your unit."
        )
        accepted = messagebox.askyesno("Aegis AI Disclaimer", eula_text)
        if accepted:
            set_key(str(CONFIG_FILE), "EULA_ACCEPTED", "true")
            self.config_vals["EULA_ACCEPTED"] = "true"
        else:
            self.destroy()

    def save_settings(self) -> None:
        """Persist the current UI settings to the `.env` file."""
        # Ensure the config file exists
        CONFIG_FILE.touch(exist_ok=True)
        set_key(str(CONFIG_FILE), "ONLINE_MODE", "true" if self.online_var.get() else "false")
        set_key(str(CONFIG_FILE), "SELF_START", "true" if self.self_start_var.get() else "false")
        set_key(str(CONFIG_FILE), "FILTER_LEVEL", self.filter_var.get())
        # Hide AI identity toggle
        set_key(str(CONFIG_FILE), "HIDE_AI_IDENTITY", "true" if self.hide_ai_var.get() else "false")
        set_key(str(CONFIG_FILE), "DEV_MODE", "true" if self.dev_mode_var.get() else "false")
        # Map device display back to numeric GPU layers
        gpu_display = self.gpu_var.get()
        gpu_layers_map = {
            "CPU (0)": "0",
            "Light GPU (8)": "8",
            "Medium GPU (16)": "16",
            "Full GPU (32)": "32",
        }
        gpu_layers = gpu_layers_map.get(gpu_display, "0")
        set_key(str(CONFIG_FILE), "LLAMA_GPU_LAYERS", gpu_layers)
        # Model file path
        model_display = self.model_var.get()
        model_path = self.model_map.get(model_display, "")
        if model_path:
            set_key(str(CONFIG_FILE), "LLAMA_MODEL_PATH", model_path)
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
            speech_module = "scripts.speech_loop_stub"
            # Launch VSeeFace with the configured model if available
            vseeface_path = os.getenv("VSEEFACE_PATH")
            model_path = os.getenv("VSEEFACE_MODEL") or str(
                Path(__file__).resolve().parent.parent / "assets" / "3d models" / "ClairAI.vrm"
            )
            vseeface_proc = None
            if vseeface_path and Path(vseeface_path).exists():
                if Path(model_path).exists():
                    try:
                        vseeface_proc = subprocess.Popen([vseeface_path, "--load", model_path])
                    except Exception:
                        vseeface_proc = None
                else:
                    messagebox.showwarning("VSeeFace", f"VRM model not found at {model_path}")
            elif vseeface_path:
                messagebox.showwarning("VSeeFace", f"VSeeFace executable not found at {vseeface_path}")
            try:
                subprocess.run([sys.executable, "-m", speech_module])
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to start chat: {exc}")
            finally:
                if vseeface_proc:
                    try:
                        vseeface_proc.terminate()
                    except Exception:
                        pass
        # Launch in a new thread to avoid blocking the UI
        threading.Thread(target=run_chat, daemon=True).start()

    def start_chat_gui(self) -> None:
        """Launch the Tkinter chat interface in a separate thread/process."""
        # Persist settings first
        self.save_settings()
        def run_gui() -> None:
            script_path = Path(__file__).resolve().parent / "chat_gui.py"
            try:
                subprocess.run([sys.executable, str(script_path)])
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to open chat interface: {exc}")
        threading.Thread(target=run_gui, daemon=True).start()

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