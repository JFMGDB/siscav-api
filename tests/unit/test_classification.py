import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.ml.classifier import StubVehicleClassifier, get_vehicle_classifier
from apps.api.src.api.v1.schemas.classification import VehicleCategory, VehicleClassificationResult


class TestClassificationContracts:
    @pytest.mark.parametrize(
        "category",
        [
            VehicleCategory.car,
            VehicleCategory.motorcycle,
            VehicleCategory.truck,
            VehicleCategory.bus,
            VehicleCategory.van,
            VehicleCategory.unknown,
        ],
    )
    def test_vehicle_category_values(self, category: VehicleCategory):
        assert category.value in {c.value for c in VehicleCategory}

    def test_vehicle_classification_result_valid(self):
        result = VehicleClassificationResult(
            predicted_category=VehicleCategory.car,
            confidence=0.85,
            model_version="test-v1",
            classifier_backend="stub",
        )
        assert result.predicted_category == VehicleCategory.car
        assert result.confidence == 0.85

    def test_vehicle_classification_result_rejects_invalid_confidence(self):
        with pytest.raises(ValidationError):
            VehicleClassificationResult(
                predicted_category=VehicleCategory.car,
                confidence=1.5,
            )

    def test_stub_classifier_returns_unknown(self):
        c = StubVehicleClassifier()
        out = c.classify(None)
        assert out.predicted_category == VehicleCategory.unknown
        assert out.confidence == 0.0
        assert out.model_version
        assert out.classifier_backend

    def test_stub_classifier_accepts_plate_hint(self):
        c = StubVehicleClassifier()
        out = c.classify(None, plate_hint="ABC1234")
        assert out.predicted_category == VehicleCategory.unknown

    def test_factory_returns_stub_backend(self):
        get_settings.cache_clear()
        with patch.dict(os.environ, {"VEHICLE_CLASSIFIER_BACKEND": "stub"}, clear=False):
            c = get_vehicle_classifier()
        assert c.backend_name == "stub"
        out = c.classify(None)
        assert out.predicted_category == VehicleCategory.unknown
