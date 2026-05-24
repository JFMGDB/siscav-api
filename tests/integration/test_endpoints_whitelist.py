"""Testes de integração para endpoints de whitelist."""

import uuid

from fastapi.testclient import TestClient


class TestWhitelistEndpoints:
    """Testes para endpoints de whitelist."""

    def test_create_plate_success(self, client: TestClient, auth_token: str):
        """Testa criação de placa autorizada com sucesso."""
        response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "ABC-1234", "description": "Test Car"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plate"] == "ABC-1234"
        assert "id" in data

    def test_create_plate_invalid_format(self, client: TestClient, auth_token: str):
        """Testa criação de placa com formato inválido."""
        response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "INVALID", "description": "Invalid plate"},
        )

        # Pydantic validation returns 422, which is correct
        assert response.status_code in (400, 422)

    def test_get_plate_by_id(self, client: TestClient, auth_token: str):
        """Testa busca de placa por ID."""
        # Criar placa primeiro com placa única
        create_response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "DEF-5678", "description": "Test Car"},
        )
        assert create_response.status_code == 200
        plate_id = create_response.json()["id"]

        # Buscar placa
        response = client.get(
            f"/api/v1/whitelist/{plate_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == plate_id

    def test_list_plates(self, client: TestClient, auth_token: str):
        """Testa listagem de placas."""
        # Criar algumas placas com placas únicas
        for i in range(3):
            response = client.post(
                "/api/v1/whitelist/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"plate": f"GHI-{i:04d}", "description": f"Car {i}"},
            )
            # Ignorar se já existir (pode acontecer em testes repetidos)
            assert response.status_code in (200, 409)

        response = client.get(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # A API retorna uma lista diretamente, não um objeto com "items"
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_update_plate(self, client: TestClient, auth_token: str):
        """Testa atualização de placa."""
        # Criar placa primeiro com placa única
        create_response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "JKL-9012", "description": "Original"},
        )
        assert create_response.status_code == 200
        plate_id = create_response.json()["id"]

        # Atualizar placa
        response = client.put(
            f"/api/v1/whitelist/{plate_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "XYZ-5678", "description": "Updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plate"] == "XYZ-5678"
        assert data["description"] == "Updated"

    def test_delete_plate(self, client: TestClient, auth_token: str):
        """Testa remoção de placa."""
        # Criar placa primeiro com placa única
        create_response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "MNO-3456", "description": "Test Car"},
        )
        assert create_response.status_code == 200
        plate_id = create_response.json()["id"]

        # Remover placa
        response = client.delete(
            f"/api/v1/whitelist/{plate_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200

        # Verificar que foi removida
        get_response = client.get(
            f"/api/v1/whitelist/{plate_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_response.status_code == 404

    def test_create_duplicate_normalized_plate_returns_409(
        self, client: TestClient, auth_token: str
    ):
        """Segunda criação com mesma placa normalizada → 409."""
        r1 = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "ABC-1234", "description": "First"},
        )
        assert r1.status_code == 200
        r2 = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "abc 1234", "description": "Duplicate normalized"},
        )
        assert r2.status_code == 409
        assert "whitelist" in r2.json().get("detail", "").lower()

    def test_create_invalid_plate_returns_client_error(self, client: TestClient, auth_token: str):
        """Placa fora do formato BR → 422 (Pydantic) ou 400 (controller)."""
        response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "AB-1", "description": "invalid"},
        )
        assert response.status_code in (400, 422)

    def test_list_whitelist_respects_limit(self, client: TestClient, auth_token: str):
        """GET com limit=1 devolve uma entrada quando há várias placas."""
        base = int(uuid.uuid4().hex[:4], 16) % 5000 + 1000
        for i in range(2):
            r = client.post(
                "/api/v1/whitelist/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "plate": f"ZZZ-{base + i:04d}",
                    "description": f"pagination test {i}",
                },
            )
            assert r.status_code == 200, r.text

        response = client.get(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"skip": 0, "limit": 1},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
