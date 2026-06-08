"""Testes de integração para métricas do dashboard."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.models.ocr_attempt import OcrAttempt
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
from apps.api.src.api.v1.repositories.ocr_attempt_repository import OcrAttemptRepository
from apps.api.src.api.v1.schemas.access_log import AccessStatus


class TestDashboardEndpoints:
    def test_daily_metrics_empty_day(self, client: TestClient, auth_token: str):
        response = client.get(
            "/api/v1/dashboard/metrics",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"date": "2024-06-01"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["traffic_volume"] == 0
        assert data["auto_approval_rate_percent"] == 0.0
        assert data["ocr_success_rate_percent"] == 0.0

    def test_daily_metrics_aggregates(
        self, client: TestClient, auth_token: str, test_user: User, db_session: Session
    ):
        day = datetime(2024, 6, 15, 14, 0, 0, tzinfo=UTC)

        auto_ok = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC1234",
            status=AccessStatus.Authorized,
            image_storage_key="a.jpg",
            is_automatic=True,
            ocr_success=True,
            owner_user_id=test_user.id,
        )
        manual_ok = AccessLogRepository.create(
            db_session,
            plate_string_detected="XYZ9999",
            status=AccessStatus.Authorized,
            image_storage_key="b.jpg",
            is_automatic=False,
            ocr_success=True,
            owner_user_id=test_user.id,
        )
        denied = AccessLogRepository.create(
            db_session,
            plate_string_detected="BADPLATE",
            status=AccessStatus.Denied,
            image_storage_key="c.jpg",
            is_automatic=False,
            ocr_success=False,
            owner_user_id=test_user.id,
        )
        for log in (auto_ok, manual_ok, denied):
            db_session.execute(
                update(AccessLog).where(AccessLog.id == log.id).values(timestamp=day)
            )
        ocr_rows = [
            OcrAttemptRepository.create(db_session, success=True, owner_user_id=test_user.id),
            OcrAttemptRepository.create(db_session, success=True, owner_user_id=test_user.id),
            OcrAttemptRepository.create(db_session, success=False, owner_user_id=test_user.id),
        ]
        for row in ocr_rows:
            db_session.execute(
                update(OcrAttempt).where(OcrAttempt.id == row.id).values(timestamp=day)
            )
        db_session.commit()

        response = client.get(
            "/api/v1/dashboard/metrics",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"date": "2024-06-15"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["traffic_volume"] == 3
        assert data["auto_approval_rate_percent"] == 33.3
        assert data["ocr_success_rate_percent"] == 66.7  # 2/3 tentativas OCR ML

    def test_daily_metrics_ocr_only_without_access_logs(
        self, client: TestClient, auth_token: str, test_user: User, db_session: Session
    ):
        """Taxa OCR independe do volume de access_logs."""
        OcrAttemptRepository.create(db_session, success=True, owner_user_id=test_user.id)
        db_session.commit()

        response = client.get(
            "/api/v1/dashboard/metrics",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"date": datetime.now(UTC).strftime("%Y-%m-%d")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["traffic_volume"] == 0
        assert data["ocr_success_rate_percent"] == 100.0
