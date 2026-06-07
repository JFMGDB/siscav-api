"""Classify real images with ONNX ambulance model.

Usage:
  uv sync --extra dev --extra onnx
  uv run python tests/manual/classify_images.py \\
    path/to/ambulance.jpg path/to/car.jpg
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import cv2

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.ml.onnx_ambulance_classifier import OnnxAmbulanceClassifier


def classify_path(classifier: OnnxAmbulanceClassifier, path: Path, threshold: float) -> None:
    frame = cv2.imread(str(path))
    if frame is None:
        print(f"ERROR: could not decode {path}")
        return

    t0 = time.perf_counter()
    result = classifier.classify(frame)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    auto_auth = result.predicted_category.value == "ambulance" and result.confidence >= threshold
    print(f"\n=== {path.name} ===")
    print(f"  predicted: {result.predicted_category.value}")
    print(f"  confidence: {result.confidence:.4f}")
    print(f"  latency: {elapsed_ms:.1f} ms")
    print(f"  auto-authorize (>= {threshold}): {auto_auth}")
    for score in result.all_scores:
        print(f"    {score.category.value}: {score.score:.4f}")


def main() -> int:
    os.environ.setdefault("VEHICLE_CLASSIFIER_BACKEND", "onnx")
    get_settings.cache_clear()
    settings = get_settings()

    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        repo = Path(__file__).resolve().parents[3]
        paths = [
            repo.parent / "siscav-web" / "public" / "Ambulnacia.jpg",
            repo.parent / "siscav-web" / "public" / "Ambulancia-Samu-2.jpg",
            repo.parent / "siscav-web" / "public" / "carro-completo.jpeg",
            repo.parent / "siscav-web" / "public" / "carro-2.webp",
        ]

    classifier = OnnxAmbulanceClassifier(settings)
    classifier.warm_up()

    print(f"Model: {settings.vehicle_classifier_model_path}")
    print(f"Labels: {settings.vehicle_classifier_labels}")
    print(f"Threshold: {settings.vehicle_classifier_threshold}")

    for path in paths:
        if not path.is_file():
            print(f"SKIP missing: {path}")
            continue
        classify_path(classifier, path, settings.vehicle_classifier_threshold)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
