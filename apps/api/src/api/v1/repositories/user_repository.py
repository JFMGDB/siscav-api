"""Repository para operações de acesso a dados de usuários."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.user import UserCreate


class UserRepository:
    """Repository para operações de banco de dados relacionadas a usuários."""

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> User | None:
        """
        Busca um usuário por ID.

        Args:
            db: Sessão do banco de dados
            user_id: ID único do usuário

        Returns:
            User se encontrado, None caso contrário
        """
        return db.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        """
        Busca um usuário por email.

        Args:
            db: Sessão do banco de dados
            email: Email do usuário

        Returns:
            User se encontrado, None caso contrário
        """
        # Usar query() diretamente para melhor compatibilidade
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user_data: UserCreate, hashed_password: str) -> User:
        """
        Cria um novo usuário no banco de dados.

        Args:
            db: Sessão do banco de dados
            user_data: Dados do usuário (schema Pydantic)
            hashed_password: Senha já hasheada

        Returns:
            User criado
        """
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
        except Exception:
            db.rollback()
            raise
        return db_user

    @staticmethod
    def update_password_hash(db: Session, user_id: UUID, hashed_password: str) -> User | None:
        """Atualiza a senha hasheada do utilizador."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        user.hashed_password = hashed_password
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
        return user

