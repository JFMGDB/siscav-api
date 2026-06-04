# ADR 005: Render API deployment with Supabase Postgres

## Status

Accepted

## Context

The SISCAV API is a FastAPI service served by Uvicorn. It connects to PostgreSQL through `DATABASE_URL`, runs Alembic migrations outside the request path, and persists access-log images under `UPLOAD_DIR`.

The database already exists in Supabase and contains the expected application schema. The deployment target therefore needs to host only the API runtime and persistent uploaded files, not a new database.

The project needs a stable production API URL while development continues in the repository.

## Decision

- Deploy `siscav-api` as a Render Web Service.
- Keep Supabase Postgres as the production database through `DATABASE_URL`.
- Use Render environment variables for `ENVIRONMENT`, `DATABASE_URL`, `SECRET_KEY`, `DEVICE_INGEST_KEY`, `BACKEND_CORS_ORIGINS`, `UPLOAD_DIR`, and `PYTHONPATH`.
- Use `GET /api/v1/health` as the service health check.
- Mount a Render persistent disk at the same path configured in `UPLOAD_DIR`.
- Keep local Python executable workflows on `uv run ...`; keep the Render service start command simple and compatible with the installed runtime dependencies.

## Consequences

- The API keeps its current ASGI web-service model with minimal code changes.
- Uploaded access-log images survive service restarts when the Render disk is attached.
- The frontend can call the API directly from the browser when `BACKEND_CORS_ORIGINS` includes the stable Vercel origin.
- Production secrets remain outside the repository.
- Alembic migrations remain an explicit operational step before or during deployment, not application startup behavior.

## Alternatives considered

- **Vercel Python serverless functions:** Rejected for this release. Vercel can host FastAPI, but this API currently depends on service-style execution, local upload persistence, and optional heavy OCR dependencies. Making that robust on serverless functions would require larger changes such as object storage and serverless-specific runtime tuning.
- **Provisioning PostgreSQL on Render:** Rejected because Supabase Postgres already exists and is the source of truth for the project.
- **Supabase Storage for uploads now:** Deferred. It is a good future improvement if multi-instance API scaling or object storage becomes necessary, but it is not required for the current single-service deployment.
