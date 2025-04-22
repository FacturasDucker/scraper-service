from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router as api_router
from app.utils.logging_config import setup_logging
from app.utils.error_handlers import add_exception_handlers
from app.config import settings

# Configurar logging
logger = logging.getLogger(__name__)
setup_logging()

# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Añadir middleware CORS (para desarrollo local)
if settings.ENVIRONMENT != "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Registrar rutas API
app.include_router(api_router, prefix=settings.API_PREFIX)

# Añadir manejadores de excepciones personalizados
add_exception_handlers(app)

# Health check endpoint (útil para Kubernetes y el API Gateway)
@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint para verificar la salud del servicio"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Evento de inicio de la aplicación
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.ENVIRONMENT} mode")

# Evento de cierre de la aplicación
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.ENVIRONMENT != "production")