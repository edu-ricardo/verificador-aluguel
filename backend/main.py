import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    allow_origins=["*"],
    allow_origin_regex=".*",
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


# Monta o frontend estático compilado diretamente no FastAPI
STATIC_DIR = Path("/app/static")
if not STATIC_DIR.exists():
    STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = STATIC_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Bem-vindo ao {settings.PROJECT_NAME}",
            "docs": "/docs",
            "health": "/health",
            "api": settings.API_V1_STR,
        }

