from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.v1.core import security
from app.api.v1.core.config import get_settings
from app.api.v1.core.rate_limit import rate_limit
from app.api.v1.crud import crud_user
from app.api.v1.db.session import get_db
from app.api.v1.schemas.token import Token, TokenPayload

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

    access_token = security.create_access_token(user_id, expires_delta=access_token_expires)
    refresh_token = security.create_refresh_token(user_id, expires_delta=refresh_token_expires)

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
@rate_limit("5/minute")
def login_access_token(
    request: Request,  # noqa: ARG001
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
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

    user = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return _create_token_pair(user.id)


@router.post("/login/refresh-token", response_model=Token)
def refresh_access_token(
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

    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return _create_token_pair(user.id)
