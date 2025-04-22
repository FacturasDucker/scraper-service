from pydantic import BaseModel, Field
from typing import Optional

class ProcessDocumentRequest(BaseModel):
    """Modelo para solicitud de procesamiento de documento"""
    user_id: Optional[str] = Field(
        default=None, 
        description="ID del usuario que solicita el procesamiento"
    )
    document_type: str = Field(
        default="CSF", 
        description="Tipo de documento a procesar"
    )