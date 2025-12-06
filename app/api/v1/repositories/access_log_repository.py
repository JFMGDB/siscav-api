"""Repository para operações de acesso a dados de logs de acesso."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.schemas.access_log import AccessStatus


class AccessLogRepository:
    """Repository para operações de banco de dados relacionadas a logs de acesso."""

    @staticmethod
    def get_by_id(db: Session, log_id: UUID) -> Optional[AccessLog]:
        """
        Busca um registro de log de acesso por ID.

        Args:
            db: Sessão do banco de dados
            log_id: ID único do registro

        Returns:
            AccessLog se encontrado, None caso contrário
        """
        return db.scalar(select(AccessLog).where(AccessLog.id == log_id))

    @staticmethod
    def get_all(
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
            conditions.append(AccessLog.plate_string_detected.ilike(f"%{plate_filter}%"))

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

    @staticmethod
    def create(
        db: Session,
        plate_string_detected: str,
        status: AccessStatus,
        image_storage_key: str,
        authorized_plate_id: Optional[UUID] = None,
    ) -> AccessLog:
        """
        Cria um novo registro de log de acesso.

        Args:
            db: Sessão do banco de dados
            plate_string_detected: String da placa detectada pelo OCR
            status: Status do acesso (AccessStatus enum)
            image_storage_key: Caminho ou chave para a imagem armazenada
            authorized_plate_id: ID da placa autorizada, se houver

        Returns:
            AccessLog criado
        """
        db_log = AccessLog(
            plate_string_detected=plate_string_detected,
            status=status,
            image_storage_key=image_storage_key,
            authorized_plate_id=authorized_plate_id,
        )
        db.add(db_log)
        try:
            db.commit()
            db.refresh(db_log)
        except Exception:
            db.rollback()
            raise
        return db_log

