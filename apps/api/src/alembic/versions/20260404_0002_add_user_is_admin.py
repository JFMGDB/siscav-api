"""add is_admin to users

Revision ID: 20260404_0002
Revises: 20251102_0001
Create Date: 2026-04-04

"""

import sqlalchemy as sa
from alembic import op

revision = "20260404_0002"
down_revision = "20251102_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
