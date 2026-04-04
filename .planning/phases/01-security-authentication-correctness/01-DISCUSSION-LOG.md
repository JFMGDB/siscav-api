# Phase 1: Security & authentication correctness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.  
> Decisions are captured in `01-CONTEXT.md`.

**Date:** 2026-04-04  
**Phase:** 1 — Security & authentication correctness  
**Mode:** Synchronous session without interactive gray-area picks — **recommended defaults** applied for all areas below.

**Areas recorded:** Device ingest auth, Refresh + SECRET_KEY policy, Admin enforcement vs docs

---

## Device ingest authentication

| Option | Description | Selected |
|--------|-------------|----------|
| Shared header key (`X-Device-Key` + env) | Single deploy secret; simple for IoT clients | ✓ |
| JWT as device identity | Per-device revocation; more moving parts | |
| mTLS only | Strong; infra-heavy for v1 | |

**User's choice:** *(session default)* Shared header key  
**Notes:** Aligns with SEC-01 testable wording; constant-time compare; OpenAPI documented.

---

## Refresh rate limits and production SECRET_KEY

| Option | Description | Selected |
|--------|-------------|----------|
| Match login limit on refresh | Same SlowAPI pattern as `login_access_token` | ✓ |
| Stricter / looser on refresh | Different threat model | |
| Fail-fast production secret | Abort startup when `ENVIRONMENT` is prod and secret weak | ✓ |
| Runtime-only warnings | Weaker guarantee | |

**User's choice:** *(session default)* Rate-limit refresh like login; fail-fast weak secret in prod  
**Notes:** `ENVIRONMENT` naming follows `apps/api/src/main.py` usage.

---

## Administrator enforcement (doc/API alignment)

| Option | Description | Selected |
|--------|-------------|----------|
| Add `is_admin` + `get_current_admin_user` | Enforce what docstrings already claim | ✓ |
| Doc-only fix (remove admin language) | Weaker vs RF-007 direction | |
| Separate roles table | Overkill for Phase 1 | |

**User's choice:** *(session default)* Boolean admin flag + dedicated dependency  
**Notes:** Bootstrap story documented outside automatic promotion.

---

## Claude's Discretion

- Error message copy, logging shape for failed ingest, migration/test details.

## Deferred Ideas

- Per-device keys, OAuth, tightening register rate limit — see `01-CONTEXT.md` `<deferred>`.
