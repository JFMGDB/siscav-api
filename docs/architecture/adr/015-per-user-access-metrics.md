# ADR 015: Per-user access log ownership and scoped dashboard metrics

## Status

Accepted

## Context

Dashboard metrics (`traffic_volume`, `auto_approval_rate_percent`, `ocr_success_rate_percent`) and `GET /access_logs/` listed **all** rows in the database. There was no tenant/client model; each authenticated user is a **client administrator** (`is_admin`, not `is_superadmin`).

Operators expected metrics to reflect **their own** activity, not every record in the shared database.

## Decision

1. **Schema** — Alembic revision `20260608_0001` adds nullable `owner_user_id` (FK → `users.id`, indexed) to:
   - `access_logs`
   - `ocr_attempts`

2. **Population**
   - Operator JWT ingest (`POST /access_logs/` without device key): set `owner_user_id = current_user.id`.
   - Device IoT ingest (device key): `owner_user_id = NULL` (legacy/global device path).
   - `POST /ml/recognize-plate`: set `owner_user_id = current_user.id` on `ocr_attempts`.

3. **Query scope**
   - `GET /api/v1/dashboard/metrics`: filter aggregates by `owner_user_id == current_user.id`.
   - `GET /api/v1/access_logs/`: same filter for list endpoint.

## Consequences

- Each client admin sees only their own traffic volume and OCR success rate.
- Historical rows with `NULL` owner are excluded from per-user metrics until backfilled (if needed).
- Device-ingested logs remain unowned unless a future device→user mapping is added.

## Migration

```bash
cd siscav-api
uv run alembic upgrade head
```

## Alternatives considered

- **Full multi-tenant `client_id` model** — Rejected for minimal demo scope; `owner_user_id` satisfies the reported bug with one column.
- **Keep global metrics** — Rejected; contradicts operator expectation and demo narrative.
