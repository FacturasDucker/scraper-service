import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Variables para almacenar métricas
# En producción, esto se reemplazaría por una integración real con Prometheus o similar
counters = {}
histograms = {}
gauges = {}

def increment_counter(name: str, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Incrementa un contador
    
    Args:
        name: Nombre del contador
        labels: Diccionario de etiquetas
    """
    labels_key = str(labels) if labels else "default"
    if name not in counters:
        counters[name] = {}
    
    if labels_key not in counters[name]:
        counters[name][labels_key] = 0
    
    counters[name][labels_key] += 1
    
    # Log para debugging
    logger.debug(f"Counter {name}{labels} = {counters[name][labels_key]}")

def observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Registra una observación en un histograma
    
    Args:
        name: Nombre del histograma
        value: Valor a registrar
        labels: Diccionario de etiquetas
    """
    labels_key = str(labels) if labels else "default"
    if name not in histograms:
        histograms[name] = {}
    
    if labels_key not in histograms[name]:
        histograms[name][labels_key] = []
    
    histograms[name][labels_key].append(value)
    
    # Log para debugging
    logger.debug(f"Histogram {name}{labels} = {value}")

def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Establece el valor de un gauge
    
    Args:
        name: Nombre del gauge
        value: Valor a establecer
        labels: Diccionario de etiquetas
    """
    labels_key = str(labels) if labels else "default"
    if name not in gauges:
        gauges[name] = {}
    
    gauges[name][labels_key] = value
    
    # Log para debugging
    logger.debug(f"Gauge {name}{labels} = {value}")

def get_metrics() -> Dict:
    """
    Obtiene todas las métricas recolectadas
    
    Returns:
        Diccionario con todas las métricas
    """
    return {
        "counters": counters,
        "histograms": histograms,
        "gauges": gauges
    }

def reset_metrics() -> None:
    """
    Reinicia todas las métricas
    """
    global counters, histograms, gauges
    counters = {}
    histograms = {}
    gauges = {}
    logger.debug("Metrics reset")