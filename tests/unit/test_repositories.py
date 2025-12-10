"""Testes unitários para repositories."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.access_log import AccessStatus
from apps.api.src.api.v1.schemas.user import UserCreate


@pytest.fixture
def db_session():
    """Cria uma sessão de banco de dados em memória para testes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


class TestUserRepository:
    """Testes para UserRepository."""

    def test_get_by_id_not_found(self, db_session):
        """Testa busca de usuário por ID inexistente."""
        user_id = uuid.uuid4()
        result = UserRepository.get_by_id(db_session, user_id)
        assert result is None

    def test_get_by_email_not_found(self, db_session):
        """Testa busca de usuário por email inexistente."""
        result = UserRepository.get_by_email(db_session, "nonexistent@example.com")
        assert result is None

    def test_create_user(self, db_session):
        """Testa criação de usuário."""
        from apps.api.src.api.v1.core.security import get_password_hash

        user_data = UserCreate(email="test@example.com", password="password123")
        hashed_password = get_password_hash("password123")
        user = UserRepository.create(db_session, user_data, hashed_password)
        assert user.email == "test@example.com"
        assert user.hashed_password == hashed_password
        assert user.id is not None

    def test_get_by_id_found(self, db_session):
        """Testa busca de usuário por ID existente."""
        from apps.api.src.api.v1.core.security import get_password_hash

        user_data = UserCreate(email="test@example.com", password="password123")
        hashed_password = get_password_hash("password123")
        created_user = UserRepository.create(db_session, user_data, hashed_password)
        found_user = UserRepository.get_by_id(db_session, created_user.id)
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"

    def test_get_by_email_found(self, db_session):
        """Testa busca de usuário por email existente."""
        from apps.api.src.api.v1.core.security import get_password_hash

        user_data = UserCreate(email="test@example.com", password="password123")
        hashed_password = get_password_hash("password123")
        UserRepository.create(db_session, user_data, hashed_password)
        found_user = UserRepository.get_by_email(db_session, "test@example.com")
        assert found_user is not None
        assert found_user.email == "test@example.com"


class TestAuthorizedPlateRepository:
    """Testes para AuthorizedPlateRepository."""

    def test_get_by_id_not_found(self, db_session):
        """Testa busca de placa por ID inexistente."""
        plate_id = uuid.uuid4()
        result = AuthorizedPlateRepository.get_by_id(db_session, plate_id)
        assert result is None

    def test_get_by_normalized_plate_not_found(self, db_session):
        """Testa busca de placa normalizada inexistente."""
        result = AuthorizedPlateRepository.get_by_normalized_plate(
            db_session, "XYZ9999"
        )
        assert result is None

    def test_create_plate(self, db_session):
        """Testa criação de placa autorizada."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test Car",
        )
        assert plate.plate == "ABC-1234"
        assert plate.normalized_plate == "ABC1234"
        assert plate.description == "Test Car"
        assert plate.id is not None

    def test_get_by_id_found(self, db_session):
        """Testa busca de placa por ID existente."""
        created_plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test Car",
        )
        found_plate = AuthorizedPlateRepository.get_by_id(db_session, created_plate.id)
        assert found_plate is not None
        assert found_plate.id == created_plate.id
        assert found_plate.plate == "ABC-1234"

    def test_get_by_normalized_plate_found(self, db_session):
        """Testa busca de placa por versão normalizada."""
        AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test Car",
        )
        found_plate = AuthorizedPlateRepository.get_by_normalized_plate(
            db_session, "ABC1234"
        )
        assert found_plate is not None
        assert found_plate.normalized_plate == "ABC1234"

    def test_get_all(self, db_session):
        """Testa listagem de placas com paginação."""
        # Criar múltiplas placas
        for i in range(5):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
                description=f"Car {i}",
            )
        plates = AuthorizedPlateRepository.get_all(db_session, skip=0, limit=3)
        assert len(plates) == 3

    def test_get_all_with_pagination(self, db_session):
        """Testa paginação na listagem de placas."""
        for i in range(5):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
            )
        plates = AuthorizedPlateRepository.get_all(db_session, skip=2, limit=2)
        assert len(plates) == 2

    def test_update_plate(self, db_session):
        """Testa atualização de placa."""
        created_plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Old Description",
        )
        updated_plate = AuthorizedPlateRepository.update(
            db_session,
            plate=created_plate,
            plate_value="XYZ-5678",
            normalized_plate="XYZ5678",
            description="New Description",
        )
        assert updated_plate.plate == "XYZ-5678"
        assert updated_plate.normalized_plate == "XYZ5678"
        assert updated_plate.description == "New Description"

    def test_delete_plate(self, db_session):
        """Testa remoção de placa."""
        created_plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        deleted_plate = AuthorizedPlateRepository.delete(db_session, created_plate.id)
        assert deleted_plate is not None
        found_plate = AuthorizedPlateRepository.get_by_id(db_session, created_plate.id)
        assert found_plate is None


class TestAccessLogRepository:
    """Testes para AccessLogRepository."""

    def test_get_by_id_not_found(self, db_session):
        """Testa busca de log por ID inexistente."""
        log_id = uuid.uuid4()
        result = AccessLogRepository.get_by_id(db_session, log_id)
        assert result is None

    def test_create_access_log(self, db_session):
        """Testa criação de log de acesso."""
        log = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="uploads/test.jpg",
        )
        assert log.plate_string_detected == "ABC-1234"
        assert log.status == AccessStatus.Authorized
        assert log.image_storage_key == "uploads/test.jpg"
        assert log.id is not None

    def test_create_access_log_with_authorized_plate_id(self, db_session):
        """Testa criação de log com ID de placa autorizada."""
        # Criar placa autorizada
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        log = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="uploads/test.jpg",
            authorized_plate_id=plate.id,
        )
        assert log.authorized_plate_id == plate.id

    def test_get_by_id_found(self, db_session):
        """Testa busca de log por ID existente."""
        created_log = AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="uploads/test.jpg",
        )
        found_log = AccessLogRepository.get_by_id(db_session, created_log.id)
        assert found_log is not None
        assert found_log.id == created_log.id

    def test_get_all(self, db_session):
        """Testa listagem de logs."""
        for i in range(5):
            AccessLogRepository.create(
                db_session,
                plate_string_detected=f"ABC-{i:04d}",
                status=AccessStatus.Authorized if i % 2 == 0 else AccessStatus.Denied,
                image_storage_key=f"uploads/test_{i}.jpg",
            )
        logs = AccessLogRepository.get_all(db_session, skip=0, limit=10)
        assert len(logs) == 5

    def test_get_all_with_plate_filter(self, db_session):
        """Testa filtro por placa."""
        AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="uploads/test1.jpg",
        )
        AccessLogRepository.create(
            db_session,
            plate_string_detected="XYZ-5678",
            status=AccessStatus.Denied,
            image_storage_key="uploads/test2.jpg",
        )
        logs = AccessLogRepository.get_all(
            db_session, skip=0, limit=10, plate_filter="ABC"
        )
        assert len(logs) == 1
        assert logs[0].plate_string_detected == "ABC-1234"

    def test_get_all_with_status_filter(self, db_session):
        """Testa filtro por status."""
        AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="uploads/test1.jpg",
        )
        AccessLogRepository.create(
            db_session,
            plate_string_detected="XYZ-5678",
            status=AccessStatus.Denied,
            image_storage_key="uploads/test2.jpg",
        )
        logs = AccessLogRepository.get_all(
            db_session, skip=0, limit=10, status_filter=AccessStatus.Authorized
        )
        assert len(logs) == 1
        assert logs[0].status == AccessStatus.Authorized

    def test_get_all_with_date_filter(self, db_session):
        """Testa filtro por data."""
        from datetime import timedelta

        now = datetime.now()
        AccessLogRepository.create(
            db_session,
            plate_string_detected="ABC-1234",
            status=AccessStatus.Authorized,
            image_storage_key="uploads/test1.jpg",
        )
        logs = AccessLogRepository.get_all(
            db_session,
            skip=0,
            limit=10,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )
        assert len(logs) >= 1

