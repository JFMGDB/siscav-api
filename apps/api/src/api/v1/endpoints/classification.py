"""Vehicle classification endpoint (optional ML integration)."""

import logging
from functools import partial
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from apps.api.src.api.v1.core import error_messages as err
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.deps import get_classifier, get_current_client_admin_user
from apps.api.src.api.v1.ml.classifier import (
    StubVehicleClassifier,
    classifier_onnx_stack_available,
    classifier_stack_available,
)
from apps.api.src.api.v1.ml.onnx_ambulance_classifier import OnnxAmbulanceClassifier
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.classification import VehicleClassificationResult

logger = logging.getLogger(__name__)

router = APIRouter()

_ALLOWED_CT = frozenset(
    {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }
)


@router.post(
    "/classify-vehicle",
    response_model=VehicleClassificationResult,
    summary="Vehicle category classification from image (authenticated operator)",
)
async def classify_vehicle_from_image(
    file: Annotated[UploadFile, File(description="Frame or crop with vehicle visible")],
    current_user: Annotated[User, Depends(get_current_client_admin_user)],
    classifier=Depends(get_classifier),
    plate_hint: Annotated[
        str | None,
        Form(description="Optional plate string for additional context (ignored by stub)"),
    ] = None,
) -> VehicleClassificationResult:
    """
    Executes vehicle classification using a backend-owned classifier abstraction.

    - Auth: JWT Bearer (any authenticated user).
    - Multipart: `file` (required), `plate_hint` (optional).
    - Dependencies: real classifiers may require optional ML deps; stub works without them.
    """

    _ = current_user  # dependency enforces a valid Bearer token

    if not file.content_type or file.content_type.split(";")[0].strip().lower() not in _ALLOWED_CT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.UNSUPPORTED_IMAGE_TYPE,
        )

    settings = get_settings()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    raw = await file.read()
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=err.IMAGE_EXCEEDS_MAX.format(max_mb=settings.max_file_size_mb),
        )

    if isinstance(classifier, StubVehicleClassifier):
        if not classifier_stack_available():
            return classifier.classify(None, plate_hint=plate_hint)
    elif isinstance(classifier, OnnxAmbulanceClassifier):
        if not classifier_onnx_stack_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=err.CLASSIFICATION_ONNX_UNAVAILABLE,
            )
    elif not classifier_stack_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=err.CLASSIFICATION_UNAVAILABLE,
        )

    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    arr = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.IMAGE_DECODE_FAILED,
        )

    try:
        return await run_in_threadpool(partial(classifier.classify, frame, plate_hint=plate_hint))
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error in vehicle classification pipeline")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err.CLASSIFICATION_PROCESS_FAILED,
        ) from None
