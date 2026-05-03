"""Testes unitários para AccessLogRepository."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
from apps.api.src.api.v1.repositories.authorized_plate_repository import AuthorizedPlateRepository
from apps.api.src.api.v1.schemas.access_log import AccessStatus


class TestAccessLogRepository:
    """Testes para AccessLogRepository."""

    def test_get_by_id_success(self, db_session: Session):
        """Testa busca de log por ID com sucesso."""
        log = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="test.jpg",
        )

        result = AccessLogRepository.get_by_id(db_session, log.id)

        assert result is not None
        assert result.id == log.id
        assert result.plate_string_detected == "ABC-1234"

    def test_get_by_id_not_found(self, db_session: Session):
        """Testa busca de log por ID inexistente."""
        fake_id = uuid4()
        result = AccessLogRepository.get_by_id(db_session, fake_id)

        assert result is None

    def test_get_all(self, db_session: Session):
        """Testa listagem de logs com paginação."""
        # Criar múltiplos logs
        for i in range(5):
            AccessLogRepository.create(
                db_session,
                plate_string_detected=f"ABC-{i:04d}",
                status=AccessStatus.Authorized,
                image_storage_key=f"test{i}.jpg",
            )

        result = AccessLogRepository.get_all(db_session, skip=0, limit=3)

        assert len(result) == 3

    def test_get_all_with_plate_filter(self, db_session: Session):
        """Testa listagem de logs com filtro de placa."""
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

        result = AccessLogRepository.get_all(db_session, plate_filter="ABC")

        assert len(result) == 1
        assert result[0].plate_string_detected == "ABC-1234"

    def test_get_all_with_status_filter(self, db_session: Session):
        """Testa listagem de logs com filtro de status."""
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

        authorized_logs = AccessLogRepository.get_all(
            db_session, status_filter=AccessStatus.Authorized
        )
        assert len(authorized_logs) == 1
        assert authorized_logs[0].status == AccessStatus.Authorized

        denied_logs = AccessLogRepository.get_all(
            db_session, status_filter=AccessStatus.Denied
        )
        assert len(denied_logs) == 1
        assert denied_logs[0].status == AccessStatus.Denied

    def test_get_all_with_date_filters(self, db_session: Session):
        """Testa listagem de logs com filtros de data."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Criar log com timestamp específico seria necessário mockar, mas testamos a lógica
        AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="test1.jpg",
        )

        result = AccessLogRepository.get_all(
            db_session, start_date=yesterday, end_date=tomorrow
        )

        assert len(result) >= 1

    def test_count(self, db_session: Session):
        """Testa contagem de logs."""
        # Criar múltiplos logs
        for i in range(3):
            AccessLogRepository.create(
                db_session,
                plate_string_detected=f"ABC-{i:04d}",
                status=AccessStatus.Authorized,
                image_storage_key=f"test{i}.jpg",
            )

        count = AccessLogRepository.count(db_session)

        assert count == 3

    def test_count_with_filters(self, db_session: Session):
        """Testa contagem de logs com filtros."""
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

        total = AccessLogRepository.count(db_session)
        assert total == 2

        authorized_count = AccessLogRepository.count(
            db_session, status_filter=AccessStatus.Authorized
        )
        assert authorized_count == 1

    def test_create_success(self, db_session: Session):
        """Testa criação de log com sucesso."""
        result = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="test.jpg",
        )

        assert result is not None
        assert result.plate_string_detected == "ABC-1234"
        assert result.status == AccessStatus.Authorized

    def test_create_with_authorized_plate_id(self, db_session: Session):
        """Testa criação de log com ID de placa autorizada."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        result = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="test.jpg",
            authorized_plate_id=plate.id,
        )

        assert result.authorized_plate_id == plate.id

