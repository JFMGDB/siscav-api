"""merge alembic heads (security hardening + is_superadmin)

Revision ID: 20260605_0001
Revises: 20260602_0004, 20260604_0003
Create Date: 2026-06-05

"""

revision = "20260605_0001"
down_revision = ("20260602_0004", "20260604_0003")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
