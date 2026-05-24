# Database Documentation

Documentation for the SISCAV data model and migrations.

## Available Documents

### [Data Model](./data-model.md)

Complete technical specification of the data model, including:

- Core entities (`users`, `authorized_plates`, `access_logs`)
- Architectural decisions (UUIDs, TIMESTAMPTZ, ENUMs)
- PostgreSQL DDL
- Indexing and referential integrity strategies
- Scalability considerations

### [Supabase Migration](./supabase-migration.md)

Manual migration guide when Docker/Alembic is not available:

- Required extensions
- ENUM types
- Tables and indexes
- Alembic integration

## Description

The SISCAV PostgreSQL database is designed for:

- **Security:** UUID primary keys
- **Consistency:** ENUM types for data integrity
- **Auditability:** timezone-aware timestamps (TIMESTAMPTZ)
- **Performance:** optimized indexes for frequent queries
- **Scalability:** support for future partitioning and extensions

## Core Entities

- **users:** system administrators
- **authorized_plates:** authorized plate whitelist
- **access_logs:** audit trail of access attempts

## SQL Scripts

Manual migration scripts are in `db/sql/supabase/`:

- `01_enable_extensions.sql` (pgcrypto, pg_trgm)
- `02_types.sql` (ENUM `access_status`)
- `03_tables.sql` (`users`, `authorized_plates`, `access_logs`)
- `04_indexes.sql` (recommended and optional pg_trgm indexes)

## References

- [API Documentation](../api/README.md)
- [Architecture Documentation](../architecture/README.md)
