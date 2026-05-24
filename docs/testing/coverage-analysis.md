# Test Coverage Analysis

**Last updated:** 2026-05-24  
**API version:** 0.1.0

## Summary

The repository has a structured pytest suite with both **unit** and **integration** tests. Coverage is configured in `pyproject.toml` (`source = ["apps"]`). Run locally:

```bash
pytest --cov=apps --cov-report=term-missing
pytest --cov=apps --cov-report=html
```

For detailed testing patterns and fixtures, see [`.planning/codebase/TESTING.md`](../../.planning/codebase/TESTING.md).

## Test layout

| Area | Path | Scope |
|------|------|--------|
| Shared fixtures | `tests/conftest.py` | SQLite in-memory DB, auth tokens, rate limiter reset |
| Root-level API tests | `tests/test_*.py` | Health, access logs, auth/whitelist, plate OCR |
| Unit tests | `tests/unit/` | Controllers, repositories, deps, core config/security, utils |
| Integration tests | `tests/integration/` | Full HTTP flows via `TestClient` |
| Manual debug helpers | `tests/manual/` | Not collected by pytest |

## Coverage by layer

| Layer | Unit tests | Integration tests |
|-------|------------|-------------------|
| Endpoints (HTTP) | Indirect via controllers | Yes — all major routes |
| Controllers | Yes | Yes |
| Repositories | Yes | Via endpoints |
| Models | Via repositories/endpoints | Via endpoints |
| Core (config, security) | Yes | Partial |
| Utils (plate) | Yes | Via whitelist/access logs |

## Known gaps

- No enforced CI coverage threshold (SonarQube can report when configured).
- `tests/test_main.py` uses a module-level `TestClient` without conftest overrides — prefer the `client` fixture for new tests.
- ML/OCR route (`POST /api/v1/ml/recognize-plate`) may skip tests when `requirements-ml.txt` is not installed.

## CI

GitHub Actions runs `pytest` with coverage XML for SonarQube when `SONAR_TOKEN` is set. See [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).
