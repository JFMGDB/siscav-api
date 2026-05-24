"""Testes unitários para AuthorizedPlateRepository."""

from uuid import uuid4

from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.repositories.authorized_plate_repository import AuthorizedPlateRepository


class TestAuthorizedPlateRepository:
    """Testes para AuthorizedPlateRepository."""

    def test_get_by_id_success(self, db_session: Session):
        """Testa busca de placa por ID com sucesso."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test plate",
        )

        result = AuthorizedPlateRepository.get_by_id(db_session, plate.id)

        assert result is not None
        assert result.id == plate.id
        assert result.plate == "ABC-1234"

    def test_get_by_id_not_found(self, db_session: Session):
        """Testa busca de placa por ID inexistente."""
        fake_id = uuid4()
        result = AuthorizedPlateRepository.get_by_id(db_session, fake_id)

        assert result is None

    def test_get_by_normalized_plate_success(self, db_session: Session):
        """Testa busca de placa por versão normalizada com sucesso."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        result = AuthorizedPlateRepository.get_by_normalized_plate(db_session, "ABC1234")

        assert result is not None
        assert result.id == plate.id

    def test_get_by_normalized_plate_not_found(self, db_session: Session):
        """Testa busca de placa por versão normalizada inexistente."""
        result = AuthorizedPlateRepository.get_by_normalized_plate(db_session, "XYZ9999")

        assert result is None

    def test_get_all(self, db_session: Session):
        """Testa listagem de placas com paginação."""
        # Criar múltiplas placas
        for i in range(5):
            AuthorizedPlateRepository.create(
                db_session,
                plate=f"ABC-{i:04d}",
                normalized_plate=f"ABC{i:04d}",
            )

        result = AuthorizedPlateRepository.get_all(db_session, skip=0, limit=3)

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

        result = AuthorizedPlateRepository.get_all(db_session, skip=2, limit=2)

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

        count = AuthorizedPlateRepository.count(db_session)

        assert count == 3

    def test_create_success(self, db_session: Session):
        """Testa criação de placa com sucesso."""
        result = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Test plate",
        )

        assert result is not None
        assert result.plate == "ABC-1234"
        assert result.normalized_plate == "ABC1234"
        assert result.description == "Test plate"

    def test_update_success(self, db_session: Session):
        """Testa atualização de placa com sucesso."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
            description="Original",
        )

        result = AuthorizedPlateRepository.update(
            db_session,
            plate=plate,
            plate_value="XYZ-5678",
            normalized_plate="XYZ5678",
            description="Updated",
        )

        assert result.plate == "XYZ-5678"
        assert result.normalized_plate == "XYZ5678"
        assert result.description == "Updated"

    def test_delete_success(self, db_session: Session):
        """Testa remoção de placa com sucesso."""
        plate = AuthorizedPlateRepository.create(
            db_session,
            plate="ABC-1234",
            normalized_plate="ABC1234",
        )

        result = AuthorizedPlateRepository.delete(db_session, plate.id)

        assert result is not None
        assert result.id == plate.id

        # Verificar que foi removida
        deleted = AuthorizedPlateRepository.get_by_id(db_session, plate.id)
        assert deleted is None

    def test_delete_not_found(self, db_session: Session):
        """Testa remoção de placa inexistente."""
        fake_id = uuid4()
        result = AuthorizedPlateRepository.delete(db_session, fake_id)

        assert result is None
