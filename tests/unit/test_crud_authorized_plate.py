"""Testes unitários para operações CRUD de placas autorizadas."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.api.v1.crud import crud_authorized_plate
from app.api.v1.schemas.authorized_plate import AuthorizedPlateCreate


class TestCrudAuthorizedPlateGet:
    """Testes para função get()."""

    def test_get_existing_plate(self, db_session: Session):
        """Testa obtenção de placa existente."""
        plate_create = AuthorizedPlateCreate(
            plate="ABC-1234", normalized_plate="ABC1234", description="Test plate"
        )
        created_plate = crud_authorized_plate.create(db_session, obj_in=plate_create)

        found_plate = crud_authorized_plate.get(db_session, id=created_plate.id)

        assert found_plate is not None
        assert found_plate.id == created_plate.id
        assert found_plate.plate == "ABC-1234"

    def test_get_nonexistent_plate(self, db_session: Session):
        """Testa obtenção de placa inexistente."""
        nonexistent_id = uuid4()
        found_plate = crud_authorized_plate.get(db_session, id=nonexistent_id)

        assert found_plate is None


class TestCrudAuthorizedPlateGetMulti:
    """Testes para função get_multi()."""

    def test_get_multi_empty(self, db_session: Session):
        """Testa listagem quando não há placas."""
        plates = crud_authorized_plate.get_multi(db_session)

        assert plates == []

    def test_get_multi_with_plates(self, db_session: Session):
        """Testa listagem de múltiplas placas."""
        # Cria 3 placas
        for i in range(3):
            plate_create = AuthorizedPlateCreate(
                plate=f"ABC-{1000 + i}",
                normalized_plate=f"ABC{1000 + i}",
                description=f"Plate {i}",
            )
            crud_authorized_plate.create(db_session, obj_in=plate_create)

        plates = crud_authorized_plate.get_multi(db_session)

        assert len(plates) == 3

    def test_get_multi_with_pagination(self, db_session: Session):
        """Testa paginação na listagem."""
        # Cria 5 placas
        for i in range(5):
            plate_create = AuthorizedPlateCreate(
                plate=f"XYZ-{2000 + i}",
                normalized_plate=f"XYZ{2000 + i}",
            )
            crud_authorized_plate.create(db_session, obj_in=plate_create)

        # Primeira página (skip=0, limit=2)
        page1 = crud_authorized_plate.get_multi(db_session, skip=0, limit=2)
        assert len(page1) == 2

        # Segunda página (skip=2, limit=2)
        page2 = crud_authorized_plate.get_multi(db_session, skip=2, limit=2)
        assert len(page2) == 2

        # Terceira página (skip=4, limit=2)
        page3 = crud_authorized_plate.get_multi(db_session, skip=4, limit=2)
        assert len(page3) == 1


class TestCrudAuthorizedPlateCount:
    """Testes para função count()."""

    def test_count_empty(self, db_session: Session):
        """Testa contagem quando não há placas."""
        count = crud_authorized_plate.count(db_session)

        assert count == 0

    def test_count_with_plates(self, db_session: Session):
        """Testa contagem de placas."""
        # Cria 3 placas
        for i in range(3):
            plate_create = AuthorizedPlateCreate(
                plate=f"DEF-{3000 + i}",
                normalized_plate=f"DEF{3000 + i}",
            )
            crud_authorized_plate.create(db_session, obj_in=plate_create)

        count = crud_authorized_plate.count(db_session)

        assert count == 3


class TestCrudAuthorizedPlateCreate:
    """Testes para função create()."""

    def test_create_plate_success(self, db_session: Session):
        """Testa criação bem-sucedida de placa."""
        plate_create = AuthorizedPlateCreate(
            plate="GHI-4567", normalized_plate="GHI4567", description="New plate"
        )

        created_plate = crud_authorized_plate.create(db_session, obj_in=plate_create)

        assert created_plate is not None
        assert created_plate.plate == "GHI-4567"
        assert created_plate.normalized_plate == "GHI4567"
        assert created_plate.description == "New plate"
        assert created_plate.id is not None

    def test_create_plate_duplicate_normalized(self, db_session: Session):
        """Testa que criação com placa normalizada duplicada levanta ValueError."""
        plate_create1 = AuthorizedPlateCreate(plate="JKL-7890", normalized_plate="JKL7890")
        crud_authorized_plate.create(db_session, obj_in=plate_create1)

        # Tenta criar outra placa com mesma normalização (usando formato válido diferente)
        # "JKL-7890" e "JKL 7890" normalizam para "JKL7890", mas "JKL 7890" não é formato válido
        # Então vamos usar a mesma placa normalizada diretamente
        plate_create2 = AuthorizedPlateCreate(
            plate="JKL-7890",  # Mesma placa (formato válido)
            normalized_plate="JKL7890",  # Mesma normalização
        )

        with pytest.raises(ValueError, match="already registered"):
            crud_authorized_plate.create(db_session, obj_in=plate_create2)


class TestCrudAuthorizedPlateUpdate:
    """Testes para função update()."""

    def test_update_plate_success(self, db_session: Session):
        """Testa atualização bem-sucedida de placa."""
        plate_create = AuthorizedPlateCreate(
            plate="MNO-1111", normalized_plate="MNO1111", description="Original"
        )
        created_plate = crud_authorized_plate.create(db_session, obj_in=plate_create)

        update_data = AuthorizedPlateCreate(
            plate="MNO-2222", normalized_plate="MNO2222", description="Updated"
        )
        updated_plate = crud_authorized_plate.update(
            db_session, db_obj=created_plate, obj_in=update_data
        )

        assert updated_plate.plate == "MNO-2222"
        assert updated_plate.normalized_plate == "MNO2222"
        assert updated_plate.description == "Updated"

    def test_update_plate_duplicate_normalized(self, db_session: Session):
        """Testa que atualização com placa normalizada duplicada levanta ValueError."""
        plate_create1 = AuthorizedPlateCreate(plate="PQR-3333", normalized_plate="PQR3333")
        plate1 = crud_authorized_plate.create(db_session, obj_in=plate_create1)

        plate_create2 = AuthorizedPlateCreate(plate="STU-4444", normalized_plate="STU4444")
        crud_authorized_plate.create(db_session, obj_in=plate_create2)

        # Tenta atualizar plate1 com normalização de plate2
        update_data = AuthorizedPlateCreate(
            plate="PQR-4444",
            normalized_plate="STU4444",  # Duplicado
        )

        with pytest.raises(ValueError, match="already registered"):
            crud_authorized_plate.update(db_session, db_obj=plate1, obj_in=update_data)


class TestCrudAuthorizedPlateRemove:
    """Testes para função remove()."""

    def test_remove_plate_success(self, db_session: Session):
        """Testa remoção bem-sucedida de placa."""
        plate_create = AuthorizedPlateCreate(plate="VWX-5555", normalized_plate="VWX5555")
        created_plate = crud_authorized_plate.create(db_session, obj_in=plate_create)

        removed_plate = crud_authorized_plate.remove(db_session, id=created_plate.id)

        assert removed_plate is not None
        assert removed_plate.id == created_plate.id

        # Verifica que foi removido
        found_plate = crud_authorized_plate.get(db_session, id=created_plate.id)
        assert found_plate is None

    def test_remove_nonexistent_plate(self, db_session: Session):
        """Testa remoção de placa inexistente."""
        nonexistent_id = uuid4()
        removed_plate = crud_authorized_plate.remove(db_session, id=nonexistent_id)

        assert removed_plate is None
