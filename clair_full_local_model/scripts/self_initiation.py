#!/usr/bin/env python3
"""Simulate Clair's proactive initiation behaviour.

This script reads the initiator rules from `config/initiator_rules.json` and
randomly triggers events to demonstrate how Clair might initiate
conversations.  It selects a response line from the appropriate
persona state file based on the action associated with the event.

Run this script with:

    python scripts/self_initiation.py

The script will run for a short number of iterations, printing the
chosen lines to the console.  Modify the logic or the mappings below
to suit your own event handling requirements.
"""

import json
import random
import time
from pathlib import Path


def load_persona_examples():
    """Load all persona example files into a dict of state → list of lines."""
    base = Path(__file__).resolve().parent.parent / "persona" / "examples"
    examples = {}
    for path in base.glob("*.json"):
        state = path.stem
        with open(path, "r", encoding="utf-8") as f:
            examples[state] = json.load(f)
    return examples


def load_rules():
    """Load initiator rules."""
    cfg_path = Path(__file__).resolve().parent.parent / "config" / "initiator_rules.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def choose_line(state, examples):
    """Choose a random line from the given state, or fallback to neutral."""
    if state in examples and examples[state]:
        return random.choice(examples[state])
    return random.choice(examples.get("neutral", ["..."]))


def map_action_to_state(action):
    """Map an action name to a persona example state."""
    mapping = {
        "comment_on_show": "attention_ping",
        "respond_to_user": "neutral",
        "get_attention": "attention_ping",
        "morning_greeting": "joy",
        "remind_stretch": "supportive",
        "bring_up_unfinished_task": "focused",
        "check_in": "attention_ping"
    }
    return mapping.get(action, "neutral")


def simulate_events():
    examples = load_persona_examples()
    rules = load_rules()
    # Flatten potential events into a list of (event_name, action)
    events = []
    for category, category_rules in rules.items():
        if category == "twitch" and not category_rules.get("enabled", True):
            continue
        for event_name, rule in category_rules.items():
            if isinstance(rule, dict):
                events.append((event_name, rule.get("action")))
    # Run a short simulation
    print("Simulating proactive events.\n")
    for i in range(10):
        event_name, action = random.choice(events)
        state = map_action_to_state(action)
        line = choose_line(state, examples)
        print(f"Event '{event_name}' → action '{action}' → state '{state}'")
        print(f"  Clair: {line}\n")
        time.sleep(1)
    print("Simulation complete. Modify `map_action_to_state` to suit your behaviour.")


if __name__ == "__main__":
    simulate_events()