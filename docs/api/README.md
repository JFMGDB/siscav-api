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

## First Administrator

Accounts created via `POST /api/v1/register` have `is_admin = false`. To promote the first operator (PostgreSQL or SQLite):

```sql
UPDATE users SET is_admin = 1 WHERE email = 'your-email@example.com';
```

On SQLite use `1` or `true` depending on your SQL client. After migration `20260404_0002`, the `is_admin` column exists on all new databases.

## Whitelist (Authorized Plates)

Base path: **`/api/v1/whitelist/`**. All operations require a valid **`Authorization: Bearer`** JWT (any authenticated user).

- **Normalization:** the server computes `normalized_plate` from the submitted text (strips non-alphanumeric characters, compares uppercase). The normalized value is **unique** — duplicate submissions return **409 Conflict**.
- **Formats:** Brazilian plates in **Mercosul** (e.g. `ABC1D23`) or **legacy** three letters + four digits (e.g. `ABC-1234`), validated by `validate_brazilian_plate` / `AuthorizedPlateCreate` schema.
- **Common errors:** **400** / **422** invalid format; **409** duplicate plate; **404** ID not found on GET/PUT/DELETE.

## Access Logs

| Operation | Authentication |
|-----------|----------------|
| Register attempt (`POST /api/v1/access_logs/`, multipart) | Header **`X-Device-Key`** matching `DEVICE_INGEST_KEY` (when set) |
| List records (`GET /api/v1/access_logs/`) | **`Authorization: Bearer`** — any authenticated user |
| Get image (`GET /api/v1/access_logs/images/{filename}`) | **`Authorization: Bearer`** from admin user (`is_admin`); otherwise **403** |

## Gate Control

`POST /api/v1/gate_control/trigger` — **`Authorization: Bearer`** from an administrator (`is_admin`).

- **`GATE_ACTUATOR_URL`:** when **not** set, the response has **`integration: "simulated"`** — no hardware command is sent.
- When set, the API **POST**s `{"action": "open"}` and only considers success on **HTTP 2xx** from the actuator (`integration: "live"`). Network or HTTP errors return **502**/**503** with explicit `detail`.
- **`GATE_ACTUATOR_TIMEOUT_SECONDS`** (optional, default 5): timeout in seconds.

## Devices (Bluetooth) — Demo

Routes under **`/api/v1/devices/`** (scan, connect, status, disconnect) are **simulation** for demos: each response includes **`demo: true`**.

- **`IOT_DEVICE_DEMO_API`:** in **`ENVIRONMENT=production`** / **`prod`** the default is **off** → **501** responses (real Bluetooth is in the **browser** via Web Bluetooth, not on this server).
- To enable explicitly: `IOT_DEVICE_DEMO_API=true` (or omit in development, where the default is on).

## Applied Principles

- **SOLID:** separation of concerns across layers (endpoints, controllers, repositories, schemas, models)
- **DRY:** shared utilities and functions
- **Modularity:** extensible structure
