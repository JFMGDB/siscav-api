"""Testes unitários para AuthController."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.controllers.auth_controller import AuthController
from app.api.v1.core.security import get_password_hash
from app.api.v1.models.user import User
from app.api.v1.repositories.user_repository import UserRepository


class TestAuthController:
    """Testes para AuthController."""

    def test_authenticate_success(self, db_session: Session):
        """Testa autenticação bem-sucedida."""
        # Criar usuário de teste
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        controller = AuthController(db_session)
        authenticated_user = controller.authenticate("test@example.com", "password123")

        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"
        assert authenticated_user.id == user.id

    def test_authenticate_user_not_found(self, db_session: Session):
        """Testa autenticação com usuário não encontrado."""
        controller = AuthController(db_session)
        result = controller.authenticate("nonexistent@example.com", "password123")

        assert result is None

    def test_authenticate_wrong_password(self, db_session: Session):
        """Testa autenticação com senha incorreta."""
        # Criar usuário de teste
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("correct_password"),
        )
        db_session.add(user)
        db_session.commit()

        controller = AuthController(db_session)
        result = controller.authenticate("test@example.com", "wrong_password")

        assert result is None

    def test_create_access_token_for_user(self, db_session: Session):
        """Testa criação de token de acesso para usuário."""
        # Criar usuário de teste
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        controller = AuthController(db_session)
        token = controller.create_access_token_for_user(user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

