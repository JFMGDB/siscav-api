# API Documentation

Documentation for the SISCAV API endpoints, authentication, and integration contracts.

## Index

- [Technical Documentation](./technical-documentation.md) — architecture overview, technical decisions, resources, Swagger access
- [Frontend Integration](./frontend-integration.md) — authentication guide, code examples, token management, error handling

For coding patterns and architecture, see [Development — Coding Standards](../development/coding-standards.md).

## Description

The SISCAV API is built with FastAPI and serves as the central backend. It manages:

- Administrator authentication (JWT)
- Authorized plate whitelist management
- Access log ingestion from edge clients (`POST /api/v1/access_logs/`)
- Remote gate control
- Secure access to uploaded images

## First Superadmin

User registration (`POST /api/v1/register`) requires a **Bearer JWT** from a Siscav superadministrator (`is_superadmin = true`). Public self-registration is not supported.

Provision the first superadmin via `python scripts/seed_demo.py` or manually (PostgreSQL or SQLite):

```sql
UPDATE users SET is_superadmin = 1, is_admin = 0 WHERE email = 'your-email@example.com';
```

On SQLite use `1` or `true` depending on your SQL client. After migration `20260604_0003`, the `is_superadmin` column exists on all new databases.

If upgrading from an older seed that set both flags, clear operational admin on platform accounts:

```sql
UPDATE users SET is_admin = 0 WHERE is_superadmin = 1;
```

### Role separation

| Role | Flags | Capabilities |
|------|-------|--------------|
| Client administrator | `is_admin = true`, `is_superadmin = false` | Full client API and UI (whitelist, logs, gate, images, ML) |
| Siscav superadmin | `is_superadmin = true`, `is_admin = false` | `POST /register`, `GET /users/me`, account management UI |

`POST /register` always creates client administrators. Accounts with both flags false are invalid; fix with:

```sql
UPDATE users SET is_admin = true WHERE is_superadmin = false AND is_admin = false;
```

## Whitelist (Authorized Plates)

Base path: **`/api/v1/whitelist/`**. All operations require a valid **`Authorization: Bearer`** JWT from a **client administrator**.

- **Normalization:** the server computes `normalized_plate` from the submitted text (strips non-alphanumeric characters, compares uppercase). The normalized value is **unique** — duplicate submissions return **409 Conflict**.
- **Formats:** Brazilian plates in **Mercosul** (e.g. `ABC1D23`) or **legacy** three letters + four digits (e.g. `ABC-1234`), validated by `validate_brazilian_plate` / `AuthorizedPlateCreate` schema.
- **Common errors:** **400** / **422** invalid format; **409** duplicate plate; **404** ID not found on GET/PUT/DELETE.

## Access Logs

| Operation | Authentication |
|-----------|----------------|
| Register attempt (`POST /api/v1/access_logs/`, multipart) | Header **`X-Device-Key`** matching `DEVICE_INGEST_KEY` (when set) |
| List records (`GET /api/v1/access_logs/`) | **`Authorization: Bearer`** — client administrator |
| Get image (`GET /api/v1/access_logs/images/{filename}`) | **`Authorization: Bearer`** — client administrator |

Successful registration returns **`201 Created`** with **`AccessLogRead`**. When **`GATE_AUTO_OPEN_ON_AUTHORIZE=true`** and status is **`Authorized`**, the response may include **`gate_trigger`** (actuator outcome). Actuator failure does not change HTTP status or roll back the log.

## Gate Control

`POST /api/v1/gate_control/trigger` — **`Authorization: Bearer`** — client administrator.

- **`GATE_ACTUATOR_URL`:** when **not** set, the response has **`integration: "simulated"`** — no hardware command is sent. Use **`http://127.0.0.1:9080/open`** for Wokwi Private IoT Gateway (never `localhost` on Windows — IPv6 bypass).
- When set, the API **POST**s `{"action": "open"}` and only considers success on **HTTP 2xx** from the actuator (`integration: "live"`). Network or HTTP errors return **502**/**503** with explicit `detail` on this manual endpoint only.
- **`GATE_ACTUATOR_TIMEOUT_SECONDS`** (optional, default 5): timeout for manual trigger.
- **`GATE_AUTO_OPEN_ON_AUTHORIZE`** (optional, default false): after authorized access log commit, call actuator synchronously.
- **`GATE_AUTO_OPEN_TIMEOUT_SECONDS`** (optional, default 2, max 2): timeout for auto-open on access logs.

## Applied Principles

- **SOLID:** separation of concerns across layers (endpoints, controllers, repositories, schemas, models)
- **DRY:** shared utilities and functions
- **Modularity:** extensible structure
