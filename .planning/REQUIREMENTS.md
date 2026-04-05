# Requirements: SISCAV API

**Defined:** 2026-04-04  
**Core Value:** Trustworthy plate-based access decisions and an auditable log of every attempt, with a path to secure devices and real gate integration.

## v1 Requirements

Backend/API capabilities targeted by the current planning cycle (brownfield hardening + integration). Derived from existing code, `.planning/codebase/CONCERNS.md`, and `docs/requirements/project-specification.md` (server-side RF-004, RF-006, RF-007 where applicable).

### Security & access control

- [x] **SEC-01**: Access log ingestion (`POST /api/v1/access_logs/`) is protected with a documented authentication mechanism (API key, device credential, or mTLS) appropriate to the deployment threat model.
- [x] **SEC-02**: Refresh token endpoint is rate-limited consistently with login, and weak/default `SECRET_KEY` cannot be used in production configuration.
- [x] **SEC-03**: OpenAPI and endpoint docstrings accurately reflect who may call privileged routes (or role-based checks are implemented where docs promise “administrator”).

### Authentication

- [x] **AUTH-01**: User can register with email and password and receive JWT access + refresh tokens.
- [x] **AUTH-02**: User can log in with OAuth2 password flow and obtain new access tokens via refresh.

### Whitelist (authorized plates)

- [ ] **WL-01**: Authenticated user can list, create, update, and delete authorized plates with normalized plate matching (case/format insensitive per existing rules).

### Access logs (audit)

- [ ] **LOG-01**: Client can submit an access attempt with plate text and optional image; server persists plate, timestamp, outcome, and image path per existing schema.
- [ ] **LOG-02**: Authenticated user can list access logs with filtering/pagination as exposed by the API.
- [ ] **LOG-03**: Authenticated user can retrieve stored images for a log entry when permitted by policy.

### Gate control

- [ ] **GATE-01**: Gate trigger endpoint performs a real integration path (or returns explicit “simulated” in response) and surfaces failure when the downstream actuator does not acknowledge.

### Devices

- [ ] **DEV-01**: Device-related endpoints are either production-ready (real discovery/control) or clearly feature-flagged/disabled so operators cannot mistake mocks for live hardware.

### Operations & quality

- [x] **OPS-01**: Debug/agent log instrumentation is removed or strictly gated; SQLite bootstrap does not silently bypass migration discipline in shared environments.
- [x] **OPS-02**: Runtime dependencies are pinned or lockfile-managed for reproducible installs.
- [x] **OPS-03**: Deprecated `crud/` modules are removed or formally deprecated with no duplicate maintenance path.

## v2 Requirements

Deferred enhancements (not committed in the current roadmap unless promoted).

### Authentication & admin

- **AUTH-10**: OAuth social login (Google, Microsoft, etc.) for dashboard users.
- **AUTH-11**: Email verification and password reset flows.

### Product

- **DASH-01**: Full hosted admin dashboard SPA in-repo (if chosen as a separate frontend milestone).
- **IOT-01**: Edge ALPR capture/OCR pipeline maintained alongside API (reintroduction of device codebase or external repo coordination).

## Out of Scope

| Feature | Reason |
|---------|--------|
| On-device RF-001–RF-003 implementation | Edge/camera software is out of this API repo unless explicitly re-scoped; API consumes plate + image from clients. |
| Physical relay wiring / hardware certification | Field installation and electrical work are operational, not API code. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SEC-01 | 1 | Complete |
| SEC-02 | 1 | Complete |
| SEC-03 | 1 | Complete |
| AUTH-01 | 1 | Complete |
| AUTH-02 | 1 | Complete |
| WL-01 | 2 | Pending |
| LOG-01 | 2 | Pending |
| LOG-02 | 2 | Pending |
| LOG-03 | 2 | Pending |
| GATE-01 | 3 | Pending |
| DEV-01 | 3 | Pending |
| OPS-01 | 4 | Complete |
| OPS-02 | 4 | Complete |
| OPS-03 | 4 | Complete |

**Coverage:**

- v1 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0

---
*Requirements defined: 2026-04-04*  
*Last updated: 2026-04-04 after roadmap traceability*
