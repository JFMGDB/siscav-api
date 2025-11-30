from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


def get(db: Session, id: UUID) -> AuthorizedPlate | None:
    return db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == id))


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[AuthorizedPlate]:
    return list(db.scalars(select(AuthorizedPlate).offset(skip).limit(limit)))


def create(db: Session, obj_in: AuthorizedPlateCreate) -> AuthorizedPlate:
    """Cria uma nova placa autorizada.

    Args:
        db: Sessão do banco de dados.
        obj_in: Dados da placa a ser criada.

    Returns:
        AuthorizedPlate: Instância da placa criada.

    Raises:
        ValueError: Se a placa normalizada já existe no banco de dados.
    """
    db_obj = AuthorizedPlate(
        plate=obj_in.plate,
        normalized_plate=obj_in.normalized_plate,
        description=obj_in.description,
    )
    db.add(db_obj)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        error_msg = f"Plate {obj_in.normalized_plate} is already registered"
        raise ValueError(error_msg) from error
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: AuthorizedPlate, obj_in: AuthorizedPlateCreate) -> AuthorizedPlate:
    """Atualiza uma placa autorizada existente.

    Args:
        db: Sessão do banco de dados.
        db_obj: Instância da placa a ser atualizada.
        obj_in: Novos dados da placa.

    Returns:
        AuthorizedPlate: Instância da placa atualizada.

    Raises:
        ValueError: Se a nova placa normalizada já existe para outra placa.
    """
    db_obj.plate = obj_in.plate
    db_obj.normalized_plate = obj_in.normalized_plate
    db_obj.description = obj_in.description
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        error_msg = f"Plate {obj_in.normalized_plate} is already registered"
        raise ValueError(error_msg) from error
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: UUID) -> AuthorizedPlate | None:
    obj = db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == id))
    if obj:
        db.delete(obj)
        db.commit()
    return obj
