# ADR 009: Superadmin User Management Endpoints

## Status

Accepted.

## Context

ADR 007 restricted `POST /api/v1/register` to superadmin JWT and rejected a separate `/admin/users` route for registration duplication. The Mantis superadmin hub (web ADR 0014) needs global account counters and a paginated account list backed by real data, not browser-local storage.

The Postgres `users` table already exposes all required columns (`is_admin`, `is_superadmin`, timestamps). Supabase RLS revokes direct client access; the FastAPI service role continues to manage rows via SQLAlchemy.

## Decision

Add superadmin-only REST endpoints under `/api/v1/users`:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/stats` | Global counters (`total_accounts`, `client_admin_count`, `superadmin_count`) |
| GET | `/users/` | Paginated list (`skip`, `limit`, `PaginatedUserList`) |
| PATCH | `/users/{id}` | Update `email` and/or `password` only |
| DELETE | `/users/{id}` | Hard-delete with guards |

- Guard: `Depends(get_current_superadmin_user)` on all routes.
- `POST /api/v1/register` remains unchanged (ADR 007).
- Roles (`is_admin`, `is_superadmin`) are **immutable via API** (ADR 008); promotion stays seed/SQL.
- Delete guards: cannot delete self; cannot delete the last superadmin.
- Implementation: `UserController`, extended `UserRepository`, new `endpoints/users.py`.

## Consequences

- Mantis superadmin UI can show real account stats and CRUD without Supabase client access.
- No Alembic migration required for this feature.
- ADR 007 alternative “reject `/admin/users`” still holds for registration; management uses standard `/users` prefix instead.

## Related

- API ADR 007 (registration), ADR 008 (two roles).
- Web ADR 0012, 0013, 0014 (superadmin UI).
