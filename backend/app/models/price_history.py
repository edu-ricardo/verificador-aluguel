from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.listing import PlatformListing


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("platform_listings.id", ondelete="CASCADE"), index=True
    )

    target_date: Mapped[date] = mapped_column(Date, index=True)  # Data específica da diária
    daily_rate: Mapped[float] = mapped_column(Float)  # Valor da diária nesta data
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relacionamento
    listing: Mapped["PlatformListing"] = relationship("PlatformListing", back_populates="price_history")
