# 🏦 NeuroBank FastAPI - Acceso a Servicios

## 🌐 **Producción (Railway)**
- **API Principal**: https://neurobank-fastapi-toolkit-production.up.railway.app/
- **Admin Dashboard**: https://neurobank-fastapi-toolkit-production.up.railway.app/backoffice/
- **API Documentation**: https://neurobank-fastapi-toolkit-production.up.railway.app/docs
- **Health Check**: https://neurobank-fastapi-toolkit-production.up.railway.app/health

## 💻 **Desarrollo Local**
- **API Principal**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/backoffice/
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🚀 **Iniciar servidor local:**
```bash
# Método 1:
python start_clean_server.py

# Método 2:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔑 **Variables de entorno necesarias:**
- **Local**: Configuradas en `.env` (no se sube a Git)
- **Producción**: Configuradas en Railway Dashboard

---
*✅ Todo funcionando perfectamente tanto en desarrollo como en producción*
