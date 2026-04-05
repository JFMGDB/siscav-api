# Phase 1: Security & authentication correctness — Research

**Date:** 2026-04-05  
**Status:** Complete

## RESEARCH COMPLETE

### Scope recap (from CONTEXT + ROADMAP)

- **SEC-01:** Authenticated device ingest (`X-Device-Key` / `DEVICE_INGEST_KEY`, constant-time compare, OpenAPI).
- **SEC-02:** Refresh rate limit parity with login; production `SECRET_KEY` fail-fast.
- **SEC-03:** `is_admin` column, `get_current_admin_user`, gate + access-log image routes, honest docs.
- **AUTH-01 / AUTH-02:** Register, login, refresh remain usable (no TTL/algorithm churn per CONTEXT D-06).

### Codebase audit (brownfield)

As of this research pass, the following are **already present** in `apps/api/src`:

| Area | Evidence |
|------|----------|
| SEC-01 | `verify_device_ingest_key`, `APIKeyHeader("X-Device-Key")`, `create_access_log` Depends; `Settings` reads `DEVICE_INGEST_KEY`; `main.py` description mentions header |
| SEC-02 | `refresh_access_token` has `@limiter.limit("5/minute")` + `Request`; `assert_production_secrets_valid()` imported at startup in `main.py`; `config.py` implements guard |
| SEC-03 | Alembic `20260404_0002_add_user_is_admin.py`; `User.is_admin`; `get_current_admin_user` in `deps.py`; `get_access_log_image` + `trigger_gate` use admin dependency; `docs/api/README.md` has primeiro administrador SQL |

### Planning implication

Executable **01-01**, **01-02**, **01-03** PLAN.md files were authored earlier and align with CONTEXT. **Execute-phase** should be treated primarily as **verification and gap closure** (tests, OpenAPI spot-checks, any doc/path drift) rather than assuming greenfield implementation.

**Path accuracy:** Gate router is mounted at **`/api/v1/gate_control`** (not `/gate`); plans were corrected to use `gate_control/trigger` where applicable.

### Nyquist

Disabled for this project — no `VALIDATION.md` for Phase 1.
