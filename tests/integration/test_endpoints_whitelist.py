"""Testes de integração para endpoints de whitelist."""

import pytest
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

        assert response.status_code == 400

    def test_get_plate_by_id(self, client: TestClient, auth_token: str):
        """Testa busca de placa por ID."""
        # Criar placa primeiro
        create_response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "ABC-1234", "description": "Test Car"},
        )
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
        # Criar algumas placas
        for i in range(3):
            client.post(
                "/api/v1/whitelist/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"plate": f"ABC-{i:04d}", "description": f"Car {i}"},
            )

        response = client.get(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 3

    def test_update_plate(self, client: TestClient, auth_token: str):
        """Testa atualização de placa."""
        # Criar placa primeiro
        create_response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "ABC-1234", "description": "Original"},
        )
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
        # Criar placa primeiro
        create_response = client.post(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"plate": "ABC-1234", "description": "Test Car"},
        )
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

