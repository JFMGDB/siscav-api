"""Tests for POST /api/v1/ml/classify-vehicle."""

import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def fake_cv2_module():
    m = MagicMock()
    m.IMREAD_COLOR = 1
    m.imdecode = MagicMock(return_value=MagicMock(name="bgr_frame"))
    return m


@pytest.fixture
def fake_numpy_module():
    m = MagicMock()
    m.uint8 = MagicMock(name="uint8")
    m.frombuffer = MagicMock(return_value=MagicMock(name="ndarray"))
    return m


class TestClassifyVehicleRoute:
    def test_requires_auth(self, client: TestClient):
        r = client.post(
            "/api/v1/ml/classify-vehicle",
            files={"file": ("x.jpg", b"dummy", "image/jpeg")},
        )
        assert r.status_code == 401

    def test_stub_works_without_ml_stack(self, client: TestClient, auth_token: str):
        with patch(
            "apps.api.src.api.v1.endpoints.classification.classifier_stack_available",
            return_value=False,
        ):
            r = client.post(
                "/api/v1/ml/classify-vehicle",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.jpg", b"dummy", "image/jpeg")},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["predicted_category"] == "unknown"
        assert data["confidence"] == 0.0

    def test_unsupported_media_type(self, client: TestClient, auth_token: str):
        r = client.post(
            "/api/v1/ml/classify-vehicle",
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
                "apps.api.src.api.v1.endpoints.classification.classifier_stack_available",
                return_value=True,
            ),
            patch.dict(sys.modules, {"cv2": fake_cv2_module, "numpy": fake_numpy_module}),
        ):
            r = client.post(
                "/api/v1/ml/classify-vehicle",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.jpg", b"not-a-real-jpeg", "image/jpeg")},
            )
        assert r.status_code == 400

    def test_accepts_optional_plate_hint(self, client: TestClient, auth_token: str):
        with patch(
            "apps.api.src.api.v1.endpoints.classification.classifier_stack_available",
            return_value=False,
        ):
            r = client.post(
                "/api/v1/ml/classify-vehicle",
                headers={"Authorization": f"Bearer {auth_token}"},
                data={"plate_hint": "ABC1234"},
                files={"file": ("x.jpg", b"dummy", "image/jpeg")},
            )
        assert r.status_code == 200
        assert r.json()["predicted_category"] == "unknown"
