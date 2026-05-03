"""Rota opcional: OCR de placas a partir de imagem (EasyOCR + OpenCV)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.deps import get_current_user
from apps.api.src.api.v1.ml.plate_ocr import ml_stack_available, recognize_plates_from_bgr
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.plate_recognition import PlateRecognizeItem, PlateRecognizeResponse
from apps.api.src.api.v1.utils.plate import normalize_plate

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
    current_user: Annotated[User, Depends(get_current_user)],
) -> PlateRecognizeResponse:
    """
    Executa o pipeline de deteção por contornos + EasyOCR (mesma lógica base do script
    `ml/recognize-plate.py`), devolvendo candidatos com **7 caracteres** alfanuméricos.

    **Requer** pacotes opcionais (`requirements-ml.txt`). Sem eles, responde **503**.

    **Autenticação:** JWT Bearer (qualquer utilizador autenticado).

    Não grava log de acesso nem imagem — use `POST /api/v1/access_logs/` com o texto escolhido.
    """
    _ = current_user  # dependência garante Bearer válido

    if not ml_stack_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "OCR não disponível: instale as dependências ML "
                "(ex.: pip install -r requirements-ml.txt) e reinicie o servidor."
            ),
        )

    if not file.content_type or file.content_type.split(";")[0].strip().lower() not in _ALLOWED_CT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de ficheiro não suportado. Use JPEG, PNG ou WebP.",
        )

    settings = get_settings()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    raw = await file.read()
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Imagem excede {settings.max_file_size_mb} MB.",
        )

    import cv2
    import numpy as np

    arr = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível decodificar a imagem.",
        )

    try:
        raw_list = recognize_plates_from_bgr(frame)
    except Exception:
        logger.exception("Erro no pipeline OCR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao processar OCR.",
        ) from None

    items = [
        PlateRecognizeItem(
            plate_raw=c["plate_raw"],
            normalized_plate=normalize_plate(c["plate_raw"]),
            plate_color_hint=c["plate_color_hint"],
        )
        for c in raw_list
    ]
    return PlateRecognizeResponse(candidates=items)
