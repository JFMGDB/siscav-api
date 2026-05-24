"""Testes unitários para AccessLogController."""

import io
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.repositories.access_log_repository import AccessLogRepository
from apps.api.src.api.v1.repositories.authorized_plate_repository import AuthorizedPlateRepository
from apps.api.src.api.v1.schemas.access_log import AccessStatus


class TestAccessLogController:
    """Testes para AccessLogController."""

    def test_create_access_log_authorized(self, db_session: Session):
        """Testa criação de log de acesso autorizado."""
        # Criar placa autorizada
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        # Criar arquivo de imagem simulado
        file_content = b"fake image content"
        file = UploadFile(
            filename="test.jpg",
            file=io.BytesIO(file_content),
            headers={"content-type": "image/jpeg"},
        )

        controller = AccessLogController(db_session)
        result = controller.create_access_log(plate="ABC-1234", file=file)

        assert result.status == AccessStatus.Authorized
        assert result.plate_string_detected == "ABC-1234"
        assert result.authorized_plate_id == plate.id
        assert result.image_storage_key is not None

        # Verificar que arquivo foi salvo
        image_path = Path(result.image_storage_key)
        assert image_path.exists()
        assert image_path.read_bytes() == file_content

        # Limpar
        image_path.unlink()

    def test_create_access_log_denied(self, db_session: Session):
        """Testa criação de log de acesso negado."""
        # Criar arquivo de imagem simulado
        file_content = b"fake image content"
        file = UploadFile(
            filename="test.jpg",
            file=io.BytesIO(file_content),
            headers={"content-type": "image/jpeg"},
        )

        controller = AccessLogController(db_session)
        result = controller.create_access_log(plate="XYZ-9999", file=file)

        assert result.status == AccessStatus.Denied
        assert result.plate_string_detected == "XYZ-9999"
        assert result.authorized_plate_id is None
        assert result.image_storage_key is not None

        # Limpar
        Path(result.image_storage_key).unlink()

    def test_create_access_log_invalid_file_type(self, db_session: Session):
        """Testa criação de log com arquivo inválido."""
        file = UploadFile(
            filename="test.txt",
            file=io.BytesIO(b"not an image"),
            headers={"content-type": "text/plain"},
        )

        controller = AccessLogController(db_session)

        with pytest.raises(HTTPException) as exc_info:
            controller.create_access_log(plate="ABC-1234", file=file)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "imagem" in str(exc_info.value.detail).lower()

    def test_create_access_log_file_too_large(self, db_session: Session, monkeypatch):
        """Testa criação de log com arquivo muito grande."""
        # Mock para reduzir tamanho máximo
        settings = get_settings()
        original_max_size = settings.max_file_size_mb
        monkeypatch.setattr(settings, "max_file_size_mb", 1)  # 1MB

        # Criar arquivo grande (2MB)
        large_content = b"x" * (2 * 1024 * 1024)
        file = UploadFile(
            filename="large.jpg",
            file=io.BytesIO(large_content),
            headers={"content-type": "image/jpeg"},
        )

        controller = AccessLogController(db_session)

        with pytest.raises(HTTPException) as exc_info:
            controller.create_access_log(plate="ABC-1234", file=file)

        assert exc_info.value.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

        # Restaurar valor original
        monkeypatch.setattr(settings, "max_file_size_mb", original_max_size)

    def test_get_image_path_success(self, db_session: Session):
        """Testa obtenção de caminho de imagem existente."""
        # Criar arquivo de teste
        test_dir = Path("uploads")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test_image.jpg"
        test_file.write_bytes(b"test content")

        controller = AccessLogController(db_session)
        result = controller.get_image_path("test_image.jpg")

        assert result == test_file
        assert result.exists()

        # Limpar
        test_file.unlink()

    def test_get_image_path_not_found(self, db_session: Session):
        """Testa obtenção de caminho de imagem inexistente."""
        controller = AccessLogController(db_session)

        with pytest.raises(HTTPException) as exc_info:
            controller.get_image_path("nonexistent.jpg")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_image_path_path_traversal(self, db_session: Session):
        """Testa prevenção de path traversal."""
        controller = AccessLogController(db_session)

        with pytest.raises(HTTPException) as exc_info:
            controller.get_image_path("../../../etc/passwd")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_all_with_filters(self, db_session: Session):
        """Testa listagem de logs com filtros."""
        # Criar logs de teste
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

        controller = AccessLogController(db_session)

        # Filtrar por status
        authorized_logs = controller.get_all(status_filter=AccessStatus.Authorized)
        assert len(authorized_logs) == 1
        assert authorized_logs[0].status == AccessStatus.Authorized

        # Filtrar por placa
        plate_logs = controller.get_all(plate_filter="ABC")
        assert len(plate_logs) >= 1

    def test_count_with_filters(self, db_session: Session):
        """Testa contagem de logs com filtros."""
        # Criar logs de teste
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

        controller = AccessLogController(db_session)

        total = controller.count()
        assert total == 2

        authorized_count = controller.count(status_filter=AccessStatus.Authorized)
        assert authorized_count == 1

        denied_count = controller.count(status_filter=AccessStatus.Denied)
        assert denied_count == 1
