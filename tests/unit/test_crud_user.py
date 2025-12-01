"""Testes unitários para operações CRUD de usuários."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.api.v1.crud import crud_user
from app.api.v1.schemas.user import UserCreate


class TestCrudUserGet:
    """Testes para função get()."""

    def test_get_existing_user(self, db_session: Session):
        """Testa obtenção de usuário existente."""
        # Cria usuário
        user_create = UserCreate(email="test@example.com", password="password123")
        created_user = crud_user.create(db_session, obj_in=user_create)

        # Busca usuário
        found_user = crud_user.get(db_session, id=created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"

    def test_get_nonexistent_user(self, db_session: Session):
        """Testa obtenção de usuário inexistente."""
        nonexistent_id = uuid4()
        found_user = crud_user.get(db_session, id=nonexistent_id)

        assert found_user is None


class TestCrudUserGetByEmail:
    """Testes para função get_by_email()."""

    def test_get_by_email_existing(self, db_session: Session):
        """Testa obtenção de usuário por email existente."""
        user_create = UserCreate(email="test@example.com", password="password123")
        created_user = crud_user.create(db_session, obj_in=user_create)

        found_user = crud_user.get_by_email(db_session, email="test@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"

    def test_get_by_email_nonexistent(self, db_session: Session):
        """Testa obtenção de usuário por email inexistente."""
        found_user = crud_user.get_by_email(db_session, email="nonexistent@example.com")

        assert found_user is None


class TestCrudUserCreate:
    """Testes para função create()."""

    def test_create_user_success(self, db_session: Session):
        """Testa criação bem-sucedida de usuário."""
        user_create = UserCreate(email="newuser@example.com", password="password123")

        created_user = crud_user.create(db_session, obj_in=user_create)

        assert created_user is not None
        assert created_user.email == "newuser@example.com"
        assert created_user.hashed_password != "password123"  # Deve estar hasheado
        assert created_user.id is not None

    def test_create_user_duplicate_email(self, db_session: Session):
        """Testa que criação com email duplicado levanta ValueError."""
        user_create = UserCreate(email="duplicate@example.com", password="password123")
        crud_user.create(db_session, obj_in=user_create)

        # Tenta criar outro usuário com mesmo email
        with pytest.raises(ValueError, match="already in use"):
            crud_user.create(db_session, obj_in=user_create)

    def test_create_user_password_hashed(self, db_session: Session):
        """Testa que senha é hasheada corretamente."""
        user_create = UserCreate(email="hashtest@example.com", password="plainpassword")

        created_user = crud_user.create(db_session, obj_in=user_create)

        assert created_user.hashed_password != "plainpassword"
        assert len(created_user.hashed_password) > 0
        assert created_user.hashed_password.startswith("$argon2")


class TestCrudUserAuthenticate:
    """Testes para função authenticate()."""

    def test_authenticate_success(self, db_session: Session):
        """Testa autenticação bem-sucedida."""
        user_create = UserCreate(email="auth@example.com", password="correctpassword")
        crud_user.create(db_session, obj_in=user_create)

        authenticated_user = crud_user.authenticate(
            db_session, email="auth@example.com", password="correctpassword"
        )

        assert authenticated_user is not None
        assert authenticated_user.email == "auth@example.com"

    def test_authenticate_wrong_password(self, db_session: Session):
        """Testa autenticação com senha incorreta."""
        user_create = UserCreate(email="auth2@example.com", password="correctpassword")
        crud_user.create(db_session, obj_in=user_create)

        authenticated_user = crud_user.authenticate(
            db_session, email="auth2@example.com", password="wrongpassword"
        )

        assert authenticated_user is None

    def test_authenticate_nonexistent_user(self, db_session: Session):
        """Testa autenticação de usuário inexistente."""
        authenticated_user = crud_user.authenticate(
            db_session, email="nonexistent@example.com", password="anypassword"
        )

        assert authenticated_user is None
