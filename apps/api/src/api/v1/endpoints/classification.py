"""Vehicle classification endpoint (optional ML integration)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.deps import get_classifier, get_current_user
from apps.api.src.api.v1.ml.classifier import StubVehicleClassifier, classifier_stack_available
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
    current_user: Annotated[User, Depends(get_current_user)],
    classifier=Depends(get_classifier),
) -> VehicleClassificationResult:
    """
    Executes vehicle classification using a backend-owned classifier abstraction.

    - Auth: JWT Bearer (any authenticated user).
    - Dependencies: real classifiers may require optional ML deps; stub works without them.
    """

    _ = current_user  # dependency enforces a valid Bearer token

    if not file.content_type or file.content_type.split(";")[0].strip().lower() not in _ALLOWED_CT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Use JPEG, PNG, or WebP.",
        )

    settings = get_settings()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    raw = await file.read()
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Image exceeds {settings.max_file_size_mb} MB.",
        )

    # Stub classifier must work even when the optional ML stack is not installed.
    if not classifier_stack_available():
        if isinstance(classifier, StubVehicleClassifier):
            return classifier.classify(None)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Vehicle classification is not available: install optional ML dependencies "
                "(e.g. pip install -r requirements-ml.txt) and restart the server."
            ),
        )

    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    arr = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode image.",
        )

    try:
        return classifier.classify(frame)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error in vehicle classification pipeline")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process vehicle classification.",
        ) from None

