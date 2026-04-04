# Phase 3: Gate & device integration honesty - Context

**Gathered:** 2026-04-04  
**Status:** Ready for planning

<domain>
## Phase Boundary

Make **gate trigger** and **device-related HTTP APIs** honest: operators must never believe hardware acted when nothing downstream ran, and **mock Bluetooth flows** must not read as production discovery/control **(GATE-01, DEV-01)**.

In scope: response contracts, configuration flags, OpenAPI/docs, integration tests proving explicit simulation vs live paths. **Out of scope:** physical relay wiring, edge firmware, choosing a specific vendor device (defer to env URL / payload documented only).

**Carrying forward from prior phases**

- **Phase 1:** `POST /api/v1/gate_control/trigger` uses **`get_current_admin_user`** (admin-only).
- **Phase 2:** Access logs policy is settled; Phase 3 does not change ingest/list/image semantics.

</domain>

<decisions>
## Implementation Decisions

### Gate trigger honesty (GATE-01)

- **D-01:** Replace the current **silent “success” stub** (`GateController.trigger_gate` always returns success implying the portão opened) with an **explicit integration mode** in the JSON body. When **no** downstream actuator is configured, the response must state **`integration: "simulated"`** (or equivalent single canonical key agreed in implementation) and **must not** claim the relay fired. When a downstream call is configured and succeeds, **`integration: "live"`** and include whether the actuator acknowledged (see D-03).
- **D-02:** Add configuration **`GATE_ACTUATOR_URL`** (optional string, empty = simulated-only). Optional **`GATE_ACTUATOR_TIMEOUT_SECONDS`** (default **5**). Document both in `env.local.example` and `docs/api/README.md`.
- **D-03:** When **`GATE_ACTUATOR_URL` is set**, perform an **HTTP POST** (or GET if documented and justified — default **POST**) to that URL with a small JSON payload (e.g. `{"action": "open"}` — exact shape locked in plan/implementation). Treat as success only on **HTTP 2xx** within timeout; on timeout, connection error, or non-2xx, return **502** or **503** with a **clear `detail`** (no silent success). **Claude's discretion:** minimal retry (0–1) vs fail-fast; prefer fail-fast for v1.
- **D-04:** Prefer a **Pydantic response model** for `POST /api/v1/gate_control/trigger` (replace raw `dict[str, str]`) so OpenAPI lists fields. **Breaking change** for clients expecting only `status`/`message` is acceptable if documented in README/OpenAPI and tests updated.

### Device API honesty (DEV-01)

- **D-05:** Bluetooth scan/connect/status/disconnect **cannot** be real server-side Bluetooth over plain HTTP; docstrings already say **Web Bluetooth in the browser**. Phase 3 must make **demo vs disabled** obvious at the HTTP layer.
- **D-06:** Introduce **`IOT_DEVICE_DEMO_API`** (boolean, default **`true`** in development, **`false`** when `ENVIRONMENT` is `production`/`prod`). When **false**, device routes return **501 Not Implemented** (or **404** if we prefer to hide surface — **default 501** with explicit detail that the API is disabled and real pairing is client-side). When **true**, keep current mock behavior **but** extend response schemas (or wrapper) so every success body includes **`demo: true`** (or `simulation: true`) — integrators and OpenAPI show it without reading docstrings only.
- **D-07:** OpenAPI: tag **`devices`** as **demonstration / non-production**; update `main.py` description with one bullet mirroring D-05–D-06. **`docs/api/README.md`:** short table for gate + device behavior.

### Testing & documentation

- **D-08:** Integration tests: (1) gate with **no** `GATE_ACTUATOR_URL` → **200** + `integration == "simulated"`; (2) with mock HTTP server / `respx` / TestClient against stub URL → **200** + `integration == "live"` on 2xx; (3) downstream returns **500** → API surfaces error (not 200 success). (4) device routes with demo flag off → **501** (or chosen status).
- **D-09:** Update **`CONCERNS.md`** gate/device bullets after behavior changes so the map stays truthful.

### Claude's Discretion

- Exact JSON field names (`integration` vs `mode`) as long as OpenAPI and tests stay consistent.
- Gate actuator auth (static bearer in env, mTLS) — **defer** unless already required; v1 may be URL in private network only.
- Whether disabled device routes are **501** vs **404**.

### Folded Todos

_None (todo match-phase returned no items)._

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning & requirements

- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, plans 03-01 / 03-02.
- `.planning/REQUIREMENTS.md` — **GATE-01**, **DEV-01**.
- `.planning/phases/01-security-authentication-correctness/01-CONTEXT.md` — Admin gate trigger, device ingest patterns.
- `.planning/phases/02-whitelist-access-log-behavior/02-CONTEXT.md` — Phase boundary vs gate/devices.

### Product / spec

- `docs/requirements/project-specification.md` — Server-side themes (RF-004, RF-006, RF-007) for audit/gate context; confirm no extra mandate beyond honesty.

### Code (integration points)

- `apps/api/src/api/v1/controllers/gate_controller.py` — Stub to replace/extend.
- `apps/api/src/api/v1/endpoints/gate_control.py` — `POST .../trigger`, admin dependency.
- `apps/api/src/api/v1/controllers/device_controller.py` — Mock Bluetooth logic.
- `apps/api/src/api/v1/endpoints/devices.py` — Device routes.
- `apps/api/src/api/v1/schemas/device.py` — Response models to extend or wrap.
- `apps/api/src/api/v1/core/config.py` — New settings fields.
- `apps/api/src/main.py` — OpenAPI description.
- `docs/api/README.md` — Operator-facing summary.
- `tests/integration/test_endpoints_gate_control.py` — Extend for new contracts.

### Quality context

- `.planning/codebase/CONCERNS.md` — Historical note on stubs (some auth lines predate `is_admin`; verify against current code when editing).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **Gate:** `GateController` + `get_gate_controller` DI; endpoint already **admin-only** (`get_current_admin_user`).
- **Devices:** `DeviceController` returns fixed mock lists; schemas in `schemas/device.py`.

### Established patterns

- **Settings:** Env-driven config via `Settings` / `config.py` (see `DEVICE_INGEST_KEY`, `ENVIRONMENT`).
- **Tests:** Integration tests use `TestClient`, `admin_auth_token` for gate (see `test_endpoints_gate_control.py`).

### Integration points

- **HTTP client for gate:** Use `httpx` if already a dependency, else `urllib.request` or add `httpx` — **planner** to check `requirements.txt` and align with project norms.

</code_context>

<specifics>
## Specific Ideas

- Prefer **fail-fast** gate downstream (no hidden retries) for predictable operator debugging.
- **501** for disabled device demo API reads clearly as “not implemented server-side.”

</specifics>

<deferred>
## Deferred Ideas

- **MQTT / WebSocket** gate channel — new integration phase if product commits to a broker.
- **Per-device gate routing** (which relay for which site) — data model + admin UI; not required for GATE-01 honesty v1.
- **mTLS / signed commands** to actuator — security hardening phase.

### Reviewed Todos (not folded)

_None._

</deferred>

---

*Phase: 03-gate-device-integration-honesty*  
*Context gathered: 2026-04-04*
