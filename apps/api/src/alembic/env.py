from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import apps.api.src.api.v1.models.access_log as _models_access_log
import apps.api.src.api.v1.models.authorized_plate as _models_authorized_plate
import apps.api.src.api.v1.models.user as _models_user
from apps.api.src.api.v1.db.base import Base

# Objeto de configuração do Alembic; provê acesso aos valores do .ini
config = context.config

# Sobrescreve sqlalchemy.url usando as configurações da aplicação ou variáveis de ambiente
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    from apps.api.src.api.v1.core.config import get_settings

    config.set_main_option("sqlalchemy.url", get_settings().database_url)

# Interpreta o arquivo de configuração para logging em Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Referências para evitar remoção por linters e assegurar import dos modelos
_ = (_models_user, _models_authorized_plate, _models_access_log)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
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


