from __future__ import annotations

import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from .types import MemoryPacket
from .active import ActiveMemory
from .short_term import ShortTermMemory
from .mid_term import MidTermMemory
from .long_term import LongTermMemory
from .archive import ArchiveMemory
from ..personal_calendar_manager import PersonalCalendar
from ..llm_adapter import generate_response
from ..curiosity_engine import (
    CuriosityEngine,
    CuriosityContext,
    EmotionState,
    MemoryPeek,
)
 codex/resolve-conflict-in-readme.md-g7qctv
from brain.dreaming import DreamManager
=======
main

# Logs directory for dream cycles
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Determine the root directory for memory storage.  Handlers can override the
# default ``config`` path via the ``MEMORY_ROOT`` environment variable.
BASE_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
CONFIG_DIR = Path(os.getenv("MEMORY_ROOT", BASE_CONFIG_DIR))


class MemoryCoordinator:
    """High level interface coordinating all memory tiers."""

    def __init__(self, user_id: str = "default") -> None:
        self.user_id = user_id
        self.active = ActiveMemory()
        # Ensure tier directories exist and are namespaced per user
        (CONFIG_DIR / "short_term").mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "mid_term").mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "long_term").mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "archive").mkdir(parents=True, exist_ok=True)
        self.short = ShortTermMemory(CONFIG_DIR / "short_term" / f"{user_id}.json")
        self.mid = MidTermMemory(CONFIG_DIR / "mid_term" / f"{user_id}.db")
        self.long = LongTermMemory(CONFIG_DIR / "long_term" / f"{user_id}.json")
        self.archive = ArchiveMemory(CONFIG_DIR / "archive" / f"{user_id}.jsonl.gz")
        self.calendar = PersonalCalendar(CONFIG_DIR)
        self.curiosity = CuriosityEngine()
        self._last_daily_summary: Optional[str] = None
 codex/resolve-conflict-in-readme.md-g7qctv
        self.dream = DreamManager()
=======
 main

    # Compatibility methods -------------------------------------------------
    def add_event(
        self,
        text: str,
        participants: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        salience: float = 0.5,
        expiry: Optional[float] = None,
    ) -> None:
        packet = MemoryPacket.create(text, participants, tags, salience, expiry)
        self.add_packet(packet)

    # Core API --------------------------------------------------------------
    def add_packet(self, packet: MemoryPacket) -> None:
        self.active.push(packet)
        self.short.add(packet)
        if packet.expiry:
            self.mid.add(packet, packet.expiry)
        if packet.salience >= 0.8:
            self.long.reinforce(packet)

    def get_last_events(self, n: int = 10) -> List[dict]:
        recent = self.short.get_recent(24)
        return [p.to_dict() for p in recent[-n:]]

    def summarise_day(self, date: str) -> str:
        packets = [p for p in self.short.entries if time.strftime("%Y-%m-%d", time.localtime(p.timestamp)) == date]
        if not packets:
            return f"No events recorded for {date}."
        participants = sorted({p for e in packets for p in e.participants})
        tags = sorted({t for e in packets for t in e.tags})
        texts = [e.text for e in packets]
        summary_parts: List[str] = []
        char_count = 0
        for t in texts:
            for s in t.split('. '):
                s_clean = s.strip()
                if s_clean:
                    summary_parts.append(s_clean)
                    char_count += len(s_clean)
                    if len(summary_parts) >= 3 or char_count > 200:
                        break
            if len(summary_parts) >= 3 or char_count > 200:
                break
        summary_text = '. '.join(summary_parts) + ('...' if summary_parts else '')
        participant_str = ', '.join(participants) if participants else 'none'
        tag_str = ', '.join(tags) if tags else 'none'
        return f"Summary of {date}: participants: {participant_str}; tags: {tag_str}. {summary_text}"

    def consolidate(self) -> None:
        # Move old short-term entries
        old_packets = self.short.prune()
        if old_packets:
            self._create_daily_summary_and_schedule_events(old_packets)
        # Expire mid-term
        expired = self.mid.sweep()
        if expired:
            self.archive.store(expired)
        # Decay long-term
        demoted = self.long.decay()
        if demoted:
            self.archive.store(demoted)
 codex/resolve-conflict-in-readme.md-g7qctv
        # Nightly emotional hygiene
        self.dream.run_nightly(self._last_daily_summary)
=======
        # Enter dream cycle after consolidation
        self.initiate_dream_cycle()
 main

    # Search ---------------------------------------------------------------
    def search(self, query: str) -> List[dict]:
        results = []
        for p in self.short.entries:
            if query.lower() in p.text.lower():
                results.append(p.to_dict())
        results.extend(self.long.query(query))
        return results

    # ------------------------------------------------------------------
    def _create_daily_summary_and_schedule_events(self, packets: List[MemoryPacket]) -> None:
        """Summarize old packets and schedule any future events."""
        text_block = "\n".join(p.text for p in packets)
 codex/resolve-conflict-in-readme.md-g7qctv
        date = datetime.utcnow().strftime("%Y-%m-%d")
=======
 main
        prompt = (
            "Summarize the key events, topics, and participants from the "
            "following daily log. Be concise.\n\n" + text_block
        )
        daily_summary = generate_response(prompt, history=None, human_mode=False) or ""
        self._last_daily_summary = daily_summary
 codex/resolve-conflict-in-readme.md-g7qctv
        summary_packet = MemoryPacket.create(
            f"Daily summary {date}: {daily_summary}",
            tags=["daily_summary"],
            salience=0.6,
        )
        self.long.reinforce(summary_packet)
        self.archive.store([summary_packet])
=======
 main

        event_prompt = (
            "Analyze this summary for future events, appointments, or "
            "deadlines. If found, return a JSON object with 'title', 'date' "
            "(YYYY-MM-DD), and 'time' (HH:MM). If not found, return null.\n\n"
            f"Summary:\n{daily_summary}"
        )
        event_json = generate_response(event_prompt, history=None, human_mode=False) or "null"
        event_data: Optional[Dict[str, Any]] = None
        try:
            parsed = json.loads(event_json)
            if isinstance(parsed, dict):
                event_data = parsed
        except Exception:
            event_data = None
        if event_data:
            self._schedule_event(event_data, daily_summary)

        for p in packets:
            if p.salience >= 0.8:
                self.long.reinforce(p)
            self.archive.store([p])

    def _schedule_event(self, event: Dict[str, Any], daily_summary: str) -> None:
        title = event.get("title", "Untitled event")
        date = event.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        time_str = event.get("time", "00:00")
        self.calendar.add_event("user", date, time_str, time_str, title, daily_summary)

        try:
            dt = datetime.fromisoformat(f"{date}T{time_str}:00")
        except Exception:
            dt = datetime.utcnow()
        reminder_dt = dt - timedelta(days=3)
        reminder_text = (
            f"Proactive Reminder: Talk to Handler about upcoming event: {title}"
        )
        packet = MemoryPacket.create(
            reminder_text,
            participants=["Handler"],
            tags=["reminder"],
            salience=0.7,
            expiry=reminder_dt.timestamp(),
        )
        self.mid.add(packet, packet.expiry)

 codex/resolve-conflict-in-readme.md-g7qctv
=======
    def initiate_dream_cycle(self) -> None:
        """Stage 2 of sleep: freeform reflection stored as a dream log."""
        if not self._last_daily_summary:
            return
        prompt = (
            "Using the following daily summary, drift into a silent monologue "
            "and explore thoughts, stories, or analogies that relate to the day.\n\n"
            f"Summary:\n{self._last_daily_summary}\n"
            "Monologue:"
        )
        dream_text = generate_response(prompt, history=None, human_mode=False) or ""
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "dream": dream_text.strip(),
        }
        with open(LOG_DIR / "dream_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        self._last_daily_summary = None

    def recall_last_dream(self) -> str:
        """Return the most recent dream entry for the handler."""
        path = LOG_DIR / "dream_log.jsonl"
        if not path.exists():
            return "No dreams recorded yet."
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return "No dreams recorded yet."
            data = json.loads(lines[-1])
            return data.get("dream", "No dream content.")
        except Exception:
            return "Error recalling dream."
 main

    def purge_archive(self, age_threshold_days: int, salience_threshold: float) -> None:
        """Manually trigger purge of the archive store."""
        self.archive.purge_old_memories(age_threshold_days, salience_threshold)
 codex/resolve-conflict-in-readme.md-g7qctv
    def recall_last_dream(self) -> Optional[str]:
        return self.dream.recall_last_dream()

=======
 main
    def check_proactive_events(self) -> Dict[str, List[str]]:
        """Return due reminders and follow-up questions."""
        reminders: List[str] = []
        expired = self.mid.sweep()
        for p in expired:
            if p.text.startswith("Proactive Reminder"):
                reminders.append(p.text)

        followups: List[str] = []
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        for e in self.calendar.list_events("user", yesterday):
            user_text = f"I went to {e.get('title', 'an event')} yesterday"
            ctx = CuriosityContext(
                user_text=user_text,
                persona_name="Clair",
                mode="enabled",
                dlc_warm_nights=False,
                emotion=EmotionState(0.0, 0.0, 0.0, []),
                memory=MemoryPeek([], {}, []),
                turns_since_user_question=2,
                user_tokens_in_last_turn=0,
                now_ts=time.time(),
                last_probe_ts=0.0,
                probes_so_far=0,
                persona_constraints={"no_ai_self_ref": True, "style": "warm-casual"},
                safety_filter_level="enabled",
                user_led_adult_topic=False,
                active_goal=None,
            )
            question = self.curiosity.maybe_ask(ctx)
            if question:
                followups.append(question)
            else:
                followups.append(f"How did {e.get('title', 'that event')} go yesterday?")

        return {"reminders": reminders, "followups": followups}


__all__ = ["MemoryCoordinator", "MemoryPacket"]
