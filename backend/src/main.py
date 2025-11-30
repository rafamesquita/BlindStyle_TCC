import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.core.config.settings import settings
from src.core.db import init_db, close_db
from src.core.di.container import Container
from src.controllers import (
    description_controller,
    item_controller,
    suggestion_controller,
    user_controller,
)

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando BlindStyle API...")
    init_db()
    yield
    logger.info("Encerrando BlindStyle API...")
    close_db()

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Dados inválidos"}
    )

# ====================================Application Factory====================================
def create_app() -> FastAPI:
    _app = FastAPI(
        title="BlindStyle API",
        description="Backend API para o projeto BlindStyle",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        debug=settings.DEBUG
    )

# ====================================Middlewares====================================
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.get_cors_methods(),
        allow_headers=settings.get_cors_headers(),
        expose_headers=["X-Process-Time"]
    )

# ====================================Exception Handlers====================================
    _app.add_exception_handler(RequestValidationError, validation_exception_handler)


# ====================================Routers====================================

    API_V1_PREFIX = "/api/v1"

    _app.include_router(user_controller.router, prefix=API_V1_PREFIX)
    _app.include_router(item_controller.router, prefix=API_V1_PREFIX)
    _app.include_router(description_controller.router, prefix=API_V1_PREFIX)
    _app.include_router(suggestion_controller.router, prefix=API_V1_PREFIX)

# ====================================Dependency Injection====================================
    Container().wire(
        modules=[
            "src.controllers.description_controller",
            "src.controllers.item_controller",
            "src.controllers.suggestion_controller",
            "src.controllers.user_controller"
        ]
    )

    return _app

app = create_app()

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "BlindStyle API está funcionando!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }