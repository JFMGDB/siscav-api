"""Repository para operações de acesso a dados de usuários."""

from uuid import UUID

from sqlalchemy import func, select
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
            is_admin=True,
            is_superadmin=False,
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

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """List users ordered by newest first."""
        return list(
            db.scalars(
                select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
            )
        )

    @staticmethod
    def count_all(db: Session) -> int:
        """Count all user accounts."""
        return int(db.scalar(select(func.count()).select_from(User)) or 0)

    @staticmethod
    def count_superadmins(db: Session) -> int:
        """Count platform superadmin accounts."""
        return int(
            db.scalar(
                select(func.count()).select_from(User).where(User.is_superadmin.is_(True))
            )
            or 0
        )

    @staticmethod
    def count_client_admins(db: Session) -> int:
        """Count client administrator accounts (is_admin, not superadmin)."""
        return int(
            db.scalar(
                select(func.count())
                .select_from(User)
                .where(User.is_admin.is_(True), User.is_superadmin.is_(False))
            )
            or 0
        )

    @staticmethod
    def update(
        db: Session,
        user_id: UUID,
        *,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> User | None:
        """Update email and/or password hash for a user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        if email is not None:
            user.email = email
        if hashed_password is not None:
            user.hashed_password = hashed_password
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
        return user

    @staticmethod
    def delete(db: Session, user_id: UUID) -> bool:
        """Hard-delete a user. Returns True if a row was removed."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return False
        db.delete(user)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        return True
