# Roadmap: SISCAV API (bugfix milestone)

## Overview

This milestone closes mapped defects in `.planning/BUGS.md` by hardening security and uploads first, then aligning configuration and API contracts with documentation, then improving reliability and operational repeatability, and finally cleaning deprecated code while settling authorization strategy for sensitive routes.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Security-critical foundations** — Fail-fast secrets, authenticated access-log ingest, and real image validation
- [ ] **Phase 2: Configuration & API honesty** — Dependency alignment, refresh-token story vs docs, configurable CORS
- [ ] **Phase 3: Reliability & operations** — Streaming/size limits, Compose and Alembic alignment docs, dependency pinning
- [ ] **Phase 4: Cleanup & authorization strategy** — Remove or shim deprecated `crud/`, document and enforce RBAC minimum for sensitive routes

## Phase Details

### Phase 1: Security-critical foundations
**Goal**: Production cannot run with development secrets; access-log ingestion is not anonymously abusable; uploaded files are validated as real images.
**Depends on**: Nothing (first phase)
**Requirements**: SEC-01, SEC-02, SEC-03
**Success Criteria** (what must be TRUE):
  1. In non-debug environments, the application refuses to start when `SECRET_KEY` is still the development default (or equivalent policy), with an operator-visible error.
  2. Anonymous clients cannot successfully abuse `POST` access-log ingestion; only requests using the agreed mechanism (e.g. device API keys or signed requests) are accepted.
  3. Uploads that are not valid image bytes are rejected even when `Content-Type` claims an image (e.g. magic bytes or decode check).
**Plans**: TBD

### Phase 2: Configuration & API honesty
**Goal**: Declared dependencies, refresh-token configuration, and CORS behavior match what operators and clients actually get at runtime.
**Depends on**: Phase 1
**Requirements**: CFG-01, CFG-02, SEC-04
**Success Criteria** (what must be TRUE):
  1. `[project.dependencies]` in `pyproject.toml` matches the runtime hashing stack used by the app (aligned with `requirements.txt` / `security.py`).
  2. Either refresh tokens are issued and documented in OpenAPI (or equivalent), or `refresh_token_expire_days` and related env documentation are removed so config matches implementation.
  3. Allowed CORS origins are driven by settings/environment so non-localhost deployments can allow the real frontend origin without code changes.
**Plans**: TBD

### Phase 3: Reliability & operations
**Goal**: Upload handling avoids unnecessary full-body buffering; local and production operators know how to run Compose, align Alembic with the app DB URL, and reproduce dependency versions.
**Depends on**: Phase 2
**Requirements**: REL-01, OPS-01, OPS-02, OPS-03
**Success Criteria** (what must be TRUE):
  1. Upload size limits are enforced without reading the entire body into memory first, or the deployment contract (e.g. reverse proxy limits) is documented and consistent with behavior.
  2. Docker Compose usage for the `local` profile (or adjusted compose files) is documented so `api`/`db` dependencies are predictable for developers.
  3. Deployment docs or scripts explain how to keep Alembic and application `DATABASE_URL` aligned across environments.
  4. A repeatable dependency pinning strategy exists (e.g. lockfile or pinned ranges) for `requirements.txt` so CI and deploys do not drift silently.
**Plans**: TBD

### Phase 4: Cleanup & authorization strategy
**Goal**: Deprecated layers are removed or isolated; privileged routes have a clear, minimally enforced authorization model.
**Depends on**: Phase 3
**Requirements**: CLN-01, SEC-05
**Success Criteria** (what must be TRUE):
  1. Deprecated `crud/` modules are removed or reduced to documented shims after confirming no remaining imports.
  2. A documented strategy exists for authorization on sensitive routes; where BUG-008 requires it, enforcement matches that strategy (e.g. roles or scoped claims verifiable by an authenticated vs unprivileged user).
**Plans**: TBD

## Progress

**Execution Order:**  
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Security-critical foundations | 0/TBD | Not started | - |
| 2. Configuration & API honesty | 0/TBD | Not started | - |
| 3. Reliability & operations | 0/TBD | Not started | - |
| 4. Cleanup & authorization strategy | 0/TBD | Not started | - |

---
*Bugfix milestone roadmap — 2026-04-10*
