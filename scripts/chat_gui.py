#!/usr/bin/env python3
"""Simple graphical chat interface for Clair.

This module provides a Tkinter-based chat window that allows users to
interact with Clair via text.  It loads the environment from the
``.env`` file, uses ``llm_adapter.generate_response`` to obtain
replies, and applies the configured content filter via ``filter_system``.

If a local LLM is configured (via ``LLAMA_MODEL_PATH``), the replies
will be generated offline.  Otherwise, responses are produced via
the online API when ``ONLINE_MODE`` is enabled.  If neither option
is available, the assistant falls back to a simple canned response.

To launch the chat UI directly, run:

```bash
python scripts/chat_gui.py
```

You can also open it from the main GUI launcher by clicking "Open Chat".

"""
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *_, **__: None  # type: ignore

try:
    from PIL import Image, ImageTk  # type: ignore
except ImportError:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore

# Import modules using package imports when available and fall back
# to top‑level imports when executed directly.  This allows running
# chat_gui.py both as part of the package (via python -m scripts.chat_gui)
# or directly (via python scripts/chat_gui.py) without import errors.
try:
    from . import llm_adapter  # type: ignore
except ImportError:
    import llm_adapter  # type: ignore

try:
    # Import the FilterPipeline and alias it as FilterSystem for backward compatibility
    from .filter_system import FilterPipeline as FilterSystem  # type: ignore
except ImportError:
    from filter_system import FilterPipeline as FilterSystem  # type: ignore

try:
    from .memory_manager import MemoryManager  # type: ignore
except ImportError:
    from memory_manager import MemoryManager  # type: ignore

# Load environment variables from .env if present
load_dotenv()


class ClairChatApp:
    """A simple chat GUI that interacts with Clair."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Clair Assistant Chat")
        # Try to set a program icon if available
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if Image and ImageTk and logo_path.is_file():
            try:
                img = Image.open(logo_path)
                img = img.resize((64, 64), Image.LANCZOS)
                self.logo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(self.root, image=self.logo)
                icon_label.pack(pady=(10, 0))
            except Exception:
                pass
        # Conversation area
        self.chat_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state="disabled",
            width=80,
            height=20,
            font=("Arial", 12),
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Entry field and send button
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame, textvariable=self.entry_var, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self._on_send)
        send_btn = tk.Button(entry_frame, text="Send", command=self._on_send)
        send_btn.pack(side=tk.RIGHT)
        # Filter system (lazy load on demand)
        self._filter: Optional[FilterSystem] = None
        # Log manager for saving conversation history
        try:
            from .log_manager import LogManager  # type: ignore
        except Exception:
            from log_manager import LogManager  # type: ignore
        log_path = Path(__file__).resolve().parent.parent / "config" / "logs.jsonl"
        self.logger = LogManager(log_path)
        # Memory manager for episodic memory
        mem_path = Path(__file__).resolve().parent.parent / "config" / "memory.json"
        self.memory = MemoryManager(mem_path)
        self.memory_status = tk.StringVar()
        status_label = tk.Label(self.root, textvariable=self.memory_status, anchor="w", font=("Arial", 8))
        status_label.pack(padx=10, pady=(0, 5), fill=tk.X)
        # Greet the user
        self._print("Clair", "Hello! I'm ready to chat.")

    @property
    def filter(self) -> FilterSystem:
        if self._filter is None:
            self._filter = FilterSystem()
        return self._filter

    def _print(self, sender: str, text: str) -> None:
        """Append a message to the chat area."""
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"{sender}: {text}\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)
        # Log the message
        try:
            self.logger.log({"sender": sender, "text": text})
        except Exception:
            pass
        # Store in memory and update status readout
        try:
            self.memory.add_event(f"{sender}: {text}", participants=[sender])
            last = self.memory.get_last_events(1)[0]["text"]
            if len(last) > 60:
                last = last[:57] + "..."
            self.memory_status.set(f"Last memory: {last}")
        except Exception:
            self.memory_status.set("Memory error")

    def _on_send(self, event: Optional[tk.Event] = None) -> None:
        user_input = self.entry_var.get().strip()
        if not user_input:
            return
        self.entry_var.set("")
        self._print("You", user_input)
        # Respond asynchronously
        threading.Thread(target=self._generate_and_display, args=(user_input,), daemon=True).start()

    def _generate_and_display(self, user_input: str) -> None:
        reply = llm_adapter.generate_response(user_input)
        if reply is None:
            # Fallback if no model available
            reply = "I'm sorry, I'm currently unable to generate a response."
        else:
            # Apply content filter using FilterPipeline.filter_text
            reply = self.filter.filter_text(reply)
        self._print("Clair", reply)


def main() -> None:
    root = tk.Tk()
    app = ClairChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()