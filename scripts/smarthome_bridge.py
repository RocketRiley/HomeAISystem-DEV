#!/usr/bin/env python3
"""MQTT bridge for Home Assistant smart home control.

This module exposes a :class:`SmartHomeBridge` that publishes commands to and
subscribes for status updates from a Home Assistant MQTT broker.  Connection
settings are read from environment variables so the Python and Unity sides can
share the same `.env` configuration file.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Optional

try:  # pragma: no cover - optional dependency
    import paho.mqtt.client as mqtt  # type: ignore
except Exception:  # pragma: no cover
    mqtt = None  # type: ignore


class SmartHomeBridge:
    """Publish commands and listen for device status via MQTT."""

    def __init__(self) -> None:
        if mqtt is None:  # pragma: no cover - paho-mqtt not installed
            self.client = None
            return
        host = os.getenv("MQTT_HOST", "localhost")
        port = int(os.getenv("MQTT_PORT", "1883"))
        user = os.getenv("MQTT_USER")
        password = os.getenv("MQTT_PASS")
        self.client = mqtt.Client()
        if user:
            self.client.username_pw_set(user, password or "")
        try:
            self.client.connect(host, port, keepalive=60)
            self.client.loop_start()
        except Exception:
            self.client = None

        # Load proactive permission list
        self.permissions = self._load_permissions()

    @staticmethod
    def _load_permissions() -> set[str]:
        path = Path("config/smarthome_permissions.json")
        try:
            data = json.loads(path.read_text("utf-8"))
            return set(data.get("proactive_control_allowed", []))
        except Exception:
            return set()

    # ------------------------------------------------------------------
    # MQTT helpers
    def publish_command(self, device_id: str, action: str, value: Optional[str] = None) -> None:
        """Publish a command for ``device_id``.

        The payload is a JSON object ``{"action": action, "value": value}`` and the
        topic follows ``aegis/<device_id>/set``.
        """
        if not self.client:
            return
        payload = json.dumps({"action": action, "value": value})
        topic = f"aegis/{device_id}/set"
        self.client.publish(topic, payload)

    def subscribe_to_status(self, device_ids: Iterable[str]) -> None:
        """Subscribe to status topics for the given devices."""
        if not self.client:
            return
        for dev in device_ids:
            topic = f"aegis/{dev}/status"
            self.client.subscribe(topic)

    # ------------------------------------------------------------------
    # Permission helper for proactive actions
    def is_allowed(self, device_id: str) -> bool:
        """Return True if proactive control is permitted for ``device_id``."""
        return device_id in self.permissions

    def propose_action(
        self,
        device_id: str,
        action: str,
        value: Optional[str],
        ask_fn,
    ) -> bool:
        """Ask the user before executing a proactive smart home action.

        ``ask_fn`` should be a callable that takes a human-readable question and
        returns ``True`` if the user agrees.  The command is only published when
        permission exists and the user confirms.
        """
        if not self.is_allowed(device_id):
            return False
        question = (
            f"Would you like me to {action.replace('_', ' ')} the "
            f"{device_id.replace('_', ' ')}?"
        )
        if ask_fn(question):
            self.publish_command(device_id, action, value)
            return True
        return False


if __name__ == "__main__":  # pragma: no cover - simple manual test
    bridge = SmartHomeBridge()
    bridge.publish_command("test_lamp", "toggle", "on")
