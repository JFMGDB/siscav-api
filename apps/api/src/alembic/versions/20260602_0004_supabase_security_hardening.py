"""Supabase security hardening: RLS, revoke API roles, pg_trgm in extensions.

Revision ID: 20260602_0004
Revises: 20260405_0003
Create Date: 2026-06-02

PostgreSQL/Supabase only. Mirrors db/sql/supabase/05_security_hardening.sql.
"""

from alembic import op

revision = "20260602_0004"
down_revision = "20260405_0003"
branch_labels = None
depends_on = None

_UPGRADE_STATEMENTS = (
    "REVOKE ALL ON TABLE public.users FROM anon, authenticated",
    "REVOKE ALL ON TABLE public.authorized_plates FROM anon, authenticated",
    "REVOKE ALL ON TABLE public.access_logs FROM anon, authenticated",
    "REVOKE ALL ON TABLE public.alembic_version FROM anon, authenticated",
    "ALTER TABLE public.users ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.authorized_plates ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.access_logs ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY",
    "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
    "REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM anon, authenticated, service_role",
    "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
    "REVOKE EXECUTE ON FUNCTIONS FROM anon, authenticated, service_role",
    "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
    "REVOKE USAGE, SELECT ON SEQUENCES FROM anon, authenticated, service_role",
    "CREATE SCHEMA IF NOT EXISTS extensions",
    "DROP INDEX IF EXISTS public.idx_access_logs_plate_trgm",
    "ALTER EXTENSION pg_trgm SET SCHEMA extensions",
    "CREATE INDEX IF NOT EXISTS idx_access_logs_plate_trgm "
    "ON public.access_logs USING GIN (plate_string_detected extensions.gin_trgm_ops)",
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    for statement in _UPGRADE_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("ALTER TABLE public.users DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.authorized_plates DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.access_logs DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.alembic_version DISABLE ROW LEVEL SECURITY")
