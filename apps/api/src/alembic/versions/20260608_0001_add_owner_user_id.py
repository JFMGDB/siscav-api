"""add owner_user_id to access_logs and ocr_attempts for per-user metrics

Revision ID: 20260608_0001
Revises: 20260605_0003
Create Date: 2026-06-08

"""

import sqlalchemy as sa
from alembic import op

revision = "20260608_0001"
down_revision = "20260605_0003"
branch_labels = None
depends_on = None


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    if "owner_user_id" not in _column_names("access_logs"):
        op.add_column(
            "access_logs",
            sa.Column("owner_user_id", sa.Uuid(), nullable=True),
        )
        op.create_foreign_key(
            "fk_access_logs_owner_user_id_users",
            "access_logs",
            "users",
            ["owner_user_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_access_logs_owner_user_id", "access_logs", ["owner_user_id"])

    if "owner_user_id" not in _column_names("ocr_attempts"):
        op.add_column(
            "ocr_attempts",
            sa.Column("owner_user_id", sa.Uuid(), nullable=True),
        )
        op.create_foreign_key(
            "fk_ocr_attempts_owner_user_id_users",
            "ocr_attempts",
            "users",
            ["owner_user_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_ocr_attempts_owner_user_id", "ocr_attempts", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index("ix_ocr_attempts_owner_user_id", table_name="ocr_attempts")
    op.drop_constraint("fk_ocr_attempts_owner_user_id_users", "ocr_attempts", type_="foreignkey")
    op.drop_column("ocr_attempts", "owner_user_id")

    op.drop_index("ix_access_logs_owner_user_id", table_name="access_logs")
    op.drop_constraint("fk_access_logs_owner_user_id_users", "access_logs", type_="foreignkey")
    op.drop_column("access_logs", "owner_user_id")
