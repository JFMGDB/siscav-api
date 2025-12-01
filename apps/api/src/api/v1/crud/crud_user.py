from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.security import get_password_hash, verify_password
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.user import UserCreate


def get(db: Session, id: UUID) -> User | None:
    return db.scalar(select(User).where(User.id == id))


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create(db: Session, obj_in: UserCreate) -> User:
    """Cria um novo usuário.

    Args:
        db: Sessão do banco de dados.
        obj_in: Dados do usuário a ser criado.

    Returns:
        User: Instância do usuário criado.

    Raises:
        ValueError: Se o email já existe no banco de dados.
    """
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
    )
    db.add(db_obj)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        error_msg = f"Email {obj_in.email} is already in use"
        raise ValueError(error_msg) from error
    db.refresh(db_obj)
    return db_obj


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
