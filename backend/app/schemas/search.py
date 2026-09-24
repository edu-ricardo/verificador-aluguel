from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    city: str = Field(..., description="Cidade para busca (ex: Atibaia, Ibiúna, Ubatuba)")
    state: Optional[str] = Field(None, max_length=2, description="Sigla do estado (ex: SP, MG, RJ)")
    property_type: Optional[str] = Field("todos", description="chacara, sitio, casa ou todos")
    check_in: Optional[date] = Field(None, description="Data de entrada (check-in)")
    check_out: Optional[date] = Field(None, description="Data de saída (check-out)")
    guests: int = Field(1, ge=1, le=100, description="Número de hóspedes")
    min_price: Optional[float] = Field(None, ge=0, description="Preço mínimo por diária ou total")
    max_price: Optional[float] = Field(None, ge=0, description="Preço máximo por diária ou total")
    has_pool: Optional[bool] = Field(None, description="Filtrar apenas com piscina")
    allows_pets: Optional[bool] = Field(None, description="Aceita animais de estimação")
    platforms: Optional[List[str]] = Field(None, description="Filtrar por plataformas específicas")
    sort_by: Optional[str] = Field("price_asc", description="price_asc, price_desc, guests_desc")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PlatformComparisonItem(BaseModel):
    platform: str
    platform_name: str
    url: str
    external_id: str
    daily_rate: float
    cleaning_fee: float
    service_fee: float
    total_price: float
    rating: Optional[float] = None
    reviews_count: int = 0
    is_cheapest: bool = False
    savings_vs_highest: float = 0.0


class SearchPropertyItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    property_type: str
    city: str
    state: str
    neighborhood: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_guests: int
    bedrooms: int
    bathrooms: int
    has_pool: bool
    has_bbq: bool
    allows_pets: bool
    images: List[str] = []
    amenities: List[str] = []

    # Comparações de preço
    platforms: List[PlatformComparisonItem]
    lowest_daily_rate: float
    lowest_total_price: float
    highest_total_price: float
    max_savings: float
    best_platform: str


class SearchResponse(BaseModel):
    city: str
    state: Optional[str] = None
    nights: int
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    guests: int
    total_results: int
    page: int
    page_size: int
    total_pages: int
    results: List[SearchPropertyItem]
    cached: bool = False
