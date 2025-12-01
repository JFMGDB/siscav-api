import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.utils import normalize_plate
from apps.api.src.api.v1.crud import crud_access_log
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.schemas.access_log import AccessLogRead, AccessStatus

router = APIRouter()
settings = get_settings()

# Constantes de validação
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB em bytes
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

# Mapeamento MIME type -> extensões válidas para validação de correspondência
MIME_TO_EXTENSIONS = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/jpg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}


@router.post("/", response_model=AccessLogRead)
def create_access_log(
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()],
    plate: Annotated[str, Form()],
) -> AccessLogRead:
    """
    Recebe log de acesso do dispositivo IoT.

    - Faz upload da imagem
    - Verifica placa contra a whitelist
    - Registra tentativa de acesso
    """
    # Validação da placa: não pode ser vazia ou só espaços
    if not plate or not plate.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plate cannot be empty",
        )

    # Normaliza a placa usando função utilitária compartilhada
    normalized_plate = normalize_plate(plate)

    # Verifica se a placa está na whitelist
    authorized_plate = db.scalar(
        select(AuthorizedPlate).where(AuthorizedPlate.normalized_plate == normalized_plate)
    )

    # Define status e ID da placa autorizada
    access_status = AccessStatus.Denied
    authorized_plate_id = None

    if authorized_plate:
        access_status = AccessStatus.Authorized
        authorized_plate_id = authorized_plate.id

    # Validação de extensão de arquivo
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validação de tamanho (máximo 10MB)
    file.file.seek(0, 2)  # Move para o final do arquivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volta para o início

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f}MB",
        )

    # Validação de MIME type (rejeita se None ou inválido)
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # Validação de correspondência entre extensão e MIME type
    valid_extensions = MIME_TO_EXTENSIONS.get(file.content_type)
    if valid_extensions and file_ext not in valid_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File extension {file_ext} does not match content type {file.content_type}",
        )

    # Salva a imagem no diretório de uploads
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Gera nome único para o arquivo (usa UUID para evitar path traversal)
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / file_name

    # Path traversal check não é necessário pois o nome do arquivo é gerado usando UUID
    # que não pode conter separadores de caminho

    # Salva o arquivo com tratamento de erros
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file",
        ) from error

    # Cria o log de acesso
    access_log = crud_access_log.create(
        db,
        plate_string_detected=plate,
        status=access_status,
        image_storage_key=str(file_path),
        authorized_plate_id=authorized_plate_id,
    )
    return AccessLogRead.model_validate(access_log, from_attributes=True)
