"""Testes de integração para endpoints da API."""

import uuid
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.models.user import User
from apps.api.src.main import app

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override da dependência get_db para testes."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def test_user():
    """Cria um usuário de teste."""
    from apps.api.src.api.v1.core.security import get_password_hash

    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_token(test_user):
    """Obtém token de autenticação para testes."""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestHealthEndpoint:
    """Testes para endpoint de health check."""

    def test_health_check(self):
        """Testa endpoint de health check."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""

    def test_login_success(self, test_user):
        """Testa login bem-sucedido."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, test_user):
        """Testa login com senha incorreta."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "wrong_password"},
        )
        assert response.status_code == 400

    def test_login_user_not_found(self):
        """Testa login com usuário inexistente."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 400


class TestWhitelistEndpoints:
    """Testes para endpoints de whitelist."""

    def test_create_plate(self, auth_token):
        """Testa criação de placa autorizada."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234", "description": "Test Car"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["plate"] == "ABC-1234"
        assert "id" in data

    def test_create_plate_unauthorized(self):
        """Testa criação de placa sem autenticação."""
        response = client.post(
            "/api/v1/whitelist/",
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        assert response.status_code == 401

    def test_get_plate(self, auth_token):
        """Testa obtenção de placa por ID."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar placa primeiro
        create_response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        plate_id = create_response.json()["id"]
        # Buscar placa
        response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == plate_id

    def test_list_plates(self, auth_token):
        """Testa listagem de placas."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar algumas placas
        for i in range(3):
            client.post(
                "/api/v1/whitelist/",
                headers=headers,
                json={"plate": f"ABC-{i:04d}", "normalized_plate": f"ABC{i:04d}"},
            )
        # Listar placas
        response = client.get("/api/v1/whitelist/", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 3

    def test_update_plate(self, auth_token):
        """Testa atualização de placa."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar placa
        create_response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        plate_id = create_response.json()["id"]
        # Atualizar placa
        response = client.put(
            f"/api/v1/whitelist/{plate_id}",
            headers=headers,
            json={"plate": "XYZ-5678", "normalized_plate": "XYZ5678", "description": "Updated"},
        )
        assert response.status_code == 200
        assert response.json()["plate"] == "XYZ-5678"

    def test_delete_plate(self, auth_token):
        """Testa remoção de placa."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar placa
        create_response = client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        plate_id = create_response.json()["id"]
        # Remover placa
        response = client.delete(f"/api/v1/whitelist/{plate_id}", headers=headers)
        assert response.status_code == 200
        # Verificar que foi removida
        response = client.get(f"/api/v1/whitelist/{plate_id}", headers=headers)
        assert response.status_code == 404


class TestAccessLogsEndpoints:
    """Testes para endpoints de logs de acesso."""

    def test_create_access_log_authorized(self, auth_token):
        """Testa criação de log de acesso autorizado."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar placa autorizada
        client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        # Criar log de acesso
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "ABC-1234"}
        response = client.post("/api/v1/access_logs/", files=files, data=data)
        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Authorized"
        assert log["plate_string_detected"] == "ABC-1234"

    def test_create_access_log_denied(self):
        """Testa criação de log de acesso negado."""
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "XYZ-9999"}
        response = client.post("/api/v1/access_logs/", files=files, data=data)
        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Denied"

    def test_list_access_logs(self, auth_token):
        """Testa listagem de logs de acesso."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar alguns logs
        for i in range(3):
            file_content = b"fake image content"
            files = {"file": (f"test_{i}.jpg", file_content, "image/jpeg")}
            data = {"plate": f"ABC-{i:04d}"}
            client.post("/api/v1/access_logs/", files=files, data=data)
        # Listar logs
        response = client.get("/api/v1/access_logs/", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 3

    def test_list_access_logs_with_filters(self, auth_token):
        """Testa listagem de logs com filtros."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Criar placa autorizada
        client.post(
            "/api/v1/whitelist/",
            headers=headers,
            json={"plate": "ABC-1234", "normalized_plate": "ABC1234"},
        )
        # Criar logs
        file_content = b"fake image content"
        files = {"file": ("test.jpg", file_content, "image/jpeg")}
        client.post("/api/v1/access_logs/", files=files, data={"plate": "ABC-1234"})
        client.post("/api/v1/access_logs/", files=files, data={"plate": "XYZ-9999"})
        # Filtrar por status
        response = client.get(
            "/api/v1/access_logs/?status=Authorized", headers=headers
        )
        assert response.status_code == 200
        logs = response.json()
        assert all(log["status"] == "Authorized" for log in logs)


class TestGateControlEndpoints:
    """Testes para endpoints de controle de portão."""

    def test_trigger_gate(self, auth_token):
        """Testa acionamento do portão."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/v1/gate_control/trigger", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_trigger_gate_unauthorized(self):
        """Testa acionamento do portão sem autenticação."""
        response = client.post("/api/v1/gate_control/trigger")
        assert response.status_code == 401


class TestDeviceEndpoints:
    """Testes para endpoints de dispositivos."""

    def test_scan_devices(self, auth_token):
        """Testa escaneamento de dispositivos."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/devices/scan", headers=headers)
        assert response.status_code == 200
        devices = response.json()
        assert isinstance(devices, list)

    def test_get_connection_status(self, auth_token):
        """Testa obtenção de status de conexão."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/devices/status", headers=headers)
        assert response.status_code == 200
        status = response.json()
        assert "connected" in status

    def test_disconnect_device(self, auth_token):
        """Testa desconexão de dispositivo."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/v1/devices/disconnect", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"

