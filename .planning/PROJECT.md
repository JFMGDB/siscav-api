# SISCAV API — planning context

## What This Is

**siscav-api** is the FastAPI backend for the *Sistema de Controle de Acesso de Veículos* (vehicle access control). It provides JWT auth for administrators, whitelist CRUD for authorized plates, access-log ingestion with image storage, and endpoints for health, devices, and gate control. The service targets PostgreSQL (including Supabase) with SQLAlchemy and Alembic.

## Core Value

**Administrators and edge devices can trust the API for authenticated administration and auditable access events** — fixes in this milestone prioritize closing security gaps, config honesty, and upload robustness over new features.

## Requirements

### Validated

- ✓ FastAPI app with versioned routers under `/api/v1` — existing (`apps/api/src/main.py`, `api/v1/api.py`)
- ✓ JWT login and password hashing (Argon2) — existing (`endpoints/auth.py`, `core/security.py`)
- ✓ Whitelist CRUD for authorized plates — existing (`endpoints/whitelist.py`, `PlateController`)
- ✓ Access log creation and image storage paths — existing (`endpoints/access_logs.py`, `AccessLogController`)
- ✓ CI pipeline (pytest, ruff) — existing (`.github/workflows/ci.yml`)

### Active

- [ ] Close mapped defects and hardening items in `.planning/BUGS.md` (tracked as v1 requirements in `REQUIREMENTS.md`)
- [ ] Align dependency/config documentation with runtime (`BUG-001`)
- [ ] Resolve refresh-token configuration vs implementation gap (`BUG-002`)
- [ ] Harden secrets, CORS, upload validation, and unauthenticated ingest (`BUG-003`–`BUG-008` per roadmap)
- [ ] Reduce ops fragility (Compose, Alembic env, pins) where in scope (`BUG-010`–`BUG-012`)
- [ ] Remove or isolate deprecated `crud/` layer when safe (`BUG-009`)

### Out of Scope (this milestone)

- Full IoT/hardware integration for real gate or Bluetooth devices — stubs remain until a dedicated integration phase
- Packaging the ML plate script into the API image — optional follow-up
- Greenfield rewrite or framework change

## Context

- Brownfield Python 3.13 / FastAPI / SQLAlchemy stack; see `.planning/codebase/STACK.md` and `ARCHITECTURE.md`.
- Known issues were consolidated into `.planning/BUGS.md` from the codebase concerns pass; no `TODO`/`FIXME` markers were found in application Python.
- Primary consumers: admin frontend (`siscav-web`, separate repo), future IoT clients for logs and gate commands.

## Constraints

- **Tech:** Stay on current stack (FastAPI, SQLAlchemy 2, Pydantic, pytest) unless a requirement explicitly demands a library swap.
- **Compatibility:** PostgreSQL remains the production target; SQLite fallback exists for dev only — changes must not break Supabase/Postgres deployments.
- **Scope:** Bugfix and hardening milestone — avoid feature creep; defer IoT completion.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dedicated `BUGS.md` + REQ traceability | User asked to map bugs explicitly for execution | — Pending |
| Skip external domain research | Codebase map + concerns sufficient for defect closure | ✓ Good |
| YOLO + balanced agents | Faster iteration on well-scoped fixes | — Pending |

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
*Last updated: 2026-04-10 after initialization (bugfix scope, bugs mapped in BUGS.md)*
