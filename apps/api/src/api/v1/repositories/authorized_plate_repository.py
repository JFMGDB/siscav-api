"""Repository para operações de acesso a dados de placas autorizadas."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate


class AuthorizedPlateRepository:
    """Repository para operações de banco de dados relacionadas a placas autorizadas."""

    @staticmethod
    def get_by_id(db: Session, plate_id: UUID) -> Optional[AuthorizedPlate]:
        """
        Busca uma placa autorizada por ID.

        Args:
            db: Sessão do banco de dados
            plate_id: ID único da placa

        Returns:
            AuthorizedPlate se encontrada, None caso contrário
        """
        return db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == plate_id))

    @staticmethod
    def get_by_normalized_plate(
        db: Session, normalized_plate: str
    ) -> Optional[AuthorizedPlate]:
        """
        Busca uma placa autorizada pela versão normalizada.

        Args:
            db: Sessão do banco de dados
            normalized_plate: Placa normalizada (sem hífens, maiúscula)

        Returns:
            AuthorizedPlate se encontrada, None caso contrário
        """
        return db.scalar(
            select(AuthorizedPlate).where(
                AuthorizedPlate.normalized_plate == normalized_plate
            )
        )

    @staticmethod
    def get_all(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[AuthorizedPlate]:
        """
        Lista placas autorizadas com paginação.

        Args:
            db: Sessão do banco de dados
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            Lista de placas autorizadas
        """
        return list(db.scalars(select(AuthorizedPlate).offset(skip).limit(limit)))

    @staticmethod
    def create(
        db: Session,
        plate: str,
        normalized_plate: str,
        description: Optional[str] = None,
    ) -> AuthorizedPlate:
        """
        Cria uma nova placa autorizada.

        Args:
            db: Sessão do banco de dados
            plate: Placa no formato original
            normalized_plate: Placa normalizada
            description: Descrição opcional da placa

        Returns:
            AuthorizedPlate criada
        """
        db_plate = AuthorizedPlate(
            plate=plate,
            normalized_plate=normalized_plate,
            description=description,
        )
        db.add(db_plate)
        try:
            db.commit()
            db.refresh(db_plate)
        except Exception:
            db.rollback()
            raise
        return db_plate

    @staticmethod
    def update(
        db: Session,
        plate: AuthorizedPlate,
        plate_value: str,
        normalized_plate: str,
        description: Optional[str] = None,
    ) -> AuthorizedPlate:
        """
        Atualiza uma placa autorizada existente.

        Args:
            db: Sessão do banco de dados
            plate: Objeto AuthorizedPlate existente
            plate_value: Nova placa no formato original
            normalized_plate: Nova placa normalizada
            description: Nova descrição opcional

        Returns:
            AuthorizedPlate atualizada
        """
        plate.plate = plate_value
        plate.normalized_plate = normalized_plate
        plate.description = description
        try:
            db.commit()
            db.refresh(plate)
        except Exception:
            db.rollback()
            raise
        return plate

    @staticmethod
    def delete(db: Session, plate_id: UUID) -> Optional[AuthorizedPlate]:
        """
        Remove uma placa autorizada por ID.

        Args:
            db: Sessão do banco de dados
            plate_id: ID único da placa

        Returns:
            AuthorizedPlate removida se encontrada, None caso contrário
        """
        plate = db.scalar(select(AuthorizedPlate).where(AuthorizedPlate.id == plate_id))
        if plate:
            db.delete(plate)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
        return plate

