"""Testes de integração para endpoints de access logs."""

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.repositories.authorized_plate_repository import AuthorizedPlateRepository


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

        response = client.post("/api/v1/access_logs/", files=files, data=data)

        assert response.status_code == 200
        log = response.json()
        assert log["status"] == "Authorized"
        assert log["plate_string_detected"] == "ABC-1234"

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

        response = client.post("/api/v1/access_logs/", files=files, data=data)

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
        from app.api.v1.repositories.access_log_repository import AccessLogRepository
        from app.api.v1.schemas.access_log import AccessStatus

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
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 3

    def test_list_access_logs_with_filters(self, client: TestClient, auth_token: str, db_session: Session):
        """Testa listagem de logs com filtros."""
        from app.api.v1.repositories.access_log_repository import AccessLogRepository
        from app.api.v1.schemas.access_log import AccessStatus

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
        assert all(item["status"] == "Authorized" for item in data["items"])

