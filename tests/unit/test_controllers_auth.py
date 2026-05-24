"""Testes unitários para AuthController."""

from datetime import timedelta

from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.core.security import (
    create_password_reset_token,
    get_password_hash,
    verify_password,
)
from apps.api.src.api.v1.models.user import User


class TestAuthController:
    """Testes para AuthController."""

    def test_authenticate_success(self, db_session: Session):
        """Testa autenticação bem-sucedida."""
        # Criar usuário de teste
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False,
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
            is_admin=False,
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
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        controller = AuthController(db_session)
        token = controller.create_access_token_for_user(user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_request_password_reset_unknown_email(self, db_session: Session):
        controller = AuthController(db_session)
        tok, msg = controller.request_password_reset("nobody@example.com")
        assert tok is None
        assert "account exists" in msg.lower()

    def test_request_password_reset_known_user(self, db_session: Session):
        user = User(
            email="reset@example.com",
            hashed_password=get_password_hash("oldpass123"),
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()

        controller = AuthController(db_session)
        tok, msg = controller.request_password_reset("reset@example.com")
        assert tok is not None
        assert len(tok) > 10
        assert "account exists" in msg.lower()

    def test_confirm_password_reset_success(self, db_session: Session):
        user = User(
            email="confirm@example.com",
            hashed_password=get_password_hash("oldpass123"),
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_password_reset_token(user.id, expires_delta=timedelta(minutes=10))

        controller = AuthController(db_session)
        controller.confirm_password_reset(token, "newpassword123")

        db_session.refresh(user)
        assert verify_password("newpassword123", user.hashed_password)
        assert not verify_password("oldpass123", user.hashed_password)
