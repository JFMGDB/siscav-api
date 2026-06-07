"""ONNX Runtime ambulance classifier (CPU-only, Render Free Tier)."""

from __future__ import annotations

import importlib.util
import logging
import threading
from pathlib import Path
from typing import Any

import numpy as np

from apps.api.src.api.v1.core.config import Settings, _find_repo_root
from apps.api.src.api.v1.schemas.classification import (
    ClassificationConfidence,
    VehicleCategory,
    VehicleClassificationResult,
)

logger = logging.getLogger(__name__)

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_session: Any | None = None
_input_name: str | None = None
_load_lock = threading.Lock()


def onnx_stack_available() -> bool:
    return (
        importlib.util.find_spec("onnxruntime") is not None
        and importlib.util.find_spec("cv2") is not None
        and importlib.util.find_spec("numpy") is not None
    )


def _resolve_model_path(settings: Settings) -> Path:
    raw = settings.vehicle_classifier_model_path.strip()
    path = Path(raw)
    if not path.is_absolute():
        path = _find_repo_root() / path
    return path


def _load_model(settings: Settings) -> tuple[Any, str]:
    global _session, _input_name
    if _session is not None and _input_name is not None:
        return _session, _input_name
    with _load_lock:
        if _session is not None and _input_name is not None:
            return _session, _input_name
        import onnxruntime as ort

        model_path = _resolve_model_path(settings)
        if not model_path.is_file():
            msg = f"ONNX model not found: {model_path}"
            raise FileNotFoundError(msg)
        logger.info("Loading ONNX ambulance classifier from %s", model_path)
        session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )
        input_name = session.get_inputs()[0].name
        _session = session
        _input_name = input_name
        return session, input_name


def preprocess_frame_bgr(frame_bgr: Any, *, input_size: int) -> np.ndarray:
    import cv2

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (input_size, input_size), interpolation=cv2.INTER_LINEAR)
    arr = resized.astype(np.float32) / 255.0
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD
    chw = np.transpose(arr, (2, 0, 1))
    return np.expand_dims(chw, axis=0).astype(np.float32)


def _softmax(logits: np.ndarray) -> np.ndarray:
    x = logits.astype(np.float64)
    x = x - np.max(x)
    exp = np.exp(x)
    return (exp / np.sum(exp)).astype(np.float32)


class OnnxAmbulanceClassifier:
    """Binary ambulance classifier backed by ONNX Runtime."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._labels = [
            label.strip()
            for label in settings.vehicle_classifier_labels.split(",")
            if label.strip()
        ]
        if len(self._labels) < 2:
            self._labels = ["ambulance", "other"]

    @property
    def model_version(self) -> str:
        return "mobilenetv2-ambulance-onnx-v1"

    @property
    def backend_name(self) -> str:
        return "onnx"

    def warm_up(self) -> None:
        size = self._settings.vehicle_classifier_input_size
        dummy = np.zeros((size, size, 3), dtype=np.uint8)
        self.classify(dummy)

    def classify(
        self,
        frame_bgr: Any,
        *,
        plate_hint: str | None = None,
    ) -> VehicleClassificationResult:
        _ = plate_hint
        session, input_name = _load_model(self._settings)
        tensor = preprocess_frame_bgr(
            frame_bgr,
            input_size=self._settings.vehicle_classifier_input_size,
        )
        outputs = session.run(None, {input_name: tensor})
        logits = np.asarray(outputs[0]).reshape(-1)
        probs = _softmax(logits)

        all_scores: list[ClassificationConfidence] = []
        for idx, label in enumerate(self._labels):
            if idx >= len(probs):
                break
            category = (
                VehicleCategory.ambulance
                if label.lower() == "ambulance"
                else VehicleCategory.unknown
            )
            all_scores.append(ClassificationConfidence(category=category, score=float(probs[idx])))

        best_idx = int(np.argmax(probs))
        best_label = self._labels[best_idx] if best_idx < len(self._labels) else "other"
        predicted = (
            VehicleCategory.ambulance
            if best_label.lower() == "ambulance"
            else VehicleCategory.unknown
        )
        confidence = float(probs[best_idx]) if best_idx < len(probs) else 0.0

        return VehicleClassificationResult(
            predicted_category=predicted,
            confidence=confidence,
            all_scores=all_scores,
            model_version=self.model_version,
            classifier_backend=self.backend_name,
        )
