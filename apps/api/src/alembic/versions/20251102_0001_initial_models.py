"""Modelos iniciais: users, authorized_plates, access_logs e ENUM access_status

Revision ID: 20251102_0001
Revises:
Create Date: 2025-11-02 00:00:00

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Identificadores de revisão, usados pelo Alembic.
revision = "20251102_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Cria o tipo ENUM para o status de acesso (PostgreSQL)
    access_status = sa.Enum("Authorized", "Denied", name="access_status")
    access_status.create(op.get_bind(), checkfirst=True)

    # Tabela users
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Tabela authorized_plates
    op.create_table(
        "authorized_plates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("plate", sa.Text(), nullable=False),
        sa.Column("normalized_plate", sa.Text(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Tabela access_logs
    op.create_table(
        "access_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("plate_string_detected", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("Authorized", "Denied", name="access_status"), nullable=False),
        sa.Column("image_storage_key", sa.Text(), nullable=False),
        sa.Column(
            "authorized_plate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("authorized_plates.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("access_logs")
    op.drop_table("authorized_plates")
    op.drop_table("users")

    # Remove o tipo ENUM
    access_status = sa.Enum("Authorized", "Denied", name="access_status")
    access_status.drop(op.get_bind(), checkfirst=True)
