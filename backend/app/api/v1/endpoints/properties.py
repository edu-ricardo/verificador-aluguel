from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.property import Property
from app.schemas.property import PropertyDetail

router = APIRouter()


@router.get("", response_model=List[PropertyDetail], summary="Lista propriedades salvas no banco de dados")
async def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Property).offset(skip).limit(limit)
    result = await db.execute(stmt)
    properties = result.scalars().all()
    return properties


@router.get("/{property_id}", response_model=PropertyDetail, summary="Obtém detalhes de uma propriedade específica")
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Property).where(Property.id == property_id)
    result = await db.execute(stmt)
    property_obj = result.scalar_one_or_none()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    return property_obj
