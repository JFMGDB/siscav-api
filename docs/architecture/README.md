# Architecture Documentation

Architecture documentation for the SISCAV system, including design decisions, repository structure, and project backlog.

## Index

- [Executive Summary](./executive-summary.md) — high-level architecture, key decisions, components, and technologies
- [Acceptance Criteria and DevOps](./acceptance-criteria-devops.md) — acceptance criteria for all project epics
- [Architecture Decision Records](./adr/) — ADRs and historical planning documents

For current coding patterns and MVC structure, see also [Development — Coding Standards](../development/coding-standards.md).

## Description

SISCAV follows a three-layer approach:

1. **Edge layer:** External devices or clients that capture plates and send data to the API
2. **Server layer (this repo):** Centralized FastAPI backend
3. **Client layer:** Web admin panel (separate frontend repository)

## Architectural Decisions

- Separate repositories for backend and frontend
- FastAPI for performance and automatic OpenAPI documentation
- PostgreSQL for persistence (SQLite for local development)
- JWT for stateless authentication
- **MVC pattern:** clear separation between endpoints, controllers, and repositories
- **Repository pattern:** data access isolation
- **Service layer (controllers):** centralized business logic
- **SOLID and DRY:** rigorous application of design principles
