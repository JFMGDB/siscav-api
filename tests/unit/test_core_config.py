"""Testes unitários para configuração da aplicação."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from apps.api.src.api.v1.core.config import (
    Settings,
    _resolve_database_url,
    assert_production_secrets_valid,
    get_settings,
)

# Limpar cache antes de cada teste
get_settings.cache_clear()


class TestResolveDatabaseUrl:
    """Testes para resolução de DATABASE_URL."""

    def test_resolve_explicit_database_url(self):
        """Testa que DATABASE_URL explícita tem prioridade."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:pass@host:5432/db"}):
            result = _resolve_database_url()
            assert result == "postgresql://test:pass@host:5432/db"

    def test_resolve_from_postgres_vars(self):
        """Testa resolução a partir de variáveis POSTGRES_*."""
        env_vars = {
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_DB": "testdb",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5433",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            # Remove DATABASE_URL se existir
            os.environ.pop("DATABASE_URL", None)
            result = _resolve_database_url()
            assert result == "postgresql+psycopg2://testuser:testpass@localhost:5433/testdb"

    def test_resolve_from_postgres_vars_default_host_port(self):
        """Testa resolução com host e porta padrão."""
        env_vars = {
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_DB": "testdb",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            os.environ.pop("DATABASE_URL", None)
            os.environ.pop("POSTGRES_HOST", None)
            os.environ.pop("POSTGRES_PORT", None)
            result = _resolve_database_url()
            assert result == "postgresql+psycopg2://testuser:testpass@db:5432/testdb"

    def test_resolve_fallback_sqlite(self):
        """Testa fallback para SQLite quando nenhuma variável está definida."""
        with patch.dict(os.environ, {}, clear=True):
            result = _resolve_database_url()
            assert result == "sqlite:///./siscav_dev.db"

    def test_resolve_priority_database_url_over_postgres_vars(self):
        """Testa que DATABASE_URL tem prioridade sobre POSTGRES_*."""
        env_vars = {
            "DATABASE_URL": "postgresql://explicit:pass@host:5432/db",
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_DB": "testdb",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            result = _resolve_database_url()
            assert result == "postgresql://explicit:pass@host:5432/db"


class TestSettings:
    """Testes para classe Settings."""

    def test_settings_default_values(self):
        """Testa valores padrão das configurações."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.secret_key == "change_me_in_development"
            assert settings.algorithm == "HS256"
            assert settings.access_token_expire_minutes == 15
            assert settings.refresh_token_expire_days == 30
            assert settings.database_url == "sqlite:///./siscav_dev.db"
            assert settings.environment == "development"
            assert settings.device_ingest_key is None

    def test_settings_from_env_vars(self):
        """Testa carregamento de configurações de variáveis de ambiente."""
        get_settings.cache_clear()
        env_vars = {
            "SECRET_KEY": "test_secret_key",
            "ALGORITHM": "RS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "60",
            "DATABASE_URL": "postgresql://test:pass@host:5432/db",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.secret_key == "test_secret_key"
            assert settings.algorithm == "RS256"
            assert settings.access_token_expire_minutes == 30
            assert settings.refresh_token_expire_days == 60
            assert settings.database_url == "postgresql://test:pass@host:5432/db"

    def test_settings_resolve_database_url_when_empty(self):
        """Testa que DATABASE_URL é resolvida quando vazia."""
        get_settings.cache_clear()
        env_vars = {
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_DB": "testdb",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            os.environ.pop("DATABASE_URL", None)
            settings = Settings()
            assert "postgresql+psycopg2://" in settings.database_url

    def test_get_settings_cached(self):
        """Testa que get_settings() retorna instância cached."""
        settings1 = get_settings()
        settings2 = get_settings()
        # Mesma instância devido ao @lru_cache
        assert settings1 is settings2


class TestAssertProductionSecretsValid:
    """Startup guard para SECRET_KEY em produção."""

    def test_no_op_in_development(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=False):
            assert_production_secrets_valid()

    def test_raises_when_production_and_default_secret(self):
        with patch.dict(
            os.environ,
            {"ENVIRONMENT": "production", "SECRET_KEY": "change_me_in_development"},
            clear=False,
        ):
            try:
                assert_production_secrets_valid()
            except RuntimeError as e:
                assert "SECRET_KEY" in str(e)
            else:
                raise AssertionError("expected RuntimeError")

    def test_import_main_fails_production_weak_secret_subprocess(self):
        root = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env["ENVIRONMENT"] = "production"
        env["SECRET_KEY"] = "change_me_in_development"
        env["PYTHONPATH"] = str(root)
        env.setdefault("DEVICE_INGEST_KEY", "subprocess-test-key")
        r = subprocess.run(
            [sys.executable, "-c", "import apps.api.src.main"],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0
        out = r.stderr + r.stdout
        assert "SECRET_KEY" in out or "RuntimeError" in out
