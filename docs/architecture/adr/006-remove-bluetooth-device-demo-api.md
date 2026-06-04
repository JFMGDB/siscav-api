# ADR 006: Remove Bluetooth Device Demo API

## Status

Accepted.

## Context

The API exposed `/api/v1/devices/*` routes (scan, connect, status, disconnect) as a **simulated** Bluetooth demo, gated by `IOT_DEVICE_DEMO_API`. The frontend paired this with Web Bluetooth in Settings. Neither path delivered production capture: real flows use browser USB/network camera configuration and `POST /api/v1/access_logs/` ingest with `X-Device-Key` when configured.

Maintaining duplicate “device” concepts (demo HTTP + Web Bluetooth + ingest key) increased confusion and dead code.

## Decision

- Remove all `/api/v1/devices/*` endpoints, `DeviceController`, device schemas, and `IOT_DEVICE_DEMO_API`.
- Keep **`DEVICE_INGEST_KEY`** and **`verify_device_ingest_key`** for access-log ingestion unchanged.
- Document that capture is **frontend USB/network camera** plus REST ingest, not server-side Bluetooth.

## Consequences

- Postman and API docs no longer list device demo routes.
- Frontend must not call `/devices/*` (removed in the sibling web ADR).
- No new stats or device-management API in this change; gate actuator and ingest remain the hardware/integration surface.

## Alternatives considered

- **Keep demo routes behind flag:** Rejected — still ships mock behavior and documentation debt.
- **Move Bluetooth to server:** Rejected — Web Bluetooth is browser-only; out of API scope.
