"""Database URL resolution for Alembic (no ConfigParser / ini interpolation)."""

from __future__ import annotations

import os

from apps.api.src.api.v1.core.config import get_settings


def get_migration_database_url() -> str:
    """Resolve DB URL with same priority as the application."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    return get_settings().database_url
