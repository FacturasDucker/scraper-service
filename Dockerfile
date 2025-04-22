# Dockerfile optimizado para el Scraper Service
FROM python:3.11-slim as base

# Establecer variables de entorno
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado
RUN groupadd -r scraper && useradd -r -g scraper scraper

# Crear directorios de trabajo
WORKDIR /app
RUN mkdir -p /app/temp && chown -R scraper:scraper /app

# Etapa de instalación de dependencias
FROM base as builder

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Etapa final
FROM base

# Copiar dependencias instaladas
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY --chown=scraper:scraper . .

# Exponer puerto
EXPOSE 8000
EXPOSE 8001

# Cambiar al usuario no privilegiado
USER scraper

# Variables de entorno para producción
ENV ENVIRONMENT=production \
    PORT=8000 \
    METRICS_PORT=8001 \
    TESSERACT_LANG=spa \
    OCR_DPI=300 \
    TEMP_DIR=/app/temp \
    API_PREFIX=""

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Metadata
LABEL maintainer="Facturación Electrónica" \
      version="1.0.0" \
      description="Servicio de extracción de datos fiscales de CSF"