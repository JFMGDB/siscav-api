"""Endpoints para autenticação de usuários."""

from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.limiter import limiter
from apps.api.src.api.v1.core.security import create_access_token, create_refresh_token
from apps.api.src.api.v1.deps import get_auth_controller, get_db
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.password_reset import (
    PasswordResetConfirm,
    PasswordResetConfirmed,
    PasswordResetRequest,
    PasswordResetRequested,
)
from apps.api.src.api.v1.schemas.token import Token, TokenPayload
from apps.api.src.api.v1.schemas.user import UserCreate, UserRead

router = APIRouter()
settings = get_settings()


def _create_token_pair(user_id: UUID) -> Token:
    """Cria um par de tokens (access e refresh) para um usuário.

    Função auxiliar para evitar duplicação de código entre login e refresh
    endpoints (princípio DRY).

    Args:
        user_id: ID do usuário.

    Returns:
        Token contendo access_token e refresh_token.
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

    access_token = create_access_token(user_id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user_id, expires_delta=refresh_token_expires)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


def _validate_and_decode_refresh_token(token: str) -> TokenPayload:
    """Valida e decodifica um refresh token.

    Função auxiliar para centralizar a lógica de validação de refresh tokens
    (princípio DRY e Single Responsibility).

    Args:
        token: Refresh token JWT como string.

    Returns:
        TokenPayload com os dados do token decodificado.

    Raises:
        HTTPException: Se o token for inválido, expirado ou de tipo incorreto.
    """
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token cannot be empty",
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate refresh token",
        ) from error

    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type",
        )

    if not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate refresh token",
        )

    return token_data


@router.post("/login/access-token", response_model=Token)
@limiter.limit("5/minute")
def login_access_token(
    request: Request,  # noqa: ARG001
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> Token:
    """
    OAuth2 compatible token login, get an access token and refresh token for future requests.

    Protegido por rate limiting: máximo de 5 tentativas por minuto por IP
    para prevenir ataques de força bruta.
    """
    # Valida que username e password não estão vazios
    if not form_data.username or not form_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cannot be empty",
        )
    if not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be empty",
        )

    user = auth_controller.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return _create_token_pair(user.id)


@router.post("/login/refresh-token", response_model=Token)
@limiter.limit("5/minute")
def refresh_access_token(
    request: Request,  # noqa: ARG001
    refresh_token: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """
    Renova o token de acesso usando um refresh token válido.

    Recebe um refresh token e retorna um novo par de access token e refresh token.
    """
    # Valida e decodifica o refresh token
    token_data = _validate_and_decode_refresh_token(refresh_token)

    # Converte sub para UUID e verifica se o usuário existe
    try:
        user_id = UUID(token_data.sub)
    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user ID in token",
        ) from error

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return _create_token_pair(user.id)


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequested,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
def password_reset_request(
    request: Request,  # noqa: ARG001
    body: PasswordResetRequest,
    auth_controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> PasswordResetRequested:
    """
    Pedido de redefinição de senha.

    Por segurança, a mensagem de resposta é **idêntica** quer o email exista ou não.
    O campo `reset_token` só é preenchido quando `PASSWORD_RESET_EXPOSE_TOKEN_IN_RESPONSE`
    está ativo (padrão: desligado em produção); caso contrário o integrador deve enviar
    o token por email ou outro canal seguro.
    """
    token, message = auth_controller.request_password_reset(body.email)
    expose = settings.password_reset_expose_token_in_response
    return PasswordResetRequested(
        message=message,
        reset_token=token if expose and token else None,
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetConfirmed,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
def password_reset_confirm(
    request: Request,  # noqa: ARG001
    body: PasswordResetConfirm,
    auth_controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> PasswordResetConfirmed:
    """Confirma nova senha com o JWT devolvido pelo fluxo de pedido (`type`: password_reset)."""
    auth_controller.confirm_password_reset(body.token, body.new_password)
    return PasswordResetConfirmed()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")  # Temporariamente aumentado para testes
def register(
    request: Request,  # noqa: ARG001
    user_data: UserCreate,
    auth_controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> UserRead:
    """
    Registra um novo usuário no sistema.

    Cria uma nova conta de usuário com email e senha.
    O email deve ser único e a senha deve ter no mínimo 8 caracteres.

    **Rate Limiting:** Máximo de 100 tentativas por minuto por IP (temporariamente aumentado para testes)
    para prevenir criação de contas em massa.

    **Validações:**
    - Email deve ser válido e único
    - Senha deve ter no mínimo 8 caracteres

    **Resposta:**
    - Retorna os dados do usuário criado (sem senha)
    - Status 201 Created em caso de sucesso
    - Status 409 Conflict se o email já estiver em uso
    """
    return auth_controller.register_user(user_data)
