# Phase 1: Security & authentication correctness - Context

**Gathered:** 2026-04-04  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver documented, enforced security for sensitive surfaces: **device ingest of access logs**, **JWT issuance and refresh**, and **honest authorization** for routes described as administrator-only. Operators and integrators must be able to rely on production-safe configuration (no weak default signing secret) without breaking existing user registration, login, and refresh flows.

Scope is **how** these behaviors are enforced within the existing FastAPI app — not new product features (gate hardware, dashboard UI, whitelist semantics beyond auth gates).

</domain>

<decisions>
## Implementation Decisions

### Access log ingest authentication (SEC-01)

- **D-01:** Require a **device ingest credential** on `POST /api/v1/access_logs/` using header **`X-Device-Key`** whose value matches environment variable **`DEVICE_INGEST_KEY`** (single shared secret for v1). Missing or wrong key → **401 Unauthorized** with a generic detail (no key enumeration). Use constant-time comparison when validating the key.
- **D-02:** Register the scheme in OpenAPI (e.g. `APIKeyHeader` named `X-Device-Key`) so generated clients and `docs/api` consumers see the contract. Keep **multipart** body unchanged (image + plate).
- **D-03:** Local/dev: allow **`ENVIRONMENT=development`** (or unset) to **optionally** skip the key when `DEVICE_INGEST_KEY` is unset **only if** explicitly documented in `env.local.example` — **preferred:** always set `DEVICE_INGEST_KEY` in `.env` for integration tests and CI; update `tests/` to send the header.

### JWT, refresh, and production secret hygiene (SEC-02)

- **D-04:** Apply **`@limiter.limit("5/minute")`** to `POST /api/v1/login/refresh-token` (same bucket semantics as login: per IP via SlowAPI), with `Request` injected so the decorator matches `login_access_token`.
- **D-05:** **Fail fast at application startup** when **`ENVIRONMENT`** is `production` or `prod` (case-insensitive): if `SECRET_KEY` is missing, empty, or equals the literal default **`change_me_in_development`**, raise a clear error and exit. Non-production environments keep current permissive default for local DX.
- **D-06:** Do not change access/refresh TTLs or signing algorithm in this phase unless a test proves a regression (out of scope for “hygiene” unless broken).

### Administrator claims vs documentation (SEC-03)

- **D-07:** Add **`is_admin: bool`** to the **`users`** table (default `False`), delivered via **Alembic migration**. Expose on internal user resolution only where needed; **do not** leak in public `UserRead` unless already aligned with product — prefer keeping admin flag server-side for dependencies only.
- **D-08:** Introduce dependency **`get_current_admin_user`** (requires valid JWT + `is_admin is True`). Use it on routes whose docstrings claim **administrator-only** access (e.g. **access log image download**, **gate control**). Authenticated non-admin → **403 Forbidden**.
- **D-09:** Update route docstrings and top-level OpenAPI description so they **match** runtime checks (Portuguese copy ok; must not say “apenas administradores” unless enforced).
- **D-10:** Document one-time **bootstrap**: how the first admin is promoted (SQL snippet in `docs/` or seed script note) — no automatic promotion from email env in v1 unless already a project pattern.

### Claude's Discretion

- Wording of error messages and OpenAPI security scheme names (as long as `X-Device-Key` + env name stay discoverable).
- Whether failed ingest attempts are logged at WARNING with hashed key fingerprint vs no logging (avoid logging raw secrets).
- Exact migration down_revision chain and test fixture patterns for `is_admin`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning & audit

- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, requirements SEC-01–03, AUTH-01–02.
- `.planning/REQUIREMENTS.md` — SEC-*, AUTH-* acceptance text.
- `.planning/codebase/CONCERNS.md` — Evidence on open ingest, refresh limits, default `SECRET_KEY`, admin doc mismatch.

### Product specification (server-relevant)

- `docs/requirements/project-specification.md` — §2.2 Controle de Acesso (RF-004, RF-006), §2.3 Painel (RF-007 admin auth themes).

### API & env

- `apps/api/src/api/v1/endpoints/access_logs.py` — Ingest and image routes (docstrings vs `Depends`).
- `apps/api/src/api/v1/endpoints/auth.py` — Login, refresh, register rate limits.
- `apps/api/src/api/v1/core/config.py` — `Settings.secret_key` and env resolution.
- `apps/api/src/api/v1/models/user.py` — Current user columns (pre-migration).
- `env.local.example` — Extend with `DEVICE_INGEST_KEY`, document `ENVIRONMENT` + production `SECRET_KEY` policy.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **`apps/api/src/api/v1/core/limiter.py`** + **`slowapi`**: Same pattern as `@limiter.limit` on `login_access_token` applies to refresh.
- **`apps/api/src/api/v1/deps.py`**: `get_current_user` — extend with admin variant reusing JWT + `UserRepository`.
- **`apps/api/src/main.py`**: App factory; suitable place for startup validation hook or `lifespan` that asserts production secrets.

### Established patterns

- **OAuth2 password flow + JWT**: Refresh and access already share `_create_token_pair` / `_validate_and_decode_refresh_token`.
- **Rate limiting**: IP-based SlowAPI middleware already mounted on the app.

### Integration points

- **`POST /api/v1/access_logs/`**: Currently no `Depends` auth — add API key dependency + wire controller unchanged where possible.
- **Gate control + access log image GET**: Swap `get_current_user` for `get_current_admin_user` where SEC-03 applies.
- **Tests**: `tests/integration/test_endpoints_access_logs.py` and auth tests must gain cases for key header, refresh limit, admin 403, and production startup guard (where testable).

</code_context>

<specifics>
## Specific Ideas

No user-authored product references in this session — decisions are **recommended defaults** from roadmap + requirements + codebase concerns. Adjust D-01 if the deployment model requires mutual TLS or per-device keys in a later iteration.

</specifics>

<deferred>
## Deferred Ideas

- **Per-device API keys** or JWT identity for each edge device — stronger than a single `DEVICE_INGEST_KEY`; defer to a dedicated security phase if needed.
- **OAuth2 / social login** — v2 in REQUIREMENTS.md.
- **Removing** high register rate limit (`100/minute`) — belongs with SEC/product hardening but can trail D-04 if scope pressure.

### Reviewed Todos (not folded)

- None — `todo match-phase` returned no matches.

</deferred>

---
*Phase: 01-security-authentication-correctness*  
*Context gathered: 2026-04-04*
