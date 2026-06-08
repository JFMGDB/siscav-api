"""Repository para tentativas de OCR (POST /ml/recognize-plate)."""

from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.ocr_attempt import OcrAttempt
from apps.api.src.api.v1.utils.timezone_br import BRAZIL_TZ


class OcrAttemptRepository:
    @staticmethod
    def create(db: Session, *, success: bool, owner_user_id: UUID | None = None) -> OcrAttempt:
        row = OcrAttempt(
            timestamp=datetime.now(UTC),
            success=success,
            owner_user_id=owner_user_id,
        )
        db.add(row)
        try:
            db.commit()
            db.refresh(row)
        except Exception:
            db.rollback()
            raise
        return row

    @staticmethod
    def get_daily_success_rate(db: Session, day: date, owner_user_id: UUID) -> tuple[int, float]:
        """Retorna (total_tentativas, taxa_sucesso_percent) para o dia civil BR."""
        start_local = datetime.combine(day, time.min, tzinfo=BRAZIL_TZ)
        end_local = start_local + timedelta(days=1)

        row = db.execute(
            select(
                func.count(OcrAttempt.id),
                func.count(case((OcrAttempt.success.is_(True), OcrAttempt.id), else_=None)),
            ).where(
                and_(
                    OcrAttempt.timestamp >= start_local,
                    OcrAttempt.timestamp < end_local,
                    OcrAttempt.owner_user_id == owner_user_id,
                )
            )
        ).one()

        total = int(row[0] or 0)
        if total == 0:
            return 0, 0.0

        ok = int(row[1] or 0)
        return total, round(ok * 100.0 / total, 1)
