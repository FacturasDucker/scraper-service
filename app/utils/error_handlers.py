import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador personalizado para errores de validación de FastAPI
    """
    error_detail = []
    for error in exc.errors():
        error_detail.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Error de validación: {error_detail}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Error de validación en los datos enviados",
            "errors": error_detail
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Manejador personalizado para excepciones HTTP
    """
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Manejador para excepciones no controladas
    """
    logger.error(f"Error no controlado: {str(exc)}", exc_info=True)
    
    # En producción no mostramos el stacktrace al usuario
    error_detail = None
    if logger.level <= logging.DEBUG:
        error_detail = traceback.format_exception(type(exc), exc, exc.__traceback__)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "detail": str(exc),
            "trace": error_detail
        }
    )

def add_exception_handlers(app: FastAPI):
    """
    Añade los manejadores de excepciones a la aplicación FastAPI
    
    Args:
        app: Aplicación FastAPI
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)