"""add is_automatic and ocr_success to access_logs

Revision ID: 20260605_0002
Revises: 20260605_0001
Create Date: 2026-06-05

"""

import sqlalchemy as sa
from alembic import op

revision = "20260605_0002"
down_revision = "20260605_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "access_logs",
        sa.Column("is_automatic", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "access_logs",
        sa.Column("ocr_success", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute(
        """
        UPDATE access_logs
        SET is_automatic = (status = 'Authorized' AND authorized_plate_id IS NOT NULL)
        """
    )
    op.alter_column("access_logs", "is_automatic", server_default=None)
    op.alter_column("access_logs", "ocr_success", server_default=None)


def downgrade() -> None:
    op.drop_column("access_logs", "ocr_success")
    op.drop_column("access_logs", "is_automatic")
