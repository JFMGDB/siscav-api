"""Manual smoke test for ONNX ambulance classifier.

Usage (from siscav-api root):
  uv sync --extra dev --extra onnx
  uv run python tests/manual/smoke_onnx_classifier.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np

# Repo root on PYTHONPATH when invoked via uv run from siscav-api
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.ml.onnx_ambulance_classifier import OnnxAmbulanceClassifier


def main() -> int:
    os.environ.setdefault("VEHICLE_CLASSIFIER_BACKEND", "onnx")
    get_settings.cache_clear()
    settings = get_settings()

    model_path = Path(settings.vehicle_classifier_model_path)
    if not model_path.is_absolute():
        from apps.api.src.api.v1.core.config import _find_repo_root

        model_path = _find_repo_root() / model_path

    if not model_path.is_file():
        print(f"Model not found: {model_path}", file=sys.stderr)
        return 1

    print(f"Model: {model_path}")
    print(f"Labels: {settings.vehicle_classifier_labels}")
    print(f"Threshold: {settings.vehicle_classifier_threshold}")

    classifier = OnnxAmbulanceClassifier(settings)
    dummy = np.zeros(
        (settings.vehicle_classifier_input_size, settings.vehicle_classifier_input_size, 3),
        dtype=np.uint8,
    )

    t0 = time.perf_counter()
    result = classifier.classify(dummy)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"Latency: {elapsed_ms:.1f} ms")
    print(f"Predicted: {result.predicted_category.value} ({result.confidence:.4f})")
    print(f"Backend: {result.classifier_backend} / {result.model_version}")
    for score in result.all_scores:
        print(f"  - {score.category.value}: {score.score:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
