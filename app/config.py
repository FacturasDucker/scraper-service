import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Configuraciones de la aplicación utilizando variables de entorno"""
    
    # Información de la aplicación
    APP_NAME: str = "CSF Scraper Service"
    APP_DESCRIPTION: str = "Servicio para extraer datos fiscales de Constancias de Situación Fiscal"
    APP_VERSION: str = "1.0.0"
    
    # Entorno de ejecución
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Configuración del servidor
    PORT: int = Field(default=8000, env="PORT")
    API_PREFIX: str = Field(default="", env="API_PREFIX")
    
    # Límites y timeouts
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10 MB
    PROCESS_TIMEOUT: int = Field(default=60, env="PROCESS_TIMEOUT")  # 60 segundos
    
    # Configuración de OCR
    TESSERACT_PATH: str = Field(default="", env="TESSERACT_PATH")
    TESSERACT_LANG: str = Field(default="spa", env="TESSERACT_LANG")
    OCR_DPI: int = Field(default=300, env="OCR_DPI")
    
    # Métricas y monitoreo
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=8001, env="METRICS_PORT")
    
    # Paths para archivos temporales
    TEMP_DIR: str = Field(default="/tmp", env="TEMP_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Cargar configuraciones
settings = Settings()

# Configurar Tesseract
if settings.TESSERACT_PATH and os.path.exists(settings.TESSERACT_PATH):
    os.environ["TESSDATA_PREFIX"] = settings.TESSERACT_PATH