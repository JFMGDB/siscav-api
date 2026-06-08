"""add is_superadmin to users

Revision ID: 20260604_0003
Revises: 20260404_0002
Create Date: 2026-06-04

"""

import sqlalchemy as sa
from alembic import op

revision = "20260604_0003"
down_revision = "20260404_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "is_superadmin" not in {col["name"] for col in inspector.get_columns("users")}:
        op.add_column(
            "users",
            sa.Column(
                "is_superadmin",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )


def downgrade() -> None:
    op.drop_column("users", "is_superadmin")
