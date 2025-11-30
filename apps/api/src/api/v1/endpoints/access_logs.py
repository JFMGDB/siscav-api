import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.crud import crud_access_log
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.schemas.access_log import AccessLogRead, AccessStatus

router = APIRouter()
settings = get_settings()


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
    # Normaliza a placa: maiúsculas e remove caracteres não alfanuméricos
    normalized_plate = "".join(c for c in plate if c.isalnum()).upper()

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

    # Salva a imagem no diretório de uploads
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Gera nome único para o arquivo
    file_ext = Path(file.filename).suffix if file.filename else ".jpg"
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / file_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Cria o log de acesso
    access_log = crud_access_log.create(
        db,
        plate_string_detected=plate,
        status=access_status,
        image_storage_key=str(file_path),
        authorized_plate_id=authorized_plate_id,
    )
    return AccessLogRead.model_validate(access_log, from_attributes=True)
