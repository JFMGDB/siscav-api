import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.crud import crud_access_log, crud_authorized_plate
from apps.api.src.api.v1.db.session import get_db
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
    Receive access log from IoT device.
    - Uploads image.
    - Verifies plate against whitelist.
    - Logs access attempt.
    """
    # 1. Normalize plate
    # Simple normalization: uppercase and remove non-alphanumeric
    # This should match the logic used in AuthorizedPlate (which is done via DB trigger,
    # but we need it here for lookup).
    # Ideally, we should have a shared utility for this. For now, simple python logic.
    normalized_plate = "".join(c for c in plate if c.isalnum()).upper()

    # 2. Check whitelist
    # We need a method to get by normalized_plate.
    # I'll add `get_by_normalized_plate` to crud_authorized_plate later if needed,
    # or just use a direct query here for now or update crud.
    # Let's assume we update crud_authorized_plate or query all and filter (inefficient).
    # Better: Update crud_authorized_plate to have get_by_normalized_plate.
    
    # For now, let's implement the lookup logic directly or call a new crud method.
    # I will update crud_authorized_plate in the next step to support this efficiently.
    # But wait, I can't leave this broken.
    # Let's check if I can do it with existing tools.
    # existing: get, get_multi.
    # I need `get_by_normalized_plate`.
    
    # Let's assume I will add it.
    from sqlalchemy import select
    from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
    
    authorized_plate = db.scalar(
        select(AuthorizedPlate).where(AuthorizedPlate.normalized_plate == normalized_plate)
    )
    
    status = AccessStatus.Denied
    authorized_plate_id = None
    
    if authorized_plate:
        status = AccessStatus.Authorized
        authorized_plate_id = authorized_plate.id

    # 3. Save image
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a unique filename or use timestamp
    import uuid
    file_ext = Path(file.filename).suffix if file.filename else ".jpg"
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / file_name
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 4. Create Log
    access_log = crud_access_log.create(
        db,
        plate_string_detected=plate,
        status=status,
        image_storage_key=str(file_path),
        authorized_plate_id=authorized_plate_id,
    )
    
    return access_log
