"""Endpoints para autenticação de usuários."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.core.limiter import limiter
from apps.api.src.api.v1.deps import get_auth_controller
from apps.api.src.api.v1.schemas.token import Token

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
@limiter.limit("5/minute")
def login_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> Token:
    """
    Login OAuth2 para obter token de acesso.

    Valida as credenciais do usuário (email e senha) e retorna um token JWT para acesso aos endpoints protegidos.
    
    **Rate Limiting:** Máximo de 5 tentativas por minuto por IP para prevenir ataques de força bruta.

    Args:
        request: Objeto Request do FastAPI (usado para rate limiting)
        form_data: Credenciais do usuário (email e senha)
        auth_controller: Controller de autenticação injetado via dependency injection

    Returns:
        Token: Token JWT de acesso

    Raises:
        HTTPException: Se as credenciais forem inválidas ou rate limit excedido
    """
    user = auth_controller.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    access_token = auth_controller.create_access_token_for_user(user)
    return Token(access_token=access_token, token_type="bearer")
