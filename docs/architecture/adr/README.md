# Architecture Decision Records

Historical architecture planning documents preserved for reference.

## Records

- [001 — Architecture Backlog and Repository Separation](./001-architecture-backlog.md) — original project backlog and rationale for separate backend/frontend repositories
- [002 — Vehicle Classification Layer (Backend-owned)](./002-vehicle-classification-layer.md) — contracts + classifier abstraction + endpoint for future model integration
- [003 — Database URL and Supabase Exposure](./003-database-url-and-supabase-exposure.md) — URL resolution, Alembic ConfigParser bypass, RLS/REVOKE hardening for api_only
- [004 — Dependency Management and Configuration](./004-dependency-management.md) — pyproject SSOT, uv.lock, exported requirements, optional ML extra
- [005 — Render API Deployment with Supabase Postgres](./005-render-api-deployment.md) — Render web service runtime, Supabase database, persistent uploads, and rejected serverless alternative
- [006 — Remove Bluetooth Device Demo API](./006-remove-bluetooth-device-demo-api.md) — removal of `/devices/*` demo routes and `IOT_DEVICE_DEMO_API`; ingest and gate actuator unchanged
- [007 — Restrict User Registration to Superadmin](./007-restrict-user-registration-to-superadmin.md) — `is_superadmin`, superadmin-only `POST /register`
- [008 — Two Roles Only](./008-two-roles-only.md) — superadmin + client administrator only; `get_current_client_admin_user`; register defaults `is_admin=true`
- [010 — Auto-open Gate on Authorized Access](./010-auto-open-gate-on-authorized-access.md) — sync actuator call after DB commit and graceful degradation
- [011 — Ambulance Auto-Authorization Policy (ONNX Runtime)](./011-ambulance-auto-authorization-policy.md) — ONNX classifier on ingest, ephemeral `vehicle_classification`, ML Playground, cold-start mitigations
- [012 — OCR Plate Flow Validation and Monitor Orchestration](./012-ocr-plate-flow-validation.md) — EasyOCR fallback, real monitor auto-flow, operator dialogs for non-whitelisted plates

For current architecture, see [Executive Summary](../executive-summary.md) and [Acceptance Criteria](../acceptance-criteria-devops.md).
