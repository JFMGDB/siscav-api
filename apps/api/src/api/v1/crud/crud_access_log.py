from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.access_log import AccessLog


def create(
    db: Session,
    plate_string_detected: str,
    status: str,
    image_storage_key: str,
    authorized_plate_id: UUID | None = None,
) -> AccessLog:
    db_obj = AccessLog(
        plate_string_detected=plate_string_detected,
        status=status,
        image_storage_key=image_storage_key,
        authorized_plate_id=authorized_plate_id,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
