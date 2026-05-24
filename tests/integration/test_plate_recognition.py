"""Testes da rota opcional POST /api/v1/ml/recognize-plate."""

import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.src.api.v1.core.config import get_settings


@pytest.fixture
def fake_cv2_module():
    """cv2 sem instalar opencv: imdecode devolve frame BGR fictício."""
    m = MagicMock()
    m.IMREAD_COLOR = 1
    m.imdecode = MagicMock(return_value=MagicMock(name="bgr_frame"))
    return m


@pytest.fixture
def fake_numpy_module():
    """numpy sem instalar o pacote (import lazy no handler)."""
    m = MagicMock()
    m.uint8 = MagicMock(name="uint8")
    m.frombuffer = MagicMock(return_value=MagicMock(name="ndarray"))
    return m


class TestRecognizePlateRoute:
    def test_requires_auth(self, client: TestClient):
        r = client.post(
            "/api/v1/ml/recognize-plate",
            files={"file": ("x.jpg", b"dummy", "image/jpeg")},
        )
        assert r.status_code == 401

    def test_ml_stack_unavailable_503(self, client: TestClient, auth_token: str):
        with patch(
            "apps.api.src.api.v1.endpoints.plate_recognition.ml_stack_available",
            return_value=False,
        ):
            r = client.post(
                "/api/v1/ml/recognize-plate",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.jpg", b"dummy", "image/jpeg")},
            )
        assert r.status_code == 503
        assert "OCR" in r.json().get("detail", "")

    def test_unsupported_media_type(self, client: TestClient, auth_token: str):
        with patch(
            "apps.api.src.api.v1.endpoints.plate_recognition.ml_stack_available",
            return_value=True,
        ):
            r = client.post(
                "/api/v1/ml/recognize-plate",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.gif", b"dummy", "image/gif")},
            )
        assert r.status_code == 400

    def test_decode_fails_400(
        self, client: TestClient, auth_token: str, fake_cv2_module, fake_numpy_module
    ):
        fake_cv2_module.imdecode.return_value = None
        with (
            patch(
                "apps.api.src.api.v1.endpoints.plate_recognition.ml_stack_available",
                return_value=True,
            ),
            patch.dict(sys.modules, {"cv2": fake_cv2_module, "numpy": fake_numpy_module}),
        ):
            r = client.post(
                "/api/v1/ml/recognize-plate",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.jpg", b"not-a-real-jpeg", "image/jpeg")},
            )
        assert r.status_code == 400

    def test_success_candidates(
        self, client: TestClient, auth_token: str, fake_cv2_module, fake_numpy_module
    ):
        with (
            patch(
                "apps.api.src.api.v1.endpoints.plate_recognition.ml_stack_available",
                return_value=True,
            ),
            patch(
                "apps.api.src.api.v1.endpoints.plate_recognition.recognize_plates_from_bgr",
                return_value=[
                    {"plate_raw": "ABC1D23", "plate_color_hint": "branca"},
                ],
            ),
            patch.dict(sys.modules, {"cv2": fake_cv2_module, "numpy": fake_numpy_module}),
        ):
            r = client.post(
                "/api/v1/ml/recognize-plate",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.jpg", b"fake-bytes", "image/jpeg")},
            )
        assert r.status_code == 200
        data = r.json()
        assert len(data["candidates"]) == 1
        assert data["candidates"][0]["plate_raw"] == "ABC1D23"
        assert data["candidates"][0]["normalized_plate"] == "ABC1D23"
        assert data["candidates"][0]["plate_color_hint"] == "branca"

    def test_payload_too_large(
        self, client: TestClient, auth_token: str, fake_cv2_module, monkeypatch
    ):
        monkeypatch.setenv("MAX_FILE_SIZE_MB", "0")
        get_settings.cache_clear()
        try:
            with (
                patch(
                    "apps.api.src.api.v1.endpoints.plate_recognition.ml_stack_available",
                    return_value=True,
                ),
                patch.dict(sys.modules, {"cv2": fake_cv2_module}),
            ):
                r = client.post(
                    "/api/v1/ml/recognize-plate",
                    headers={"Authorization": f"Bearer {auth_token}"},
                    files={"file": ("x.jpg", b"AB", "image/jpeg")},
                )
            assert r.status_code == 413
        finally:
            monkeypatch.delenv("MAX_FILE_SIZE_MB", raising=False)
            get_settings.cache_clear()
