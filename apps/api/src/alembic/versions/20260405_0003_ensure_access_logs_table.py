"""Criar access_logs em bases onde falta (drift face a alembic_version).

Revision ID: 20260405_0003
Revises: 20260404_0002
Create Date: 2026-04-05

Cenário típico: SQLite com users/authorized_plates criados manualmente ou migração
incompleta, mas alembic_version já em head — listagem de logs falhava com
"no such table: access_logs".
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = "20260405_0003"
down_revision = "20260404_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "access_logs" in inspector.get_table_names():
        return

    is_postgresql = bind.dialect.name == "postgresql"
    uuid_type = postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(36)
    uuid_default = sa.text("gen_random_uuid()") if is_postgresql else None

    if is_postgresql:
        access_status = sa.Enum("Authorized", "Denied", name="access_status")
        access_status.create(bind, checkfirst=True)

    status_col = (
        sa.Enum("Authorized", "Denied", name="access_status") if is_postgresql else sa.String(20)
    )

    op.create_table(
        "access_logs",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            nullable=False,
            server_default=uuid_default,
        ),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("plate_string_detected", sa.Text(), nullable=False),
        sa.Column("status", status_col, nullable=False),
        sa.Column("image_storage_key", sa.Text(), nullable=False),
        sa.Column(
            "authorized_plate_id",
            uuid_type,
            sa.ForeignKey("authorized_plates.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "access_logs" not in inspector.get_table_names():
        return
    op.drop_table("access_logs")
