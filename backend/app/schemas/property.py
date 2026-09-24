from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ListingBase(BaseModel):
    platform: str
    external_id: str
    url: str
    base_daily_rate: float
    cleaning_fee: float = 0.0
    service_fee: float = 0.0
    rating: Optional[float] = None
    reviews_count: int = 0
    is_active: bool = True


class PropertyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    property_type: str = "chacara"
    state: str
    city: str
    neighborhood: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_guests: int = 1
    bedrooms: int = 1
    bathrooms: int = 1
    has_pool: bool = False
    has_bbq: bool = False
    allows_pets: bool = False
    amenities: List[str] = []
    images: List[str] = []
    listings: List[ListingBase] = []


class PropertyDetail(PropertyCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
