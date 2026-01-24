from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models import Base


class ClassificationResultModel(Base):
    __tablename__ = "classification_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url_short_code: Mapped[str] = mapped_column(
        String(16), ForeignKey("urls.short_code"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    threat_score: Mapped[float] = mapped_column(Float, nullable=False)
    classifier: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
