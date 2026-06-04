# Architecture Decision Records

Historical architecture planning documents preserved for reference.

## Records

- [001 — Architecture Backlog and Repository Separation](./001-architecture-backlog.md) — original project backlog and rationale for separate backend/frontend repositories
- [002 — Vehicle Classification Layer (Backend-owned)](./002-vehicle-classification-layer.md) — contracts + classifier abstraction + endpoint for future model integration
- [003 — Database URL and Supabase Exposure](./003-database-url-and-supabase-exposure.md) — URL resolution, Alembic ConfigParser bypass, RLS/REVOKE hardening for api_only
- [004 — Dependency Management and Configuration](./004-dependency-management.md) — pyproject SSOT, uv.lock, exported requirements, optional ML extra
- [005 — Render API Deployment with Supabase Postgres](./005-render-api-deployment.md) — Render web service runtime, Supabase database, persistent uploads, and rejected serverless alternative
- [006 — Remove Bluetooth Device Demo API](./006-remove-bluetooth-device-demo-api.md) — removal of `/devices/*` demo routes and `IOT_DEVICE_DEMO_API`; ingest and gate actuator unchanged

For current architecture, see [Executive Summary](../executive-summary.md) and [Acceptance Criteria](../acceptance-criteria-devops.md).
