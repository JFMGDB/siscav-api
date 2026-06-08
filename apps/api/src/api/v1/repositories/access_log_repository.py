"""Repository para operações de acesso a dados de logs de acesso."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.schemas.access_log import AccessStatus
from apps.api.src.api.v1.utils.timezone_br import BRAZIL_TZ


@dataclass(frozen=True)
class DailyAccessMetrics:
    traffic_volume: int
    auto_approval_rate_percent: float


class AccessLogRepository:
    """Repository para operações de banco de dados relacionadas a logs de acesso."""

    @staticmethod
    def get_by_id(db: Session, log_id: UUID) -> AccessLog | None:
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
        plate_filter: str | None = None,
        status_filter: AccessStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        owner_user_id: UUID | None = None,
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

        if owner_user_id is not None:
            conditions.append(AccessLog.owner_user_id == owner_user_id)

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
        authorized_plate_id: UUID | None = None,
        *,
        is_automatic: bool = False,
        ocr_success: bool = True,
        owner_user_id: UUID | None = None,
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

        # Definir timestamp manualmente (necessário para SQLite)
        now = datetime.now(UTC)

        db_log = AccessLog(
            plate_string_detected=plate_string_detected,
            status=status,
            image_storage_key=image_storage_key,
            authorized_plate_id=authorized_plate_id,
            is_automatic=is_automatic,
            ocr_success=ocr_success,
            owner_user_id=owner_user_id,
            timestamp=now,
        )
        db.add(db_log)
        try:
            db.commit()
            db.refresh(db_log)
        except Exception:
            db.rollback()
            raise
        return db_log

    @staticmethod
    def count(
        db: Session,
        plate_filter: str | None = None,
        status_filter: AccessStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """
        Conta o total de registros de acesso com filtros opcionais.

        Args:
            db: Sessão do banco de dados
            plate_filter: Filtrar por placa (busca parcial, case-insensitive)
            status_filter: Filtrar por status de acesso
            start_date: Data inicial para filtrar (inclusive)
            end_date: Data final para filtrar (inclusive)

        Returns:
            Número total de registros que correspondem aos filtros
        """
        query = select(func.count(AccessLog.id))

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

        return db.scalar(query) or 0

    @staticmethod
    def get_daily_metrics(db: Session, day: date, owner_user_id: UUID) -> DailyAccessMetrics:
        """Agrega métricas de acesso para um dia civil em America/Sao_Paulo."""
        start_local = datetime.combine(day, time.min, tzinfo=BRAZIL_TZ)
        end_local = start_local + timedelta(days=1)

        row = db.execute(
            select(
                func.count(AccessLog.id),
                func.count(
                    case(
                        (
                            and_(
                                AccessLog.status == AccessStatus.Authorized,
                                AccessLog.is_automatic.is_(True),
                            ),
                            AccessLog.id,
                        ),
                        else_=None,
                    )
                ),
            ).where(
                and_(
                    AccessLog.timestamp >= start_local,
                    AccessLog.timestamp < end_local,
                    AccessLog.owner_user_id == owner_user_id,
                )
            )
        ).one()

        total = int(row[0] or 0)
        auto_approved = int(row[1] or 0)

        if total == 0:
            return DailyAccessMetrics(0, 0.0)

        return DailyAccessMetrics(
            traffic_volume=total,
            auto_approval_rate_percent=round(auto_approved * 100.0 / total, 1),
        )
