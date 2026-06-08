"""OCR de placas a partir de imagem (EasyOCR + OpenCV)."""

import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core import error_messages as err
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.deps import get_current_client_admin_user
from apps.api.src.api.v1.ml.plate_ocr import (
    ml_stack_available,
    ocr_engine_ready,
    ocr_engine_unavailable_reason,
    recognize_plates_from_bgr,
)
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.ocr_attempt_repository import OcrAttemptRepository
from apps.api.src.api.v1.schemas.plate_recognition import PlateRecognizeItem, PlateRecognizeResponse
from apps.api.src.api.v1.utils.plate import normalize_plate, validate_brazilian_plate

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
    "/recognize-plate",
    response_model=PlateRecognizeResponse,
    summary="OCR de placa em imagem (operador autenticado)",
)
async def recognize_plate_from_image(
    file: Annotated[UploadFile, File(description="Frame ou recorte com veículo / placa visível")],
    current_user: Annotated[User, Depends(get_current_client_admin_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PlateRecognizeResponse:
    """
    Executa o pipeline de deteção por contornos + EasyOCR (mesma lógica base do script
    `ml/recognize-plate.py`), devolvendo candidatos com **7 caracteres** alfanuméricos.

    **Autenticação:** JWT Bearer (administrador do cliente).

    Regista tentativa em `ocr_attempts` para métricas do dashboard. Não grava log de acesso
    nem imagem — use `POST /api/v1/access_logs/` com o texto escolhido.
    """
    if not ml_stack_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=err.OCR_UNAVAILABLE,
        )

    if not ocr_engine_ready():
        try:
            from apps.api.src.api.v1.ml.plate_ocr import warm_up_easyocr

            await run_in_threadpool(warm_up_easyocr)
        except Exception:
            reason = ocr_engine_unavailable_reason() or "EasyOCR engine not ready"
            logger.error("recognize-plate rejected: %s", reason)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=reason,
            ) from None
        if not ocr_engine_ready():
            reason = ocr_engine_unavailable_reason() or "EasyOCR engine not ready"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=reason,
            )

    if not file.content_type or file.content_type.split(";")[0].strip().lower() not in _ALLOWED_CT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.UNSUPPORTED_IMAGE_TYPE,
        )

    request_started_at = time.perf_counter()
    settings = get_settings()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    raw = await file.read()
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=err.IMAGE_EXCEEDS_MAX.format(max_mb=settings.max_file_size_mb),
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
        inference_started_at = time.perf_counter()
        raw_list = await run_in_threadpool(recognize_plates_from_bgr, frame)
    except Exception:
        logger.exception("Erro no pipeline OCR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err.OCR_PROCESS_FAILED,
        ) from None

    inference_ms = round((time.perf_counter() - inference_started_at) * 1000)
    total_ms = round((time.perf_counter() - request_started_at) * 1000)
    logger.info(
        "recognize-plate inference_ms=%s total_ms=%s candidates=%s",
        inference_ms,
        total_ms,
        len(raw_list),
    )

    items = [
        PlateRecognizeItem(
            plate_raw=c["plate_raw"],
            normalized_plate=normalize_plate(c["plate_raw"]),
            plate_color_hint=c["plate_color_hint"],
            confidence=c["confidence"],
        )
        for c in raw_list
    ]

    ocr_success = any(
        validate_brazilian_plate(item.normalized_plate or item.plate_raw)[0] for item in items
    )
    OcrAttemptRepository.create(
        db,
        success=ocr_success,
        owner_user_id=current_user.id,
    )

    return PlateRecognizeResponse(candidates=items)
