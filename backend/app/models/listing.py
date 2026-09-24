from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.price_history import PriceHistory
    from app.models.property import Property


class PlatformListing(Base):
    __tablename__ = "platform_listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), index=True)

    platform: Mapped[str] = mapped_column(String(50), index=True)  # temporadalivre, olx, airbnb, booking
    external_id: Mapped[str] = mapped_column(String(100), index=True)
    url: Mapped[str] = mapped_column(String(1000))

    base_daily_rate: Mapped[float] = mapped_column(Float, default=0.0)  # Preço por diária anunciado
    cleaning_fee: Mapped[float] = mapped_column(Float, default=0.0)  # Taxa de limpeza
    service_fee: Mapped[float] = mapped_column(Float, default=0.0)  # Taxa da plataforma
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Ex: 4.85
    reviews_count: Mapped[int] = mapped_column(Float, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    property: Mapped["Property"] = relationship("Property", back_populates="listings")
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="listing", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (Index("idx_platform_external_id", "platform", "external_id", unique=True),)
