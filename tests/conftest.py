"""Configuração compartilhada para testes de integração."""

import os
import uuid

# Antes de importar a app: garantir chave de ingestão e ambiente de teste
os.environ.setdefault("DEVICE_INGEST_KEY", "test-device-ingest-key")
os.environ.setdefault("ENVIRONMENT", "development")

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.core.limiter import limiter
from apps.api.src.api.v1.core.security import create_access_token, get_password_hash
from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.user import User
from apps.api.src.main import app

# Constantes para testes
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_ADMIN_EMAIL = "admin-test@example.com"
TEST_ADMIN_PASSWORD = "adminpassword123"
TEST_DEVICE_INGEST_KEY = "test-device-ingest-key"

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session]:
    """Override da dependência get_db para testes."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _reset_login_rate_limiter() -> None:
    """Evita 429 entre testes (SlowAPI usa o mesmo 'client' no TestClient)."""
    limiter.reset()


@pytest.fixture
def client() -> TestClient:
    """Fixture para criar um cliente de teste."""
    return TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session]:
    """Fixture para criar uma sessão de banco de dados de teste."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Fixture para criar um usuário de teste."""
    # Verificar se o usuário já existe
    existing_user = db_session.query(User).filter(User.email == TEST_USER_EMAIL).first()
    if existing_user:
        return existing_user

    # Criar novo usuário
    user = User(
        id=uuid.uuid4(),
        email=TEST_USER_EMAIL,
        hashed_password=get_password_hash(TEST_USER_PASSWORD),
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Usuário com is_admin para rotas privilegiadas."""
    existing = db_session.query(User).filter(User.email == TEST_ADMIN_EMAIL).first()
    if existing:
        return existing
    user = User(
        id=uuid.uuid4(),
        email=TEST_ADMIN_EMAIL,
        hashed_password=get_password_hash(TEST_ADMIN_PASSWORD),
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Fixture para criar um token de autenticação válido."""
    return create_access_token(test_user.id)


@pytest.fixture
def admin_auth_token(admin_user: User) -> str:
    """Token JWT para usuário administrador."""
    return create_access_token(admin_user.id)
