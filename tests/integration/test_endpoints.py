"""Testes de integração para endpoints da API."""

import os

os.environ.setdefault("DEVICE_INGEST_KEY", "test-device-ingest-key")
os.environ.setdefault("ENVIRONMENT", "development")

import pytest
from fastapi.testclient import TestClient

from apps.api.src.api.v1.models.user import User
from tests.conftest import (
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_PASSWORD,
    TEST_DEVICE_INGEST_KEY,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


@pytest.fixture
def admin_auth_token(client: TestClient, admin_user: User):
    """Token JWT de administrador (mesmo banco que conftest)."""
    assert admin_user.is_admin
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestHealthEndpoint:
    """Testes para endpoint de health check."""

    def test_health_check(self, client: TestClient):
        """Testa endpoint de health check."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""

    @pytest.mark.usefixtures("test_user")
    def test_login_success(self, client: TestClient):
        """Testa login bem-sucedido."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.usefixtures("test_user")
    def test_login_wrong_password(self, client: TestClient):
        """Testa login com senha incorreta."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": TEST_USER_EMAIL, "password": "wrong_password"},
        )
        assert response.status_code == 401

    def test_login_user_not_found(self, client: TestClient):
        """Testa login com usuário inexistente."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401


class TestWhitelistEndpoints:
    """Testes para endpoints de whitelist."""

    def test_create_plate(self, client: TestClient, auth_token: str):
        """Testa criação de placa autorizada."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={
                "plate": "ABC-1234",
                "normalized_plate": "ABC1234",
                "description": "Test Car",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["plate"] == "ABC-1234"
        assert "id" in data

    def test_create_plate_unauthorized(self, client: TestClient):
        """Testa criação de placa sem autenticação."""
        response = client.post(
            "/api/v1/whitelist/",
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        assert response.status_code == 401

    def test_get_plate(self, client: TestClient, auth_token: str):
        """Testa obtenção de placa por ID."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        plate_id = create_response.json()["id"]
        response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == plate_id

    def test_list_plates(self, client: TestClient, auth_token: str):
        """Testa listagem de placas."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        for i in range(3):
            client.post(
                "/api/v1/whitelist/",
                headers=headers,
                json={"plate": f"ABC-{i:04d}", "normalized_plate": f"ABC{i:04d}"},
            )
        response = client.get("/api/v1/whitelist/", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 3

    def test_update_plate(self, client: TestClient, auth_token: str):
        """Testa atualização de placa."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        plate_id = create_response.json()["id"]
        response = client.put(
            f"/api/v1/whitelist/{plate_id}",
            headers=headers,
            json={
                "plate": "XYZ-5678",
                "normalized_plate": "XYZ5678",
                "description": "Updated",
            },
        )
        assert response.status_code == 200
        assert response.json()["plate"] == "XYZ-5678"

    def test_delete_plate(self, client: TestClient, auth_token: str):
        """Testa remoção de placa."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        plate_id = create_response.json()["id"]
        response = client.delete(f"/api/v1/whitelist/{plate_id}", headers=headers)
        assert response.status_code == 200
        response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
        assert response.status_code == 404


_DEVICE_HEADERS = {"X-Device-Key": TEST_DEVICE_INGEST_KEY}


class TestAccessLogsEndpoints:
    """Testes para endpoints de logs de acesso."""

    def test_create_access_log_authorized(self, client: TestClient, auth_token: str):
        """Testa criação de log de acesso autorizado."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "ABC-1234"}
        response = client.post(
            "/api/v1/access_logs/", files=files, data=data, headers=_DEVICE_HEADERS
        )
        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Authorized"
        assert log["plate_string_detected"] == "ABC-1234"

    def test_create_access_log_denied(self, client: TestClient):
        """Testa criação de log de acesso negado."""
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "XYZ-9999"}
        response = client.post(
            "/api/v1/access_logs/", files=files, data=data, headers=_DEVICE_HEADERS
        )
        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Denied"

    def test_list_access_logs(self, client: TestClient, auth_token: str):
        """Testa listagem de logs de acesso."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        for i in range(3):
            file_content = b"fake image content"
            files = {"file": (f"test_{i}.jpg", file_content, "image/jpeg")}
            data = {"plate": f"ABC-{i:04d}"}
            client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE_HEADERS)
        response = client.get("/api/v1/access_logs/", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 3

    def test_list_access_logs_with_filters(self, client: TestClient, auth_token: str):
        """Testa listagem de logs com filtros."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        file_content = b"fake image content"
        files = {"file": ("test.jpg", file_content, "image/jpeg")}
        client.post(
            "/api/v1/access_logs/",
            files=files,
            data={"plate": "ABC-1234"},
            headers=_DEVICE_HEADERS,
        )
        client.post(
            "/api/v1/access_logs/",
            files=files,
            data={"plate": "XYZ-9999"},
            headers=_DEVICE_HEADERS,
        )
        response = client.get("/api/v1/access_logs/?status=Authorized", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        assert all(log["status"] == "Authorized" for log in logs)


class TestGateControlEndpoints:
    """Testes para endpoints de controle de portão."""

    def test_trigger_gate(self, client: TestClient, admin_auth_token: str):
        """Testa acionamento do portão (requer admin)."""
        headers = {"Authorization": f"Bearer {admin_auth_token}"}
        response = client.post("/api/v1/gate_control/trigger", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["integration"] == "simulated"

    def test_trigger_gate_unauthorized(self, client: TestClient):
        """Testa acionamento do portão sem autenticação."""
        response = client.post("/api/v1/gate_control/trigger")
        assert response.status_code == 401


class TestDeviceEndpoints:
    """Testes para endpoints de dispositivos."""

    def test_scan_devices(self, client: TestClient, auth_token: str):
        """Testa escaneamento de dispositivos."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/devices/scan", headers=headers)
        assert response.status_code == 200
        devices = response.json()
        assert isinstance(devices, list)

    def test_get_connection_status(self, client: TestClient, auth_token: str):
        """Testa obtenção de status de conexão."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/devices/status", headers=headers)
        assert response.status_code == 200
        status = response.json()
        assert "connected" in status

    def test_disconnect_device(self, client: TestClient, auth_token: str):
        """Testa desconexão de dispositivo."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/v1/devices/disconnect", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"
