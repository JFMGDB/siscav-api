"""Repositories - Camada de acesso a dados (Data Access Layer).

Esta camada é responsável apenas por operações de banco de dados,
seguindo o princípio de Single Responsibility (SOLID).
"""

from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.repositories.user_repository import UserRepository

__all__ = [
    "UserRepository",
    "AuthorizedPlateRepository",
    "AccessLogRepository",
]

