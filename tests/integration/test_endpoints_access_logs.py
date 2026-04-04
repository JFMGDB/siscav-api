"""Testes de integração para endpoints de access logs."""

import io
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import update
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.repositories.authorized_plate_repository import AuthorizedPlateRepository
from tests.conftest import TEST_DEVICE_INGEST_KEY


class TestAccessLogsEndpoints:
    """Testes para endpoints de access logs."""

    def test_create_access_log_authorized(self, client: TestClient, db_session: Session):
        """Testa criação de log de acesso autorizado."""
        # Criar placa autorizada
        AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        db_session.commit()

        # Criar arquivo de imagem simulado
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "ABC-1234"}

        response = client.post(
            "/api/v1/access_logs/",
            files=files,
            data=data,
            headers={"X-Device-Key": TEST_DEVICE_INGEST_KEY},
        )

        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Authorized"
        assert log["plate_string_detected"] == "ABC-1234"
        assert log.get("authorized_plate_id") is not None
        assert log["image_storage_key"].endswith(".jpg")

        # Limpar arquivo
        if "image_storage_key" in log:
            image_path = Path(log["image_storage_key"])
            if image_path.exists():
                image_path.unlink()

    def test_create_access_log_denied(self, client: TestClient):
        """Testa criação de log de acesso negado."""
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "XYZ-9999"}

        response = client.post(
            "/api/v1/access_logs/",
            files=files,
            data=data,
            headers={"X-Device-Key": TEST_DEVICE_INGEST_KEY},
        )

        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Denied"
        assert log["plate_string_detected"] == "XYZ-9999"

        # Limpar arquivo
        if "image_storage_key" in log:
            image_path = Path(log["image_storage_key"])
            if image_path.exists():
                image_path.unlink()

    def test_list_access_logs(self, client: TestClient, auth_token: str, db_session: Session):
        """Testa listagem de logs de acesso."""
        from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
        from apps.api.src.api.v1.schemas.access_log import AccessStatus

        # Criar alguns logs
        for i in range(3):
            AccessLogRepository.create(
                db_session,
                plate_string_detected=f"ABC-{i:04d}",
                status=AccessStatus.Authorized,
                image_storage_key=f"test{i}.jpg",
            )
        db_session.commit()

        response = client.get(
            "/api/v1/access_logs/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # A API retorna uma lista diretamente, não um objeto com "items"
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_list_access_logs_with_filters(self, client: TestClient, auth_token: str, db_session: Session):
        """Testa listagem de logs com filtros."""
        from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
        from apps.api.src.api.v1.schemas.access_log import AccessStatus

        # Criar logs com diferentes status
        AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="test1.jpg",
        )
        AccessLogRepository.create(
            db_session,
            plate_string_detected="XYZ-9999",
            status=AccessStatus.Denied,
            image_storage_key="test2.jpg",
        )
        db_session.commit()

        # Filtrar por status
        response = client.get(
            "/api/v1/access_logs/",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"status": "Authorized"},
        )

        assert response.status_code == 200
        data = response.json()
        # A API retorna uma lista diretamente
        assert isinstance(data, list)
        assert all(item["status"] == "Authorized" for item in data)

    def test_list_access_logs_ordered_by_timestamp_desc(
        self, client: TestClient, auth_token: str, db_session: Session
    ):
        """Lista retorna mais recente primeiro (timestamp DESC)."""
        from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
        from apps.api.src.api.v1.schemas.access_log import AccessStatus

        older = datetime(2024, 1, 2, 10, 0, 0, tzinfo=timezone.utc)
        newer = datetime(2024, 1, 2, 18, 0, 0, tzinfo=timezone.utc)

        log_a = AccessLogRepository.create(
            db_session,
            plate_string_detected="ORD-A",
            status=AccessStatus.Authorized,
            image_storage_key="ord_a.jpg",
        )
        log_b = AccessLogRepository.create(
            db_session,
            plate_string_detected="ORD-B",
            status=AccessStatus.Authorized,
            image_storage_key="ord_b.jpg",
        )
        db_session.execute(
            update(AccessLog).where(AccessLog.id == log_a.id).values(timestamp=older)
        )
        db_session.execute(
            update(AccessLog).where(AccessLog.id == log_b.id).values(timestamp=newer)
        )
        db_session.commit()

        response = client.get(
            "/api/v1/access_logs/",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"limit": 20},
        )
        assert response.status_code == 200
        data = response.json()
        plates = [row["plate_string_detected"] for row in data if row["plate_string_detected"] in ("ORD-A", "ORD-B")]
        assert plates == ["ORD-B", "ORD-A"]

    def test_list_access_logs_start_date_end_date_filters(
        self, client: TestClient, auth_token: str, db_session: Session
    ):
        """start_date e end_date (inclusivos) restringem o conjunto retornado."""
        from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
        from apps.api.src.api.v1.schemas.access_log import AccessStatus

        day1 = datetime(2024, 3, 10, 12, 0, 0, tzinfo=timezone.utc)
        day2 = datetime(2024, 3, 12, 12, 0, 0, tzinfo=timezone.utc)

        log_in = AccessLogRepository.create(
            db_session,
            plate_string_detected="DATE-IN",
            status=AccessStatus.Denied,
            image_storage_key="din.jpg",
        )
        log_out = AccessLogRepository.create(
            db_session,
            plate_string_detected="DATE-OUT",
            status=AccessStatus.Denied,
            image_storage_key="dout.jpg",
        )
        db_session.execute(
            update(AccessLog).where(AccessLog.id == log_in.id).values(timestamp=day1)
        )
        db_session.execute(
            update(AccessLog).where(AccessLog.id == log_out.id).values(timestamp=day2)
        )
        db_session.commit()

        response = client.get(
            "/api/v1/access_logs/",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={
                "start_date": "2024-03-10T00:00:00+00:00",
                "end_date": "2024-03-11T23:59:59+00:00",
            },
        )
        assert response.status_code == 200
        plates = {row["plate_string_detected"] for row in response.json()}
        assert "DATE-IN" in plates
        assert "DATE-OUT" not in plates

    def test_create_access_log_missing_device_key_returns_401(self, client: TestClient):
        """Sem X-Device-Key quando DEVICE_INGEST_KEY está definido → 401."""
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "XYZ-9999"}

        response = client.post("/api/v1/access_logs/", files=files, data=data)

        assert response.status_code == 401

    def test_create_access_log_wrong_device_key_returns_401(self, client: TestClient):
        """Chave de dispositivo incorreta → 401."""
        file_content = b"fake image content"
        files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
        data = {"plate": "XYZ-9999"}

        response = client.post(
            "/api/v1/access_logs/",
            files=files,
            data=data,
            headers={"X-Device-Key": "wrong-key"},
        )

        assert response.status_code == 401

    def test_get_access_log_image_requires_admin(
        self,
        client: TestClient,
        db_session: Session,
        auth_token: str,
        admin_auth_token: str,
    ):
        """LOG-03 / Phase 2: imagem só para admin; não-admin 403, admin 200."""
        from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
        from apps.api.src.api.v1.schemas.access_log import AccessStatus

        AccessLogRepository.create(
            db_session,
            plate_string_detected="IMG-TEST",
            status=AccessStatus.Authorized,
            image_storage_key="integration_test_plate.jpg",
        )
        db_session.commit()

        upload_root = Path(__file__).resolve().parents[2] / "uploads"
        upload_root.mkdir(parents=True, exist_ok=True)
        image_path = upload_root / "integration_test_plate.jpg"
        image_path.write_bytes(b"\xff\xd8\xff fake jpeg")

        try:
            r_user = client.get(
                "/api/v1/access_logs/images/integration_test_plate.jpg",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert r_user.status_code == 403

            r_admin = client.get(
                "/api/v1/access_logs/images/integration_test_plate.jpg",
                headers={"Authorization": f"Bearer {admin_auth_token}"},
            )
            assert r_admin.status_code == 200
            assert r_admin.content == b"\xff\xd8\xff fake jpeg"
        finally:
            if image_path.exists():
                image_path.unlink()

