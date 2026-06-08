# Wokwi Virtual Gate Actuator

Minimal ESP32 sketch that implements the Siscav gate actuator contract:

```http
POST /open
Content-Type: application/json

{"action": "open"}
```

```http
POST /close
Content-Type: application/json

{"action": "close"}
```

Response: HTTP `200` with body `{"ok":true}`.

Visual feedback: green LED ON + servo arm **up** (open) + `GATE OPEN` on Serial Monitor; close moves arm **horizontal** (barrier down) + LED off + `GATE CLOSE`. After open, the gate **auto-closes after 10 seconds**.

## Setup (wokwi.com)

1. Create a [new ESP32 project](https://wokwi.com/projects/new/esp32).
2. Paste [`sketch.ino`](sketch.ino).
3. Install **ESP32Servo** (see [`libraries.txt`](libraries.txt)).
4. Replace the diagram with [`diagram.json`](diagram.json) (`board-esp32-devkit-c-v4`; do **not** set `"env"` in `attrs` — that attribute is for MicroPython only).
5. Run [wokwigw](https://github.com/wokwi/wokwigw/releases/latest), then on wokwi.com press **`F1` → Enable Private Wokwi IoT Gateway**.
6. Start the simulation. Serial Monitor appears below the diagram.
7. Confirm gateway output shows `Client connected` and Serial shows `HTTP server listening on port 80`.

If Run fails on an older wokwi.com project, create a [new ESP32 project](https://wokwi.com/projects/new/esp32) and paste all three files from this folder.

Default gateway forward: `http://127.0.0.1:9080/` → ESP32 port 80.

## Prerequisites

- Wokwi paid plan + Chrome or Edge (Safari does not support Private Gateway)
- [Wokwi Private IoT Gateway (`wokwigw`)](https://github.com/wokwi/wokwigw/releases/latest)
- API env:

```env
GATE_AUTO_OPEN_ON_AUTHORIZE=true
GATE_ACTUATOR_URL=http://127.0.0.1:9080/open
GATE_AUTO_OPEN_TIMEOUT_SECONDS=2
```

Use **`127.0.0.1`**, not `localhost` (Windows IPv6 bypass).

## Smoke test

```powershell
curl.exe -X POST http://127.0.0.1:9080/open `
  -H "Content-Type: application/json" `
  -d "{\"action\":\"open\"}"
```

Expected: Serial `GATE OPEN`, servo arm up, LED on, HTTP body `{"ok":true}`. After ~10 s the arm returns horizontal (`GATE CLOSE`).

Close manually:

```powershell
curl.exe -X POST http://127.0.0.1:9080/close `
  -H "Content-Type: application/json" `
  -d "{\"action\":\"close\"}"
```

Or use **Fechar Portão** on `/dashboard` (calls `POST /api/v1/gate_control/close`).

## Browser tab visibility

Chromium suspends background tabs. Keep the Wokwi simulation tab visible or the simulated HTTP server may stop responding.

## VS Code (optional)

Requires compiled `.bin`/`.elf`. See [`wokwi.toml`](wokwi.toml) for gateway port forwarding when using the Wokwi VS Code extension.

## Tests

From repository root:

```bash
uv run pytest tests/integration/test_access_log_auto_open_gate.py -q
```
