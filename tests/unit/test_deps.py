"""Testes unitários para dependências do FastAPI."""

import uuid

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.security import create_access_token, get_password_hash
from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.deps import (
    get_current_client_admin_user,
    get_current_superadmin_user,
    get_current_user,
)
from apps.api.src.api.v1.models.user import User


@pytest.fixture
def db_session():
    """Cria uma sessão de banco de dados em memória para testes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Cria um usuário de teste."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_admin=True,
        is_superadmin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestGetCurrentUser:
    """Testes para a dependência get_current_user."""

    def test_get_current_user_success(self, db_session, test_user):
        """Testa obtenção de usuário autenticado com token válido."""
        token = create_access_token(str(test_user.id))
        user = get_current_user(token=token, db=db_session)
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_current_user_invalid_token(self, db_session):
        """Testa obtenção de usuário com token inválido."""
        invalid_token = "invalid_token_string"
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=invalid_token, db=db_session)
        assert exc_info.value.status_code == 403

    def test_get_current_user_expired_token(self, db_session, test_user):
        """Testa obtenção de usuário com token expirado."""
        # Criar token expirado
        settings = get_settings()
        expired_token = jwt.encode(
            {"exp": 0, "sub": str(test_user.id)},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=expired_token, db=db_session)
        assert exc_info.value.status_code == 403

    def test_get_current_user_nonexistent_user(self, db_session):
        """Testa obtenção de usuário com token válido mas usuário inexistente."""
        nonexistent_user_id = uuid.uuid4()
        token = create_access_token(str(nonexistent_user_id))
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)
        assert exc_info.value.status_code == 404

    def test_get_current_user_malformed_token(self, db_session):
        """Testa obtenção de usuário com token malformado."""
        malformed_token = "not.a.valid.jwt.token"
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=malformed_token, db=db_session)
        assert exc_info.value.status_code == 403


class TestGetCurrentClientAdminUser:
    """Tests for get_current_client_admin_user."""

    def test_client_admin_allowed(self, test_user):
        user = get_current_client_admin_user(current_user=test_user)
        assert user.id == test_user.id

    def test_superadmin_forbidden(self, db_session, test_user):
        test_user.is_superadmin = True
        test_user.is_admin = False
        db_session.commit()
        db_session.refresh(test_user)
        with pytest.raises(HTTPException) as exc_info:
            get_current_client_admin_user(current_user=test_user)
        assert exc_info.value.status_code == 403

    def test_non_admin_client_forbidden(self, db_session, test_user):
        test_user.is_admin = False
        test_user.is_superadmin = False
        db_session.commit()
        db_session.refresh(test_user)
        with pytest.raises(HTTPException) as exc_info:
            get_current_client_admin_user(current_user=test_user)
        assert exc_info.value.status_code == 403


class TestGetCurrentSuperadminUser:
    """Testes para a dependência get_current_superadmin_user."""

    def test_superadmin_allowed(self, db_session, test_user):
        test_user.is_superadmin = True
        db_session.commit()
        db_session.refresh(test_user)
        user = get_current_superadmin_user(current_user=test_user)
        assert user.id == test_user.id

    def test_operational_admin_forbidden(self, db_session, test_user):
        test_user.is_admin = True
        db_session.commit()
        db_session.refresh(test_user)
        with pytest.raises(HTTPException) as exc_info:
            get_current_superadmin_user(current_user=test_user)
        assert exc_info.value.status_code == 403

    def test_regular_user_forbidden(self, test_user):
        with pytest.raises(HTTPException) as exc_info:
            get_current_superadmin_user(current_user=test_user)
        assert exc_info.value.status_code == 403
