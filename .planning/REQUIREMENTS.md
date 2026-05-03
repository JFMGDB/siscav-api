# Requirements: SISCAV API (bugfix milestone)

**Defined:** 2026-04-10  
**Core Value:** Trustworthy API for administration and auditable access events — close mapped security and correctness gaps.

**Bug inventory:** `.planning/BUGS.md`

## v1 Requirements

### Configuration & dependency honesty

- [ ] **CFG-01**: `pyproject.toml` `[project.dependencies]` matches actual runtime hashing stack (`passlib[argon2]` per `requirements.txt` / `security.py`) — closes BUG-001.
- [ ] **CFG-02**: Either implement refresh-token issuance and document OpenAPI flows, or remove `refresh_token_expire_days` and related env documentation — closes BUG-002.

### Security & authentication

- [ ] **SEC-01**: Application refuses to start in non-debug environments when `SECRET_KEY` is still the development default (or equivalent fail-fast policy) — closes BUG-003.
- [ ] **SEC-02**: Access-log ingestion (`POST` access logs) cannot be abused by anonymous clients (device API keys, signed requests, or other agreed mechanism) — closes BUG-004.
- [ ] **SEC-03**: Uploaded images are validated as real image bytes (e.g. magic bytes / PIL decode), not only `content_type` — closes BUG-005.
- [ ] **SEC-04**: CORS allowed origins are configurable via settings/environment for non-localhost deployments — closes BUG-007.
- [ ] **SEC-05**: Enforce authorization appropriate to sensitive routes (minimum: document strategy; implement roles or scoped claims if required for BUG-008) — closes BUG-008.

### Reliability & performance

- [ ] **REL-01**: Upload size limits are enforced without reading the entire body into memory first (streaming cap or proxy contract documented) — closes BUG-006.

### Cleanup & maintenance

- [ ] **CLN-01**: Deprecated `crud/` modules are removed or reduced to documented shims after confirming no imports — closes BUG-009.

### Operations & supply chain

- [ ] **OPS-01**: Docker Compose usage is documented for the `local` profile (or compose files adjusted) so `api`/`db` dependencies are not surprising — closes BUG-010.
- [ ] **OPS-02**: Deployment docs or scripts state how to keep Alembic and app `DATABASE_URL` aligned — closes BUG-011.
- [ ] **OPS-03**: Introduce repeatable dependency pinning strategy (e.g. lockfile or pinned ranges) for `requirements.txt` — closes BUG-012.

## v2 Requirements

Deferred — not part of this bugfix milestone.

### IoT / hardware

- Real gate actuator and device Bluetooth integration (currently stubbed controllers).

### ML pipeline

- Integrate `recognize-plate.py` as an optional extra or separate service with its own dependency set.

## Out of Scope

| Item | Reason |
|------|--------|
| New end-user features beyond fixing listed defects | Milestone is stabilization |
| Frontend changes | Lives in `siscav-web` |
| Full RBAC product design | SEC-05 may scope minimal enforcement only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CFG-01 | Phase 2 | Pending |
| CFG-02 | Phase 2 | Pending |
| SEC-01 | Phase 1 | Pending |
| SEC-02 | Phase 1 | Pending |
| SEC-03 | Phase 1 | Pending |
| SEC-04 | Phase 2 | Pending |
| SEC-05 | Phase 4 | Pending |
| REL-01 | Phase 3 | Pending |
| CLN-01 | Phase 4 | Pending |
| OPS-01 | Phase 3 | Pending |
| OPS-02 | Phase 3 | Pending |
| OPS-03 | Phase 3 | Pending |

**Coverage:**

- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-04-10*  
*Last updated: 2026-04-10 — traceability mapped in ROADMAP.md (Phases 1–4)*
