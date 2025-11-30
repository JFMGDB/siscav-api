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
    assert "já está cadastrada" in response.json()["detail"].lower()
