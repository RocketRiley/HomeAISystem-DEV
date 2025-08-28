# Smart Home Setup

This guide explains how to connect Clair to a Home Assistant instance using
MQTT.  The bridge allows the assistant to send commands to lights, speakers and
other devices while respecting a user-defined permission list.

## 1. Enable the MQTT broker in Home Assistant

1. In Home Assistant go to **Settings → Add-ons → Add-on Store** and install the
   MQTT add-on.
2. Note the broker host, port, username and password.  These values are required
   by Clair.

## 2. Configure environment variables

Edit your `.env` and set:

```ini
MQTT_HOST=127.0.0.1
MQTT_PORT=1883
MQTT_USER=homeassistant
MQTT_PASS=your_password
```

Restart the Python side after saving.

## 3. Define proactive permissions

Clair will never control devices on her own unless they are explicitly allowed.
Create or edit `config/smarthome_permissions.json` with:

```json
{
  "proactive_control_allowed": [
    "living_room_lamp",
    "office_speaker"
  ]
}
```

Only devices listed here can be suggested or controlled automatically.

## 4. Usage

- **Direct commands** – if you say "turn on the living room lamp" the voice loop
  parses the request and publishes an MQTT command.
- **Proactive actions** – when a goal requires a device (e.g. dimming lights at
  bedtime) Clair checks the permission file and will ask:
  "It’s getting late.  Should I dim the living room lamp?"  The command runs
  only after you agree.

## 5. Troubleshooting

Run `python -m scripts.diagnostics` to verify MQTT connectivity.  The output will
show whether the broker host and port are reachable.
