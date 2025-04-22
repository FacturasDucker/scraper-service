import logging
import re
from app.models.response_models import CSFData

logger = logging.getLogger(__name__)

class DataExtractor:
    """Clase para extraer datos fiscales a partir del texto del PDF CSF"""
    
    def extract_from_text(self, text):
        """
        Extrae datos fiscales del texto extraído de un PDF de CSF
        
        Args:
            text (str): Texto extraído del PDF
            
        Returns:
            CSFData: Objeto con los datos extraídos
        """
        try:
            logger.info("Extrayendo datos del texto CSF")
            
            # Extraer datos usando expresiones regulares y patrones
            rfc = self._extract_rfc(text)
            nombre = self._extract_nombre(text)
            regimen_fiscal = self._extract_regimen_fiscal(text)
            codigo_postal = self._extract_codigo_postal(text)
            domicilio = self._extract_domicilio(text)
            
            # Calcular si tenemos los datos mínimos completos
            completo = bool(rfc and nombre and regimen_fiscal and codigo_postal)
            
            # Limpiar datos extraídos
            if rfc:
                rfc = self._clean_text(rfc)
            if nombre:
                nombre = self._clean_text(nombre)
            if regimen_fiscal:
                regimen_fiscal = self._clean_text(regimen_fiscal)
                # Si el régimen fiscal contiene un código de 3 dígitos, extraerlo
                codigo_match = re.search(r'(\d{3})', regimen_fiscal)
                if codigo_match:
                    regimen_fiscal = codigo_match.group(1)
            if codigo_postal:
                codigo_postal = self._clean_text(codigo_postal)
                # Asegurar que sea solo 5 dígitos
                codigo_postal = re.sub(r'[^\d]', '', codigo_postal)[:5]
            
            return CSFData(
                rfc=rfc or '',
                nombre=nombre or '',
                regimen_fiscal=regimen_fiscal or '',
                codigo_postal=codigo_postal or '',
                domicilio=domicilio or '',
                completo=completo,
                mensaje="Datos extraídos del PDF de la Constancia de Situación Fiscal"
            )
            
        except Exception as e:
            logger.error(f"Error al extraer datos de texto: {str(e)}")
            return CSFData(
                rfc='',
                nombre='',
                regimen_fiscal='',
                codigo_postal='',
                completo=False,
                mensaje=f"Error al procesar el documento: {str(e)}"
            )
    
    def _extract_rfc(self, text):
        """
        Extrae el RFC del texto usando múltiples patrones
        
        Args:
            text (str): Texto completo
            
        Returns:
            str: RFC extraído o None si no se encuentra
        """
        # Patrones comunes para RFC en la CSF
        patterns = [
            r'R\.?F\.?C\.?\s*:?\s*([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})',
            r'REGISTRO\s+FEDERAL\s+DE\s+CONTRIBUYENTES\s*:?\s*([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})',
            r'CÉDULA\s+DE\s+IDENTIFICACIÓN\s+FISCAL\s*:?\s*([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.info(f"RFC encontrado con patrón: {pattern}")
                return match.group(1)
        
        # Búsqueda genérica de formato RFC
        general_rfc = re.search(r'(?<!\w)([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})(?!\w)', text)
        if general_rfc:
            logger.info("RFC encontrado con búsqueda general")
            return general_rfc.group(1)
        
        logger.warning("No se pudo encontrar el RFC en el texto")
        return None
    
    def _extract_nombre(self, text):
        """
        Extrae el nombre o razón social del texto
        
        Args:
            text (str): Texto completo
            
        Returns:
            str: Nombre extraído o None si no se encuentra
        """
        # Patrones para nombre o razón social
        patterns = [
            r'NOMBRE(?:\s*,\s*DENOMINACIÓN\s*O\s*RAZÓN\s*SOCIAL)?\s*:?\s*([^\n]{5,150})',
            r'DENOMINACIÓN/RAZÓN\s*SOCIAL\s*:?\s*([^\n]{5,150})',
            r'CONTRIBUYENTE\s*:?\s*([^\n]{5,150})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.info(f"Nombre encontrado con patrón: {pattern}")
                return match.group(1)
        
        logger.warning("No se pudo encontrar el nombre en el texto")
        return None
    
    def _extract_regimen_fiscal(self, text):
        """
        Extrae el régimen fiscal del texto
        
        Args:
            text (str): Texto completo
            
        Returns:
            str: Régimen fiscal extraído o None si no se encuentra
        """
        # Patrones para régimen fiscal
        patterns = [
            r'RÉGIMEN\s*FISCAL\s*:?\s*(\d{3}[^\n]{0,100})',
            r'RÉGIMEN\s*:?\s*(\d{3}[^\n]{0,100})',
            r'RÉGIMEN\s*([^\n]*\d{3}[^\n]{0,100})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                logger.info(f"Régimen fiscal encontrado con patrón: {pattern}")
                return match.group(1)
        
        # Buscar sección de régimen
        regime_section = re.search(r'REGÍMENES[\s\S]*?((?:\d{3}[^\n]*\n){1,5})', text, re.IGNORECASE)
        if regime_section:
            # Extraer solo el código numérico
            codigo = re.search(r'(\d{3})', regime_section.group(1))
            if codigo:
                logger.info("Régimen fiscal encontrado en sección de regímenes")
                return codigo.group(1)
        
        logger.warning("No se pudo encontrar el régimen fiscal en el texto")
        return None
    
    def _extract_codigo_postal(self, text):
        """
        Extrae el código postal del texto
        
        Args:
            text (str): Texto completo
            
        Returns:
            str: Código postal extraído o None si no se encuentra
        """
        # Patrones para código postal
        patterns = [
            r'C\.?P\.?\s*:?\s*(\d{5})',
            r'CÓDIGO\s*POSTAL\s*:?\s*(\d{5})',
            r'DOMICILIO\s*FISCAL[\s\S]*?C\.?P\.?\s*:?\s*(\d{5})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.info(f"Código postal encontrado con patrón: {pattern}")
                return match.group(1)
        
        # Buscar formato de código postal en general
        cp_match = re.search(r'(?<!\d)(\d{5})(?!\d)', text)
        if cp_match:
            logger.info("Código postal encontrado con búsqueda general")
            return cp_match.group(1)
        
        logger.warning("No se pudo encontrar el código postal en el texto")
        return None
    
    def _extract_domicilio(self, text):
        """
        Extrae el domicilio fiscal del texto
        
        Args:
            text (str): Texto completo
            
        Returns:
            str: Domicilio extraído o None si no se encuentra
        """
        # Patrones para domicilio fiscal
        patterns = [
            r'DOMICILIO\s*FISCAL\s*:?\s*([^\n]{10,200})',
            r'UBICACIÓN\s*:?\s*([^\n]{10,200})',
            r'DOMICILIO\s*:?\s*([^\n]{10,200})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.info(f"Domicilio encontrado con patrón: {pattern}")
                return match.group(1)
        
        # Buscar sección de domicilio
        domicilio_section = re.search(r'DOMICILIO([\s\S]{10,300})(?:ACTIVIDADES|OBLIGACIONES|REGIMEN)', text, re.IGNORECASE)
        if domicilio_section:
            # Limpiar y devolver
            domicilio = domicilio_section.group(1).strip()
            logger.info("Domicilio encontrado en sección de domicilio")
            return domicilio
        
        logger.warning("No se pudo encontrar el domicilio en el texto")
        return None
    
    def _clean_text(self, text):
        """
        Limpia el texto extraído eliminando caracteres no deseados
        
        Args:
            text (str): Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        if not text:
            return ""
        
        # Eliminar espacios múltiples y caracteres extraños
        text = re.sub(r'\s+', ' ', text)
        # Eliminar caracteres que no son imprimibles
        text = re.sub(r'[^\x20-\x7E\xA0-\xFF]', '', text)
        # Eliminar etiquetas como "RFC:" si quedaron en el texto
        text = re.sub(r'RFC\s*:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'NOMBRE\s*:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'C\.?P\.?\s*:', '', text, flags=re.IGNORECASE)
        
        return text.strip()