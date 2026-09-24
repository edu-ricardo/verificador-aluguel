import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Verificador Aluguel Casas API...")

    async def init_db_with_retries():
        for attempt in range(1, 11):
            try:
                await init_db()
                logger.info("Banco de dados inicializado com sucesso.")
                return
            except Exception as e:
                logger.warning(f"Tentativa {attempt}/10: Banco de dados ainda não pronto ({e}). Aguardando 2s...")
                await asyncio.sleep(2)
        logger.error(
            "Não foi possível conectar ao banco de dados após 10 tentativas. Operando em modo de busca direto."
        )

    db_task = asyncio.create_task(init_db_with_retries())
    yield
    if not db_task.done():
        db_task.cancel()
    logger.info("Encerrando aplicação.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de verificação de integridade para Docker/Portainer."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Bem-vindo ao {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_STR,
    }
