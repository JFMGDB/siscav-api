# ADR 005: Render API deployment with Supabase Postgres

## Status

Accepted

## Context

The SISCAV API is a FastAPI service served by Uvicorn. It connects to PostgreSQL through `DATABASE_URL`, runs Alembic migrations outside the request path, and writes access-log images under `UPLOAD_DIR`.

The database already exists in Supabase and contains the expected application schema. The deployment target therefore needs to host only the API runtime, not a new database.

The project needs a stable production API URL while development continues in the repository. For the class demo, the API must also deploy on Render's free tier.

## Decision

- Deploy `siscav-api` as a Render Web Service.
- Keep Supabase Postgres as the production database through `DATABASE_URL`.
- Use Render environment variables for `ENVIRONMENT`, `DATABASE_URL`, `SECRET_KEY`, `DEVICE_INGEST_KEY`, `BACKEND_CORS_ORIGINS`, `UPLOAD_DIR`, and `PYTHONPATH`.
- Use `GET /api/v1/health` as the service health check.
- Use Render free tier without a persistent disk for the initial demo deployment.
- Set `UPLOAD_DIR` to an ephemeral path such as `/tmp/siscav-uploads` on the free tier.
- Keep local Python executable workflows on `uv run ...`; keep the Render service start command simple and compatible with the installed runtime dependencies.

## Consequences

- The API keeps its current ASGI web-service model with minimal code changes.
- Uploaded access-log images are available only while the free service instance keeps its ephemeral filesystem. They can be lost on redeploy, restart, or spin-down.
- The frontend can call the API directly from the browser when `BACKEND_CORS_ORIGINS` includes the stable Vercel origin.
- Production secrets remain outside the repository.
- Alembic migrations remain an explicit operational step before or during deployment, not application startup behavior.
- If persistent access-log images become required, upgrade the Render service to a paid plan and attach a disk mounted at the same path configured in `UPLOAD_DIR`, or migrate uploads to object storage.

## Alternatives considered

- **Vercel Python serverless functions:** Rejected for this release. Vercel can host FastAPI, but this API currently depends on service-style execution, local upload persistence, and optional heavy OCR dependencies. Making that robust on serverless functions would require larger changes such as object storage and serverless-specific runtime tuning.
- **Provisioning PostgreSQL on Render:** Rejected because Supabase Postgres already exists and is the source of truth for the project.
- **Render persistent disk on free tier:** Rejected because Render only supports persistent disks for paid services.
- **Supabase Storage for uploads now:** Deferred. It is a good future improvement if multi-instance API scaling or object storage becomes necessary, but it is not required for the current single-service deployment.
