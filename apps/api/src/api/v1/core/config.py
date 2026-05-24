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

from pydantic import BaseModel, Field


def _read_secret_key() -> str:
    return os.getenv("SECRET_KEY", "change_me_in_development")


def _read_algorithm() -> str:
    return os.getenv("ALGORITHM", "HS256")


def _read_access_token_expire_minutes() -> int:
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


def _read_refresh_token_expire_days() -> int:
    return int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))


def _read_password_reset_token_expire_minutes() -> int:
    return int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "60"))


def _read_password_reset_expose_token_in_response() -> bool:
    """Em produção, não devolver o token no JSON (use email ou canal seguro)."""
    explicit = os.getenv("PASSWORD_RESET_EXPOSE_TOKEN_IN_RESPONSE")
    if explicit is not None and explicit.strip() != "":
        return explicit.strip().lower() in ("1", "true", "yes", "on")
    env = _read_environment()
    return env not in ("production", "prod")


def _read_upload_dir() -> str:
    return os.getenv("UPLOAD_DIR", "uploads")


def _read_max_file_size_mb() -> int:
    return int(os.getenv("MAX_FILE_SIZE_MB", "10"))


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


def _read_environment() -> str:
    v = (os.getenv("ENVIRONMENT") or "development").strip().lower()
    return v if v else "development"


def _read_device_ingest_key() -> str | None:
    v = (os.getenv("DEVICE_INGEST_KEY") or "").strip()
    return v if v else None


def _read_gate_actuator_url() -> str | None:
    v = (os.getenv("GATE_ACTUATOR_URL") or "").strip()
    return v if v else None


def _read_gate_actuator_timeout_seconds() -> int:
    raw = os.getenv("GATE_ACTUATOR_TIMEOUT_SECONDS", "5").strip()
    try:
        n = int(raw)
    except ValueError:
        return 5
    return max(1, min(n, 120))


def _read_iot_device_demo_api() -> bool:
    """Demo Bluetooth HTTP API: off by default in production."""
    explicit = os.getenv("IOT_DEVICE_DEMO_API")
    if explicit is not None and explicit.strip() != "":
        return explicit.strip().lower() in ("1", "true", "yes", "on")
    env = _read_environment()
    return env not in ("production", "prod")


def assert_production_secrets_valid() -> None:
    """Abort startup in production if JWT signing secret is missing or default."""
    env = (os.getenv("ENVIRONMENT") or "development").strip().lower()
    if env not in ("production", "prod"):
        return
    sk = (os.getenv("SECRET_KEY") or "").strip()
    if not sk or sk == "change_me_in_development":
        msg = (
            "SECRET_KEY must be set to a strong, non-default value when "
            "ENVIRONMENT is production or prod"
        )
        raise RuntimeError(msg)


class Settings(BaseModel):
    """Configurações da aplicação carregadas de variáveis de ambiente.

    Observação: evitamos propositalmente usar pydantic-settings para manter as
    dependências de runtime mínimas.
    """

    database_url: str = Field(default_factory=_resolve_database_url)
    environment: str = Field(default_factory=_read_environment)
    device_ingest_key: str | None = Field(default_factory=_read_device_ingest_key)
    gate_actuator_url: str | None = Field(default_factory=_read_gate_actuator_url)
    gate_actuator_timeout_seconds: int = Field(default_factory=_read_gate_actuator_timeout_seconds)
    iot_device_demo_api: bool = Field(default_factory=_read_iot_device_demo_api)
    secret_key: str = Field(default_factory=_read_secret_key)
    algorithm: str = Field(default_factory=_read_algorithm)
    access_token_expire_minutes: int = Field(default_factory=_read_access_token_expire_minutes)
    refresh_token_expire_days: int = Field(default_factory=_read_refresh_token_expire_days)
    password_reset_token_expire_minutes: int = Field(
        default_factory=_read_password_reset_token_expire_minutes
    )
    password_reset_expose_token_in_response: bool = Field(
        default_factory=_read_password_reset_expose_token_in_response
    )
    upload_dir: str = Field(default_factory=_read_upload_dir)
    max_file_size_mb: int = Field(default_factory=_read_max_file_size_mb)


@lru_cache
def get_settings() -> Settings:
    return Settings()
