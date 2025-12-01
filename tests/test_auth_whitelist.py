from app.api.v1.crud import crud_authorized_plate
from app.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


def test_create_user_and_login(client, test_user):
    """Testa criação de usuário e login."""

    # Testa login
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_with_invalid_credentials(client, test_user):
    """Testa login com credenciais inválidas."""
    # Testa login com senha incorreta
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": "wrong_password"},
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]

    # Testa login com email inexistente
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "nonexistent@example.com", "password": "password123"},
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


def test_whitelist_crud(client, auth_token):
    """Testa operações CRUD completas na whitelist."""
    token = auth_token
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


def test_create_duplicate_plate(client, auth_token):
    """Testa criação de placa com normalized_plate duplicada."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Cria primeira placa
    response = client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "First"},
    )
    assert response.status_code == 200

    # Tenta criar placa com mesmo normalized_plate
    response = client.post(
        "/api/v1/whitelist/",
        headers=headers,
        json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "Duplicate"},
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_refresh_token_endpoint(client, test_user):
    """Testa endpoint de refresh token."""
    # Primeiro faz login para obter refresh token
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    tokens = response.json()
    refresh_token = tokens["refresh_token"]

    # Usa refresh token para obter novos tokens
    response = client.post(
        "/api/v1/login/refresh-token",
        data={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["token_type"] == "bearer"
    # Novos tokens devem ser diferentes dos originais
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]


def test_refresh_token_with_invalid_token(client):
    """Testa refresh token com token inválido."""
    response = client.post(
        "/api/v1/login/refresh-token",
        data={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 403
    assert "Could not validate refresh token" in response.json()["detail"]


def test_refresh_token_with_access_token(client, test_user):
    """Testa refresh token usando access token (deve falhar)."""
    # Obtém access token
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Tenta usar access token como refresh token
    response = client.post(
        "/api/v1/login/refresh-token",
        data={"refresh_token": access_token},
    )
    assert response.status_code == 403
    assert "Invalid token type" in response.json()["detail"]


def test_refresh_token_empty(client):
    """Testa refresh token com token vazio."""
    response = client.post(
        "/api/v1/login/refresh-token",
        data={"refresh_token": ""},
    )
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"].lower()


def test_whitelist_pagination(client, auth_token, db_session):
    """Testa paginação na listagem de placas autorizadas."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Cria várias placas para testar paginação
    for i in range(5):
        plate_in = AuthorizedPlateCreate(
            plate=f"ABC-{1000 + i}",
            normalized_plate=f"ABC{1000 + i}",
            description=f"Test {i}",
        )
        crud_authorized_plate.create(db_session, plate_in)
    db_session.commit()

    # Testa primeira página
    response = client.get("/api/v1/whitelist/?skip=0&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_next" in data
    assert "has_prev" in data
    assert len(data["items"]) == 2
    assert data["total"] >= 5
    assert data["has_next"] is True
    assert data["has_prev"] is False

    # Testa segunda página
    response = client.get("/api/v1/whitelist/?skip=2&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["has_prev"] is True
