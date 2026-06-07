# ADR 012: API error messages in Brazilian Portuguese

## Status

Accepted

## Context

The SISCAV API returned a mix of English and Portuguese strings in HTTP error responses (`HTTPException.detail`, Pydantic validation errors, SlowAPI rate-limit payloads, and the global 500 handler). The Mantis web frontend displays API `detail` text directly to operators, so inconsistent language degraded UX and made error handling unpredictable.

FastAPI already uses a de-facto contract: `{ "detail": string | ValidationErrorItem[] }`. We did not need RFC 7807 or a new error schema.

## Decision

1. **Centralize client-facing messages** in `apps/api/src/api/v1/core/error_messages.py` (pt-BR constants).
2. **Keep the existing HTTP status semantics** (401 missing/invalid credentials at OAuth layer; 403 invalid access token type in `get_current_user`; etc.) — documented in `docs/api/frontend-integration.md` and covered by integration tests.
3. **Add global handlers** in `main.py`:
   - `RequestValidationError` → 422 with translated `msg` fields (via `validation_errors.py`).
   - `RateLimitExceeded` → 429 with `{ "detail": "..." }` (replacing SlowAPI's `error` key).
   - Unhandled `Exception` → 500 with pt-BR `detail` in production; dev may append type/traceback for debugging.
4. **Remove ad-hoc 422 string responses** from controllers where Pydantic/FastAPI already validates input.

## Consequences

- All user-visible API error strings are pt-BR and DRY.
- Frontend can rely on `{ detail }` for every HTTP error except gate auto-open inline errors (201 body).
- Tests asserting English substrings were updated to Portuguese equivalents.
- Technical details remain in server logs only.

## Alternatives considered

- **RFC 7807 Problem Details**: rejected — extra schema and parsing cost for no current consumer need.
- **Changing 401/403 semantics**: rejected — would break existing tests and documented auth flow with minimal UX gain.
