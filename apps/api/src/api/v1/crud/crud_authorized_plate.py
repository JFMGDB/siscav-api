"""
DEPRECATED: Este módulo está obsoleto.

Use os novos repositories e controllers:
- Para acesso a dados: `apps.api.src.api.v1.repositories.authorized_plate_repository.AuthorizedPlateRepository`
- Para lógica de negócio: `apps.api.src.api.v1.controllers.plate_controller.PlateController`

Este módulo será removido em uma versão futura.
"""

import warnings
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.schemas.authorized_plate import AuthorizedPlateCreate
from apps.api.src.api.v1.utils.plate import normalize_plate

warnings.warn(
    "crud_authorized_plate está deprecated. Use AuthorizedPlateRepository e PlateController.",
    DeprecationWarning,
    stacklevel=2,
)


def get(db: Session, id: UUID) -> Optional[AuthorizedPlate]:
    """Busca uma placa autorizada por ID."""
    return db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == id))


def get_by_normalized_plate(
    db: Session, normalized_plate: str
) -> Optional[AuthorizedPlate]:
    """
    Busca uma placa autorizada pela versão normalizada.
    
    Args:
        db: Sessão do banco de dados
        normalized_plate: Placa normalizada (sem hífens, maiúscula)
        
    Returns:
        AuthorizedPlate se encontrada, None caso contrário
    """
    return db.scalar(
        select(AuthorizedPlate).where(AuthorizedPlate.normalized_plate == normalized_plate)
    )


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[AuthorizedPlate]:
    """Lista placas autorizadas com paginação."""
    return list(db.scalars(select(AuthorizedPlate).offset(skip).limit(limit)))


def create(db: Session, obj_in: AuthorizedPlateCreate) -> AuthorizedPlate:
    """
    Cria uma nova placa autorizada.
    
    A normalização é feita automaticamente se não fornecida.
    """
    normalized = obj_in.normalized_plate or normalize_plate(obj_in.plate)
    db_obj = AuthorizedPlate(
        plate=obj_in.plate,
        normalized_plate=normalized,
        description=obj_in.description,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, db_obj: AuthorizedPlate, obj_in: AuthorizedPlateCreate
) -> AuthorizedPlate:
    """
    Atualiza uma placa autorizada existente.
    
    A normalização é recalculada automaticamente se a placa mudou.
    """
    db_obj.plate = obj_in.plate
    db_obj.normalized_plate = obj_in.normalized_plate or normalize_plate(obj_in.plate)
    db_obj.description = obj_in.description
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: UUID) -> Optional[AuthorizedPlate]:
    """Remove uma placa autorizada por ID."""
    obj = db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == id))
    if obj:
        db.delete(obj)
        db.commit()
    return obj
