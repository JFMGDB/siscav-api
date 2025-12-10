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

from pydantic import BaseModel


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


class Settings(BaseModel):
    """Configurações da aplicação carregadas de variáveis de ambiente.

    Observação: evitamos propositalmente usar pydantic-settings para manter as
    dependências de runtime mínimas.
    """

    database_url: str = _resolve_database_url()
    secret_key: str = os.getenv("SECRET_KEY", "change_me_in_development")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
