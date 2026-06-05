# ADR 007: Restrict User Registration to Superadmin

## Status

Accepted.

## Context

`POST /api/v1/register` was public (rate-limited only). Anyone could create accounts via HTTP or the web `/register` page. The system had a single `is_admin` flag with no distinction between Siscav system operators and client operational administrators.

## Decision

- Add `is_superadmin` on `users` (Alembic `20260604_0003`).
- Protect `POST /api/v1/register` with `Depends(get_current_superadmin_user)` — unauthenticated → **401**, non-superadmin → **403**.
- Expose `is_admin` and `is_superadmin` on `UserRead` / `GET /users/me`.
- Bootstrap first superadmin via `scripts/seed_demo.py` or SQL; no public self-registration or master password.

### Amendment (operational separation)

See ADR 008 for the final two-role model and `get_current_client_admin_user`.

### Role separation (superseded by ADR 008)

| Role | Fields | Create users | Client API |
|------|--------|--------------|------------|
| Client administrator | `is_admin`, not superadmin | No | Yes |
| Siscav superadmin | `is_superadmin`, `is_admin=false` | Yes | No |

## Consequences

- Registration requires a valid Bearer access token from a superadmin.
- Clients must send `Authorization` on register; public signup flows break until updated.
- Promoting operational admins remains a DB operation (`UPDATE users SET is_admin = 1 ...`).

## Alternatives considered

- **Frontend-only hide:** Rejected — not a security boundary.
- **Master password in UI/env:** Rejected — secret exposure risk; role-based JWT is sufficient.
- **New `/admin/users` endpoint:** Rejected — same behavior with more surface area; existing `/register` path kept with auth dependency.

## Related

- Web ADR 0012: protected `/users/create`, public `/register` removed.
