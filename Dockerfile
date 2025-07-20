# NeuroBank FastAPI Toolkit - Production Dockerfile
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY ./app ./app
COPY lambda_handler.py .

# Crear usuario no-root para seguridad y configurar permisos
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
  chown -R appuser:appuser /app
USER appuser

# Exponer el puerto
EXPOSE 8000

# Configurar variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando por defecto para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]