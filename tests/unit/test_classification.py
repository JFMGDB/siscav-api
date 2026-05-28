import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from apps.api.src.api.v1.ml.classifier import StubVehicleClassifier, get_vehicle_classifier
from apps.api.src.api.v1.schemas.classification import VehicleCategory


class TestClassificationContracts:
    def test_vehicle_category_has_unknown(self):
        assert VehicleCategory.unknown.value == "unknown"

    def test_stub_classifier_returns_unknown(self):
        c = StubVehicleClassifier()
        out = c.classify(None)
        assert out.predicted_category == VehicleCategory.unknown
        assert out.confidence == 0.0
        assert out.model_version
        assert out.classifier_backend

    def test_factory_returns_vehicle_classifier(self):
        c = get_vehicle_classifier()
        out = c.classify(None)
        assert out.predicted_category == VehicleCategory.unknown


class TestClassificationEndpoint:
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

    def test_decode_fails_400(self, client: TestClient, auth_token: str):
        fake_cv2 = MagicMock()
        fake_cv2.IMREAD_COLOR = 1
        fake_cv2.imdecode = MagicMock(return_value=None)

        fake_np = MagicMock()
        fake_np.uint8 = MagicMock(name="uint8")
        fake_np.frombuffer = MagicMock(return_value=MagicMock(name="ndarray"))

        with (
            patch(
                "apps.api.src.api.v1.endpoints.classification.classifier_stack_available",
                return_value=True,
            ),
            patch.dict(sys.modules, {"cv2": fake_cv2, "numpy": fake_np}),
        ):
            r = client.post(
                "/api/v1/ml/classify-vehicle",
                headers={"Authorization": f"Bearer {auth_token}"},
                files={"file": ("x.jpg", b"not-a-real-jpeg", "image/jpeg")},
            )
        assert r.status_code == 400

