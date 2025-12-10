"""Testes de integração para endpoints de autenticação."""

import pytest
from fastapi.testclient import TestClient

from app.api.v1.core.security import get_password_hash
from app.api.v1.models.user import User
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

        assert response.status_code == 403

