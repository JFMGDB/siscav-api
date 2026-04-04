# Phase 2: Whitelist & access log behavior - Context

**Gathered:** 2026-04-04  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **trustworthy whitelist management** and **audit-trail behavior** that matches requirements WL-01 and LOG-01 through LOG-03: normalized plate CRUD, device-keyed ingest (Phase 1), persisted log records, **list/filter/pagination** for authenticated clients, and **image retrieval** where policy allows.

Phase 2 clarifies **authorization layers** between JSON audit views and binary images, **locks whitelist validation rules**, and **freezes the public list contract** for integrators. It does **not** add gate hardware, device simulation honesty (Phase 3), or operational hygiene (Phase 4).

</domain>

<decisions>
## Implementation Decisions

### Who may view access logs vs images (LOG-02, LOG-03)

- **D-01:** **`GET /api/v1/access_logs/`** (list with filters) remains available to **any authenticated user** via `get_current_user`, matching LOG-02. Operators with a valid JWT may review metadata and audit fields returned by `AccessLogRead`.
- **D-02:** **`GET /api/v1/access_logs/images/{image_filename}`** remains **administrator-only** via `get_current_admin_user` (Phase 1 SEC-03). Phase 2 **does not** broaden image access to all authenticated users; LOG-03 is satisfied for v1 by this stricter policy for binary media.
- **D-03:** If OpenAPI or `docs/api` text implies any logged-in user can fetch images, **correct documentation** to state admin-only for image bytes while list remains authenticated-user.

### Whitelist normalization & validation (WL-01)

- **D-04:** Keep **strict** Brazilian plate validation (Mercosul + legacy pattern) as enforced by Pydantic / `PlateController` today; **no** fuzzy matching, provisional plates, or OCR-tolerance exceptions in Phase 2.
- **D-05:** **`normalized_plate` uniqueness** remains mandatory; duplicate normalized values continue to surface as **409 Conflict** (or current behavior) — document clearly rather than relaxing the rule.

### Access log list API contract (LOG-02)

- **D-06:** Treat the **current** query surface as the **v1 contract** to verify, document, and regression-test in Phase 2: `skip` (≥0), `limit` (1–100), optional `plate` (partial / case-insensitive per existing implementation), optional `status`, optional `start_date` / `end_date` (ISO 8601), ordering **newest first** as stated in route docstrings.
- **D-07:** **Defer** new filters (e.g. export formats, cursor pagination, higher `limit`), unless `docs/requirements/project-specification.md` mandates a specific missing field — if so, add a single backlog item rather than expanding scope ad hoc.

### Ingest & persistence (LOG-01)

- **D-08:** **No change** to Phase 1 ingest auth (`X-Device-Key`). Phase 2 **verifies** that persisted fields (plate text, timestamp, status, image storage key, optional `authorized_plate_id`) match schema and requirements end-to-end, including **multipart** behavior and error responses documented in OpenAPI.

### Claude's Discretion

- Wording of OpenAPI descriptions for filters and admin-only image routes.
- Integration test depth for `start_date`/`end_date` boundary and timezone (UTC vs local) — follow existing `AccessLogController` / repository behavior.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning & requirements

- `.planning/ROADMAP.md` — Phase 2 goal, success criteria, requirements WL-01, LOG-01–03.
- `.planning/REQUIREMENTS.md` — WL-*, LOG-* acceptance text.
- `.planning/phases/01-security-authentication-correctness/01-CONTEXT.md` — Device ingest key, admin image route, `is_admin` (Phase 1 locked).

### Product specification (server-relevant)

- `docs/requirements/project-specification.md` — RF-004 / RF-006 / RF-007 themes for audit and access (confirm no extra Phase 2 mandate).

### API implementation

- `apps/api/src/api/v1/endpoints/access_logs.py` — POST ingest, GET list, GET image.
- `apps/api/src/api/v1/endpoints/whitelist.py` — Whitelist CRUD.
- `apps/api/src/api/v1/controllers/access_log_controller.py` — Create, list filters, image path resolution.
- `apps/api/src/api/v1/controllers/plate_controller.py` — Create/update validation.
- `apps/api/src/api/v1/schemas/access_log.py` — `AccessLogRead`, `AccessStatus`.
- `apps/api/src/api/v1/schemas/authorized_plate.py` — `AuthorizedPlateCreate`, validation rules.
- `apps/api/src/api/v1/repositories/access_log_repository.py` — Query/filter implementation.
- `apps/api/src/api/v1/repositories/authorized_plate_repository.py` — Normalized plate persistence.
- `docs/api/README.md` — Operator-facing API notes (align with D-01–D-03).

### Concerns / quality (context only)

- `.planning/codebase/CONCERNS.md` — Upload validation (`Content-Type` vs magic bytes) — optional hardening **only** if in scope after checklist review; default defer if it grows scope.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **`PlateController` + `AuthorizedPlateRepository`:** CRUD with explicit timestamps and normalization in repository `create`/`update`.
- **`AccessLogController` + `AccessLogRepository`:** `get_all` / `count` with `plate_filter`, `status_filter`, `start_date`, `end_date`.
- **`verify_device_ingest_key`:** Phase 1 dependency on `POST /access_logs/`.
- **`get_current_admin_user`:** Phase 1 dependency on image GET.

### Established patterns

- **Pagination:** `skip`/`limit` mirrors whitelist listing (max 100).
- **JWT:** Standard `get_current_user` for list and whitelist; admin dependency only where Phase 1 applied.

### Integration points

- **OpenAPI** in `main.py` / route metadata should reflect D-01 vs D-03 split (list vs image).
- **`tests/integration/test_endpoints_access_logs.py`**, **`tests/test_access_logs.py`**, whitelist integration tests — extend for contract and doc alignment.

</code_context>

<specifics>
## Specific Ideas

User chose **`defaults`** in discuss-phase: apply recommended options for all four gray areas (list vs image policy, confirm admin images, strict whitelist, freeze list API contract).

</specifics>

<deferred>
## Deferred Ideas

- **Authenticated non-admin image viewing** (thumbnails or full image for operators without `is_admin`).
- **Fuzzy / provisional whitelist entries** for OCR errors.
- **Export** (CSV/JSON bulk), **cursor-based pagination**, or **raising `limit` above 100**.
- **Magic-byte image validation** — see CONCERNS.md; treat as separate hardening unless explicitly pulled into Phase 2 scope during planning.

### Reviewed Todos (not folded)

- None — `todo match-phase` returned no matches for Phase 2.

</deferred>

---
*Phase: 02-whitelist-access-log-behavior*  
*Context gathered: 2026-04-04*
