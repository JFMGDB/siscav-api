"""Testes unitários para controllers."""

import uuid
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.controllers.device_controller import DeviceController
from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.controllers.plate_controller import PlateController
from apps.api.src.api.v1.db.base import Base
from apps.api.src.api.v1.models.access_log import AccessLog
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.schemas.access_log import AccessStatus
from apps.api.src.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


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


@pytest.fixture
def sample_user(db_session):
    """Cria um usuário de teste."""
    from apps.api.src.api.v1.core.security import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestAuthController:
    """Testes para AuthController."""

    def test_authenticate_success(self, db_session, sample_user):
        """Testa autenticação bem-sucedida."""
        controller = AuthController(db_session)
        user = controller.authenticate("test@example.com", "password123")
        assert user is not None
        assert user.email == "test@example.com"

    def test_authenticate_wrong_password(self, db_session, sample_user):
        """Testa autenticação com senha incorreta."""
        controller = AuthController(db_session)
        user = controller.authenticate("test@example.com", "wrong_password")
        assert user is None

    def test_authenticate_user_not_found(self, db_session):
        """Testa autenticação com usuário inexistente."""
        controller = AuthController(db_session)
        user = controller.authenticate("nonexistent@example.com", "password123")
        assert user is None

    def test_create_access_token_for_user(self, db_session, sample_user):
        """Testa criação de token de acesso."""
        controller = AuthController(db_session)
        token = controller.create_access_token_for_user(sample_user)
        assert isinstance(token, str)
        assert len(token) > 0


class TestPlateController:
    """Testes para PlateController."""

    def test_get_by_id_not_found(self, db_session):
        """Testa busca de placa inexistente."""
        controller = PlateController(db_session)
        with pytest.raises(HTTPException) as exc_info:
            controller.get_by_id(uuid.uuid4())
        assert exc_info.value.status_code == 404

    def test_get_by_id_found(self, db_session):
        """Testa busca de placa existente."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test Car",
        )
        controller = PlateController(db_session)
        found_plate = controller.get_by_id(plate.id)
        assert found_plate.id == plate.id

    def test_get_all(self, db_session):
        """Testa listagem de placas."""
        for i in range(3):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
            )
        controller = PlateController(db_session)
        plates = controller.get_all(skip=0, limit=10)
        assert len(plates) == 3

    def test_create_plate_success(self, db_session):
        """Testa criação de placa válida."""
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(
            plate="ABC-1234", normalized_plate="ABC1234", description="Test Car"
        )
        plate = controller.create(plate_data)
        assert plate.plate == "ABC-1234"
        assert plate.normalized_plate == "ABC1234"

    def test_create_plate_invalid_format(self, db_session):
        """Testa criação de placa com formato inválido."""
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(
            plate="INVALID", normalized_plate="INVALID", description="Test"
        )
        with pytest.raises(HTTPException) as exc_info:
            controller.create(plate_data)
        assert exc_info.value.status_code == 400

    def test_create_plate_duplicate(self, db_session):
        """Testa criação de placa duplicada."""
        AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(
            plate="ABC-1234", normalized_plate="ABC1234", description="Test"
        )
        with pytest.raises(HTTPException) as exc_info:
            controller.create(plate_data)
        assert exc_info.value.status_code == 409

    def test_update_plate_success(self, db_session):
        """Testa atualização de placa."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(
            plate="XYZ-5678", normalized_plate="XYZ5678", description="Updated"
        )
        updated_plate = controller.update(plate.id, plate_data)
        assert updated_plate.plate == "XYZ-5678"

    def test_delete_plate_success(self, db_session):
        """Testa remoção de placa."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        controller = PlateController(db_session)
        deleted_plate = controller.delete(plate.id)
        assert deleted_plate.id == plate.id
        with pytest.raises(HTTPException):
            controller.get_by_id(plate.id)

    def test_check_authorization_authorized(self, db_session):
        """Testa verificação de autorização para placa autorizada."""
        AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        controller = PlateController(db_session)
        is_authorized, plate_id = controller.check_authorization("ABC-1234")
        assert is_authorized is True
        assert plate_id is not None

    def test_check_authorization_denied(self, db_session):
        """Testa verificação de autorização para placa não autorizada."""
        controller = PlateController(db_session)
        is_authorized, plate_id = controller.check_authorization("XYZ-9999")
        assert is_authorized is False
        assert plate_id is None


class TestAccessLogController:
    """Testes para AccessLogController."""

    @pytest.fixture
    def upload_dir(self, tmp_path):
        """Cria diretório temporário para uploads."""
        return tmp_path / "uploads"

    def test_create_access_log_authorized(self, db_session, upload_dir):
        """Testa criação de log de acesso autorizado."""
        # Criar placa autorizada
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )
        # Criar arquivo de imagem mock
        file_content = b"fake image content"
        from fastapi import UploadFile as FastAPIUploadFile
        from starlette.datastructures import UploadFile as StarletteUploadFile
        
        file = StarletteUploadFile(
            filename="test.jpg",
            file=BytesIO(file_content),
            headers={"content-type": "image/jpeg"},
        )

        with patch(
            "apps.api.src.api.v1.controllers.access_log_controller.get_settings"
        ) as mock_settings:
            mock_settings.return_value.upload_dir = str(upload_dir)
            mock_settings.return_value.max_file_size_mb = 10
            controller = AccessLogController(db_session)
            log = controller.create_access_log(plate="ABC-1234", file=file)
            assert log.status == AccessStatus.Authorized
            assert log.plate_string_detected == "ABC-1234"
            assert log.authorized_plate_id == plate.id

    def test_create_access_log_denied(self, db_session, upload_dir):
        """Testa criação de log de acesso negado."""
        file_content = b"fake image content"
        from fastapi import UploadFile as FastAPIUploadFile
        from starlette.datastructures import UploadFile as StarletteUploadFile
        
        file = StarletteUploadFile(
            filename="test.jpg",
            file=BytesIO(file_content),
            headers={"content-type": "image/jpeg"},
        )

        with patch(
            "apps.api.src.api.v1.controllers.access_log_controller.get_settings"
        ) as mock_settings:
            mock_settings.return_value.upload_dir = str(upload_dir)
            mock_settings.return_value.max_file_size_mb = 10
            controller = AccessLogController(db_session)
            log = controller.create_access_log(plate="XYZ-9999", file=file)
            assert log.status == AccessStatus.Denied
            assert log.authorized_plate_id is None

    def test_create_access_log_invalid_file_type(self, db_session):
        """Testa criação de log com tipo de arquivo inválido."""
        from starlette.datastructures import UploadFile as StarletteUploadFile
        
        file = StarletteUploadFile(
            filename="test.txt",
            file=BytesIO(b"not an image"),
            headers={"content-type": "text/plain"},
        )

        controller = AccessLogController(db_session)
        with pytest.raises(HTTPException) as exc_info:
            controller.create_access_log(plate="ABC-1234", file=file)
        assert exc_info.value.status_code == 400

    def test_create_access_log_file_too_large(self, db_session, upload_dir):
        """Testa criação de log com arquivo muito grande."""
        # Criar arquivo maior que o limite
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
        from starlette.datastructures import UploadFile as StarletteUploadFile
        
        file = StarletteUploadFile(
            filename="test.jpg",
            file=BytesIO(large_content),
            headers={"content-type": "image/jpeg"},
        )
        file.content_type = "image/jpeg"

        with patch(
            "apps.api.src.api.v1.controllers.access_log_controller.get_settings"
        ) as mock_settings:
            mock_settings.return_value.upload_dir = str(upload_dir)
            mock_settings.return_value.max_file_size_mb = 10
            controller = AccessLogController(db_session)
            with pytest.raises(HTTPException) as exc_info:
                controller.create_access_log(plate="ABC-1234", file=file)
            assert exc_info.value.status_code == 413

    def test_get_image_path_not_found(self, db_session, upload_dir):
        """Testa busca de imagem inexistente."""
        with patch(
            "apps.api.src.api.v1.controllers.access_log_controller.get_settings"
        ) as mock_settings:
            mock_settings.return_value.upload_dir = str(upload_dir)
            controller = AccessLogController(db_session)
            with pytest.raises(HTTPException) as exc_info:
                controller.get_image_path("nonexistent.jpg")
            assert exc_info.value.status_code == 404

    def test_get_image_path_path_traversal(self, db_session, upload_dir):
        """Testa prevenção de path traversal."""
        with patch(
            "apps.api.src.api.v1.controllers.access_log_controller.get_settings"
        ) as mock_settings:
            mock_settings.return_value.upload_dir = str(upload_dir)
            controller = AccessLogController(db_session)
            with pytest.raises(HTTPException) as exc_info:
                controller.get_image_path("../../../etc/passwd")
            assert exc_info.value.status_code == 400

    def test_get_all_with_filters(self, db_session):
        """Testa listagem de logs com filtros."""
        # Criar logs de teste
        for i in range(5):
            AccessLogRepository.create(
                db_session,
                plate_string_detected=f"ABC-{i:04d}",
                status=AccessStatus.Authorized if i % 2 == 0 else AccessStatus.Denied,
                image_storage_key=f"uploads/test_{i}.jpg",
            )
        controller = AccessLogController(db_session)
        logs = controller.get_all(
            skip=0, limit=10, status_filter=AccessStatus.Authorized
        )
        assert len(logs) == 3  # Apenas os com status Authorized


class TestGateController:
    """Testes para GateController."""

    def test_trigger_gate(self):
        """Testa acionamento do portão."""
        controller = GateController()
        result = controller.trigger_gate()
        assert result["status"] == "success"
        assert "message" in result


class TestDeviceController:
    """Testes para DeviceController."""

    def test_scan_bluetooth_devices(self):
        """Testa escaneamento de dispositivos Bluetooth."""
        controller = DeviceController()
        devices = controller.scan_bluetooth_devices()
        assert isinstance(devices, list)
        assert len(devices) > 0

    def test_connect_device(self):
        """Testa conexão com dispositivo."""
        from apps.api.src.api.v1.schemas.device import ConnectionRequest

        controller = DeviceController()
        request = ConnectionRequest(device_id="test_device")
        response = controller.connect_device(request)
        assert response.status == "connected"
        assert response.device_id == "test_device"

    def test_get_connection_status(self):
        """Testa obtenção de status de conexão."""
        controller = DeviceController()
        status = controller.get_connection_status()
        assert status.connected is False

    def test_disconnect_device(self):
        """Testa desconexão de dispositivo."""
        controller = DeviceController()
        response = controller.disconnect_device()
        assert response.status == "disconnected"

