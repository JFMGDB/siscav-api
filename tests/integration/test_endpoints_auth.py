"""Testes de integração para endpoints de autenticação."""

import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api.src.api.v1.core.security import get_password_hash
from apps.api.src.api.v1.models.user import User
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Testa login bem-sucedido."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Testa login com credenciais inválidas."""
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

    def test_get_current_user_success(self, client: TestClient, auth_token: str):
        """Testa obtenção de usuário atual com token válido."""
        # Este teste é indireto através de um endpoint protegido
        # Vamos usar o endpoint de whitelist que requer autenticação
        response = client.get(
            "/api/v1/whitelist/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Testa obtenção de usuário atual com token inválido."""
        response = client.get(
            "/api/v1/whitelist/",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 403

    def test_get_current_user_missing_token(self, client: TestClient):
        """Testa acesso sem token."""
        response = client.get("/api/v1/whitelist/")

        assert response.status_code == 401

    def test_refresh_token_success(self, client: TestClient, test_user: User):
        """Refresh retorna novo par de tokens."""
        login = client.post(
            "/api/v1/login/access-token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert login.status_code == 200
        refresh = login.json()["refresh_token"]

        response = client.post(
            "/api/v1/login/refresh-token",
            data={"refresh_token": refresh},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_rate_limit(self, client: TestClient, test_user: User):
        """Sexta chamada de refresh no mesmo minuto → 429."""
        login = client.post(
            "/api/v1/login/access-token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert login.status_code == 200
        refresh = login.json()["refresh_token"]

        last_status = 200
        for i in range(6):
            response = client.post(
                "/api/v1/login/refresh-token",
                data={"refresh_token": refresh},
            )
            last_status = response.status_code
            if response.status_code == 200:
                refresh = response.json()["refresh_token"]
        assert last_status == 429

    def test_register_then_login_returns_token_pair(self, client: TestClient):
        """AUTH-01: registro com email/senha e login OAuth2 retornam access + refresh."""
        email = f"register-{uuid.uuid4().hex[:12]}@example.com"
        password = "registerpass123"

        reg = client.post(
            "/api/v1/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201
        assert reg.json()["email"] == email

        login = client.post(
            "/api/v1/login/access-token",
            data={"username": email, "password": password},
        )
        assert login.status_code == 200
        body = login.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

