from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core import security
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.crud import crud_user
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.schemas.token import Token

router = APIRouter()
settings = get_settings()


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = security.create_access_token(user.id, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
