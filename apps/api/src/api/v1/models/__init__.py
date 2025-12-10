"""Modelos SQLAlchemy - Definição das entidades do banco de dados.

Este módulo contém os modelos ORM que representam as tabelas do banco de dados.
"""

from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.models.user import User

__all__ = [
    "User",
    "AuthorizedPlate",
    "AccessLog",
]

