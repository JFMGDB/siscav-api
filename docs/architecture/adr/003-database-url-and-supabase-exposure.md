# ADR 003: Database URL Resolution and Supabase Public Schema Exposure

## Status

Accepted

## Context

The SISCAV API connects to PostgreSQL (Supabase in production, Docker Postgres or explicit SQLite in development) via SQLAlchemy. Clients use FastAPI with JWT; there is no Supabase JS or PostgREST client in the application.

We identified three related problems:

1. **Silent SQLite fallback** when `DATABASE_URL` and `POSTGRES_*` were unset, masking misconfiguration (e.g. API started without loading `.env.local` while migrations targeted Supabase).
2. **Alembic `ValueError: invalid interpolation syntax`** when `DATABASE_URL` contained URL-encoded passwords (`%3F`, etc.) because `env.py` wrote the URL into `configparser` via `set_main_option`.
3. **Supabase security advisors** reported RLS disabled, full grants to `anon`/`authenticated`, and `pg_trgm` in `public`, exposing domain tables via PostgREST/GraphQL.

## Decision

### Database URL resolution

1. Resolve URL in this order: non-empty `DATABASE_URL` → composed `POSTGRES_*` → **`RuntimeError`** (no silent SQLite fallback).
2. SQLite is allowed only when `DATABASE_URL` explicitly uses the `sqlite:` scheme (e.g. `sqlite:///./siscav_dev.db`).
3. In `ENVIRONMENT=production|prod`, startup fails unless `DATABASE_URL` (or composed URL) is a PostgreSQL URL and `SECRET_KEY` is non-default.
4. Log dialect and host at engine creation (`log_database_target`); never log credentials.

In production, environment variables must be injected by the platform (Docker, K8s, etc.).

### Local `.env` loading

On import of `apps.api.src.api.v1.core.config` (non-production only):

1. Resolve repo root via `alembic.ini` next to this package.
2. If `.env` exists: `load_dotenv(path, override=False)` — does not override variables already set in the process.
3. If `.env.local` exists: `load_dotenv(path, override=True)` — local values override `.env` and unset process keys.

Skipped when `ENVIRONMENT` is `production` or `prod`. Tests and CI set `PYTHON_DOTENV_DISABLED=1` (python-dotenv built-in) before importing application code so a developer’s `.env.local` cannot override `DATABASE_URL=sqlite:///:memory:`.

`source .env.local` and `scripts/run_migrations.sh` remain valid and idempotent with this behavior.

### Alembic and URL-encoded passwords

- `apps/api/src/alembic/env.py` uses `get_migration_database_url()` and `create_engine(url)` directly, **without** writing the URL into `alembic.ini` / ConfigParser.
- Official alternative (not used here): escape `%` as `%%` when storing in ini ([Alembic ini escaping](https://alembic.sqlalchemy.org/en/latest/tutorial.html#escaping-characters-in-ini-files)).

### Supabase pooler

- **Session mode** (pooler port `5432`) is the default for this project: suitable for FastAPI + Alembic on the same `DATABASE_URL`.
- **Transaction mode** (port `6543`, `?pgbouncer=true`) is for high-volume/serverless; if adopted for the app, use a separate session-mode URL for migrations.

See `env.local.example`; other backends in `docs/setup/env-alternatives.md`.

### Public schema hardening (api_only)

Because data access is only through the API (postgres pooler role, bypasses RLS):

1. `REVOKE ALL` on domain tables and `alembic_version` from `anon` and `authenticated`.
2. `ENABLE ROW LEVEL SECURITY` on those tables with **no policies** for API roles (deny-by-default for PostgREST/GraphQL).
3. `ALTER DEFAULT PRIVILEGES FOR ROLE postgres` to revoke table/function/sequence grants from `anon`, `authenticated`, and `service_role` ([Securing your API](https://supabase.com/docs/guides/api/securing-your-api)).
4. Install/move `pg_trgm` to schema `extensions` (not `public`).

Delivered as `db/sql/supabase/05_security_hardening.sql` and Alembic revision `20260602_0004`.

We do **not** add `auth.uid()` policies; the frontend does not use Supabase Auth for data access.

## Consequences

### Positive

- Misconfiguration surfaces immediately instead of writing to a local `siscav_dev.db`.
- Migrations work with URL-encoded Supabase passwords.
- PostgREST/GraphQL exposure is closed; API behavior unchanged for the `postgres` connection role.

### Negative / operational

- Local quick start requires explicit `DATABASE_URL=sqlite:///...` or `POSTGRES_*`.
- After manual SQL setup, run `05_security_hardening.sql` or `alembic upgrade head` so `alembic_version` is also locked down.
- Moving `pg_trgm` drops and recreates `idx_access_logs_plate_trgm` (brief lock on `access_logs`).

## References

- [Supabase: Securing your API](https://supabase.com/docs/guides/api/securing-your-api)
- [Supabase: Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [PostgreSQL 17: Row security policies](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)
- [Alembic: Escaping characters in ini files](https://alembic.sqlalchemy.org/en/latest/tutorial.html#escaping-characters-in-ini-files)
