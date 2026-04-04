"""Testes de integração para endpoints de controle de portão."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.src.api.v1.core.config import get_settings


class TestGateControlEndpoints:
    """Testes para endpoints de controle de portão."""

    def test_trigger_gate_admin_simulated(self, client: TestClient, admin_auth_token: str):
        """Sem GATE_ACTUATOR_URL → integration simulated (GATE-01)."""
        get_settings.cache_clear()
        response = client.post(
            "/api/v1/gate_control/trigger",
            headers={"Authorization": f"Bearer {admin_auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["integration"] == "simulated"
        assert data["acknowledged"] is False
        assert "message" in data

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_live_upstream_2xx(
        self, mock_urlopen: MagicMock, client: TestClient, admin_auth_token: str, monkeypatch: pytest.MonkeyPatch
    ):
        """Com URL e upstream 200 → integration live, acknowledged."""
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_resp
        mock_cm.__exit__.return_value = None
        mock_urlopen.return_value = mock_cm

        monkeypatch.setenv("GATE_ACTUATOR_URL", "http://actuator.test/open")
        get_settings.cache_clear()
        try:
            response = client.post(
                "/api/v1/gate_control/trigger",
                headers={"Authorization": f"Bearer {admin_auth_token}"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["integration"] == "live"
            assert data["acknowledged"] is True
            assert data["downstream_status_code"] == 200
            mock_urlopen.assert_called_once()
        finally:
            monkeypatch.delenv("GATE_ACTUATOR_URL", raising=False)
            get_settings.cache_clear()

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_live_upstream_500_returns_502(
        self, mock_urlopen: MagicMock, client: TestClient, admin_auth_token: str, monkeypatch: pytest.MonkeyPatch
    ):
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            "http://actuator.test",
            500,
            "Internal",
            hdrs={},
            fp=BytesIO(b""),
        )

        monkeypatch.setenv("GATE_ACTUATOR_URL", "http://actuator.test/open")
        get_settings.cache_clear()
        try:
            response = client.post(
                "/api/v1/gate_control/trigger",
                headers={"Authorization": f"Bearer {admin_auth_token}"},
            )
            assert response.status_code == 502
            assert "detail" in response.json()
        finally:
            monkeypatch.delenv("GATE_ACTUATOR_URL", raising=False)
            get_settings.cache_clear()

    def test_trigger_gate_non_admin_forbidden(self, client: TestClient, auth_token: str):
        """Usuário autenticado sem is_admin recebe 403."""
        response = client.post(
            "/api/v1/gate_control/trigger",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 403

    def test_trigger_gate_requires_auth(self, client: TestClient):
        """Sem token → 401."""
        response = client.post("/api/v1/gate_control/trigger")
        assert response.status_code == 401
