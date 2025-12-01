"""Testes unitários para operações CRUD de logs de acesso."""

from uuid import uuid4

from sqlalchemy.orm import Session

from app.api.v1.crud import crud_access_log
from app.api.v1.models.access_log import AccessLog


class TestCrudAccessLogCreate:
    """Testes para função create()."""

    def test_create_access_log_success(self, db_session: Session):
        """Testa criação bem-sucedida de log de acesso."""
        log = crud_access_log.create(
            db_session,
            plate_string_detected="ABC-1234",
            status="Authorized",
            image_storage_key="/path/to/image.jpg",
        )

        assert log is not None
        assert log.plate_string_detected == "ABC-1234"
        assert log.status == "Authorized"
        assert log.image_storage_key == "/path/to/image.jpg"
        assert log.authorized_plate_id is None
        assert log.id is not None
        assert log.timestamp is not None

    def test_create_access_log_with_authorized_plate_id(self, db_session: Session):
        """Testa criação de log com ID de placa autorizada."""
        authorized_plate_id = uuid4()

        log = crud_access_log.create(
            db_session,
            plate_string_detected="XYZ-5678",
            status="Authorized",
            image_storage_key="/path/to/image2.jpg",
            authorized_plate_id=authorized_plate_id,
        )

        assert log.authorized_plate_id == authorized_plate_id
        assert log.status == "Authorized"

    def test_create_access_log_denied(self, db_session: Session):
        """Testa criação de log com status Denied."""
        log = crud_access_log.create(
            db_session,
            plate_string_detected="DEF-9999",
            status="Denied",
            image_storage_key="/path/to/image3.jpg",
        )

        assert log.status == "Denied"
        assert log.authorized_plate_id is None

    def test_create_access_log_persisted(self, db_session: Session):
        """Testa que log é persistido no banco de dados."""
        log = crud_access_log.create(
            db_session,
            plate_string_detected="GHI-0000",
            status="Authorized",
            image_storage_key="/path/to/image4.jpg",
        )

        # Busca diretamente no banco
        found_log = db_session.get(AccessLog, log.id)

        assert found_log is not None
        assert found_log.plate_string_detected == "GHI-0000"
        assert found_log.status == "Authorized"
