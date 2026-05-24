# SISCAV API Documentation

Technical and operational documentation for **SISCAV API** — a FastAPI backend for vehicle access control based on authorized plates, with auditable logging and optional gate actuator integration.

**Last structural review:** 2026-05-24

## Overview

This repository delivers the **central API**: JWT authentication with refresh tokens, authorized-plate whitelist CRUD, access-log ingestion (multipart: image + plate), filtered listings, and an admin endpoint to trigger gate actions (simulated or via external HTTP). Server-side plate OCR is available at `POST /api/v1/ml/recognize-plate` when ML dependencies are installed.

## Documentation Structure

### [Setup](./setup/)

- [Installation guide](./setup/installation.md)
- [Start the server](./setup/init-server-guide.md)
- [Database setup (Supabase)](./setup/database-setup.md)
- [Common commands (lint, test, git)](./setup/commands.md)

### [API](./api/)

- [API documentation index](./api/README.md)
- [Frontend integration](./api/frontend-integration.md) — tokens, refresh, CORS, OCR
- [Technical documentation](./api/technical-documentation.md)
- **Postman:** [`SISCAV_API.postman_collection.json`](SISCAV_API.postman_collection.json), [`SISCAV_API.postman_environment.json`](SISCAV_API.postman_environment.json)

### [Database](./database/)

- [Data model](./database/data-model.md)
- [Supabase migration guide](./database/supabase-migration.md)

### [Architecture](./architecture/)

- [Architecture index](./architecture/README.md)
- [Executive summary](./architecture/executive-summary.md)
- [Acceptance criteria and DevOps](./architecture/acceptance-criteria-devops.md)
- [ADRs](./architecture/adr/) — architecture decision records

### [Requirements](./requirements/)

- [Project specification](./requirements/project-specification.md)

### [Development](./development/)

- [Coding standards and MVC patterns](./development/coding-standards.md)

### [Testing](./testing/)

- [Coverage analysis](./testing/coverage-analysis.md)

## Guides by Role

### Backend developer

1. [setup/installation.md](./setup/installation.md) and [setup/init-server-guide.md](./setup/init-server-guide.md)
2. [api/technical-documentation.md](./api/technical-documentation.md)
3. [development/coding-standards.md](./development/coding-standards.md)
4. Tests: `pytest` at repo root (see [`.planning/codebase/TESTING.md`](../.planning/codebase/TESTING.md))

### Frontend developer

1. [api/frontend-integration.md](./api/frontend-integration.md)
2. OpenAPI at `/docs` with the API running

### Device / partner integration

1. [api/README.md](./api/README.md) — access-log ingestion contract
2. Postman collection in `docs/`

### Product / management

1. [requirements/project-specification.md](./requirements/project-specification.md)
2. [architecture/executive-summary.md](./architecture/executive-summary.md)

## Stack (quick reference)

Pinned values in [`pyproject.toml`](../pyproject.toml): FastAPI, Uvicorn, SQLAlchemy 2.x, Alembic, Pydantic, Argon2, JWT (`python-jose`), SlowAPI. CI uses Python 3.13 with `requirements-dev.txt` (see [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

## Maintenance

When changing endpoints or environment variables, update: `docs/api/`, `docs/setup/installation.md`, `docs/setup/init-server-guide.md`, and the Postman collection in `docs/` when applicable.

## Contributing

Keep relative links aligned with the current repository layout. The application package is `apps.api.src` — not `app/` or `apps/iot-device/`.
