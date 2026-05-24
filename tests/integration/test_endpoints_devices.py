"""Testes de integração para endpoints de dispositivos."""

import pytest
from fastapi.testclient import TestClient

from apps.api.src.api.v1.core.config import get_settings


class TestDevicesEndpoints:
    """Testes para endpoints de dispositivos."""

    def test_scan_bluetooth_devices(self, client: TestClient, auth_token: str):
        """Testa escaneamento de dispositivos Bluetooth."""
        response = client.get(
            "/api/v1/devices/scan",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        devices = response.json()
        assert isinstance(devices, list)
        assert len(devices) > 0
        assert all(d.get("demo") is True for d in devices)

    def test_connect_device(self, client: TestClient, auth_token: str):
        """Testa conexão com dispositivo."""
        response = client.post(
            "/api/v1/devices/connect",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"device_id": "test_device_123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"
        assert data["device_id"] == "test_device_123"
        assert data.get("demo") is True

    def test_get_connection_status(self, client: TestClient, auth_token: str):
        """Testa obtenção de status de conexão."""
        response = client.get(
            "/api/v1/devices/status",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        assert data.get("demo") is True

    def test_disconnect_device(self, client: TestClient, auth_token: str):
        """Testa desconexão de dispositivo."""
        response = client.post(
            "/api/v1/devices/disconnect",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"
        assert data.get("demo") is True

    def test_devices_scan_returns_501_when_demo_disabled(
        self, client: TestClient, auth_token: str, monkeypatch: pytest.MonkeyPatch
    ):
        """IOT_DEVICE_DEMO_API=false → 501 (DEV-01)."""
        monkeypatch.setenv("IOT_DEVICE_DEMO_API", "false")
        get_settings.cache_clear()
        try:
            response = client.get(
                "/api/v1/devices/scan",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert response.status_code == 501
            assert "Web Bluetooth" in response.json().get("detail", "")
        finally:
            monkeypatch.delenv("IOT_DEVICE_DEMO_API", raising=False)
            get_settings.cache_clear()
