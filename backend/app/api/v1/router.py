from fastapi import APIRouter

from app.api.v1.endpoints import properties, search

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["Busca e Comparação"])
api_router.include_router(properties.router, prefix="/properties", tags=["Propriedades"])
