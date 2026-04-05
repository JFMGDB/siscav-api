# Roadmap: SISCAV API

**Milestone:** Current planning cycle (brownfield hardening + integration)  
**Granularity:** Coarse (3–5 broad phases)  
**Source:** `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`

## Phases

- [x] **Phase 1: Security & authentication correctness** — Protected ingest, token/rate-limit hygiene, docs aligned with real authorization; auth flows remain usable.
 (completed 2026-04-05)
- [x] **Phase 2: Whitelist & access log behavior** — Normalized whitelist CRUD and full audit trail submit/list/image behavior for authenticated clients.
 (completed 2026-04-04)
- [x] **Phase 3: Gate & device integration honesty** — Real integration path or explicit simulation; device endpoints production-ready or clearly disabled.
 (completed 2026-04-04)
- [x] **Phase 4: Operations & dependency hygiene** — Debug noise removed or gated, migration discipline, pinned deps, deprecated `crud/` path resolved.
 (completed 2026-04-05)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Security & authentication correctness | 3/3 | Complete   | 2026-04-05 |
| 2. Whitelist & access log behavior | 3/3 | Complete    | 2026-04-04 |
| 3. Gate & device integration honesty | 2/2 | Complete    | 2026-04-04 |
| 4. Operations & dependency hygiene | 3/3 | Complete   | 2026-04-05 |

## Phase Details

### Phase 1: Security & authentication correctness
**Goal**: Operators and integrators can rely on documented, enforced security for sensitive surfaces; JWT and refresh behavior are safe and honest in production-oriented configuration.

**Depends on**: Nothing (first phase)

**Requirements**: SEC-01, SEC-02, SEC-03, AUTH-01, AUTH-02

**Success Criteria** (what must be TRUE):
1. Creating access logs via `POST /api/v1/access_logs/` requires the documented authentication mechanism (API key, device credential, or mTLS, etc.), consistent with the chosen threat model.
2. Refresh token usage is rate-limited in line with login, and production configuration cannot start with a weak or default `SECRET_KEY` (fail-fast or equivalent guard).
3. OpenAPI and route documentation state who may call privileged endpoints, and runtime checks match those claims (or docs are corrected to match behavior).
4. A user can still register with email/password and use login plus refresh to obtain new access tokens (no regression of core auth).

**Plans**:
- 01-01 — SEC-01: `X-Device-Key` ingest, OpenAPI, tests ([01-01-PLAN.md](phases/01-security-authentication-correctness/01-01-PLAN.md))
- 01-02 — SEC-02 + AUTH: refresh rate limit, production `SECRET_KEY` guard, auth tests ([01-02-PLAN.md](phases/01-security-authentication-correctness/01-02-PLAN.md))
- 01-03 — SEC-03: `is_admin`, admin deps, gate_control + image routes, docs ([01-03-PLAN.md](phases/01-security-authentication-correctness/01-03-PLAN.md))

### Phase 2: Whitelist & access log behavior
**Goal**: Authorized users can manage the plate whitelist and consume a trustworthy audit trail (submit, list, images) through the API.

**Depends on**: Phase 1

**Requirements**: WL-01, LOG-01, LOG-02, LOG-03

**Success Criteria** (what must be TRUE):
1. An authenticated user can list, create, update, and delete authorized plates with normalized plate matching per API rules.
2. An authorized client can submit an access attempt with plate text and optional image; the server persists plate, timestamp, outcome, and image path per schema.
3. An authenticated user can list access logs with the filtering and pagination the API exposes.
4. An authenticated user can retrieve stored images for a log entry when policy allows.

**Plans**:
- 02-01 — Whitelist CRUD contract: OpenAPI, README, integration tests ([02-01-PLAN.md](phases/02-whitelist-access-log-behavior/02-01-PLAN.md))
- 02-02 — Access log ingest + list: repository hygiene, filters/order, tests ([02-02-PLAN.md](phases/02-whitelist-access-log-behavior/02-02-PLAN.md))
- 02-03 — LOG-03 docs honesty: main OpenAPI, README matrix, admin image test ([02-03-PLAN.md](phases/02-whitelist-access-log-behavior/02-03-PLAN.md))

### Phase 3: Gate & device integration honesty
**Goal**: Gate triggers and device-related APIs reflect real integration or explicit simulation so operators are never misled by silent success or mock data presented as live hardware.

**Depends on**: Phase 2

**Requirements**: GATE-01, DEV-01

**Success Criteria** (what must be TRUE):
1. The gate trigger endpoint either completes a real downstream integration with verifiable acknowledgment or returns an explicit simulated indication; failures from the actuator surface as errors to the client.
2. Device-related endpoints are production-ready for discovery/control, or are feature-flagged/disabled such that operators cannot treat mocks as live hardware.

**Plans**:
- 03-01 — GATE-01: actuator env, `GateTriggerResponse`, simulated vs HTTP live, tests, README gate ([03-01-PLAN.md](phases/03-gate-device-integration-honesty/03-01-PLAN.md))
- 03-02 — DEV-01: `IOT_DEVICE_DEMO_API`, 501 when off, `demo` on schemas, OpenAPI/README, tests ([03-02-PLAN.md](phases/03-gate-device-integration-honesty/03-02-PLAN.md))

### Phase 4: Operations & dependency hygiene
**Goal**: The codebase and runtime are suitable for shared and production-like environments: no accidental debug paths, reproducible installs, and a single maintained data-access story.

**Depends on**: Phase 3

**Requirements**: OPS-01, OPS-02, OPS-03

**Success Criteria** (what must be TRUE):
1. Debug/agent log instrumentation is removed or strictly environment-gated; SQLite or other bootstrap paths do not silently bypass migration discipline where migrations are required.
2. Runtime dependencies are pinned or managed via a lockfile so installs are reproducible.
3. Deprecated `crud/` modules are removed or formally deprecated with no duplicate maintenance path for the same operations.

**Plans**:
- 04-01 — OPS-01: strip `session.py` agent log / `create_all`, docs + CONCERNS ([04-01-PLAN.md](phases/04-operations-dependency-hygiene/04-01-PLAN.md))
- 04-02 — OPS-02: pin `requirements.txt` / `requirements-dev.txt` / `pyproject.toml`, CONCERNS + install doc ([04-02-PLAN.md](phases/04-operations-dependency-hygiene/04-02-PLAN.md))
- 04-03 — OPS-03: remove `crud/`, update STRUCTURE/ARCHITECTURE/coding-standards ([04-03-PLAN.md](phases/04-operations-dependency-hygiene/04-03-PLAN.md))

## Requirement coverage

| Requirement | Phase |
|-------------|-------|
| SEC-01 | 1 |
| SEC-02 | 1 |
| SEC-03 | 1 |
| AUTH-01 | 1 |
| AUTH-02 | 1 |
| WL-01 | 2 |
| LOG-01 | 2 |
| LOG-02 | 2 |
| LOG-03 | 2 |
| GATE-01 | 3 |
| DEV-01 | 3 |
| OPS-01 | 4 |
| OPS-02 | 4 |
| OPS-03 | 4 |

---
*Roadmap created: 2026-04-04*
