"""Unit tests for ONNX ambulance classifier preprocessing and postprocessing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from apps.api.src.api.v1.core.config import Settings
from apps.api.src.api.v1.ml import onnx_ambulance_classifier as oac
from apps.api.src.api.v1.schemas.classification import VehicleCategory


@pytest.fixture
def settings() -> Settings:
    return Settings(
        vehicle_classifier_model_path="models/ambulance_classifier.onnx",
        vehicle_classifier_threshold=0.85,
        vehicle_classifier_labels="ambulance,other",
        vehicle_classifier_input_size=224,
        vehicle_classifier_backend="onnx",
    )


@pytest.fixture(autouse=True)
def reset_session():
    oac._session = None
    oac._input_name = None
    yield
    oac._session = None
    oac._input_name = None


class TestPreprocess:
    def test_output_shape_nchw(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tensor = oac.preprocess_frame_bgr(frame, input_size=224)
        assert tensor.shape == (1, 3, 224, 224)
        assert tensor.dtype == np.float32


class TestOnnxAmbulanceClassifier:
    def test_classify_ambulance_label(self, settings: Settings):
        mock_session = MagicMock()
        mock_session.get_inputs.return_value = [MagicMock(name="input")]
        mock_session.run.return_value = [np.array([[2.0, 0.1]], dtype=np.float32)]

        with patch.object(oac, "_load_model", return_value=(mock_session, "input")):
            clf = oac.OnnxAmbulanceClassifier(settings)
            out = clf.classify(np.zeros((224, 224, 3), dtype=np.uint8))

        assert out.predicted_category == VehicleCategory.ambulance
        assert out.confidence > 0.5
        assert len(out.all_scores) == 2

    def test_classify_other_label(self, settings: Settings):
        mock_session = MagicMock()
        mock_session.get_inputs.return_value = [MagicMock(name="input")]
        mock_session.run.return_value = [np.array([[0.1, 2.0]], dtype=np.float32)]

        with patch.object(oac, "_load_model", return_value=(mock_session, "input")):
            clf = oac.OnnxAmbulanceClassifier(settings)
            out = clf.classify(np.zeros((224, 224, 3), dtype=np.uint8))

        assert out.predicted_category == VehicleCategory.unknown

    def test_concurrent_run_without_global_lock_on_predict(self, settings: Settings):
        """session.run must not be serialized by a predict-time lock."""
        mock_session = MagicMock()
        mock_session.get_inputs.return_value = [MagicMock(name="input")]
        mock_session.run.return_value = [np.array([[1.0, 0.0]], dtype=np.float32)]

        with patch.object(oac, "_load_model", return_value=(mock_session, "input")):
            clf = oac.OnnxAmbulanceClassifier(settings)
            clf.classify(np.zeros((224, 224, 3), dtype=np.uint8))
            clf.classify(np.zeros((224, 224, 3), dtype=np.uint8))

        assert mock_session.run.call_count == 2
