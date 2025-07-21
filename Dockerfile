# NeuroBank FastAPI Toolkit - Production Dockerfile optimized for Railway
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema optimizado para Railway
RUN apt-get update && apt-get install -y \
  gcc \
  curl \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean

# Copiar archivos de dependencias primero para mejor cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python con optimizaciones
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
  pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY ./app ./app
COPY lambda_handler.py .
COPY start.sh .

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Crear usuario no-root para seguridad y configurar permisos
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
  chown -R appuser:appuser /app
USER appuser

# Exponer el puerto dinámico de Railway
EXPOSE $PORT

# Configurar variables de entorno optimizadas para Railway
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV ENVIRONMENT=production
ENV WORKERS=1

# Health check específico para Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Comando optimizado para Railway con single worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop", "--timeout-keep-alive", "120", "--access-log"]