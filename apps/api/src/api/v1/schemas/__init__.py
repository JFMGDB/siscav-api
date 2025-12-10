"""Schemas Pydantic - Validação e serialização de dados.

Este módulo contém os schemas Pydantic usados para validação de entrada
e serialização de saída da API.
"""

from apps.api.src.api.v1.schemas.access_log import AccessLogRead, AccessStatus
from apps.api.src.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)
from apps.api.src.api.v1.schemas.device import (
    BluetoothDevice,
    ConnectionRequest,
    ConnectionResponse,
    ConnectionStatus,
    DisconnectResponse,
)
from apps.api.src.api.v1.schemas.token import Token, TokenPayload
from apps.api.src.api.v1.schemas.user import UserCreate, UserRead

__all__ = [
    "UserCreate",
    "UserRead",
    "AuthorizedPlateCreate",
    "AuthorizedPlateRead",
    "AccessLogRead",
    "AccessStatus",
    "Token",
    "TokenPayload",
    "BluetoothDevice",
    "ConnectionRequest",
    "ConnectionResponse",
    "ConnectionStatus",
    "DisconnectResponse",
]

