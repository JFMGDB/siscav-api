"""add ocr_attempts table for ML recognize-plate metrics

Revision ID: 20260605_0003
Revises: 20260605_0002
Create Date: 2026-06-05

"""

import sqlalchemy as sa
from alembic import op

revision = "20260605_0003"
down_revision = "20260605_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ocr_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocr_attempts_timestamp", "ocr_attempts", ["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_ocr_attempts_timestamp", table_name="ocr_attempts")
    op.drop_table("ocr_attempts")
