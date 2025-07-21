#!/bin/bash

# NeuroBank FastAPI Railway Startup Script
echo "🏦 Iniciando NeuroBank FastAPI Toolkit..."

# Configurar variables de entorno para Railway
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1
export ENVIRONMENT=production

# Configurar API Key si no existe (Railway auto-generate)
if [ -z "$API_KEY" ]; then
    export API_KEY="${RAILWAY_PRIVATE_DOMAIN}_secure_production_key"
    echo "🔐 Auto-configured API_KEY for Railway deployment"
fi

# Mostrar configuración
echo "🌐 PORT: $PORT"
echo "🚂 RAILWAY_PROJECT_NAME: $RAILWAY_PROJECT_NAME"
echo "🔗 RAILWAY_PRIVATE_DOMAIN: $RAILWAY_PRIVATE_DOMAIN"

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

# Start server with optimized configuration
echo "🚀 Starting server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --timeout-keep-alive 120 \
    --access-log \
    --use-colors
