import time
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid

from app.services.pdf_processor import PDFProcessor
from app.services.data_extractor import DataExtractor
from app.utils.metrics import increment_counter, observe_histogram
from app.models.request_models import ProcessDocumentRequest
from app.models.response_models import ProcessingResponse
from app.api.dependencies import get_pdf_processor, get_data_extractor

# Configuración de logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(tags=["scraper"])

@router.post(
    "/extract-csf",
    response_model=ProcessingResponse,
    summary="Extraer datos de CSF",
    description="Extrae datos fiscales de un PDF de Constancia de Situación Fiscal"
)
async def extract_csf_data(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    pdf_processor: PDFProcessor = Depends(get_pdf_processor),
    data_extractor: DataExtractor = Depends(get_data_extractor)
):
    """
    Extrae datos fiscales directamente de un PDF de Constancia de Situación Fiscal
    
    - **file**: Archivo PDF de la Constancia de Situación Fiscal
    - **user_id**: ID del usuario (opcional)
    """
    # Medir tiempo de proceso
    start_time = time.time()
    
    # Generar ID para el procesamiento
    process_id = str(uuid.uuid4())
    user_id = user_id or "anonymous"
    
    # Incrementar contador de solicitudes
    increment_counter("scraper_requests_total", {"user_id": user_id})
    
    # Validar tipo de archivo
    content_type = file.content_type
    if content_type != "application/pdf":
        logger.warning(f"Tipo de archivo no soportado: {content_type}")
        increment_counter("scraper_errors_total", {"reason": "invalid_file_type"})
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no soportado: {content_type}. Solo se admiten archivos PDF."
        )
    
    try:
        # Leer contenido del archivo
        contents = await file.read()
        file_size = len(contents)
        logger.info(f"Archivo recibido: {file.filename}, tamaño: {file_size} bytes, ID proceso: {process_id}")
        
        # Extraer texto del PDF
        extracted_text = pdf_processor.extract_text(contents)
        
        if not extracted_text:
            logger.warning(f"No se pudo extraer texto del PDF para proceso: {process_id}")
            increment_counter("scraper_errors_total", {"reason": "no_text_extracted"})
            return ProcessingResponse(
                success=False,
                message="No se pudo extraer texto del PDF. Es posible que el archivo esté protegido o sea una imagen escaneada.",
                process_id=process_id
            )
        
        # Extraer datos fiscales del texto
        csf_data = data_extractor.extract_from_text(extracted_text)
        
        # Registrar métricas de confianza
        observe_histogram("scraper_confidence", csf_data.completo, {"field": "overall"})
        
        # Verificar si se extrajeron datos mínimos (RFC, nombre)
        if not csf_data.rfc and not csf_data.nombre:
            logger.warning(f"No se identificaron datos fiscales para proceso: {process_id}")
            increment_counter("scraper_errors_total", {"reason": "no_fiscal_data"})
            return ProcessingResponse(
                success=False,
                message="No se pudieron identificar datos fiscales en el documento. Verifique que sea una Constancia de Situación Fiscal válida.",
                process_id=process_id
            )
        
        # Registrar éxito
        process_time = time.time() - start_time
        observe_histogram("scraper_process_time", process_time)
        increment_counter("scraper_success_total")
        
        logger.info(f"Datos extraídos exitosamente para proceso: {process_id}, tiempo: {process_time:.2f}s")
        
        # Devolver respuesta con datos extraídos para confirmación por el usuario
        return ProcessingResponse(
            success=True,
            message="Datos extraídos correctamente. Por favor verifique y corrija si es necesario.",
            process_id=process_id,
            data=csf_data,
            processing_time=process_time
        )
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error al procesar documento: {str(e)}", exc_info=True)
        increment_counter("scraper_errors_total", {"reason": "processing_error"})
        
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar el documento: {str(e)}"
        )