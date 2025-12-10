"""Testes unitários para módulo de configuração."""

import os
from unittest.mock import patch

import pytest

from apps.api.src.api.v1.core.config import Settings, _resolve_database_url, get_settings


class TestResolveDatabaseUrl:
    """Testes para resolução da URL do banco de dados."""

    def test_resolve_database_url_from_env(self):
        """Testa resolução quando DATABASE_URL está definida."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"}):
            url = _resolve_database_url()
            assert url == "postgresql://test:test@localhost/test"

    def test_resolve_database_url_from_postgres_vars(self):
        """Testa resolução a partir de variáveis POSTGRES_*."""
        env_vars = {
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_pass",
            "POSTGRES_DB": "test_db",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            url = _resolve_database_url()
            assert "test_user" in url
            assert "test_pass" in url
            assert "test_db" in url
            assert "postgresql" in url

    def test_resolve_database_url_from_postgres_vars_with_custom_host(self):
        """Testa resolução com host customizado."""
        env_vars = {
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "pass",
            "POSTGRES_DB": "db",
            "POSTGRES_HOST": "custom_host",
            "POSTGRES_PORT": "5433",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            url = _resolve_database_url()
            assert "custom_host" in url
            assert "5433" in url

    def test_resolve_database_url_fallback_to_sqlite(self):
        """Testa fallback para SQLite quando nenhuma variável está definida."""
        with patch.dict(os.environ, {}, clear=True):
            url = _resolve_database_url()
            assert "sqlite" in url.lower()

    def test_resolve_database_url_priority_database_url(self):
        """Testa que DATABASE_URL tem prioridade sobre POSTGRES_*."""
        env_vars = {
            "DATABASE_URL": "postgresql://priority:pass@host/db",
            "POSTGRES_USER": "ignored",
            "POSTGRES_PASSWORD": "ignored",
            "POSTGRES_DB": "ignored",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            url = _resolve_database_url()
            assert url == "postgresql://priority:pass@host/db"


class TestSettings:
    """Testes para a classe Settings."""

    def test_settings_default_values(self):
        """Testa valores padrão das configurações."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.secret_key == "change_me_in_development"
            assert settings.algorithm == "HS256"
            assert settings.access_token_expire_minutes == 15
            assert settings.refresh_token_expire_days == 30
            assert settings.upload_dir == "uploads"
            assert settings.max_file_size_mb == 10

    def test_settings_from_env(self):
        """Testa carregamento de configurações do ambiente."""
        from apps.api.src.api.v1.core.config import get_settings
        
        env_vars = {
            "SECRET_KEY": "test_secret",
            "ALGORITHM": "HS512",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "60",
            "UPLOAD_DIR": "custom_uploads",
            "MAX_FILE_SIZE_MB": "20",
        }
        # Limpar cache do lru_cache
        get_settings.cache_clear()
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.secret_key == "test_secret"
            assert settings.algorithm == "HS512"
            assert settings.access_token_expire_minutes == 30
            assert settings.refresh_token_expire_days == 60
            assert settings.upload_dir == "custom_uploads"
            assert settings.max_file_size_mb == 20
        # Limpar cache novamente
        get_settings.cache_clear()

    def test_get_settings_cached(self):
        """Testa que get_settings retorna instância cached."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

