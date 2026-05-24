"""Controller para lógica de negócio de placas autorizadas."""

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)
from apps.api.src.api.v1.utils.plate import normalize_plate, validate_brazilian_plate

logger = logging.getLogger(__name__)


class PlateController:
    """Controller para operações de placas autorizadas."""

    def __init__(self, db: Session):
        """
        Inicializa o controller com uma sessão do banco de dados.

        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        # Repositories são classes com métodos estáticos, não requerem instanciação
        self.plate_repository = AuthorizedPlateRepository

    def get_by_id(self, plate_id: UUID) -> AuthorizedPlateRead:
        """
        Busca uma placa autorizada por ID.

        Args:
            plate_id: ID único da placa

        Returns:
            AuthorizedPlateRead encontrada

        Raises:
            HTTPException: Se a placa não for encontrada
        """
        plate = self.plate_repository.get_by_id(self.db, plate_id)
        if not plate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")
        return AuthorizedPlateRead.model_validate(plate)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[AuthorizedPlateRead]:
        """
        Lista todas as placas autorizadas com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            Lista de placas autorizadas
        """
        plates = self.plate_repository.get_all(self.db, skip=skip, limit=limit)
        return [AuthorizedPlateRead.model_validate(plate) for plate in plates]

    def create(self, plate_data: AuthorizedPlateCreate) -> AuthorizedPlateRead:
        """
        Cria uma nova placa autorizada.

        Aplica validação de formato e normalização automática.

        Args:
            plate_data: Dados da placa a ser criada

        Returns:
            AuthorizedPlateRead criada

        Raises:
            HTTPException: Se a placa for inválida ou já existir
        """
        logger.info("Creating authorized plate: %s", plate_data.plate)

        # Validar formato da placa
        is_valid, error_message = validate_brazilian_plate(plate_data.plate)
        if not is_valid:
            logger.warning("Invalid plate: %s - %s", plate_data.plate, error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        # Normalizar placa
        normalized = plate_data.normalized_plate or normalize_plate(plate_data.plate)

        # Verificar se já existe
        existing = self.plate_repository.get_by_normalized_plate(self.db, normalized)
        if existing:
            logger.warning("Duplicate plate creation attempt: %s", normalized)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plate already exists in whitelist",
            )

        # Criar placa
        try:
            plate = self.plate_repository.create(
                self.db,
                plate=plate_data.plate,
                normalized_plate=normalized,
                description=plate_data.description,
            )
            logger.info("Authorized plate created: %s (ID: %s)", normalized, plate.id)
            return AuthorizedPlateRead.model_validate(plate)
        except Exception as e:
            logger.exception("Error creating authorized plate")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar placa autorizada",
            ) from e

    def update(self, plate_id: UUID, plate_data: AuthorizedPlateCreate) -> AuthorizedPlateRead:
        """
        Atualiza uma placa autorizada existente.

        Aplica validação de formato e normalização automática.

        Args:
            plate_id: ID da placa a ser atualizada
            plate_data: Novos dados da placa

        Returns:
            AuthorizedPlateRead atualizada

        Raises:
            HTTPException: Se a placa não for encontrada ou for inválida
        """
        # Buscar placa existente
        plate = self.plate_repository.get_by_id(self.db, plate_id)
        if not plate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")

        # Validar formato da placa
        is_valid, error_message = validate_brazilian_plate(plate_data.plate)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        # Normalizar placa
        normalized = plate_data.normalized_plate or normalize_plate(plate_data.plate)

        # Verificar se a nova placa normalizada já existe em outro registro
        existing = self.plate_repository.get_by_normalized_plate(self.db, normalized)
        if existing and existing.id != plate_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plate already exists in whitelist",
            )

        # Atualizar placa
        updated_plate = self.plate_repository.update(
            self.db,
            plate=plate,
            plate_value=plate_data.plate,
            normalized_plate=normalized,
            description=plate_data.description,
        )
        return AuthorizedPlateRead.model_validate(updated_plate)

    def delete(self, plate_id: UUID) -> AuthorizedPlateRead:
        """
        Remove uma placa autorizada.

        Args:
            plate_id: ID da placa a ser removida

        Returns:
            AuthorizedPlateRead removida

        Raises:
            HTTPException: Se a placa não for encontrada
        """
        plate = self.plate_repository.get_by_id(self.db, plate_id)
        if not plate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")
        self.plate_repository.delete(self.db, plate_id)
        return AuthorizedPlateRead.model_validate(plate)

    def check_authorization(self, plate: str) -> tuple[bool, UUID | None]:
        """
        Verifica se uma placa está autorizada.

        Args:
            plate: Placa a ser verificada (será normalizada automaticamente)

        Returns:
            Tupla (is_authorized, authorized_plate_id)
            - is_authorized: True se a placa está autorizada
            - authorized_plate_id: ID da placa autorizada se encontrada, None caso contrário
        """
        normalized = normalize_plate(plate)
        authorized_plate = self.plate_repository.get_by_normalized_plate(self.db, normalized)

        if authorized_plate:
            return True, authorized_plate.id
        return False, None

    def count(self) -> int:
        """
        Conta o total de placas autorizadas no banco de dados.

        Returns:
            Número total de placas autorizadas
        """
        return self.plate_repository.count(self.db)
