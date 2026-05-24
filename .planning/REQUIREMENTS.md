# Requirements: SISCAV API (bugfix milestone)

**Defined:** 2026-04-10  
**Last updated:** 2026-05-24  
**Core Value:** Trustworthy API for administration and auditable access events — close mapped security and correctness gaps.

**Bug inventory:** [.planning/BUGS.md](BUGS.md)

## v1 Requirements

### Configuration & dependency honesty

- [ ] **CFG-01**: `pyproject.toml` `[project.dependencies]` matches actual runtime hashing stack (`passlib[argon2]` per `requirements.txt` / `security.py`) — closes BUG-001.
- [x] **CFG-02**: Refresh-token issuance and OpenAPI flows — `POST /api/v1/login/refresh-token` implemented — closes BUG-002 (resolved).

### Security & authentication

- [ ] **SEC-01**: Application refuses to start in non-debug environments when `SECRET_KEY` is still the development default (or equivalent fail-fast policy) — closes BUG-003.
- [ ] **SEC-02**: Access-log ingestion (`POST` access logs) cannot be abused by anonymous clients (device API keys, signed requests, or other agreed mechanism) — closes BUG-004.
- [ ] **SEC-03**: Uploaded images are validated as real image bytes (e.g. magic bytes / PIL decode), not only `content_type` — closes BUG-005.
- [ ] **SEC-04**: CORS allowed origins are configurable via settings/environment for non-localhost deployments — closes BUG-007.
- [ ] **SEC-05**: Enforce authorization appropriate to sensitive routes (minimum: document strategy; implement roles or scoped claims if required for BUG-008) — closes BUG-008.

### Reliability & performance

- [ ] **REL-01**: Upload size limits are enforced without reading the entire body into memory first (streaming cap or proxy contract documented) — closes BUG-006.

### Cleanup & maintenance

- [x] **CLN-01**: Deprecated `crud/` modules removed — closes BUG-009 (resolved).

### Operations & supply chain

- [x] **OPS-01**: No `docker-compose.yml` in repo — intentional; local Postgres documented in `docs/setup/installation.md` — closes BUG-010 (resolved/irrelevant).
- [ ] **OPS-02**: Deployment docs or scripts state how to keep Alembic and app `DATABASE_URL` aligned — closes BUG-011.
- [ ] **OPS-03**: Introduce repeatable dependency pinning strategy (e.g. lockfile or pinned ranges) for `requirements.txt` — closes BUG-012.

## v2 Requirements

Deferred — not part of this bugfix milestone.

### IoT / hardware

- Real gate actuator and device Bluetooth integration (currently stubbed/demo controllers).

### ML pipeline

- Server-side OCR via `POST /api/v1/ml/recognize-plate` (requires `requirements-ml.txt`); standalone script removed during cleanup.

## Out of Scope

| Item | Reason |
|------|--------|
| New end-user features beyond fixing listed defects | Milestone is stabilization |
| Frontend changes | Lives in separate frontend repository |
| Full RBAC product design | SEC-05 may scope minimal enforcement only |

## Traceability

| Requirement | Status |
|-------------|--------|
| CFG-01 | Pending |
| CFG-02 | Resolved |
| SEC-01 | Pending |
| SEC-02 | Pending |
| SEC-03 | Pending |
| SEC-04 | Pending |
| SEC-05 | Pending |
| REL-01 | Pending |
| CLN-01 | Resolved |
| OPS-01 | Resolved |
| OPS-02 | Pending |
| OPS-03 | Pending |

**Coverage:**

- v1 requirements: 12 total
- Resolved: 3
- Pending: 9
