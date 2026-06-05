"""Configuração central da aplicação.

Resolução do DATABASE_URL (prioridade):
1. Se a variável de ambiente `DATABASE_URL` estiver definida (não vazia), ela é usada como está.
   - Ex.: `.env.local` — Supabase pooler session mode (`:5432`) com `sslmode=require`.
   - Ex.: `sqlite:///./siscav_dev.db` para desenvolvimento local explícito.
2. Caso contrário, se `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` estiverem
   presentes, a URL é montada com `POSTGRES_HOST` (padrão: `db`) e `POSTGRES_PORT` (5432).
3. Se nenhuma opção estiver disponível, levanta `RuntimeError` (sem fallback silencioso).

Em desenvolvimento, `.env` e `.env.local` na raiz do repositório (onde está `alembic.ini`)
são carregados automaticamente na importação deste módulo. Shell/Docker/`source` e
`run_migrations.sh` continuam válidos. Em produção (`ENVIRONMENT=production|prod`)
arquivos `.env` não são lidos — use variáveis da plataforma.
"""

import logging
import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[misc, assignment]

logger = logging.getLogger(__name__)

_SUPPORTED_VEHICLE_CLASSIFIER_BACKENDS = frozenset({"stub"})
_DEFAULT_BACKEND_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
)


def _find_repo_root() -> Path:
    """Repository root (directory containing alembic.ini)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "alembic.ini").is_file():
            return parent
    return Path.cwd()


def _load_dotenv_files() -> None:
    """Load .env then .env.local from repo root (non-production only)."""
    env = (os.getenv("ENVIRONMENT") or "development").strip().lower()
    if env in ("production", "prod"):
        return
    if load_dotenv is None:
        logger.debug("python-dotenv not installed; skipping .env file load")
        return
    root = _find_repo_root()
    for name, override in ((".env", False), (".env.local", True)):
        path = root / name
        if path.is_file():
            load_dotenv(path, override=override)


_load_dotenv_files()


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


def _read_backend_cors_origins() -> list[str]:
    raw = (os.getenv("BACKEND_CORS_ORIGINS") or "").strip()
    if not raw:
        return list(_DEFAULT_BACKEND_CORS_ORIGINS)
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or list(_DEFAULT_BACKEND_CORS_ORIGINS)


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

    msg = (
        "Database URL is not configured. Set DATABASE_URL (e.g. postgresql+psycopg2://... "
        "or sqlite:///./siscav_dev.db for local dev) or POSTGRES_USER, POSTGRES_PASSWORD, "
        "and POSTGRES_DB."
    )
    raise RuntimeError(msg)


def log_database_target(database_url: str) -> None:
    """Log dialect and host for startup diagnostics (never logs credentials)."""
    parsed = urlparse(database_url)
    dialect = parsed.scheme.split("+", 1)[0] if parsed.scheme else "unknown"
    host = parsed.hostname or "(local)"
    logger.info("Database target: dialect=%s host=%s", dialect, host)


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


def _read_gate_auto_open_on_authorize() -> bool:
    v = (os.getenv("GATE_AUTO_OPEN_ON_AUTHORIZE") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _read_gate_auto_open_timeout_seconds() -> float:
    raw = os.getenv("GATE_AUTO_OPEN_TIMEOUT_SECONDS", "2").strip()
    try:
        n = float(raw)
    except ValueError:
        return 2.0
    return max(1.5, min(n, 2.0))


def _read_vehicle_classifier_backend() -> str:
    """Vehicle classifier backend id (default: stub until a real model is integrated)."""
    raw = (os.getenv("VEHICLE_CLASSIFIER_BACKEND") or "stub").strip().lower()
    if not raw:
        return "stub"
    if raw not in _SUPPORTED_VEHICLE_CLASSIFIER_BACKENDS:
        logger.warning(
            "Unknown VEHICLE_CLASSIFIER_BACKEND=%r; falling back to stub",
            raw,
        )
        return "stub"
    return raw


def assert_production_secrets_valid() -> None:
    """Abort startup in production if secrets or database URL are misconfigured."""
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
    database_url = _resolve_database_url().strip().lower()
    if not database_url.startswith("postgresql"):
        msg = (
            "DATABASE_URL must be a PostgreSQL URL when ENVIRONMENT is production or prod "
            "(sqlite and other drivers are not allowed)"
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
    gate_auto_open_on_authorize: bool = Field(default_factory=_read_gate_auto_open_on_authorize)
    gate_auto_open_timeout_seconds: float = Field(
        default_factory=_read_gate_auto_open_timeout_seconds
    )
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
    vehicle_classifier_backend: str = Field(default_factory=_read_vehicle_classifier_backend)
    backend_cors_origins: list[str] = Field(default_factory=_read_backend_cors_origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
