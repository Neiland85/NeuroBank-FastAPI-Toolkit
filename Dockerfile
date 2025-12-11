# ============================================
# STAGE 1 — BUILDER
# Compilación limpia, reproducible, sin root
# ============================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema mínimas y suficientes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos dependencias del proyecto
COPY requirements.txt .

# Usamos wheels para maximizar reproducibilidad
RUN pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


# ============================================
# STAGE 2 — RUNTIME ULTRALIGHT
# Cero herramientas innecesarias, zero trust
# ============================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

WORKDIR /app

# Crear usuario no-root y seguro
RUN useradd -m appuser

# Copiar wheels + instalar sin red
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copiamos solo el código (sin tests, sin dev)
COPY app ./app

# Ajustar permisos
RUN chown -R appuser:appuser /app
USER appuser

# ============================================
# EJECUCIÓN — UVICORN KARPATHIAN MODE
# ============================================
EXPOSE 8000

# Workers definidos por CPU (Karpathy-approved)
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]
