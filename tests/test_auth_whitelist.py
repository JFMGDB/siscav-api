from apps.api.src.api.v1.crud import crud_user
from apps.api.src.api.v1.schemas.user import UserCreate

# Constantes para testes
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"


def _create_test_user(db_session):
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


def get_token(client, db_session):
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
