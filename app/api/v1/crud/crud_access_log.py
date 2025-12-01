from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.models.access_log import AccessLog


def _apply_filters(
    query: Any,
    status: str | None = None,
    plate: str | None = None,
) -> Any:
    """Aplica filtros opcionais a uma query.

    Helper interno para evitar duplicação de lógica de filtros
    entre get_multi() e count(), seguindo o princípio DRY.

    Args:
        query: Query SQLAlchemy base.
        status: Filtrar por status (Authorized ou Denied).
        plate: Filtrar por placa (busca parcial).

    Returns:
        Query SQLAlchemy com filtros aplicados.
    """
    # Aplicar filtros (valida que não são strings vazias)
    if status and status.strip():
        query = query.where(AccessLog.status == status)
    if plate and plate.strip():
        # SQLAlchemy protege automaticamente contra SQL injection usando
        # parâmetros vinculados, então não há risco mesmo com ILIKE
        query = query.where(AccessLog.plate_string_detected.ilike(f"%{plate.strip()}%"))

    return query


def create(
    db: Session,
    plate_string_detected: str,
    status: str,
    image_storage_key: str,
    authorized_plate_id: UUID | None = None,
) -> AccessLog:
    """Cria um novo log de acesso.

    Args:
        db: Sessão do banco de dados.
        plate_string_detected: Placa detectada pelo sistema ALPR.
        status: Status do acesso (Authorized ou Denied).
        image_storage_key: Caminho do arquivo de imagem armazenado.
        authorized_plate_id: ID da placa autorizada, se o acesso foi autorizado.

    Returns:
        Instância do log de acesso criado.

    Raises:
        ValueError: Se algum parâmetro obrigatório for None ou vazio.
    """
    if not plate_string_detected or not plate_string_detected.strip():
        error_msg = "Plate string detected cannot be None or empty"
        raise ValueError(error_msg)
    if not status or not status.strip():
        error_msg = "Status cannot be None or empty"
        raise ValueError(error_msg)
    if not image_storage_key or not image_storage_key.strip():
        error_msg = "Image storage key cannot be None or empty"
        raise ValueError(error_msg)

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


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    plate: str | None = None,
) -> list[AccessLog]:
    """Lista logs de acesso com filtros opcionais.

    Args:
        db: Sessão do banco de dados.
        skip: Número de registros a pular.
        limit: Número máximo de registros a retornar.
        status: Filtrar por status (Authorized ou Denied).
        plate: Filtrar por placa (busca parcial).

    Returns:
        Lista de logs de acesso ordenados por timestamp descendente.
    """
    query = select(AccessLog)
    query = _apply_filters(query, status=status, plate=plate)

    # Ordenar por timestamp descendente (mais recentes primeiro)
    query = query.order_by(AccessLog.timestamp.desc())

    # Aplicar paginação
    query = query.offset(skip).limit(limit)

    return list(db.scalars(query))


def count(
    db: Session,
    status: str | None = None,
    plate: str | None = None,
) -> int:
    """Conta o total de logs de acesso com filtros opcionais.

    Args:
        db: Sessão do banco de dados.
        status: Filtrar por status (Authorized ou Denied).
        plate: Filtrar por placa (busca parcial).

    Returns:
        Total de logs de acesso.
    """
    query = select(func.count(AccessLog.id))
    query = _apply_filters(query, status=status, plate=plate)

    result = db.scalar(query)
    return result if result is not None else 0
