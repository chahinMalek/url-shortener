from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.entities.url import SafetyStatus
from infra.db.models import Base


class UrlModel(Base):
    __tablename__ = "urls"

    short_code: Mapped[str] = mapped_column(String(16), primary_key=True)
    long_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.user_id"), nullable=False, index=True
    )
    safety_status: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, default=SafetyStatus.PENDING.value
    )
    threat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    classifier_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
