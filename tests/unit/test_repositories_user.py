"""Testes unitários para UserRepository."""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.v1.core.security import get_password_hash
from app.api.v1.models.user import User
from app.api.v1.repositories.user_repository import UserRepository
from app.api.v1.schemas.user import UserCreate


class TestUserRepository:
    """Testes para UserRepository."""

    def test_get_by_id_success(self, db_session: Session):
        """Testa busca de usuário por ID com sucesso."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
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

