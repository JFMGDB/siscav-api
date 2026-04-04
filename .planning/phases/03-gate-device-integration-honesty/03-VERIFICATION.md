---
status: passed
phase: 03-gate-device-integration-honesty
updated: 2026-04-04
---

# Phase 3 verification

## Requirements

| ID | Evidence |
|----|----------|
| GATE-01 | Simulated vs live JSON; HTTP POST to `GATE_ACTUATOR_URL`; 502 on `HTTPError` 500; integration tests |
| DEV-01 | `IOT_DEVICE_DEMO_API`; `demo` on schemas; 501 when disabled; OpenAPI tag + README |

## Automated

- `pytest tests/integration/ -q`
- `pytest tests/unit/ -q`

## human_verification

None required.
