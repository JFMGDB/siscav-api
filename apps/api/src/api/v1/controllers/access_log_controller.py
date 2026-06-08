"""Controller para lógica de negócio de logs de acesso veicular."""

import logging
import uuid
from datetime import date, datetime
from functools import partial
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.controllers.plate_controller import PlateController
from apps.api.src.api.v1.core import error_messages as err
from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.validation_errors import translate_validation_errors
from apps.api.src.api.v1.ml.classifier import (
    classifier_onnx_stack_available,
    get_vehicle_classifier,
)
from apps.api.src.api.v1.models.authorized_plate import AuthorizedPlate
from apps.api.src.api.v1.repositories.access_log_repository import (
    AccessLogRepository,
    DailyAccessMetrics,
)
from apps.api.src.api.v1.repositories.authorized_plate_repository import (
    AuthorizedPlateRepository,
)
from apps.api.src.api.v1.repositories.ocr_attempt_repository import OcrAttemptRepository
from apps.api.src.api.v1.schemas.access_log import AccessLogRead, AccessStatus
from apps.api.src.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)
from apps.api.src.api.v1.schemas.classification import (
    VehicleCategory,
    VehicleClassificationResult,
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

    async def create_access_log(
        self,
        plate: str,
        file: UploadFile,
        *,
        _ingest_via_device: bool = True,
        operator_override: bool = False,
        owner_user_id: UUID | None = None,
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
                detail=err.FILE_MUST_BE_IMAGE,
            )

        # Ler conteúdo do arquivo
        file_content = file.file.read()
        max_size_bytes = self.settings.max_file_size_mb * 1024 * 1024
        if len(file_content) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=err.FILE_TOO_LARGE.format(max_mb=self.settings.max_file_size_mb),
            )

        vehicle_classification: VehicleClassificationResult | None = None
        ambulance_authorized = False

        if self.settings.vehicle_classifier_backend == "onnx" and classifier_onnx_stack_available():
            import cv2  # noqa: PLC0415
            import numpy as np  # noqa: PLC0415

            arr = np.frombuffer(file_content, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is not None:
                classifier = get_vehicle_classifier()
                try:
                    vehicle_classification = await run_in_threadpool(
                        partial(classifier.classify, frame, plate_hint=plate)
                    )
                except Exception:
                    logger.exception("Vehicle classification failed during access log ingest")
                else:
                    if (
                        vehicle_classification.predicted_category == VehicleCategory.ambulance
                        and vehicle_classification.confidence
                        >= self.settings.vehicle_classifier_threshold
                    ):
                        ambulance_authorized = True
                        logger.info(
                            "ambulance_auto_authorized",
                            extra={
                                "plate": plate,
                                "confidence": vehicle_classification.confidence,
                                "model_version": vehicle_classification.model_version,
                            },
                        )

        # Normalizar placa
        normalized_plate = normalize_plate(plate)

        # Verificar se a placa está na whitelist
        authorized_plate: AuthorizedPlate | None = self.plate_repository.get_by_normalized_plate(
            self.db, normalized_plate
        )

        # Determinar status
        if ambulance_authorized:
            access_status = AccessStatus.Authorized
            authorized_plate_id = authorized_plate.id if authorized_plate else None
        else:
            access_status = AccessStatus.Authorized if authorized_plate else AccessStatus.Denied
            authorized_plate_id = authorized_plate.id if authorized_plate else None

        ocr_success, _ = validate_brazilian_plate(plate)
        is_automatic = access_status == AccessStatus.Authorized and not operator_override

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
            owner_user_id=owner_user_id,
        )

        log_read = AccessLogRead.model_validate(access_log)
        if vehicle_classification is not None:
            log_read = log_read.model_copy(
                update={"vehicle_classification": vehicle_classification}
            )

        if self.settings.gate_auto_open_on_authorize and access_status == AccessStatus.Authorized:
            gate_controller = GateController(self.settings)
            gate_trigger = gate_controller.trigger_gate_safe()
            log_read = log_read.model_copy(update={"gate_trigger": gate_trigger})

        return log_read

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
                detail=err.ACCESS_LOG_NOT_FOUND,
            )
        if access_log.status != AccessStatus.Denied:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err.ONLY_DENIED_LOG_WHITELIST,
            )

        plate_controller = PlateController(self.db)
        try:
            plate_data = AuthorizedPlateCreate(
                plate=access_log.plate_string_detected,
                description=description,
            )
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=translate_validation_errors(exc.errors()),
            ) from exc
        return plate_controller.create(plate_data)

    def get_daily_metrics(self, day: date, owner_user_id: UUID) -> tuple[DailyAccessMetrics, float]:
        access = self.access_log_repository.get_daily_metrics(self.db, day, owner_user_id)
        _, ocr_rate = OcrAttemptRepository.get_daily_success_rate(self.db, day, owner_user_id)
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
        if ".." in image_filename or "/" in image_filename or "\\" in image_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err.INVALID_FILENAME,
            )

        upload_dir = Path(self.settings.upload_dir)
        image_path = upload_dir / image_filename

        if not image_path.exists() or not image_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err.IMAGE_NOT_FOUND,
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
        owner_user_id: UUID | None = None,
    ) -> list[AccessLogRead]:
        """Lista registros de acesso veicular com filtros opcionais."""
        access_logs = self.access_log_repository.get_all(
            db=self.db,
            skip=skip,
            limit=limit,
            plate_filter=plate_filter,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            owner_user_id=owner_user_id,
        )

        return [AccessLogRead.model_validate(log) for log in access_logs]

    def count(
        self,
        plate_filter: str | None = None,
        status_filter: AccessStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Conta o total de registros de acesso com filtros opcionais."""
        return self.access_log_repository.count(
            db=self.db,
            plate_filter=plate_filter,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
        )
