"""
DEPRECATED: Este módulo está obsoleto.

Use os novos repositories e controllers:
- Para acesso a dados: `apps.api.src.api.v1.repositories.user_repository.UserRepository`
- Para lógica de negócio: `apps.api.src.api.v1.controllers.auth_controller.AuthController`

Este módulo será removido em uma versão futura.
"""

import warnings
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.security import get_password_hash, verify_password
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.user import UserCreate

warnings.warn(
    "crud_user está deprecated. Use UserRepository e AuthController.",
    DeprecationWarning,
    stacklevel=2,
)


def get(db: Session, id: UUID) -> Optional[User]:
    return db.scalar(select(User).where(User.id == id))


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email))


def create(db: Session, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    user = get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
