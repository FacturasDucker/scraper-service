import io
import logging
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import pytesseract
import tempfile
import os

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Clase para procesar archivos PDF y extraer texto"""
    def __init__(self, ocr_dpi=300, tessdata_lang="spa", tessdata_path="", temp_dir="/tmp"):
        self.ocr_dpi = ocr_dpi
        self.tessdata_lang = tessdata_lang
        self.tessdata_path = tessdata_path
        self.temp_dir = temp_dir
        
        # Configurar Tesseract
        if self.tessdata_path:
            import os
            os.environ["TESSDATA_PREFIX"] = self.tessdata_path
            
    def extract_text(self, pdf_content):
        """
        Extrae todo el texto de un archivo PDF usando múltiples métodos
        
        Args:
            pdf_content (bytes): Contenido del archivo PDF en formato de bytes
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            # Método 1: Usar PyMuPDF para extraer texto directamente
            text_from_pdf = self._extract_text_with_pymupdf(pdf_content)
            
            # Si PyMuPDF extrajo suficiente texto, usarlo
            if text_from_pdf and len(text_from_pdf) > 100:
                logger.info(f"Texto extraído con PyMuPDF: {len(text_from_pdf)} caracteres")
                return text_from_pdf
            
            # Método 2: Renderizar páginas como imágenes y usar OCR
            text_from_ocr = self._extract_text_with_ocr(pdf_content)
            
            # Si el OCR extrajo texto, usarlo
            if text_from_ocr:
                logger.info(f"Texto extraído con OCR: {len(text_from_ocr)} caracteres")
                return text_from_ocr
            
            # Si PyMuPDF extrajo algo, aunque sea poco, es mejor que nada
            if text_from_pdf:
                return text_from_pdf
            
            logger.warning("No se pudo extraer texto del PDF")
            return ""
            
        except Exception as e:
            logger.error(f"Error al extraer texto del PDF: {str(e)}")
            raise
    
    def _extract_text_with_pymupdf(self, pdf_content):
        """
        Extrae texto usando PyMuPDF directamente
        
        Args:
            pdf_content (bytes): Contenido del PDF
            
        Returns:
            str: Texto extraído
        """
        try:
            # Crear documento PDF desde bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            
            # Extraer texto de cada página
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text += page.get_text("text")
            
            return text
            
        except Exception as e:
            logger.warning(f"Error al extraer texto con PyMuPDF: {str(e)}")
            return ""
    
    def _extract_text_with_ocr(self, pdf_content):
        """
        Extrae texto usando OCR después de renderizar páginas como imágenes
        
        Args:
            pdf_content (bytes): Contenido del PDF
            
        Returns:
            str: Texto extraído con OCR
        """
        try:
            # Crear documento PDF desde bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            all_text = ""
            
            # Procesar cada página
            for page_num in range(len(pdf_document)):
                try:
                    page = pdf_document[page_num]
                    
                    # Renderizar página como imagen con alta resolución para OCR
                    # 300 DPI es bueno para OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                    
                    # Convertir a imagen PIL
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Aplicar mejoras para OCR
                    img = self._enhance_image_for_ocr(img)
                    
                    # Usar Tesseract para OCR (con configuración para español)
                    text = pytesseract.image_to_string(img, lang='spa')
                    all_text += text + "\n\n"
                    
                except Exception as e:
                    logger.warning(f"Error al procesar página {page_num} para OCR: {str(e)}")
                    continue
            
            return all_text
            
        except Exception as e:
            logger.warning(f"Error al extraer texto con OCR: {str(e)}")
            return ""
    
    def _enhance_image_for_ocr(self, image):
        """
        Mejora la imagen para OCR
        
        Args:
            image (PIL.Image): Imagen a mejorar
            
        Returns:
            PIL.Image: Imagen mejorada
        """
        try:
            # Convertir a escala de grises para mejor OCR
            img_gray = image.convert('L')
            
            # Aplicar un poco de contraste automático para mejorar la legibilidad
            # Este método simple usa PIL para autoajustar el contraste
            from PIL import ImageOps
            img_contrast = ImageOps.autocontrast(img_gray, cutoff=0.5)
            
            return img_contrast
            
        except Exception as e:
            logger.warning(f"Error al mejorar imagen para OCR: {str(e)}")
            return image
    
    def extract_pages_as_images(self, pdf_content):
        """
        Extrae páginas del PDF como imágenes
        Útil para depuración o para mostrar vista previa
        
        Args:
            pdf_content (bytes): Contenido del PDF
            
        Returns:
            list: Lista de imágenes en formato bytes
        """
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            images = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                
                img_bytes = io.BytesIO()
                pix.save(img_bytes, format="png")
                img_bytes.seek(0)
                
                images.append(img_bytes.getvalue())
            
            return images
            
        except Exception as e:
            logger.error(f"Error al extraer páginas como imágenes: {str(e)}")
            return []