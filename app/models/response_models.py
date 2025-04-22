from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CSFData(BaseModel):
    """Datos extraídos de la Constancia de Situación Fiscal"""
    rfc: str = Field(
        default="",
        description="RFC extraído del documento"
    )
    nombre: str = Field(
        default="",
        description="Nombre o Razón Social extraído del documento"
    )
    regimen_fiscal: str = Field(
        default="",
        description="Código de Régimen Fiscal extraído del documento (3 dígitos)"
    )
    codigo_postal: str = Field(
        default="",
        description="Código Postal extraído del documento"
    )
    domicilio: str = Field(
        default="",
        description="Domicilio fiscal extraído del documento"
    )
    completo: bool = Field(
        default=False,
        description="Indica si se extrajeron todos los datos obligatorios"
    )
    mensaje: str = Field(
        default="",
        description="Mensaje informativo sobre la extracción"
    )

class ProcessingResponse(BaseModel):
    """Respuesta para el procesamiento de documentos"""
    success: bool = Field(
        description="Indica si el procesamiento fue exitoso"
    )
    message: str = Field(
        description="Mensaje descriptivo del resultado"
    )
    process_id: str = Field(
        description="Identificador único del proceso"
    )
    data: Optional[CSFData] = Field(
        default=None,
        description="Datos extraídos del documento"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Fecha y hora del procesamiento"
    )
    processing_time: Optional[float] = Field(
        default=None,
        description="Tiempo de procesamiento en segundos"
    )