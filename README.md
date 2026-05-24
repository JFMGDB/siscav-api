# SISCAV API

Backend for the **Vehicle Access Control System (SISCAV)** — a FastAPI API for plate whitelist management, access attempt logging (with image upload), JWT authentication, and optional gate triggering via HTTP.

## Documentation

Live project documentation is in **[`docs/`](docs/README.md)**:

| Resource | Path |
|----------|------|
| Documentation index | [`docs/README.md`](docs/README.md) |
| Installation and overview | [`docs/setup/installation.md`](docs/setup/installation.md) |
| Start the server | [`docs/setup/init-server-guide.md`](docs/setup/init-server-guide.md) |
| Frontend integration (tokens, OCR `POST /api/v1/ml/recognize-plate`) | [`docs/api/frontend-integration.md`](docs/api/frontend-integration.md) |
| Postman | [`docs/SISCAV_API.postman_collection.json`](docs/SISCAV_API.postman_collection.json) + [`docs/SISCAV_API.postman_environment.json`](docs/SISCAV_API.postman_environment.json) |
| OpenAPI (with API running) | `http://localhost:8000/docs` |

## Quick Start

```bash
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
# At repo root (where alembic.ini lives):
set PYTHONPATH=.   # Linux/Mac: export PYTHONPATH=.
alembic upgrade head
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
```

On Windows, from the repo root: `.\scripts\start_server.ps1`.

## Code

- Application: `apps/api/src/` (`main.py`, `api/v1/…`)
- Tests: `tests/`
- Alembic migrations: `apps/api/src/alembic/` (config in root `alembic.ini`)

## Repository Scope

This repository focuses on the **API**. Edge clients (ALPR, cameras, gateways) integrate via `POST /api/v1/access_logs/` — see [`docs/api/README.md`](docs/api/README.md).
