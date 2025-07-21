# 🚂 Railway Deployment Guide - NeuroBank FastAPI Toolkit

## 📋 Pre-Deployment Checklist

### ✅ **Archivos Requeridos Creados:**
- `Procfile` ✅ - Configuración de arranque para Railway
- `.env.template` ✅ - Template de variables de entorno
- Configuración CORS segura ✅
- Validación de API Keys ✅

## 🔧 **Pasos para Deploy en Railway**

### 1. **Preparación del Repositorio**
```bash
# Asegúrate de que todos los cambios estén commiteados
git add .
git commit -m "feat: Railway deployment configuration"
git push origin main
```

### 2. **Crear Proyecto en Railway**
1. Ve a [Railway.app](https://railway.app)
2. Conecta tu repositorio GitHub
3. Selecciona `NeuroBank-FastAPI-Toolkit`

### 3. **⚠️ Variables de Entorno CRÍTICAS**
Configura estas variables en Railway Dashboard (Settings → Variables):

#### 🔐 **Seguridad (OBLIGATORIAS)**
```env
API_KEY=tu_api_key_super_segura_minimo_32_caracteres
SECRET_KEY=tu_secret_key_super_segura_minimo_32_caracteres
```

#### 🌐 **Aplicación**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://*.railway.app,https://tudominio.com
```

### 4. **🚀 Deploy Automático**
Railway detectará automáticamente el `Procfile` y iniciará el deploy.

## 🛡️ **Mitigaciones de Seguridad Implementadas**

### ✅ **Problemas Resueltos:**

1. **CORS Configurado Correctamente**
   - ❌ Antes: `allow_origins=["*"]` (INSEGURO)
   - ✅ Ahora: Dominios específicos desde env var

2. **API Keys Obligatorias**
   - ❌ Antes: Key por defecto débil
   - ✅ Ahora: Falla si no está configurada

3. **Puerto Dinámico**
   - ✅ Usa variable `$PORT` de Railway

4. **Environment Detection**
   - ✅ Detecta automáticamente entorno Railway

## 🔍 **Validación Post-Deploy**

### 1. **Health Check**
```bash
curl https://tu-app.railway.app/health
```

### 2. **API Test**
```bash
curl -H "X-API-Key: tu_api_key" https://tu-app.railway.app/
```

### 3. **CORS Test**
```bash
curl -H "Origin: https://tu-dominio.com" https://tu-app.railway.app/
```

## 🚨 **Acciones Post-Deploy Inmediatas**

### 1. **Cambiar URLs en Documentación**
Actualiza estos URLs en `main.py`:
```python
servers=[
    {
        "url": "https://tu-app.railway.app",  # ← Cambiar por tu URL real
        "description": "Production server"
    }
]
```

### 2. **Configurar Dominio Personalizado (Opcional)**
En Railway Dashboard → Settings → Domains

### 3. **Monitoring**
- Health endpoint: `https://tu-app.railway.app/health`
- Logs: Railway Dashboard → Deployments → Logs

## ⚡ **Optimizaciones Railway**

### 1. **Resources (Opcional)**
En Railway → Settings → Resources:
- RAM: 512MB (mínimo)
- CPU: 1 vCPU

### 2. **Networking**
Railway asigna automáticamente:
- HTTPS habilitado ✅
- CDN global ✅
- Load balancing ✅

## 🆘 **Troubleshooting**

### Error: "API_KEY environment variable is required"
**Solución:** Configura `API_KEY` en Railway Variables

### Error: CORS blocked
**Solución:** Actualiza `CORS_ORIGINS` con tu dominio

### Error: Port binding
**Solución:** Verifica que el `Procfile` use `$PORT`

## 📊 **Monitoreo**

### Endpoints Importantes:
- Health: `/health`
- Docs: `/docs`  
- Admin: `/backoffice/`

### Variables Railway Disponibles:
- `RAILWAY_ENVIRONMENT_ID`
- `RAILWAY_PROJECT_ID`
- `PORT` (automático)

---

**🎉 ¡Listo para producción en Railway!**
