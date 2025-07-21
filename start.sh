#!/bin/bash

# NeuroBank FastAPI Railway Startup Script
echo "🏦 Iniciando NeuroBank FastAPI Toolkit..."

# Configurar variables de entorno para Railway
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Validar variables críticas
if [ -z "$API_KEY" ]; then
    echo "❌ ERROR: API_KEY environment variable is required"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY environment variable is required"
    exit 1
fi

# Mostrar configuración
echo "🌐 PORT: $PORT"
echo "� ENVIRONMENT: $ENVIRONMENT"
echo "✅ API_KEY configured"
echo "✅ SECRET_KEY configured"

# Health check pre-start
echo "🏥 Pre-start health check..."
python -c "
try:
    from app.main import app
    print('✅ App import successful')
except Exception as e:
    print(f'❌ App import failed: {e}')
    exit(1)
"

# Start server with Railway-optimized configuration
echo "🚀 Starting server..."
exec python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --timeout-keep-alive 120 \
    --access-log
