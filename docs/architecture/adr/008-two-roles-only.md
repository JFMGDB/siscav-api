# ADR 008: Two Roles Only (Superadmin and Client Administrator)

## Status

Accepted.

## Context

The system previously allowed a third state: authenticated users with `is_superadmin=false` and `is_admin=false`. Registration did not set `is_admin`, so new accounts defaulted to non-admin. That tier was never exposed in the UI and conflicted with product intent (only Siscav creates accounts; those accounts operate the parking system).

## Decision

- **Two roles only:**
  - Platform superadmin: `is_superadmin=true`, `is_admin=false`
  - Client administrator: `is_superadmin=false`, `is_admin=true`
- `POST /api/v1/register` (superadmin only) always creates client administrators (`is_admin=true`, `is_superadmin=false`).
- All client API routes use `get_current_client_admin_user`: rejects superadmin and rejects `is_admin=false`.
- Remove `get_current_admin_user` and `get_current_operational_user`.
- Legacy DB rows with both flags false are migrated to `is_admin=true`.

## Consequences

- No code path for non-admin client users.
- Superadmin cannot access client endpoints (unchanged).
- Promoting a user to client admin is only needed for legacy data; new users are admins by default.

## Related

- ADR 007: superadmin-only registration.
- Web ADR 0012, 0013: account management UI.
