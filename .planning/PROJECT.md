# SISCAV API

## What This Is

SISCAV (Sistema de Controle de Acesso de Veículos) is a **central HTTP API** that supports automated vehicle access: operators authenticate, manage an authorized-plate whitelist, record access attempts with optional images, and trigger gate actions. The repository currently delivers a **FastAPI + SQLAlchemy** backend (`apps/api/src/`) with Alembic migrations, JWT auth, and integration tests. Edge ALPR/camera work is described in `docs/requirements/project-specification.md` but is **not** fully represented in this repo after removal of the former `apps/iot-device` tree.

## Core Value

**Trustworthy plate-based access decisions and an auditable log of every attempt** (authorized or denied), with a clear path to secure device-to-server communication and real gate hardware integration.

## Requirements

### Validated

- ✓ **REST API v1** under `/api/v1` with OpenAPI — existing (`apps/api/src/main.py`, `apps/api/src/api/v1/api.py`)
- ✓ **User registration and JWT access/refresh** — existing (`apps/api/src/api/v1/endpoints/auth.py`, `core/security.py`)
- ✓ **Authorized plate whitelist CRUD** — existing (`endpoints/whitelist.py`, `PlateController`, `AuthorizedPlateRepository`)
- ✓ **Access log ingestion and listing** (multipart image + plate, persisted metadata) — existing (`endpoints/access_logs.py`, `AccessLogController`)
- ✓ **Gate trigger honesty (Phase 3)** — `integration` simulated vs optional HTTP `GATE_ACTUATOR_URL` (`gate_controller.py`, `schemas/gate_control.py`)
- ✓ **Device demo API honesty (Phase 3)** — `IOT_DEVICE_DEMO_API`, `demo` on responses, 501 when disabled (`devices` router, `schemas/device.py`)
- ✓ **Health check** — existing (`endpoints/health.py`)
- ✓ **Database migrations (Alembic)** — existing (`alembic.ini`, `apps/api/src/alembic/versions/`)
- ✓ **Automated tests (pytest unit + integration)** — existing (`tests/`)
- ✓ **Whitelist + access-log behavior (Phase 2)** — WL-01 / LOG-01–LOG-03: CRUD whitelist documented and tested; audit list filters/order and ingest fields covered; operator docs and OpenAPI describe device-key ingest, JWT list, admin-only image download (`docs/api/README.md`, `main.py`, integration tests)

### Active

- [ ] **Harden production security** (remaining): refresh rate limits, fail-fast weak `SECRET_KEY`, and any SEC/AUTH items not yet closed in Phase 1
- [ ] **Deeper actuator / edge integration** (beyond optional HTTP POST): MQTT, signed commands, per-site routing — future phases
- [ ] **Operational quality**: remove debug/agent log regions, prefer Alembic over ad hoc SQLite `create_all`, pin dependencies, address deprecated `crud/` package
- [ ] **Alignment with RF goals** in `docs/requirements/project-specification.md` for everything the **central server** must guarantee (RF-004, RF-006, dashboard/auth aspects that land in this API)

### Out of Scope

- **On-device ALPR pipeline** (RF-001–RF-003 as implemented on edge hardware) — tracked as a separate deliverable unless reintroduced in-repo; API assumes a client sends plate + image.
- **Full web dashboard UI** — not in this repository; API supports future SPA consumers (CORS already partially configured for local dev ports).

## Context

- **Brownfield:** Codebase map in `.planning/codebase/` (STACK, ARCHITECTURE, CONCERNS, etc.) reflects current implementation.
- **Product intent:** Corporate/hospital private vehicle access, audit trail, relay-based gate opening — see `docs/requirements/project-specification.md`.
- **Stack:** Python 3.10+ (CI 3.13), FastAPI, SQLAlchemy, PostgreSQL or SQLite dev fallback, Supabase-compatible Postgres in docs.
- **Git:** `main` branch; planning artifacts live under `.planning/`.

## Constraints

- **Tech stack:** Continue with existing FastAPI/SQLAlchemy/Alembic unless an explicit migration phase is approved.
- **Compatibility:** Preserve API contracts consumed by integration tests and documented clients (`docs/api/`).
- **Security:** Production deployments must not rely on default `SECRET_KEY` or unauthenticated public log ingestion without a documented threat model.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Initialize GSD planning on existing API repo | User ran `/gsd-new-project` without `--auto`; brownfield bootstrap from codebase map + product spec | — Pending |
| Defer parallel “ecosystem” research for now | `.planning/codebase/` and `docs/requirements/project-specification.md` already bound the domain | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-04 — Phase 3 executed (gate + device API honesty)*
