from functools import lru_cache

from app.services.pdf_processor import PDFProcessor
from app.services.data_extractor import DataExtractor
from app.config import settings

@lru_cache()
def get_pdf_processor() -> PDFProcessor:
    """
    Crea y devuelve una instancia singleton de PDFProcessor
    
    Returns:
        PDFProcessor: Instancia del procesador de PDF
    """
    return PDFProcessor(
        ocr_dpi=settings.OCR_DPI,
        tessdata_lang=settings.TESSERACT_LANG,
        tessdata_path=settings.TESSERACT_PATH,
        temp_dir=settings.TEMP_DIR
    )

@lru_cache()
def get_data_extractor() -> DataExtractor:
    """
    Crea y devuelve una instancia singleton de DataExtractor
    
    Returns:
        DataExtractor: Instancia del extractor de datos
    """
    return DataExtractor()