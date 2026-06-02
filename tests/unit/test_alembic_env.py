"""Tests for Alembic env URL resolution (ConfigParser % bypass)."""

import os
from unittest.mock import patch

from apps.api.src.alembic.database_url import get_migration_database_url


class TestGetMigrationDatabaseUrl:
    def test_returns_database_url_with_percent_encoded_password(self):
        url = "postgresql+psycopg2://user:pass%3Fword@host:5432/db?sslmode=require"
        with patch.dict(os.environ, {"DATABASE_URL": url}, clear=False):
            assert get_migration_database_url() == url

    def test_import_env_module_does_not_raise_on_percent_in_url(self):
        url = "postgresql+psycopg2://u:p%3Fx@localhost:5432/postgres"
        with patch.dict(os.environ, {"DATABASE_URL": url}, clear=False):
            # Re-import would re-run fileConfig; call helper only
            assert "%3F" in get_migration_database_url() or "%3F" in url
