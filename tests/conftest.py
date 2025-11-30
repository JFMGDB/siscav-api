"""Configuração compartilhada para todos os testes.

Este arquivo centraliza a configuração do banco de dados de testes e fixtures
compartilhadas, garantindo que todos os testes usem o mesmo mecanismo de banco
de dados e evitando conflitos entre arquivos de teste.
"""

import contextlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.crud import crud_user
from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.user import UserCreate
from apps.api.src.main import app

# Configuração do banco de dados de testes
# Usa SQLite em memória para isolamento e performance
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset do banco de dados antes de cada teste.

    Esta fixture garante que cada teste comece com um banco de dados limpo,
    criando todas as tabelas antes do teste e removendo-as após.
    """
    # Criar todas as tabelas antes do teste
    Base.metadata.create_all(bind=test_engine)
    yield
    # Limpar todas as tabelas após o teste
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Fornece uma sessão de banco de dados para testes.

    Esta sessão é isolada por teste e é fechada automaticamente após o uso.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    """Override da dependência get_db para testes.

    Esta função substitui a dependência original do FastAPI para usar o
    banco de dados de testes em vez do banco de dados de produção.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Configurar o override uma única vez para toda a suíte de testes
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Fornece um cliente de teste FastAPI.

    O cliente é configurado com o override do banco de dados de testes.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Limpa arquivos da pasta uploads antes e depois de cada teste.

    Esta fixture garante que arquivos criados durante os testes sejam removidos,
    mesmo se o teste falhar antes de executar a limpeza manual.
    """
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)

    # Limpar arquivos antes do teste (caso tenha sobrado de execuções anteriores)
    if upload_dir.exists():
        for file_path in upload_dir.iterdir():
            if file_path.is_file() and file_path.name != ".gitkeep":
                with contextlib.suppress(Exception):
                    file_path.unlink()

    yield

    # Limpar arquivos após o teste (garantia de limpeza mesmo em caso de falha)
    if upload_dir.exists():
        for file_path in upload_dir.iterdir():
            if file_path.is_file() and file_path.name != ".gitkeep":
                with contextlib.suppress(Exception):
                    file_path.unlink()


# Constantes para testes
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"  # Senha simples apenas para testes


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Cria um usuário de teste se não existir.

    Esta fixture garante que um usuário de teste esteja disponível para testes
    que precisam de autenticação. O usuário é criado uma vez e reutilizado.

    Args:
        db_session: Sessão do banco de dados de testes.

    Returns:
        User: Instância do usuário de teste criado ou existente.
    """
    user = crud_user.get_by_email(db_session, TEST_USER_EMAIL)
    if not user:
        user_in = UserCreate(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        user = crud_user.create(db_session, user_in)
    db_session.commit()
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:  # noqa: ARG001
    """Obtém um token de autenticação válido para testes.

    Esta fixture faz login com o usuário de teste e retorna o token de acesso.
    Útil para testes que precisam de autenticação sem repetir a lógica de login.

    Args:
        client: Cliente de teste FastAPI.
        test_user: Usuário de teste (criado pela fixture test_user).
                   O parâmetro garante que o usuário existe antes do login.

    Returns:
        str: Token de acesso JWT para uso em headers de autenticação.
    """
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    return response.json()["access_token"]
