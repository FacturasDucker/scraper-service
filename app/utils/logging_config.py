import logging
import sys
import json
from datetime import datetime
from app.config import settings

class JSONFormatter(logging.Formatter):
    """
    Formateador personalizado para logs en formato JSON, útil para integración con
    sistemas como ELK, Loki, etc.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
        
        # Agregar excepción si existe
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Agregar campos extra si existen
        if hasattr(record, "props"):
            log_record.update(record.props)
        
        return json.dumps(log_record)

def setup_logging():
    """
    Configura el sistema de logging para la aplicación
    """
    # Configurar el nivel de logging según el entorno
    root_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Obtener el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)
    
    # Limpiar handlers existentes
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Crear handler para salida a consola
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Aplicar formato según el entorno
    if settings.ENVIRONMENT == "production":
        # Formato JSON para producción (mejor para procesamiento automatizado)
        formatter = JSONFormatter()
    else:
        # Formato legible para desarrollo
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Establecer niveles específicos para bibliotecas ruidosas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    
    # Log de inicio de configuración
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configurado para entorno: {settings.ENVIRONMENT}")