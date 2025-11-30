from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


def get(db: Session, id: UUID) -> AuthorizedPlate | None:
    return db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == id))


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[AuthorizedPlate]:
    return list(db.scalars(select(AuthorizedPlate).offset(skip).limit(limit)))


def create(db: Session, obj_in: AuthorizedPlateCreate) -> AuthorizedPlate:
    db_obj = AuthorizedPlate(
        plate=obj_in.plate,
        normalized_plate=obj_in.normalized_plate,
        description=obj_in.description,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: AuthorizedPlate, obj_in: AuthorizedPlateCreate) -> AuthorizedPlate:
    db_obj.plate = obj_in.plate
    db_obj.normalized_plate = obj_in.normalized_plate
    db_obj.description = obj_in.description
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: UUID) -> AuthorizedPlate | None:
    obj = db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == id))
    if obj:
        db.delete(obj)
        db.commit()
    return obj
