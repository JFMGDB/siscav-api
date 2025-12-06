"""Dependências do FastAPI para injeção de dependências.

Este módulo centraliza todas as dependências reutilizáveis da aplicação,
seguindo o padrão DRY e facilitando testes e manutenção.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.controllers.plate_controller import PlateController
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token"
)

settings = get_settings()


def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Dependência para obter o usuário autenticado atual.

    Valida o token JWT e retorna o usuário correspondente.
    Se o token for inválido ou o usuário não existir, levanta HTTPException.

    Args:
        token: Token JWT do header Authorization
        db: Sessão do banco de dados

    Returns:
        User: Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = UserRepository.get_by_id(db, UUID(token_data.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_plate_controller(
    db: Annotated[Session, Depends(get_db)],
) -> PlateController:
    """
    Dependência para obter uma instância de PlateController.

    Args:
        db: Sessão do banco de dados

    Returns:
        PlateController: Instância do controller de placas
    """
    return PlateController(db)


def get_access_log_controller(
    db: Annotated[Session, Depends(get_db)],
) -> AccessLogController:
    """
    Dependência para obter uma instância de AccessLogController.

    Args:
        db: Sessão do banco de dados

    Returns:
        AccessLogController: Instância do controller de logs de acesso
    """
    return AccessLogController(db)


def get_auth_controller(
    db: Annotated[Session, Depends(get_db)],
) -> AuthController:
    """
    Dependência para obter uma instância de AuthController.

    Args:
        db: Sessão do banco de dados

    Returns:
        AuthController: Instância do controller de autenticação
    """
    return AuthController(db)


def get_gate_controller() -> GateController:
    """
    Dependência para obter uma instância de GateController.

    Nota: GateController não requer sessão de banco de dados,
    pois apenas orquestra comunicação com dispositivos IoT.

    Returns:
        GateController: Instância do controller de controle de portão
    """
    return GateController()


def get_device_controller() -> "DeviceController":
    """
    Dependência para obter uma instância de DeviceController.

    Nota: DeviceController não requer sessão de banco de dados,
    pois apenas orquestra operações de dispositivos IoT (simuladas).

    Returns:
        DeviceController: Instância do controller de dispositivos
    """
    from apps.api.src.api.v1.controllers.device_controller import DeviceController

    return DeviceController()
