"""Dependências do FastAPI para injeção de dependências.

Este módulo centraliza todas as dependências reutilizáveis da aplicação,
seguindo o padrão DRY e facilitando testes e manutenção.
"""

import logging
import secrets as std_secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.controllers.device_controller import DeviceController
from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.controllers.plate_controller import PlateController
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.token import TokenPayload

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

settings = get_settings()

device_ingest_header = APIKeyHeader(name="X-Device-Key", auto_error=False)


def verify_device_ingest_key(
    x_device_key: Annotated[str | None, Security(device_ingest_header)],
) -> None:
    """Valida chave de ingestão de dispositivos (access logs)."""
    s = get_settings()
    key = s.device_ingest_key
    if key:
        if not x_device_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        if len(x_device_key) != len(key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        if not std_secrets.compare_digest(
            x_device_key.encode("utf-8"),
            key.encode("utf-8"),
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return
    env_lower = s.environment.strip().lower()
    if env_lower in ("development", "dev", ""):
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


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
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        logger.warning("Token validation failed: %s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None

    # Validar que é um token de acesso (não refresh)
    if token_data.type != "access":
        logger.warning("Invalid token type: %s (expected 'access')", token_data.type)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type. Use access token for authenticated requests.",
        )

    if not token_data.sub:
        logger.warning("Token missing 'sub' field")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    try:
        user_id = UUID(token_data.sub)
    except (ValueError, TypeError) as e:
        logger.exception(
            "Invalid user ID format in token: %s - %s",
            token_data.sub,
            type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user ID in token",
        ) from e

    logger.debug("Looking up user with ID: %s", user_id)
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        # Log adicional para debug: verificar se há usuários no banco
        user_count = db.query(User).count()
        logger.error(
            "User not found: ID=%s (sub=%s). Total users in database: %s",
            user_id,
            token_data.sub,
            user_count,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    logger.debug("User authenticated: %s (ID: %s)", user.email, user.id)
    return user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Usuário autenticado com privilégios de administrador."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required",
        )
    return current_user


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
    return GateController(get_settings())


def verify_device_demo_api_enabled() -> None:
    """Bloqueia rotas de demo de dispositivos quando desativadas (produção por padrão)."""
    if not get_settings().iot_device_demo_api:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "API de demonstração de dispositivos desativada (IOT_DEVICE_DEMO_API). "
                "Bluetooth real é feito no navegador via Web Bluetooth, não neste servidor."
            ),
        )


def get_device_controller() -> DeviceController:
    """
    Dependência para obter uma instância de DeviceController.

    Nota: DeviceController não requer sessão de banco de dados,
    pois apenas orquestra operações de dispositivos IoT (simuladas).

    Returns:
        DeviceController: Instância do controller de dispositivos
    """
    return DeviceController()
