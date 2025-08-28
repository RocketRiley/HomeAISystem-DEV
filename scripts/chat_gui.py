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
import time
from pathlib import Path
from typing import Optional, List, Dict

import tkinter as tk
from tkinter import scrolledtext

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_, **__):  # type: ignore
        """Fallback if python-dotenv is not installed."""
        return None

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
    from .curiosity_engine import (
        CuriosityEngine,
        CuriosityContext,
        EmotionState,
        MemoryPeek,
    )  # type: ignore
except ImportError:
    from curiosity_engine import (  # type: ignore
        CuriosityEngine,
        CuriosityContext,
        EmotionState,
        MemoryPeek,
    )

# Load environment variables from .env if present
load_dotenv()

curiosity_engine = CuriosityEngine()
_last_probe_ts = 0.0
_probes_so_far = 0


class ClairChatApp:
    """A simple chat GUI that interacts with Clair."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Clair Assistant Chat")
        self.persona_name = os.getenv("PERSONA_NAME", "Clair")
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
            from .memory_manager import MemoryManager  # type: ignore
        except Exception:
            from log_manager import LogManager  # type: ignore
            from memory_manager import MemoryManager  # type: ignore
        log_path = Path(__file__).resolve().parent.parent / "config" / "logs.jsonl"
        self.logger = LogManager(log_path)
        user_id = os.getenv("USER_ID", "default")
        self.memory = MemoryManager(user_id)
        # Conversation history for prompt construction
        self.history: List[Dict[str, str]] = []
        self.human_mode = os.getenv("HIDE_AI_IDENTITY", "false").lower() in {"true", "1", "yes"}
        # Greet the user
        self._print(self.persona_name, "Hello! I'm ready to chat.")

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

    def _on_send(self, event: Optional[tk.Event] = None) -> None:
        user_input = self.entry_var.get().strip()
        if not user_input:
            return
        self.entry_var.set("")
        self._print("You", user_input)
        try:
            self.memory.add_event(user_input, participants=["user"], tags=["conversation"])
        except Exception:
            pass
        # Respond asynchronously
        threading.Thread(target=self._generate_and_display, args=(user_input,), daemon=True).start()

    def _generate_and_display(self, user_input: str) -> None:
        reply = llm_adapter.generate_response(
            user_input,
            history=self.history,
            human_mode=self.human_mode,
        )
        self.history.append({"role": "user", "content": user_input})
        if reply is None:
            reply = "I'm sorry, I'm currently unable to generate a response."
        else:
            reply = self.filter.filter_text(reply)
            self.history.append({"role": "assistant", "content": reply})
        if len(self.history) > 20:
            self.history = self.history[-20:]
        self._print(self.persona_name, reply)
        try:
            self.memory.add_event(reply, participants=["clair"], tags=["conversation"])
        except Exception:
            pass

        global _last_probe_ts, _probes_so_far
        ctx = CuriosityContext(
            user_text=user_input,
            persona_name=self.persona_name,
            mode=os.getenv("FILTER_MODE", "enabled"),
            dlc_warm_nights=os.getenv("DLC_WARM_NIGHTS", "false").lower() in {"true", "1", "yes"},
            emotion=EmotionState(valence=0.0, arousal=0.0, dominance=0.0, top_labels=[]),
            memory=MemoryPeek(known_topics=[], missing_slots={}, last_followups=[]),
            turns_since_user_question=1,
            user_tokens_in_last_turn=len(user_input.split()),
            now_ts=time.time(),
            last_probe_ts=_last_probe_ts,
            probes_so_far=_probes_so_far,
            persona_constraints={"no_ai_self_ref": True, "style": "warm-casual"},
            safety_filter_level=os.getenv("FILTER_MODE", "enabled"),
            user_led_adult_topic=False,
            active_goal=None,
        )
        followup = curiosity_engine.maybe_ask(ctx)
        if followup:
            self._print(self.persona_name, followup)
            try:
                self.memory.add_event(followup, participants=["clair"], tags=["curiosity"])
            except Exception:
                pass
            _last_probe_ts = ctx.now_ts
            _probes_so_far += 1


def main() -> None:
    root = tk.Tk()
    ClairChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
