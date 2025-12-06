"""
DEPRECATED: Este módulo está obsoleto.

Use os novos repositories e controllers:
- Para acesso a dados: `apps.api.src.api.v1.repositories.access_log_repository.AccessLogRepository`
- Para lógica de negócio: `apps.api.src.api.v1.controllers.access_log_controller.AccessLogController`

Este módulo será removido em uma versão futura.
"""

import warnings
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.schemas.access_log import AccessStatus

warnings.warn(
    "crud_access_log está deprecated. Use AccessLogRepository e AccessLogController.",
    DeprecationWarning,
    stacklevel=2,
)


def create(
    db: Session,
    plate_string_detected: str,
    status: AccessStatus | str,
    image_storage_key: str,
    authorized_plate_id: UUID | None = None,
) -> AccessLog:
    """
    Cria um novo registro de log de acesso.
    
    Args:
        db: Sessão do banco de dados
        plate_string_detected: String da placa detectada pelo OCR
        status: Status do acesso (AccessStatus enum ou string)
        image_storage_key: Caminho ou chave para a imagem armazenada
        authorized_plate_id: ID da placa autorizada, se houver
        
    Returns:
        AccessLog: Registro de acesso criado
    """
    # Converter string para Enum se necessário
    if isinstance(status, str):
        status = AccessStatus(status)
    
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


def get(db: Session, id: UUID) -> Optional[AccessLog]:
    """
    Busca um registro de log de acesso por ID.
    
    Args:
        db: Sessão do banco de dados
        id: ID único do registro
        
    Returns:
        AccessLog se encontrado, None caso contrário
    """
    return db.scalar(select(AccessLog).where(AccessLog.id == id))


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    plate_filter: Optional[str] = None,
    status_filter: Optional[AccessStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[AccessLog]:
    """
    Lista registros de log de acesso com filtros opcionais.
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros a retornar
        plate_filter: Filtrar por placa (busca parcial, case-insensitive)
        status_filter: Filtrar por status de acesso
        start_date: Data inicial para filtrar (inclusive)
        end_date: Data final para filtrar (inclusive)
        
    Returns:
        Lista de registros de acesso ordenados por timestamp (mais recente primeiro)
    """
    query = select(AccessLog)
    
    # Aplicar filtros
    conditions = []
    
    if plate_filter:
        conditions.append(
            AccessLog.plate_string_detected.ilike(f"%{plate_filter}%")
        )
    
    if status_filter:
        conditions.append(AccessLog.status == status_filter)
    
    if start_date:
        conditions.append(AccessLog.timestamp >= start_date)
    
    if end_date:
        conditions.append(AccessLog.timestamp <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Ordenar por timestamp (mais recente primeiro) e aplicar paginação
    query = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit)
    
    return list(db.scalars(query))
