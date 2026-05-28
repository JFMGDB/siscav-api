"""Vehicle classification abstractions.

This module defines the backend-owned contract that classifier implementations must
satisfy. It ships with a stub implementation so the API layer can be prepared before
any real model is integrated.
"""

from __future__ import annotations

import importlib.util
from typing import Any, Protocol, runtime_checkable

from apps.api.src.api.v1.schemas.classification import (
    VehicleCategory,
    VehicleClassificationResult,
)


def classifier_stack_available() -> bool:
    """True when basic image decoding dependencies are available.

    We intentionally keep this separate from OCR's `ml_stack_available()` (which also
    requires easyocr). A future vehicle classifier may only need numpy + opencv.
    """

    return (
        importlib.util.find_spec("cv2") is not None
        and importlib.util.find_spec("numpy") is not None
    )


@runtime_checkable
class VehicleClassifier(Protocol):
    @property
    def model_version(self) -> str: ...

    @property
    def backend_name(self) -> str: ...

    def classify(self, frame_bgr: Any) -> VehicleClassificationResult: ...


class StubVehicleClassifier:
    """Fallback that always returns 'unknown'."""

    @property
    def model_version(self) -> str:
        return "stub-v0"

    @property
    def backend_name(self) -> str:
        return "stub"

    def classify(self, _frame_bgr: Any) -> VehicleClassificationResult:
        return VehicleClassificationResult(
            predicted_category=VehicleCategory.unknown,
            confidence=0.0,
            model_version=self.model_version,
            classifier_backend=self.backend_name,
        )


def get_vehicle_classifier() -> VehicleClassifier:
    """Factory: returns the best available classifier implementation."""

    # Future: switch by env config and availability (local model vs remote service).
    return StubVehicleClassifier()
