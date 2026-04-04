# Phase 3: Gate & device integration honesty - Discussion Log

> **Audit trail only.** Decisions are captured in `03-CONTEXT.md`.

**Date:** 2026-04-04  
**Phase:** 3 — Gate & device integration honesty  
**Mode:** Synchronous session — gray areas listed below; **recommended defaults were written to CONTEXT** without interactive multi-select (Cursor text session). Revise `03-CONTEXT.md` if you want different locks before planning.

**Areas that would have been offered for discussion**

1. **Gate downstream transport** — HTTP to `GATE_ACTUATOR_URL` vs stub-only honesty (no network) for v1.  
   **Default locked:** optional HTTP when URL set; explicit `integration: "simulated"` when unset.

2. **Shape of “simulated” vs “live” signal** — New Pydantic model vs extend `status`/`message` only.  
   **Default locked:** Pydantic model + `integration` field; breaking change acceptable with docs/tests.

3. **Device endpoints strategy** — Feature-flag off in production vs always-on mock with `demo: true` in body.  
   **Default locked:** `IOT_DEVICE_DEMO_API` false in prod → **501**; true in dev → mocks + `demo: true` on schemas.

4. **Downstream failure mapping** — 502 vs 503 for timeout/upstream errors.  
   **Default locked:** either is acceptable; prefer **502** for bad gateway / upstream error, **503** if service unavailable — **Claude discretion** in plan.

## Claude's Discretion (recorded in CONTEXT)

- Retry policy for gate HTTP (default fail-fast).  
- Exact actuator JSON payload.  
- 501 vs 404 for disabled device API.

## Deferred Ideas

See `<deferred>` in `03-CONTEXT.md` (MQTT, per-device routing, mTLS).
