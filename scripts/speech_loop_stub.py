#!/usr/bin/env python3
"""A simple conversational loop for Clair.

This script demonstrates how Clair could respond to user input in
character, while managing a sleep/awake state and tracking a few
emotions.  It uses the persona example files to choose responses and
decays emotions over time.  The script does not perform real speech
recognition or synthesis; it simply reads text from stdin and prints
responses to stdout.

Usage:

    python scripts/speech_loop_stub.py

Type your messages and press Enter.  Type "sleep" to put Clair into
sleep mode (she will only respond to "wake").  Type "wake" to wake
her up.  Type "exit" to quit.
"""

import json
import os
import random
import re
from pathlib import Path
from typing import Dict, Optional, List

# Import opinion and filter systems
try:
    # Allow running from package root where scripts is a package
    from .opinion_system import OpinionManager  # type: ignore
    from .filter_system import FilterPipeline  # type: ignore
    from .memory_manager import MemoryManager  # type: ignore
    from .contact_manager import ContactManager  # type: ignore
    from .tasks_manager import TaskManager  # type: ignore
    from .calendar_integration_stub import CalendarIntegration  # type: ignore
    from .personal_calendar_manager import PersonalCalendar  # type: ignore
    from .music_player import play_music  # type: ignore
    from .llm_adapter import generate_response  # type: ignore
    from .emotion_style import style_from_pad  # type: ignore
    from .osc_bridge_stub import send_pad  # type: ignore
except ImportError:
    # Fallback for direct execution without package context
    from opinion_system import OpinionManager  # type: ignore
    from filter_system import FilterPipeline  # type: ignore
    from memory_manager import MemoryManager  # type: ignore
    from contact_manager import ContactManager  # type: ignore
    from tasks_manager import TaskManager  # type: ignore
    from calendar_integration_stub import CalendarIntegration  # type: ignore
    from personal_calendar_manager import PersonalCalendar  # type: ignore
    from music_player import play_music  # type: ignore
    from llm_adapter import generate_response  # type: ignore
    from emotion_style import style_from_pad  # type: ignore
    from osc_bridge_stub import send_pad  # type: ignore


def load_persona_examples():
    base = Path(__file__).resolve().parent.parent / "persona" / "examples"
    examples = {}
    for path in base.glob("*.json"):
        state = path.stem
        with open(path, "r", encoding="utf-8") as f:
            examples[state] = json.load(f)
    return examples


def choose_line(state, examples):
    return random.choice(examples.get(state, examples.get("neutral", ["..."])) )


def update_emotions(active, text):
    """Update emotions based on keywords in the user input."""
    text = text.lower()
    triggers = [
        (re.compile(r"\b(thanks?|thank you)\b"), "joy"),
        (re.compile(r"\b(amazing|wow|cool)\b"), "excitement"),
        (re.compile(r"\b(question|how|what|why)\b"), "curiosity"),
        (re.compile(r"\b(sad|hard|tired|depress)\b"), "gentle_sad"),
        (re.compile(r"\b(help|can you|please)\b"), "supportive")
    ]
    for pattern, emo in triggers:
        if pattern.search(text):
            active[emo] = min(1.0, active.get(emo, 0.0) + 0.5)
    return active


def decay_emotions(active):
    for emo in list(active.keys()):
        active[emo] *= 0.8
        if active[emo] < 0.05:
            active[emo] = 0.0
    return active


def pad_from_emotions(active, emo_defs):
    total = sum(active.values()) or 1e-9
    P = sum(active[name] * emo_defs[name]["pad"]["P"] for name in active) / total
    A = sum(active[name] * emo_defs[name]["pad"]["A"] for name in active) / total
    D = sum(active[name] * emo_defs[name]["pad"]["D"] for name in active) / total
    return {"P": P, "A": A, "D": D}


def choose_state_from_pad(pad):
    """Map PAD values to a persona state for reply."""
    if pad["P"] > 0.5:
        return "joy"
    if pad["P"] < -0.5:
        return "gentle_sad"
    if pad["A"] > 0.5:
        return "energetic"
    if pad["A"] < -0.3:
        return "calm_home"
    return "neutral"


def main() -> None:
    """Run an interactive demonstration of Clair's persona with
    opinion management and content filtering.

    The loop reads user input from the terminal and responds in
    character.  Commands are available to change the filter level,
    inspect and update opinions.  Type ``exit`` to quit, ``sleep``
    to put Clair to sleep, and ``wake`` to wake her again.

    Examples::

        set filter pg13
        opinion show standing desks effectiveness
        opinion update standing desks effectiveness -0.5 0.7 0.9 Too wobbly

    """
    # Load persona examples and emotion definitions
    examples = load_persona_examples()
    emo_path = Path(__file__).resolve().parent.parent / "emotion_pack" / "emotions.json"
    with open(emo_path, "r", encoding="utf-8") as f:
        emo_data = json.load(f)["emotions"]
    emo_defs = {e["name"]: e for e in emo_data}

    # Load opinion store
    opinions_path = Path(__file__).resolve().parent.parent / "config" / "opinions.json"
    opinion_manager = OpinionManager(opinions_path)

    # Create filter pipeline from environment or default
    filter_level = os.getenv("FILTER_LEVEL", "enabled").lower()
    try:
        filter_pipeline = FilterPipeline(filter_level)
    except ValueError:
        print(f"Warning: Unknown FILTER_LEVEL '{filter_level}', falling back to 'enabled'.")
        filter_pipeline = FilterPipeline("enabled")

    state = "awake"
    active_emotions: Dict[str, float] = {}
    history: List[Dict[str, str]] = []
    hide_identity = os.getenv("HIDE_AI_IDENTITY", "false").lower() in {"true", "1", "yes"}

    # Instantiate memory, contacts, tasks and calendar managers
    user_id = os.getenv("USER_ID", "default")
    contacts_path = Path(__file__).resolve().parent.parent / "config" / "contacts.json"
    tasks_path = Path(__file__).resolve().parent.parent / "config" / "tasks.json"
    calendar_path = Path(__file__).resolve().parent.parent / "config" / "calendar_events.json"
    memory_manager = MemoryManager(user_id)
    contact_manager = ContactManager(contacts_path)
    task_manager = TaskManager(tasks_path)
    calendar_integration = CalendarIntegration(calendar_path)
    # Personal calendars for Clair and the user
    personal_calendar = PersonalCalendar(Path(__file__).resolve().parent.parent / "config")

    # Optional sensory monitors
    try:
        from .vision_monitor import start_vision_monitor  # type: ignore
    except Exception:  # pragma: no cover
        try:
            from vision_monitor import start_vision_monitor  # type: ignore
        except Exception:  # pragma: no cover
            start_vision_monitor = None  # type: ignore
    try:
        from .audio_monitor import start_audio_monitor  # type: ignore
    except Exception:  # pragma: no cover
        try:
            from audio_monitor import start_audio_monitor  # type: ignore
        except Exception:  # pragma: no cover
            start_audio_monitor = None  # type: ignore
    if start_vision_monitor:
        try:
            start_vision_monitor()
        except Exception:
            pass
    if start_audio_monitor:
        try:
            start_audio_monitor()
        except Exception:
            pass

    dev_mode = os.getenv("DEV_MODE", "true").lower() in {"true", "1", "yes"}
    if not dev_mode:
        print(
            "THIS PROJECT IS UNDER PERMANENT DEVELOPMENT.\n"
            "If Clair misbehaves, shut her down and report the issue."
        )
        ack = input("Type 'I AGREE' to continue: ").strip().lower()
        if ack != "i agree":
            print("Exiting.")
            return

    print(
        "Clair is ready. You can chat or issue commands.\n"
        "Commands:\n"
        "  set filter <twitch|pg13|enabled|adult|dev0>\n"
        "  opinion show <topic>\n"
        "  opinion update <topic> <direction> <strength> <trust> <reason>\n"
        "  memory last [n] – list the last n events\n"
        "  memory summary <YYYY-MM-DD> – summarise events from a day\n"
        "  task add <due YYYY-MM-DD> <description> – add a task (also schedules it in Clair's calendar)\n"
        "  task list [completed|incomplete] – list tasks\n"
        "  task done <task_id> – mark a task complete\n"
        "  contact list – list known contacts\n"
        "  contact show <id> – show relationship values\n"
        "  contact update <id> <valence|trust|familiarity> <direction> <strength> <trust> <reason>\n"
        "  calendar next – show the next upcoming event (personal + external)\n"
        "  calendar day <YYYY-MM-DD> – list events on a date (personal + external)\n"
        "  calendar add <clair|user> <date YYYY-MM-DD> <start HH:MM> <end HH:MM> <title> [description] – add a personal event\n"
        "  music play <query> – open YouTube to play music matching the query\n"
        "  status – show a quick status board\n"
        "  rollup [YYYY-MM-DD] – generate a daily memory summary (default: yesterday)\n"
        "Type 'sleep' to put Clair to sleep and 'wake' to wake her. Type 'exit' to quit."
    )

    from datetime import datetime

    first_run = True

    def maybe_auto_speak() -> None:
        nonlocal state, first_run
        if os.getenv("SELF_START", "true").lower() in {"false", "0", "no"}:
            return
        if state != "awake":
            return
        today = datetime.utcnow().date().isoformat()
        due_tasks = [t for t in task_manager.list_tasks(False) if t.get("due") and t["due"] <= today]
        if due_tasks:
            t = due_tasks[0]
            msg = f"Reminder – task '{t['description']}' is due today ({t['due']})."
            print(filter_pipeline.filter_text(f"Clair (auto): {msg}"))
            memory_manager.add_event(msg, participants=["clair"], tags=["task"])
            return
        events_today = personal_calendar.list_events("clair", today) + personal_calendar.list_events("user", today)
        if events_today:
            e = events_today[0]
            msg = f"Upcoming event at {e['start']} – {e['title']}."
            print(filter_pipeline.filter_text(f"Clair (auto): {msg}"))
            memory_manager.add_event(msg, participants=["clair"], tags=["event"])
            return
        if first_run:
            msg = random.choice(["Hey there!", "Hello!", "Hi, ready when you are."])
            print(filter_pipeline.filter_text(f"Clair (auto): {msg}"))
            memory_manager.add_event(msg, participants=["clair"], tags=["greeting"])
            first_run = False

    maybe_auto_speak()

    while True:
        maybe_auto_speak()
        try:
            user_input = input("You: ").strip()
        except EOFError:
            # End of input
            print()
            break
        if not user_input:
            continue
        lower = user_input.lower()

        # Exit command
        if lower == "exit":
            print("Clair: Goodbye!")
            break

        # Sleep/wake handling
        if state == "sleep":
            if lower == "wake":
                state = "awake"
                print("Clair: Good morning! I'm awake now.")
            else:
                print("Clair (sleeping): ...")
            continue
        else:
            if lower == "sleep":
                state = "sleep"
                line = choose_line("sleep_reminder", examples)
                print(filter_pipeline.filter_text(f"Clair: {line}"))
                continue

        # Command: set filter
        if lower.startswith("set filter"):
            parts = lower.split()
            if len(parts) >= 3:
                new_level = parts[2]
                try:
                    filter_pipeline.set_level(new_level)
                    print(f"Clair: Filter level set to '{new_level}'.")
                except ValueError:
                    print("Clair: Unknown filter level. Available levels: twitch, pg13, enabled, adult, dev0.")
            else:
                print("Clair: Usage: set filter <twitch|pg13|enabled|adult|dev0>")
            continue

        # Command: opinion show
        if lower.startswith("opinion show"):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                topic = parts[2]
                op = opinion_manager.get(topic)
                if op:
                    stance = op.get("stance", 0.0)
                    conf = op.get("confidence", 0.0)
                    print(filter_pipeline.filter_text(
                        f"Clair: Opinion on '{topic}': stance={stance:.2f}, confidence={conf:.2f}"
                    ))
                else:
                    print(filter_pipeline.filter_text(f"Clair: I don't have a recorded opinion on '{topic}'."))
            else:
                print("Clair: Usage: opinion show <topic>")
            continue

        # Command: opinion update
        if lower.startswith("opinion update"):
            # Expect format: opinion update <topic> <dir> <strength> <trust> <reason...>
            parts = user_input.split(maxsplit=5)
            if len(parts) >= 6:
                _, _, topic, dir_str, strength_str, trust_reason = parts
                trust_tokens = trust_reason.split(maxsplit=1)
                if len(trust_tokens) >= 1:
                    trust_str = trust_tokens[0]
                    reason = trust_tokens[1] if len(trust_tokens) > 1 else ""
                    try:
                        direction = float(dir_str)
                        strength = float(strength_str)
                        trust_val = float(trust_str)
                        opinion_manager.update(topic, strength, trust_val, direction, reason, source="user")
                        print(filter_pipeline.filter_text(f"Clair: Updated opinion on '{topic}'."))
                    except ValueError:
                        print("Clair: Invalid numbers for direction, strength or trust.\n"
                              "Usage: opinion update <topic> <direction> <strength> <trust> <reason>")
                else:
                    print("Clair: Invalid format. Usage: opinion update <topic> <direction> <strength> <trust> <reason>")
            else:
                print("Clair: Usage: opinion update <topic> <direction> <strength> <trust> <reason>")
            continue

        # Command: memory last
        if lower.startswith("memory last"):
            parts = user_input.split()
            n = 5
            if len(parts) >= 3:
                try:
                    n = int(parts[2])
                except Exception:
                    pass
            events = memory_manager.get_last_events(n)
            if not events:
                print(filter_pipeline.filter_text("Clair: I have no recorded events yet."))
            else:
                print(filter_pipeline.filter_text(f"Clair: Last {len(events)} events:"))
                for e in events:
                    ts = e.get("timestamp")
                    text = e.get("text")
                    print(filter_pipeline.filter_text(f"  {ts} – {text}"))
            continue

        # Command: memory summary
        if lower.startswith("memory summary"):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                date = parts[2]
                summary = memory_manager.summarise_day(date)
                print(filter_pipeline.filter_text(f"Clair: {summary}"))
            else:
                print("Clair: Usage: memory summary <YYYY-MM-DD>")
            continue

        # Command: task add
        if lower.startswith("task add"):
            parts = user_input.split(maxsplit=3)
            if len(parts) >= 4:
                _, _, due, desc = parts
                task_id = task_manager.add_task(desc, due)
                # Also schedule this task in Clair's personal calendar at a default time
                try:
                    # Use a default window of 09:00–09:30 for tasks
                    personal_calendar.add_event("clair", due, "09:00", "09:30", f"Task: {desc}", "Automatically scheduled task")
                except Exception:
                    pass
                print(filter_pipeline.filter_text(f"Clair: Added task {task_id} and scheduled it on my calendar."))
            else:
                print("Clair: Usage: task add <due YYYY-MM-DD> <description>")
            continue

        # Command: task list
        if lower.startswith("task list"):
            parts = user_input.split()
            status = None
            if len(parts) >= 3:
                arg = parts[2].lower()
                if arg == "completed":
                    status = True
                elif arg == "incomplete":
                    status = False
            tasks = task_manager.list_tasks(status)
            if not tasks:
                print(filter_pipeline.filter_text("Clair: There are no matching tasks."))
            else:
                print(filter_pipeline.filter_text("Clair: Tasks:"))
                for t in tasks:
                    sid = t.get("id")
                    desc = t.get("description")
                    due = t.get("due")
                    comp = "✓" if t.get("completed") else "✗"
                    print(filter_pipeline.filter_text(f"  {sid} [{comp}] due {due}: {desc}"))
            continue

        # Command: task done
        if lower.startswith("task done"):
            parts = user_input.split()
            if len(parts) >= 3:
                tid = parts[2]
                if task_manager.complete_task(tid):
                    print(filter_pipeline.filter_text(f"Clair: Marked task {tid} as complete."))
                else:
                    print(filter_pipeline.filter_text(f"Clair: Couldn't find task {tid}."))
            else:
                print("Clair: Usage: task done <task_id>")
            continue

        # Command: contact list
        if lower.startswith("contact list"):
            ids = contact_manager.list_contacts()
            if not ids:
                print(filter_pipeline.filter_text("Clair: I have no known contacts."))
            else:
                ids_str = ", ".join(ids)
                print(filter_pipeline.filter_text(f"Clair: Known contacts: {ids_str}"))
            continue

        # Command: contact show
        if lower.startswith("contact show"):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                cid = parts[2]
                c = contact_manager.get(cid)
                if c:
                    feelings = c.get("feelings", {})
                    names = ", ".join(c.get("names", [cid]))
                    valence = feelings.get("valence", 0.0)
                    trust_val = feelings.get("trust", 0.0)
                    familiar = feelings.get("familiarity", 0.0)
                    print(filter_pipeline.filter_text(
                        f"Clair: Contact {cid} (names: {names}) feelings – valence={valence:.2f}, trust={trust_val:.2f}, familiarity={familiar:.2f}."
                    ))
                else:
                    print(filter_pipeline.filter_text(f"Clair: No data on contact '{cid}'."))
            else:
                print("Clair: Usage: contact show <id>")
            continue

        # Command: contact update
        if lower.startswith("contact update"):
            # Format: contact update <id> <dimension> <direction> <strength> <trust> <reason>
            parts = user_input.split(maxsplit=6)
            if len(parts) >= 7:
                _, _, cid, dim, dir_str, strength_str, trust_reason = parts
                trust_tokens = trust_reason.split(maxsplit=1)
                if len(trust_tokens) >= 1:
                    trust_str = trust_tokens[0]
                    reason = trust_tokens[1] if len(trust_tokens) > 1 else ""
                    try:
                        direction = float(dir_str)
                        strength = float(strength_str)
                        trust_val = float(trust_str)
                        contact_manager.update_feeling(cid, dim, strength, trust_val, direction, reason)
                        print(filter_pipeline.filter_text(f"Clair: Updated contact {cid}."))
                    except ValueError:
                        print("Clair: Invalid numbers for direction, strength or trust.")
                    except Exception as e:
                        print(filter_pipeline.filter_text(f"Clair: Error updating contact: {e}"))
                else:
                    print("Clair: Invalid format. Usage: contact update <id> <dimension> <direction> <strength> <trust> <reason>")
            else:
                print("Clair: Usage: contact update <id> <dimension> <direction> <strength> <trust> <reason>")
            continue

        # Command: calendar next
        if lower.startswith("calendar next"):
            from datetime import datetime
            now_dt = datetime.utcnow()
            # Next event from personal calendars (both Clair and user)
            personal_event = personal_calendar.get_next_event(None, now_dt)
            # Next event from external calendar
            external_event = calendar_integration.get_next_event(now_dt)
            # Select the earliest event across both sources
            def parse_time(evt: Dict[str, str]) -> datetime:
                if not evt:
                    return datetime.max
                # personal events have separate date and start
                if "date" in evt:
                    return datetime.fromisoformat(f"{evt['date']}T{evt['start']}:00")
                # external events have ISO timestamp in 'start'
                return datetime.fromisoformat(evt.get("start"))
            # Determine which event is earlier
            candidates = []
            if personal_event:
                candidates.append((parse_time(personal_event), personal_event, personal_event.get("who")))
            if external_event:
                candidates.append((parse_time(external_event), external_event, "external"))
            if not candidates:
                print(filter_pipeline.filter_text("Clair: No upcoming events."))
            else:
                candidates.sort(key=lambda x: x[0])
                _, evt, owner = candidates[0]
                # Format message based on owner
                if owner == "external":
                    title = evt.get("title", "(no title)")
                    start = evt.get("start")
                    desc = evt.get("description", "")
                    print(filter_pipeline.filter_text(
                        f"Clair: Next event is '{title}' at {start}: {desc}"
                    ))
                else:
                    # personal event
                    title = evt.get("title", "(no title)")
                    date = evt.get("date")
                    start = evt.get("start")
                    desc = evt.get("description", "")
                    who = evt.get("who", owner)
                    prefix = "My" if who == "clair" else "Your"
                    print(filter_pipeline.filter_text(
                        f"Clair: {prefix} next event is '{title}' on {date} at {start}: {desc}"
                    ))
            continue

        # Command: calendar day
        if lower.startswith("calendar day"):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                date = parts[2]
                # Combine personal and external events
                external_events = calendar_integration.list_events_on(date)
                personal_clair = personal_calendar.list_events("clair", date)
                personal_user = personal_calendar.list_events("user", date)
                if not external_events and not personal_clair and not personal_user:
                    print(filter_pipeline.filter_text(f"Clair: No events on {date}."))
                else:
                    print(filter_pipeline.filter_text(f"Clair: Events on {date}:"))
                    # Print personal events first
                    for e in personal_clair:
                        title = e.get("title", "(no title)")
                        start = e.get("start")
                        end = e.get("end")
                        desc = e.get("description", "")
                        print(filter_pipeline.filter_text(f"  (my) {start}–{end}: {title} – {desc}"))
                    for e in personal_user:
                        title = e.get("title", "(no title)")
                        start = e.get("start")
                        end = e.get("end")
                        desc = e.get("description", "")
                        print(filter_pipeline.filter_text(f"  (your) {start}–{end}: {title} – {desc}"))
                    for e in external_events:
                        title = e.get("title", "(no title)")
                        start_str = e.get("start")
                        end_str = e.get("end")
                        desc = e.get("description", "")
                        # Extract times from ISO format
                        try:
                            start_time = start_str.split("T")[1] if "T" in start_str else start_str
                            end_time = end_str.split("T")[1] if end_str and "T" in end_str else end_str
                        except Exception:
                            start_time = start_str
                            end_time = end_str
                        print(filter_pipeline.filter_text(f"  {start_time}–{end_time}: {title} – {desc}"))
            else:
                print("Clair: Usage: calendar day <YYYY-MM-DD>")
            continue

        # Command: calendar add
        if lower.startswith("calendar add"):
            # Expected format: calendar add <clair|user> <YYYY-MM-DD> <HH:MM> <HH:MM> <title> [description]
            parts = user_input.split(maxsplit=6)
            if len(parts) < 6:
                print("Clair: Usage: calendar add <clair|user> <date YYYY-MM-DD> <start HH:MM> <end HH:MM> <title> [description]")
            else:
                _, _, who, date_str, start_time, end_time, *rest = parts
                who = who.lower()
                if who not in ("clair", "user"):
                    print("Clair: The calendar owner must be 'clair' or 'user'.")
                else:
                    title_desc = rest[0] if rest else ""
                    # Split title and description if user provided both as a single quoted string or with a separator
                    # We assume the title does not contain newlines.  Description is optional.
                    # If the title contains spaces, it will already be captured by the rest parameter.
                    title = title_desc
                    description = ""
                    # If the user provided a | to separate title and description, split it
                    if "|" in title_desc:
                        title, description = [x.strip() for x in title_desc.split("|", 1)]
                    try:
                        personal_calendar.add_event(who, date_str, start_time, end_time, title, description)
                        owner_label = "my" if who == "clair" else "your"
                        print(filter_pipeline.filter_text(f"Clair: Added {owner_label} event '{title}' on {date_str} from {start_time} to {end_time}."))
                    except Exception as e:
                        print(filter_pipeline.filter_text(f"Clair: Couldn't add event: {e}"))
            continue

        # Command: music play
        if lower.startswith("music play"):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                query = parts[2]
                play_music(query)
            else:
                print("Clair: Usage: music play <search query or URL>")
            continue

        # Command: status board
        if lower == "status":
            # Lazy import to avoid circular deps on start
            try:
                from status_board import main as show_status
            except ImportError:
                from .status_board import main as show_status  # type: ignore
            show_status()
            continue

        # Command: rollup
        if lower.startswith("rollup"):
            parts = user_input.split()
            if len(parts) >= 2:
                date_str = parts[1]
            else:
                # Default to yesterday's date in local time
                from datetime import datetime, timedelta
                today = datetime.utcnow().date()
                date_str = (today - timedelta(days=1)).isoformat()
            summary = memory_manager.summarise_day(date_str)
            print(filter_pipeline.filter_text(f"Clair: {summary}"))
            continue

        # Regular conversation: update emotions based on keywords
        active_emotions = update_emotions(active_emotions, user_input)
        # Compute PAD from active emotions
        pad = pad_from_emotions(active_emotions, emo_defs)
        try:
            send_pad(pad["P"], pad["A"], pad["D"])
        except Exception:
            pass
        # Apply contact feelings adjustment (bias mood by relationship)
        current_contact_id = "riley"  # in this demo we assume the user is Riley
        contact = contact_manager.get(current_contact_id)
        if contact:
            feelings = contact.get("feelings", {})
            # Map feelings to PAD adjustments.  Valence boosts P, familiarity boosts A,
            # trust boosts D.  Scale down to avoid overpowering base mood.
            cP = 0.3 * float(feelings.get("valence", 0.0))
            cA = 0.2 * float(feelings.get("familiarity", 0.0))
            cD = 0.3 * float(feelings.get("trust", 0.0))
            pad["P"] = max(-1.0, min(1.0, pad["P"] + 0.15 * cP))
            pad["A"] = max(-1.0, min(1.0, pad["A"] + 0.15 * cA))
            pad["D"] = max(-1.0, min(1.0, pad["D"] + 0.15 * cD))
        # Select a response state
        response_state = choose_state_from_pad(pad)
        style = style_from_pad(pad)
        # Attempt to generate a reply via the LLM
        reply: Optional[str] = None
        try:
            reply = generate_response(
                user_input,
                history=history,
                human_mode=hide_identity,
                style=style,
            )
        except Exception:
            reply = None
        history.append({"role": "user", "content": user_input})
        if reply:
            response = reply
            history.append({"role": "assistant", "content": reply})
        else:
            response = choose_line(response_state, examples)
        if len(history) > 20:
            history = history[-20:]
        # Filter the response according to the current filter level
        filtered = filter_pipeline.filter_text(response)
        # Log the user input and response to memory
        memory_manager.add_event(user_input, participants=["user"], tags=["conversation"])
        memory_manager.add_event(filtered, participants=["clair"], tags=["conversation"])
        # Respond
        print(f"Clair: {filtered}")
        # Decay emotions so they fade over time
        active_emotions = decay_emotions(active_emotions)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClair: Conversation ended.")
