#!/bin/bash

# 🚀 NeuroBank FastAPI Production Deployment Script
# Production-ready deployment for banking recruiters demo

set -e  # Exit on any error

echo "🏦 NeuroBank FastAPI - Production Deployment"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project directory validated"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "🐍 Python version: $PYTHON_VERSION"

# Install dependencies
echo ""
echo "📦 Installing production dependencies..."
pip install -r requirements.txt --quiet

# Validate the application can start
echo ""
echo "🔍 Validating application..."
python3 -c "from app.main import app; print('✅ Application validated successfully')"

# Create production environment file
echo ""
echo "⚙️  Creating production environment..."
cat > .env.prod << EOF
# 🏦 NeuroBank FastAPI - Production Environment
APP_NAME=NeuroBank FastAPI Toolkit
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false

# Security
API_KEY_HEADER=X-API-Key
CORS_ORIGINS=["https://yourdomain.com"]

# Database (Configure as needed)
DATABASE_URL=sqlite:///./neurobank_prod.db

# Monitoring
ENABLE_METRICS=true
HEALTH_CHECK_ENDPOINT=/health
EOF

echo "✅ Production environment created"

# Create systemd service file (optional)
echo ""
echo "🔧 Creating systemd service file..."
cat > neurobank-fastapi.service << EOF
[Unit]
Description=NeuroBank FastAPI Production Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/neurobank-fastapi
Environment="PATH=/opt/neurobank-fastapi/venv/bin"
ExecStart=/opt/neurobank-fastapi/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service file created"

# Create production startup script
echo ""
echo "🚀 Creating production startup script..."
cat > start_production.sh << 'EOF'
#!/bin/bash
echo "🏦 Starting NeuroBank FastAPI in Production Mode..."

# Load production environment
export APP_ENV=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start with gunicorn for production
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --preload
EOF

chmod +x start_production.sh
echo "✅ Production startup script created and made executable"

# Create Docker configuration
echo ""
echo "🐳 Creating Docker configuration..."
cat > Dockerfile.prod << 'EOF'
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY app/ ./app/
COPY start_production.sh .
RUN chmod +x start_production.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start application
CMD ["./start_production.sh"]
EOF

echo "✅ Docker configuration created"

# Create docker-compose for production
echo ""
echo "📄 Creating docker-compose for production..."
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  neurobank-api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - neurobank-api
    restart: unless-stopped
EOF

echo "✅ Docker Compose configuration created"

# Create nginx configuration
echo ""
echo "🌐 Creating nginx configuration..."
mkdir -p nginx
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream neurobank_api {
        server neurobank-api:8000;
    }

    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Proxy to FastAPI
        location / {
            proxy_pass http://neurobank_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300;
            proxy_connect_timeout 300;
            proxy_send_timeout 300;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://neurobank_api/health;
            access_log off;
        }

        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

echo "✅ Nginx configuration created"

# Final production checklist
echo ""
echo "🎯 PRODUCTION DEPLOYMENT COMPLETE!"
echo "=================================="
echo ""
echo "📋 Deployment Summary:"
echo "   ✅ Dependencies installed"
echo "   ✅ Application validated"
echo "   ✅ Production environment configured"
echo "   ✅ Systemd service created"
echo "   ✅ Production startup script ready"
echo "   ✅ Docker configuration created"
echo "   ✅ Nginx reverse proxy configured"
echo ""
echo "🚀 Quick Start Options:"
echo ""
echo "1️⃣  Direct Python (Development/Testing):"
echo "   ./start_production.sh"
echo ""
echo "2️⃣  Docker (Recommended for Production):"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "3️⃣  Systemd Service (Linux Production):"
echo "   sudo cp neurobank-fastapi.service /etc/systemd/system/"
echo "   sudo systemctl enable neurobank-fastapi"
echo "   sudo systemctl start neurobank-fastapi"
echo ""
echo "🌐 Access Points:"
echo "   📊 Admin Dashboard: http://localhost:8000/backoffice/"
echo "   💳 Transactions: http://localhost:8000/backoffice/admin/transactions"
echo "   📖 API Documentation: http://localhost:8000/docs"
echo "   🏥 Health Check: http://localhost:8000/health"
echo ""
echo "🎉 Ready for banking recruiters demo!"
echo "🔒 Production-grade security and monitoring included"
echo ""
