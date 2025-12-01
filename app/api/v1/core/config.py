"""Configuração central da aplicação.

Resolução do DATABASE_URL (prioridade):
1. Se a variável de ambiente `DATABASE_URL` estiver definida, ela é usada como está.
   - Ex.: `.env.supabase` define um `DATABASE_URL` do Supabase com `sslmode=require`.
   - Ex.: `.env.local` também pode definir `DATABASE_URL` apontando para o serviço Docker `db`.
2. Caso contrário, se `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` estiverem
   presentes, a URL é montada automaticamente usando `POSTGRES_HOST` (padrão: `db`) e
   `POSTGRES_PORT` (padrão: `5432`).
   - Ex.: ambiente Docker local com profile `local`.
3. Caso nenhuma das opções acima esteja disponível, usa-se um fallback local SQLite
   (`sqlite:///./siscav_dev.db`) útil para execuções bare sem `.env` e sem Docker.

Esse comportamento permite alternar entre Supabase, Postgres local (Docker) e um
fallback de desenvolvimento sem alterar código.
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_database_url() -> str:
    """Resolve a URL do banco de dados conforme prioridades documentadas.

    Retorna uma URL compatível com SQLAlchemy.
    """
    # Prioridade 1: `DATABASE_URL` explícita
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Prioridade 2: montar a partir de variáveis POSTGRES_* quando disponíveis (dev/local)
    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")
    pg_db = os.getenv("POSTGRES_DB")
    if pg_user and pg_password and pg_db:
        pg_host = os.getenv("POSTGRES_HOST", "db")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        return f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

    # Fallback: SQLite para execuções locais simples (sem Docker/.env)
    return "sqlite:///./siscav_dev.db"


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = ""
    secret_key: str = "change_me_in_development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    upload_dir: str = str(Path.cwd() / "uploads")

    @model_validator(mode="before")
    @classmethod
    def resolve_database_url(cls, data: dict) -> dict:
        """Resolve DATABASE_URL usando a lógica de prioridades.

        Se DATABASE_URL não estiver definido ou estiver vazio, resolve
        automaticamente usando a função _resolve_database_url().
        """
        if isinstance(data, dict) and not data.get("database_url"):
            data["database_url"] = _resolve_database_url()
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
