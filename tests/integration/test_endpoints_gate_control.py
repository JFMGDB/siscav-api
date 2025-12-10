"""Testes de integração para endpoints de controle de portão."""

import pytest
from fastapi.testclient import TestClient


class TestGateControlEndpoints:
    """Testes para endpoints de controle de portão."""

    def test_trigger_gate(self, client: TestClient, auth_token: str):
        """Testa acionamento do portão."""
        response = client.post(
            "/api/v1/gate_control/trigger",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data

    def test_trigger_gate_requires_auth(self, client: TestClient):
        """Testa que acionamento do portão requer autenticação."""
        response = client.post("/api/v1/gate_control/trigger")

        assert response.status_code == 403

