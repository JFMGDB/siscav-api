import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.src.api.v1.db.base import GUID, Base
from apps.api.src.api.v1.schemas.access_log import AccessStatus


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    plate_string_detected: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[AccessStatus] = mapped_column(
        SAEnum(AccessStatus, name="access_status", create_constraint=True),
        nullable=False,
    )
    image_storage_key: Mapped[str] = mapped_column(String, nullable=False)
    authorized_plate_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("authorized_plates.id"), nullable=True
    )
