from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.listing import PlatformListing


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    property_type: Mapped[str] = mapped_column(String(50), default="chacara", index=True)  # chacara, sitio, casa

    # Localização
    state: Mapped[str] = mapped_column(String(2), index=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Capacidade e comodidades
    max_guests: Mapped[int] = mapped_column(Integer, default=1, index=True)
    bedrooms: Mapped[int] = mapped_column(Integer, default=1)
    bathrooms: Mapped[int] = mapped_column(Integer, default=1)
    has_pool: Mapped[bool] = mapped_column(Boolean, default=False)
    has_bbq: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_pets: Mapped[bool] = mapped_column(Boolean, default=False)
    amenities: Mapped[Optional[dict]] = mapped_column(JSON, default=list)  # ["wifi", "piscina", "churrasqueira", etc.]
    images: Mapped[Optional[dict]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    listings: Mapped[List["PlatformListing"]] = relationship(
        "PlatformListing", back_populates="property", cascade="all, delete-orphan", lazy="selectin"
    )
