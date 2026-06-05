# ADR 010: Auto-open Gate on Authorized Access (Sync, Graceful Degradation)

## Status

Accepted.

## Context

The API already exposes:

- `POST /api/v1/access_logs/` — plate validation, whitelist check, audit log persistence
- `POST /api/v1/gate_control/trigger` — optional HTTP actuator via `GATE_ACTUATOR_URL`

Gate opening was **manual** and decoupled from authorization. Authorized access should optionally trigger the external actuator in the same request/response cycle as the access log.

Stress testing ruled out `BackgroundTasks` for auto-open: the access-log response must include a definitive `gate_trigger` object in the same HTTP response. Background execution cannot populate that field reliably before the client receives the payload.

## Decision

1. Add **`GATE_AUTO_OPEN_ON_AUTHORIZE`** (default `false`) and **`GATE_AUTO_OPEN_TIMEOUT_SECONDS`** (default `2.0`, clamped 1.5–2.0).
2. When enabled and access status is **`Authorized`**, after the access log is **committed** to the database, invoke **`GateController.trigger_gate_safe()`** synchronously with the auto-open timeout.
3. **Transactional order (graceful degradation):**
   - **(A)** Insert and commit `access_logs` row.
   - **(B)** Call actuator HTTP (`POST {"action":"open"}`).
   - **(C)** On actuator failure (timeout, connection refused, HTTP error), catch internally — **no DB rollback**, **no HTTP 5xx** on the access-log endpoint.
   - **(D)** Return **`201 Created`** with `AccessLogRead` plus optional **`gate_trigger`**; hardware failure uses `gate_trigger.status = "error"` and explicit `reason` (e.g. `actuator_timeout`).
4. Manual gate trigger (`POST /gate_control/trigger`) keeps existing behavior: actuator failures may still return **502/503**.
5. Reference actuator: Wokwi ESP32 HTTP server in [`demo/wokwi-gate/`](../../demo/wokwi-gate/), reached via Private IoT Gateway at **`http://127.0.0.1:9080/open`** (IPv4 literal required on Windows).

## Consequences

- Default-off flag preserves backward compatibility.
- Monitor UI can show partial success (authorized + actuator error) without failing the audit path.
- Access-log latency is bounded by `GATE_AUTO_OPEN_TIMEOUT_SECONDS` (~2s max).
- When using a browser-based simulator, keep the simulation tab visible to avoid Chromium tab suspension breaking the HTTP server.

## Alternatives considered

- **`BackgroundTasks`:** Rejected — cannot return accurate `gate_trigger` in the same response.
- **Frontend `openGate()` after Authorized:** Rejected as primary path — wrong layer; kept only as manual dashboard fallback.
- **MQTT / WebSocket event bus:** Rejected — unnecessary complexity for current scope.
- **New actuator microservice:** Rejected — existing `GATE_ACTUATOR_URL` contract is sufficient.
