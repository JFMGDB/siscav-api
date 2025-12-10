"""Testes unitários para PlateController."""

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.v1.controllers.plate_controller import PlateController
from app.api.v1.models.authorized_plate import AuthorizedPlate
from app.api.v1.repositories.authorized_plate_repository import AuthorizedPlateRepository
from app.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


class TestPlateController:
    """Testes para PlateController."""

    def test_get_by_id_success(self, db_session: Session):
        """Testa busca de placa por ID com sucesso."""
        # Criar placa de teste
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test plate",
        )

        controller = PlateController(db_session)
        result = controller.get_by_id(plate.id)

        assert result is not None
        assert result.id == plate.id
        assert result.plate == "ABC-1234"
        assert result.normalized_plate == "ABC1234"

    def test_get_by_id_not_found(self, db_session: Session):
        """Testa busca de placa por ID inexistente."""
        controller = PlateController(db_session)
        fake_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            controller.get_by_id(fake_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Plate not found" in str(exc_info.value.detail)

    def test_get_all(self, db_session: Session):
        """Testa listagem de placas com paginação."""
        # Criar múltiplas placas
        for i in range(5):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
            )

        controller = PlateController(db_session)
        result = controller.get_all(skip=0, limit=3)

        assert len(result) == 3
        assert all(isinstance(p, AuthorizedPlate) for p in result)

    def test_get_all_with_pagination(self, db_session: Session):
        """Testa paginação na listagem de placas."""
        # Criar múltiplas placas
        for i in range(5):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
            )

        controller = PlateController(db_session)
        result = controller.get_all(skip=2, limit=2)

        assert len(result) == 2

    def test_count(self, db_session: Session):
        """Testa contagem de placas."""
        # Criar múltiplas placas
        for i in range(3):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
            )

        controller = PlateController(db_session)
        count = controller.count()

        assert count == 3

    def test_create_success(self, db_session: Session):
        """Testa criação de placa autorizada com sucesso."""
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(plate="ABC-1234", description="Test plate")

        result = controller.create(plate_data)

        assert result is not None
        assert result.plate == "ABC-1234"
        assert result.normalized_plate == "ABC1234"
        assert result.description == "Test plate"

    def test_create_invalid_plate_format(self, db_session: Session):
        """Testa criação de placa com formato inválido."""
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(plate="INVALID", description="Invalid plate")

        with pytest.raises(HTTPException) as exc_info:
            controller.create(plate_data)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_duplicate_plate(self, db_session: Session):
        """Testa criação de placa duplicada."""
        # Criar placa existente
        AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(plate="ABC-1234", description="Duplicate")

        with pytest.raises(HTTPException) as exc_info:
            controller.create(plate_data)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in str(exc_info.value.detail).lower()

    def test_create_mercosul_plate(self, db_session: Session):
        """Testa criação de placa no formato Mercosul."""
        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(plate="ABC1D23", description="Mercosul plate")

        result = controller.create(plate_data)

        assert result is not None
        assert result.normalized_plate == "ABC1D23"

    def test_update_success(self, db_session: Session):
        """Testa atualização de placa com sucesso."""
        # Criar placa existente
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Original",
        )

        controller = PlateController(db_session)
        plate_data = AuthorizedPlateCreate(plate="XYZ-5678", description="Updated")

        result = controller.update(plate.id, plate_data)

        assert result.plate == "XYZ-5678"
        assert result.normalized_plate == "XYZ5678"
        assert result.description == "Updated"

    def test_update_not_found(self, db_session: Session):
        """Testa atualização de placa inexistente."""
        controller = PlateController(db_session)
        fake_id = uuid4()
        plate_data = AuthorizedPlateCreate(plate="ABC-1234")

        with pytest.raises(HTTPException) as exc_info:
            controller.update(fake_id, plate_data)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_success(self, db_session: Session):
        """Testa remoção de placa com sucesso."""
        # Criar placa existente
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        controller = PlateController(db_session)
        result = controller.delete(plate.id)

        assert result.id == plate.id

        # Verificar que foi removida
        with pytest.raises(HTTPException):
            controller.get_by_id(plate.id)

    def test_check_authorization_authorized(self, db_session: Session):
        """Testa verificação de autorização para placa autorizada."""
        # Criar placa autorizada
        AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        controller = PlateController(db_session)
        is_authorized, plate_id = controller.check_authorization("ABC-1234")

        assert is_authorized is True
        assert plate_id is not None

    def test_check_authorization_denied(self, db_session: Session):
        """Testa verificação de autorização para placa não autorizada."""
        controller = PlateController(db_session)
        is_authorized, plate_id = controller.check_authorization("XYZ-9999")

        assert is_authorized is False
        assert plate_id is None

    def test_check_authorization_normalizes_plate(self, db_session: Session):
        """Testa que verificação de autorização normaliza a placa."""
        # Criar placa autorizada
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        controller = PlateController(db_session)
        # Testar com diferentes formatos que devem ser normalizados para o mesmo
        is_authorized1, _ = controller.check_authorization("ABC-1234")
        is_authorized2, _ = controller.check_authorization("abc 1234")
        is_authorized3, _ = controller.check_authorization("ABC1234")

        assert is_authorized1 is True
        assert is_authorized2 is True
        assert is_authorized3 is True

