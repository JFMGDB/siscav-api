"""Integration tests for auto-open gate on authorized access log ingest."""

from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest
from fastapi.testclient import TestClient

from apps.api.src.api.v1.core.config import get_settings
from tests.conftest import TEST_DEVICE_INGEST_KEY

_DEVICE = {"X-Device-Key": TEST_DEVICE_INGEST_KEY}


def _create_whitelist_plate(client: TestClient, auth_token: str, plate: str = "ABC-1234") -> None:
    client.post(
        "/api/v1/whitelist/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"plate": plate, "normalized_plate": "ABC1234", "description": "Demo"},
    )


def _post_access_log(_client: TestClient, plate: str = "ABC-1234"):
    file_content = b"fake image content"
    files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
    data = {"plate": plate}
    return files, data, file_content


class TestAccessLogAutoOpenGate:
    """Auto-open gate after authorized access log (GATE_AUTO_OPEN_ON_AUTHORIZE)."""

    def test_create_access_log_returns_201(self, client: TestClient, auth_token: str):
        _create_whitelist_plate(client, auth_token)
        files, data, _ = _post_access_log(client)
        response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
        assert response.status_code == 201

    def test_auto_open_flag_off_no_gate_trigger(
        self, client: TestClient, auth_token: str, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GATE_AUTO_OPEN_ON_AUTHORIZE", "false")
        get_settings.cache_clear()
        try:
            _create_whitelist_plate(client, auth_token)
            files, data, _ = _post_access_log(client)
            response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
            assert response.status_code == 201
            assert response.json().get("gate_trigger") is None
        finally:
            monkeypatch.delenv("GATE_AUTO_OPEN_ON_AUTHORIZE", raising=False)
            get_settings.cache_clear()

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_auto_open_when_authorized_calls_actuator(
        self,
        mock_urlopen: MagicMock,
        client: TestClient,
        auth_token: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_resp
        mock_cm.__exit__.return_value = None
        mock_urlopen.return_value = mock_cm

        monkeypatch.setenv("GATE_AUTO_OPEN_ON_AUTHORIZE", "true")
        monkeypatch.setenv("GATE_ACTUATOR_URL", "http://127.0.0.1:9080/open")
        get_settings.cache_clear()
        try:
            _create_whitelist_plate(client, auth_token)
            files, data, _ = _post_access_log(client)
            response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
            assert response.status_code == 201
            body = response.json()
            assert body["status"] == "Authorized"
            gate = body["gate_trigger"]
            assert gate is not None
            assert gate["integration"] == "live"
            assert gate["acknowledged"] is True
            assert gate["status"] == "ok"
            mock_urlopen.assert_called_once()
        finally:
            monkeypatch.delenv("GATE_AUTO_OPEN_ON_AUTHORIZE", raising=False)
            monkeypatch.delenv("GATE_ACTUATOR_URL", raising=False)
            get_settings.cache_clear()

    def test_auto_open_skipped_when_denied(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GATE_AUTO_OPEN_ON_AUTHORIZE", "true")
        get_settings.cache_clear()
        try:
            files, data, _ = _post_access_log(client, plate="XYZ-9999")
            with patch("apps.api.src.api.v1.controllers.gate_controller.urlopen") as mock_urlopen:
                response = client.post(
                    "/api/v1/access_logs/", files=files, data=data, headers=_DEVICE
                )
            assert response.status_code == 201
            assert response.json()["status"] == "Denied"
            assert response.json().get("gate_trigger") is None
            mock_urlopen.assert_not_called()
        finally:
            monkeypatch.delenv("GATE_AUTO_OPEN_ON_AUTHORIZE", raising=False)
            get_settings.cache_clear()

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_actuator_timeout_returns_201_with_error_gate_trigger(
        self,
        mock_urlopen: MagicMock,
        client: TestClient,
        auth_token: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        mock_urlopen.side_effect = TimeoutError()

        monkeypatch.setenv("GATE_AUTO_OPEN_ON_AUTHORIZE", "true")
        monkeypatch.setenv("GATE_ACTUATOR_URL", "http://127.0.0.1:9080/open")
        get_settings.cache_clear()
        try:
            _create_whitelist_plate(client, auth_token)
            files, data, _ = _post_access_log(client)
            response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
            assert response.status_code == 201
            body = response.json()
            assert body["status"] == "Authorized"
            gate = body["gate_trigger"]
            assert gate["status"] == "error"
            assert gate["reason"] == "actuator_timeout"
            assert gate["acknowledged"] is False
            assert body["image_storage_key"].endswith(".jpg")
        finally:
            monkeypatch.delenv("GATE_AUTO_OPEN_ON_AUTHORIZE", raising=False)
            monkeypatch.delenv("GATE_ACTUATOR_URL", raising=False)
            get_settings.cache_clear()

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_connection_refused_returns_201_with_error_gate_trigger(
        self,
        mock_urlopen: MagicMock,
        client: TestClient,
        auth_token: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        mock_urlopen.side_effect = URLError("Connection refused")

        monkeypatch.setenv("GATE_AUTO_OPEN_ON_AUTHORIZE", "true")
        monkeypatch.setenv("GATE_ACTUATOR_URL", "http://127.0.0.1:9080/open")
        get_settings.cache_clear()
        try:
            _create_whitelist_plate(client, auth_token)
            files, data, _ = _post_access_log(client)
            response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
            assert response.status_code == 201
            gate = response.json()["gate_trigger"]
            assert gate["status"] == "error"
            assert gate["reason"] == "connection_refused"
        finally:
            monkeypatch.delenv("GATE_AUTO_OPEN_ON_AUTHORIZE", raising=False)
            monkeypatch.delenv("GATE_ACTUATOR_URL", raising=False)
            get_settings.cache_clear()

    def test_auto_open_simulated_when_url_unset(
        self, client: TestClient, auth_token: str, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GATE_AUTO_OPEN_ON_AUTHORIZE", "true")
        monkeypatch.delenv("GATE_ACTUATOR_URL", raising=False)
        get_settings.cache_clear()
        try:
            _create_whitelist_plate(client, auth_token)
            files, data, _ = _post_access_log(client)
            response = client.post("/api/v1/access_logs/", files=files, data=data, headers=_DEVICE)
            assert response.status_code == 201
            gate = response.json()["gate_trigger"]
            assert gate["integration"] == "simulated"
            assert gate["status"] == "ok"
        finally:
            monkeypatch.delenv("GATE_AUTO_OPEN_ON_AUTHORIZE", raising=False)
            get_settings.cache_clear()
