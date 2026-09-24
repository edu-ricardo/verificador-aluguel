from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search import SearchQuery, SearchResponse
from app.services.search_service import search_service

router = APIRouter()


@router.get("", response_model=SearchResponse, summary="Busca e compara aluguéis de temporada")
async def search_rentals(
    city: str = Query(..., description="Cidade (ex: Atibaia, Ibiúna, Ubatuba, Brotas)"),
    state: Optional[str] = Query("SP", max_length=2, description="UF (ex: SP, MG, RJ)"),
    property_type: Optional[str] = Query("todos", description="chacara, sitio, casa ou todos"),
    check_in: Optional[date] = Query(None, description="Data de início (YYYY-MM-DD)"),
    check_out: Optional[date] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    guests: int = Query(1, ge=1, le=100, description="Quantidade de hóspedes"),
    min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo da diária"),
    max_price: Optional[float] = Query(None, ge=0, description="Preço máximo da diária"),
    has_pool: Optional[bool] = Query(None, description="Apenas com piscina"),
    allows_pets: Optional[bool] = Query(None, description="Aceita pets"),
    platforms: Optional[List[str]] = Query(None, description="temporadalivre, olx"),
    sort_by: Optional[str] = Query("price_asc", description="price_asc, price_desc, savings_desc, guests_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = SearchQuery(
        city=city,
        state=state,
        property_type=property_type,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        min_price=min_price,
        max_price=max_price,
        has_pool=has_pool,
        allows_pets=allows_pets,
        platforms=platforms,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return await search_service.search(query, db=db)
