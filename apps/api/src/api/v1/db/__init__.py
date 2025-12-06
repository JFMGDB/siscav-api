"""Configuração do banco de dados - SQLAlchemy setup.

Este módulo contém a configuração base do SQLAlchemy, incluindo
a base declarativa e a sessão do banco de dados.
"""

from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.db.session import SessionLocal, engine, get_db

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
]

