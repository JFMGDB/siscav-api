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


def _get_uuid_type():
    """Retorna o tipo de UUID apropriado baseado no banco de dados."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.UUID(as_uuid=True)
    else:
        # SQLite e outros: usar String(36)
        return sa.String(36)


def _get_uuid_default():
    """Retorna o default apropriado para UUID baseado no banco de dados."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("gen_random_uuid()")
    else:
        # SQLite não tem função nativa, será gerado pelo Python
        return None


def upgrade() -> None:
    # Detecta o tipo de banco de dados
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"
    
    # Cria o tipo ENUM para o status de acesso (apenas PostgreSQL)
    if is_postgresql:
        access_status = sa.Enum("Authorized", "Denied", name="access_status")
        access_status.create(bind, checkfirst=True)

    # Tabela users
    uuid_type = _get_uuid_type()
    uuid_default = _get_uuid_default()
    
    op.create_table(
        "users",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            nullable=False,
            server_default=uuid_default,
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
            uuid_type,
            primary_key=True,
            nullable=False,
            server_default=uuid_default,
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
        sa.Column(
            "status",
            sa.Enum("Authorized", "Denied", name="access_status") if is_postgresql else sa.String(20),
            nullable=False,
        ),
        sa.Column("image_storage_key", sa.Text(), nullable=False),
        sa.Column(
            "authorized_plate_id",
            uuid_type,
            sa.ForeignKey("authorized_plates.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("access_logs")
    op.drop_table("authorized_plates")
    op.drop_table("users")

    # Remove o tipo ENUM (apenas PostgreSQL)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        access_status = sa.Enum("Authorized", "Denied", name="access_status")
        access_status.drop(bind, checkfirst=True)
