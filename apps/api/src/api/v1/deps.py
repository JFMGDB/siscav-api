from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.crud import crud_user
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

settings = get_settings()


def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Obtém o usuário atual a partir do token JWT.

    Valida o token e retorna o usuário correspondente.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from error
    user = crud_user.get(db, id=UUID(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
