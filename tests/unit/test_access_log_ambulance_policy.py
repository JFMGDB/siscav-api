"""Tests for ambulance auto-authorization in access log ingest."""

from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import UploadFile

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.schemas.access_log import AccessStatus
from apps.api.src.api.v1.schemas.classification import (
    VehicleCategory,
    VehicleClassificationResult,
)


def _upload_file(content: bytes = b"fake") -> UploadFile:
    return UploadFile(
        filename="test.jpg", file=BytesIO(content), headers={"content-type": "image/jpeg"}
    )


def _mock_access_log(status: AccessStatus) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        timestamp=datetime.now(UTC),
        plate_string_detected="ABC1234",
        status=status,
        image_storage_key="uploads/x.jpg",
        authorized_plate_id=None,
        is_automatic=status == AccessStatus.Authorized,
        ocr_success=True,
    )


@pytest.mark.anyio
class TestAccessLogAmbulancePolicy:
    async def test_ambulance_above_threshold_authorizes_without_whitelist(self):
        db = MagicMock()
        controller = AccessLogController(db)
        settings = MagicMock()
        settings.vehicle_classifier_backend = "onnx"
        settings.vehicle_classifier_threshold = 0.60
        settings.gate_auto_open_on_authorize = False
        settings.upload_dir = "uploads"
        settings.max_file_size_mb = 10
        controller.settings = settings

        controller.plate_repository = MagicMock()
        controller.plate_repository.get_by_normalized_plate = MagicMock(return_value=None)

        classification = VehicleClassificationResult(
            predicted_category=VehicleCategory.ambulance,
            confidence=0.92,
            model_version="test",
            classifier_backend="onnx",
        )
        mock_repo = MagicMock()
        mock_repo.create = MagicMock(return_value=_mock_access_log(AccessStatus.Authorized))
        controller.access_log_repository = mock_repo

        frame = MagicMock()
        mock_cv2 = MagicMock()
        mock_cv2.imdecode.return_value = frame
        mock_cv2.IMREAD_COLOR = 1
        mock_np = MagicMock()
        mock_np.frombuffer.return_value = MagicMock()
        mock_np.uint8 = "uint8"
        mock_classifier = MagicMock()

        with (
            patch(
                "apps.api.src.api.v1.controllers.access_log_controller.classifier_onnx_stack_available",
                return_value=True,
            ),
            patch(
                "apps.api.src.api.v1.controllers.access_log_controller.get_vehicle_classifier",
                return_value=mock_classifier,
            ),
            patch(
                "apps.api.src.api.v1.controllers.access_log_controller.run_in_threadpool",
                new=AsyncMock(return_value=classification),
            ),
            patch("builtins.open", MagicMock()),
            patch("pathlib.Path.mkdir"),
            patch.dict(
                "sys.modules",
                {"cv2": mock_cv2, "numpy": mock_np},
            ),
        ):
            result = await controller.create_access_log(
                plate="ABC1234",
                file=_upload_file(),
                ingest_via_device=True,
            )

        assert result.status == AccessStatus.Authorized
        assert result.vehicle_classification is not None
        assert result.vehicle_classification.predicted_category == VehicleCategory.ambulance

    async def test_below_threshold_falls_back_to_whitelist_denied(self):
        db = MagicMock()
        controller = AccessLogController(db)
        settings = MagicMock()
        settings.vehicle_classifier_backend = "onnx"
        settings.vehicle_classifier_threshold = 0.60
        settings.gate_auto_open_on_authorize = False
        settings.upload_dir = "uploads"
        settings.max_file_size_mb = 10
        controller.settings = settings

        controller.plate_repository = MagicMock()
        controller.plate_repository.get_by_normalized_plate = MagicMock(return_value=None)

        classification = VehicleClassificationResult(
            predicted_category=VehicleCategory.ambulance,
            confidence=0.55,
            model_version="test",
            classifier_backend="onnx",
        )
        mock_repo = MagicMock()
        mock_repo.create = MagicMock(return_value=_mock_access_log(AccessStatus.Denied))
        controller.access_log_repository = mock_repo

        mock_cv2 = MagicMock()
        mock_cv2.imdecode.return_value = MagicMock()
        mock_cv2.IMREAD_COLOR = 1
        mock_np = MagicMock()
        mock_np.frombuffer.return_value = MagicMock()
        mock_np.uint8 = "uint8"

        with (
            patch(
                "apps.api.src.api.v1.controllers.access_log_controller.classifier_onnx_stack_available",
                return_value=True,
            ),
            patch(
                "apps.api.src.api.v1.controllers.access_log_controller.get_vehicle_classifier",
                return_value=MagicMock(),
            ),
            patch(
                "apps.api.src.api.v1.controllers.access_log_controller.run_in_threadpool",
                new=AsyncMock(return_value=classification),
            ),
            patch("builtins.open", MagicMock()),
            patch("pathlib.Path.mkdir"),
            patch.dict(
                "sys.modules",
                {"cv2": mock_cv2, "numpy": mock_np},
            ),
        ):
            result = await controller.create_access_log(
                plate="ABC1234",
                file=_upload_file(),
            )

        assert result.status == AccessStatus.Denied
