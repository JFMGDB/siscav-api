from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

import apps.api.src.api.v1.models.access_log as _models_access_log
import apps.api.src.api.v1.models.authorized_plate as _models_authorized_plate
import apps.api.src.api.v1.models.user as _models_user
from apps.api.src.alembic.database_url import get_migration_database_url
from apps.api.src.api.v1.db.base import Base

# Objeto de configuração do Alembic; provê acesso aos valores do .ini (logging only).
config = context.config

# Referências para evitar remoção por linters e assegurar import dos modelos
_ = (_models_user, _models_authorized_plate, _models_access_log)

target_metadata = Base.metadata

# Interpreta o arquivo de configuração para logging em Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    url = get_migration_database_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_migration_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
