from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from apps.api.src.api.v1.crud import crud_user
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.user import UserCreate

# Constantes para testes
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"


def _create_test_user(db_session: Session) -> User:
    """Helper para criar usuário de teste se não existir.

    Evita duplicação de código seguindo o princípio DRY.
    """
    user = crud_user.get_by_email(db_session, TEST_USER_EMAIL)
    if not user:
        user_in = UserCreate(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        user = crud_user.create(db_session, user_in)
    db_session.commit()
    return user


def test_create_user_and_login(client, db_session):
    """Testa criação de usuário e login."""
    _create_test_user(db_session)

    # Testa login
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_with_invalid_credentials(client, db_session):
    """Testa login com credenciais inválidas."""
    _create_test_user(db_session)

    # Testa login com senha incorreta
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": TEST_USER_EMAIL, "password": "wrong_password"},
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]

    # Testa login com email inexistente
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "nonexistent@example.com", "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_access_without_token(client, db_session):  # noqa: ARG001
    """Testa acesso a endpoints protegidos sem token."""
    # Tenta acessar whitelist sem token
    response = client.get("/api/v1/whitelist/")
    assert response.status_code == 401

    response = client.post(
        "/api/v1/whitelist/",
        json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "Test"},
    )
    assert response.status_code == 401


def test_access_with_invalid_token(client, db_session):  # noqa: ARG001
    """Testa acesso a endpoints protegidos com token inválido."""
    headers = {"Authorization": "Bearer invalid_token_here"}

    # Tenta acessar whitelist com token inválido
    response = client.get("/api/v1/whitelist/", headers=headers)
    assert response.status_code == 403

    # Tenta criar placa com token inválido
    response = client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "Test"},
    )
    assert response.status_code == 403


def test_access_with_malformed_token(client, db_session):  # noqa: ARG001
    """Testa acesso com token malformado."""
    headers = {"Authorization": "Bearer not.a.valid.jwt.token"}

    response = client.get("/api/v1/whitelist/", headers=headers)
    assert response.status_code == 403


def get_token(client: TestClient, db_session: Session) -> str:
    """Helper para obter token de autenticação."""
    _create_test_user(db_session)

    response = client.post(
        "/api/v1/login/access-token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    return response.json()["access_token"]


def test_whitelist_crud(client, db_session):
    """Testa operações CRUD completas na whitelist."""
    token = get_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # Cria
    response = client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "Test Car"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plate"] == "ABC-1234"
    assert "id" in data
    plate_id = data["id"]

    # Lê
    response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == plate_id

    # Lista
    response = client.get("/api/v1/whitelist/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Atualiza
    response = client.put(
        f"/api/v1/whitelist/{plate_id}",
        headers=headers,
        json={"plate": "ABC-9999", "normalized_plate": "ABC9999", "description": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["plate"] == "ABC-9999"

    # Remove
    response = client.delete(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 200

    # Verifica remoção
    response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 404

    # Testa tentativa de atualizar placa deletada (deve retornar 404)
    response = client.put(
        f"/api/v1/whitelist/{plate_id}",
        headers=headers,
        json={"plate": "ABC-9999", "normalized_plate": "ABC9999", "description": "Updated"},
    )
    assert response.status_code == 404

    # Testa tentativa de deletar placa já deletada (deve retornar 404)
    response = client.delete(f"/api/v1/whitelist/{plate_id}", headers=headers)
    assert response.status_code == 404
