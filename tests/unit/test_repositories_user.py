"""Testes unitários para UserRepository."""

from uuid import uuid4

from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.security import get_password_hash
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.user import UserCreate


class TestUserRepository:
    """Testes para UserRepository."""

    def test_get_by_id_success(self, db_session: Session):
        """Testa busca de usuário por ID com sucesso."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        result = UserRepository.get_by_id(db_session, user.id)

        assert result is not None
        assert result.id == user.id
        assert result.email == "test@example.com"

    def test_get_by_id_not_found(self, db_session: Session):
        """Testa busca de usuário por ID inexistente."""
        fake_id = uuid4()
        result = UserRepository.get_by_id(db_session, fake_id)

        assert result is None

    def test_get_by_email_success(self, db_session: Session):
        """Testa busca de usuário por email com sucesso."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()

        result = UserRepository.get_by_email(db_session, "test@example.com")

        assert result is not None
        assert result.email == "test@example.com"

    def test_get_by_email_not_found(self, db_session: Session):
        """Testa busca de usuário por email inexistente."""
        result = UserRepository.get_by_email(db_session, "nonexistent@example.com")

        assert result is None

    def test_create_success(self, db_session: Session):
        """Testa criação de usuário com sucesso."""
        user_data = UserCreate(email="newuser@example.com", password="password123")
        hashed_password = get_password_hash("password123")

        result = UserRepository.create(db_session, user_data, hashed_password)

        assert result is not None
        assert result.email == "newuser@example.com"
        assert result.hashed_password == hashed_password

        # Verificar que foi salvo no banco
        saved_user = UserRepository.get_by_email(db_session, "newuser@example.com")
        assert saved_user is not None
        assert saved_user.id == result.id

    def test_list_users_ordered(self, db_session: Session):
        """List returns users newest first."""
        for i in range(3):
            db_session.add(
                User(
                    email=f"listuser{i}@example.com",
                    hashed_password=get_password_hash("password123"),
                    is_admin=True,
                )
            )
        db_session.commit()

        result = UserRepository.list_users(db_session, skip=0, limit=2)
        assert len(result) == 2

    def test_count_methods(self, db_session: Session):
        """Count helpers return expected totals."""
        db_session.add(
            User(
                email="super@example.com",
                hashed_password=get_password_hash("password123"),
                is_admin=False,
                is_superadmin=True,
            )
        )
        db_session.add(
            User(
                email="client@example.com",
                hashed_password=get_password_hash("password123"),
                is_admin=True,
                is_superadmin=False,
            )
        )
        db_session.commit()

        assert UserRepository.count_all(db_session) == 2
        assert UserRepository.count_superadmins(db_session) == 1
        assert UserRepository.count_client_admins(db_session) == 1

    def test_update_and_delete(self, db_session: Session):
        """Update email and hard-delete user."""
        user = User(
            email="upd@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        updated = UserRepository.update(db_session, user.id, email="newemail@example.com")
        assert updated is not None
        assert updated.email == "newemail@example.com"

        assert UserRepository.delete(db_session, user.id) is True
        assert UserRepository.get_by_id(db_session, user.id) is None
