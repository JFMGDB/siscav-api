"""Controller para lógica de negócio de placas autorizadas."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.schemas.authorized_plate import AuthorizedPlateCreate
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

    def get_by_id(self, plate_id: UUID) -> AuthorizedPlate:
        """
        Busca uma placa autorizada por ID.

        Args:
            plate_id: ID único da placa

        Returns:
            AuthorizedPlate encontrada

        Raises:
            HTTPException: Se a placa não for encontrada
        """
        plate = self.plate_repository.get_by_id(self.db, plate_id)
        if not plate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found"
            )
        return plate

    def get_all(self, skip: int = 0, limit: int = 100) -> list[AuthorizedPlate]:
        """
        Lista todas as placas autorizadas com paginação.

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            Lista de placas autorizadas
        """
        return self.plate_repository.get_all(self.db, skip=skip, limit=limit)

    def create(self, plate_data: AuthorizedPlateCreate) -> AuthorizedPlate:
        """
        Cria uma nova placa autorizada.

        Aplica validação de formato e normalização automática.

        Args:
            plate_data: Dados da placa a ser criada

        Returns:
            AuthorizedPlate criada

        Raises:
            HTTPException: Se a placa for inválida ou já existir
        """
        logger.info(f"Tentativa de criar placa autorizada: {plate_data.plate}")
        
        # Validar formato da placa
        is_valid, error_message = validate_brazilian_plate(plate_data.plate)
        if not is_valid:
            logger.warning(f"Placa inválida: {plate_data.plate} - {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )

        # Normalizar placa
        normalized = (
            plate_data.normalized_plate or normalize_plate(plate_data.plate)
        )

        # Verificar se já existe
        existing = self.plate_repository.get_by_normalized_plate(self.db, normalized)
        if existing:
            logger.warning(f"Tentativa de criar placa duplicada: {normalized}")
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
            logger.info(f"Placa autorizada criada com sucesso: {normalized} (ID: {plate.id})")
            return plate
        except Exception as e:
            logger.error(f"Erro ao criar placa autorizada: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar placa autorizada",
            )

    def update(
        self, plate_id: UUID, plate_data: AuthorizedPlateCreate
    ) -> AuthorizedPlate:
        """
        Atualiza uma placa autorizada existente.

        Aplica validação de formato e normalização automática.

        Args:
            plate_id: ID da placa a ser atualizada
            plate_data: Novos dados da placa

        Returns:
            AuthorizedPlate atualizada

        Raises:
            HTTPException: Se a placa não for encontrada ou for inválida
        """
        # Buscar placa existente
        plate = self.get_by_id(plate_id)

        # Validar formato da placa
        is_valid, error_message = validate_brazilian_plate(plate_data.plate)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )

        # Normalizar placa
        normalized = (
            plate_data.normalized_plate or normalize_plate(plate_data.plate)
        )

        # Verificar se a nova placa normalizada já existe em outro registro
        existing = self.plate_repository.get_by_normalized_plate(self.db, normalized)
        if existing and existing.id != plate_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plate already exists in whitelist",
            )

        # Atualizar placa
        return self.plate_repository.update(
            self.db,
            plate=plate,
            plate_value=plate_data.plate,
            normalized_plate=normalized,
            description=plate_data.description,
        )

    def delete(self, plate_id: UUID) -> AuthorizedPlate:
        """
        Remove uma placa autorizada.

        Args:
            plate_id: ID da placa a ser removida

        Returns:
            AuthorizedPlate removida

        Raises:
            HTTPException: Se a placa não for encontrada
        """
        plate = self.get_by_id(plate_id)
        self.plate_repository.delete(self.db, plate_id)
        return plate

    def check_authorization(self, plate: str) -> tuple[bool, Optional[UUID]]:
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
        authorized_plate = self.plate_repository.get_by_normalized_plate(
            self.db, normalized
        )

        if authorized_plate:
            return True, authorized_plate.id
        return False, None

