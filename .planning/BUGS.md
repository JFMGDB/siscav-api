# Bug & defect map — SISCAV API

**Created:** 2026-04-10  
**Sources:** `.planning/codebase/CONCERNS.md`, repository scan (`TODO`/`FIXME` in `*.py`: none), architecture review.

This document is the **authoritative inventory** of known issues for the current bugfix initiative. Each item has a stable ID for traceability in `REQUIREMENTS.md` and `ROADMAP.md`.

## Legend

| Severity | Meaning |
|----------|---------|
| P0 | Security or data-loss risk; fix before broader exposure |
| P1 | Correctness, reliability, or operability; fix in v1 |
| P2 | Tech debt or docs; schedule after P0/P1 |

| Type | Meaning |
|------|---------|
| defect | Behavior contradicts intent or documented API |
| hardening | Security/robustness improvement |
| debt | Maintenance / confusion risk |
| ops | Deploy, CI, or local-dev friction |

---

## Inventory

| ID | Severity | Type | Summary | Primary locations |
|----|----------|------|---------|-------------------|
| BUG-001 | P2 | debt | `pyproject.toml` lists `passlib[bcrypt]` while runtime uses Argon2 via `passlib[argon2]` in `requirements.txt` / `security.py` | `pyproject.toml`, `requirements.txt`, `apps/api/src/api/v1/core/security.py` |
| BUG-002 | P1 | defect | `refresh_token_expire_days` and env docs exist; no refresh-token API or JWT refresh flow | `apps/api/src/api/v1/core/config.py`, `env.local.example`, `auth_controller.py`, `endpoints/auth.py` |
| BUG-003 | P0 | hardening | Default `SECRET_KEY` is predictable when unset (`change_me_in_development`) | `apps/api/src/api/v1/core/config.py` |
| BUG-004 | P0 | hardening | `POST /api/v1/access_logs/` accepts uploads without authentication | `apps/api/src/api/v1/endpoints/access_logs.py`, `access_log_controller.py` |
| BUG-005 | P1 | hardening | Upload path trusts client `content_type`; no image magic-byte / decode validation | `apps/api/src/api/v1/controllers/access_log_controller.py` |
| BUG-006 | P1 | defect | Entire upload body read into memory before `max_file_size_mb` enforced | `apps/api/src/api/v1/controllers/access_log_controller.py` |
| BUG-007 | P1 | defect | CORS allowlist hardcoded to localhost; production frontends need env-driven config | `apps/api/src/main.py` |
| BUG-008 | P1 | hardening | No roles on `User`; any authenticated user can use privileged routes | `models/user.py`, `whitelist.py`, `gate_control.py`, etc. |
| BUG-009 | P2 | debt | Deprecated `crud/` modules still present alongside repositories/controllers | `apps/api/src/api/v1/crud/*.py` |
| BUG-010 | P2 | ops | Docker Compose `api` depends on `db` with `profiles: ["local"]` — easy to mis-run | `docker-compose.yml` |
| BUG-011 | P2 | ops | Alembic DB URL vs app `DATABASE_URL` mismatch risk if env differs | `apps/api/src/alembic/env.py`, `config.py` |
| BUG-012 | P2 | ops | Unpinned runtime deps; CI can drift between runs | `requirements.txt`, CI workflow |

## Explicitly not “bugs” (features / future work)

These are **stubs or missing features**, not regressions. Track separately if you open a feature milestone:

- `GateController` / `DeviceController` return mock success without I/O (IoT not integrated).
- `recognize-plate.py` ML script: optional tooling, not wired to API deps.

---

## How to use

1. Pick items by severity (P0 first).
2. Link each fix to a **REQ-** ID in `.planning/REQUIREMENTS.md`.
3. Close BUG-* rows when verified (tests + manual check), and note the PR or phase in `ROADMAP.md` traceability.

---
*Last updated: 2026-04-10 — created during `/gsd-new-project` (bugfix scope)*
