"""Controller para lógica de negócio de logs de acesso veicular."""

import logging
import uuid
from datetime import date, datetime
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.plate_controller import PlateController
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.repositories.access_log_repository import (
    AccessLogRepository,
    DailyAccessMetrics,
)
from apps.api.src.api.v1.repositories.ocr_attempt_repository import OcrAttemptRepository
from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.schemas.access_log import AccessLogRead, AccessStatus
from apps.api.src.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)
from apps.api.src.api.v1.utils.plate import normalize_plate, validate_brazilian_plate

logger = logging.getLogger(__name__)


class AccessLogController:
    """Controller para operações de logs de acesso veicular."""

    def __init__(self, db: Session):
        """
        Inicializa o controller com uma sessão do banco de dados.

        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        self.access_log_repository = AccessLogRepository
        self.plate_repository = AuthorizedPlateRepository
        self.settings = get_settings()

    def create_access_log(
        self,
        plate: str,
        file: UploadFile,
        *,
        ingest_via_device: bool = True,
    ) -> AccessLogRead:
        """
        Cria um novo registro de log de acesso veicular.

        Processa a imagem, normaliza a placa, verifica se está na whitelist
        e cria o registro de log com o status apropriado.

        Args:
            plate: String da placa detectada pelo OCR
            file: Arquivo de imagem do veículo

        Returns:
            AccessLogRead: Registro de acesso criado

        Raises:
            HTTPException: Se o arquivo for inválido ou muito grande
        """
        # Validar arquivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo deve ser uma imagem",
            )

        # Ler conteúdo do arquivo
        file_content = file.file.read()
        max_size_bytes = self.settings.max_file_size_mb * 1024 * 1024
        if len(file_content) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo: {self.settings.max_file_size_mb}MB",
            )

        # Normalizar placa
        normalized_plate = normalize_plate(plate)

        # Verificar se a placa está na whitelist
        authorized_plate: AuthorizedPlate | None = self.plate_repository.get_by_normalized_plate(
            self.db, normalized_plate
        )

        # Determinar status
        access_status = AccessStatus.Authorized if authorized_plate else AccessStatus.Denied
        authorized_plate_id = authorized_plate.id if authorized_plate else None
        ocr_success, _ = validate_brazilian_plate(plate)
        is_automatic = (
            ingest_via_device
            and access_status == AccessStatus.Authorized
        )

        # Salvar arquivo
        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Gerar nome único para o arquivo
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        image_filename = f"{uuid.uuid4()}{file_extension}"
        image_path = upload_dir / image_filename

        # Salvar arquivo
        with image_path.open("wb") as f:
            f.write(file_content)

        # Criar registro de log
        access_log = self.access_log_repository.create(
            db=self.db,
            plate_string_detected=plate,
            status=access_status,
            image_storage_key=str(image_path),
            authorized_plate_id=authorized_plate_id,
            is_automatic=is_automatic,
            ocr_success=ocr_success,
        )

        return AccessLogRead.model_validate(access_log)

    def whitelist_from_denied_log(
        self,
        log_id: UUID,
        description: str | None = None,
    ) -> AuthorizedPlateRead:
        """Adiciona à whitelist a placa de um log negado sem alterar o histórico."""
        access_log = self.access_log_repository.get_by_id(self.db, log_id)
        if not access_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Access log not found",
            )
        if access_log.status != AccessStatus.Denied:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only denied access logs can be whitelisted via this endpoint",
            )

        plate_controller = PlateController(self.db)
        return plate_controller.create(
            AuthorizedPlateCreate(
                plate=access_log.plate_string_detected,
                description=description,
            )
        )

    def get_daily_metrics(self, day: date) -> tuple[DailyAccessMetrics, float]:
        access = self.access_log_repository.get_daily_metrics(self.db, day)
        _, ocr_rate = OcrAttemptRepository.get_daily_success_rate(self.db, day)
        return access, ocr_rate

    def get_image_path(self, image_filename: str) -> Path:
        """
        Retorna o caminho completo de uma imagem armazenada.

        Args:
            image_filename: Nome do arquivo de imagem

        Returns:
            Path: Caminho completo do arquivo

        Raises:
            HTTPException: Se o arquivo não for encontrado ou houver tentativa de path traversal
        """
        # Prevenir path traversal
        if ".." in image_filename or "/" in image_filename or "\\" in image_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de arquivo inválido",
            )

        upload_dir = Path(self.settings.upload_dir)
        image_path = upload_dir / image_filename

        if not image_path.exists() or not image_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imagem não encontrada",
            )

        return image_path

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        plate_filter: str | None = None,
        status_filter: AccessStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AccessLogRead]:
        """
        Lista registros de acesso veicular com filtros opcionais.

        Args:
            skip: Número de registros a pular (paginação)
            limit: Número máximo de registros a retornar
            plate_filter: Filtrar por placa (busca parcial, case-insensitive)
            status_filter: Filtrar por status de acesso
            start_date: Data inicial para filtrar (inclusive)
            end_date: Data final para filtrar (inclusive)

        Returns:
            Lista de registros de acesso ordenados por timestamp (mais recente primeiro)
        """
        access_logs = self.access_log_repository.get_all(
            db=self.db,
            skip=skip,
            limit=limit,
            plate_filter=plate_filter,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
        )

        return [AccessLogRead.model_validate(log) for log in access_logs]

    def count(
        self,
        plate_filter: str | None = None,
        status_filter: AccessStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """
        Conta o total de registros de acesso com filtros opcionais.

        Args:
            plate_filter: Filtrar por placa (busca parcial, case-insensitive)
            status_filter: Filtrar por status de acesso
            start_date: Data inicial para filtrar (inclusive)
            end_date: Data final para filtrar (inclusive)

        Returns:
            Número total de registros que correspondem aos filtros
        """
        return self.access_log_repository.count(
            db=self.db,
            plate_filter=plate_filter,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
        )
