# 🚀 Guía de Deployment Manual - NeuroBank FastAPI Toolkit

## 🎯 **Proceso Completo de Deployment**

### **Fase 0: Configuración de GitHub Secrets**

Antes de ejecutar el CI/CD pipeline, debes configurar los siguientes secrets en tu repositorio de GitHub:

#### **Configurar Secrets en GitHub**

1. **🌐 Ir a Settings → Secrets and variables → Actions**
   ```
   URL: https://github.com/USERNAME/NeuroBank-FastAPI-Toolkit/settings/secrets/actions
   ```

2. **🔑 Agregar los siguientes secrets:**
   - `DOCKER_USERNAME`: Tu usuario de Docker Hub
   - `DOCKER_PASSWORD`: Tu contraseña o token de Docker Hub
   - `RAILWAY_TOKEN`: Token de Railway (si usas Railway para deployment)
   - `SONAR_TOKEN`: Token de SonarCloud (opcional, para análisis de código)
   - `CODECOV_TOKEN`: Token de Codecov (opcional, para coverage)

#### **Obtención de Tokens**

**Docker Hub:**
- ⚠️ **IMPORTANTE**: Usa un **Access Token**, NO tu contraseña
- Login en: https://hub.docker.com
- Ir a: Account Settings → Security → New Access Token
- Crear token con permisos "Read, Write & Delete"
- Copiar el token generado (solo se muestra una vez)

**Railway:**
- Login en: https://railway.app
- Ir a Settings → Tokens → Create New Token

**SonarCloud:**
- Login en: https://sonarcloud.io
- Ir a My Account → Security → Generate Token

**Codecov:**
- Login en: https://codecov.io
- Ir a Settings → Integrations → GitHub → Token

### **Fase 1: Pre-Deployment Checklist**

```bash
# 1. Verificar configuración AWS OIDC
./scripts/verify-aws-oidc.sh

# 2. Ejecutar tests locales
pytest -v

# 3. Verificar rama main actualizada
git status
git log --oneline -3
```

### **Fase 2: Deployment via GitHub Actions**

#### **Opción A: Via Web Interface (Recomendado)**

1. **🌐 Ir a GitHub Actions**
   ```
   URL: https://github.com/Neiland85/NeuroBank-FastAPI-Toolkit/actions
   ```

2. **⚙️ Seleccionar Workflow**
   - Click en "CI/CD Pipeline"
   - Click en "Run workflow" (botón azul)

3. **🔧 Configurar Deployment**
   ```
   Branch: main ✅
   Deploy to AWS: true ✅
   Environment: production
   ```

4. **🚀 Ejecutar Deployment**
   - Click en "Run workflow"
   - Monitorear progreso en tiempo real

#### **Opción B: Via GitHub CLI**

```bash
# Ejecutar workflow desde terminal
gh workflow run "CI/CD Pipeline" \
  --ref main \
  --field deploy_to_aws=true \
  --field environment=production

# Verificar estado del workflow
gh run list --workflow="CI/CD Pipeline" --limit 1

# Ver logs en tiempo real
gh run watch
```

### **Fase 3: Monitoring Post-Deployment**

#### **3.1 Verificación Inmediata**

```bash
# Verificar stack de CloudFormation
aws cloudformation describe-stacks \
  --stack-name neurobank-api \
  --region eu-west-1 \
  --query 'Stacks[0].StackStatus'

# Obtener URL del API Gateway
aws cloudformation describe-stacks \
  --stack-name neurobank-api \
  --region eu-west-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

#### **3.2 Health Check**

```bash
# Obtener URL de la API
API_URL=$(aws cloudformation describe-stacks \
  --stack-name neurobank-api \
  --region eu-west-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Test del health endpoint
curl -X GET "$API_URL/health" \
  -H "Content-Type: application/json" | jq '.'

# Test del root endpoint
curl -X GET "$API_URL/" \
  -H "Content-Type: application/json" | jq '.'
```

#### **3.3 Test de Autenticación**

```bash
# Test con API Key (si está configurada)
API_KEY="your-api-key-here"

# Test endpoint protegido
curl -X GET "$API_URL/operator/order-status/ORD123" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" | jq '.'

# Test con Bearer token
curl -X GET "$API_URL/operator/order-status/ORD123" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" | jq '.'
```

### **Fase 4: Troubleshooting**

#### **4.1 Errores Comunes**

```bash
# Ver logs de Lambda
aws logs tail /aws/lambda/NeuroBank-Function \
  --region eu-west-1 \
  --follow \
  --since 10m

# Ver métricas de CloudWatch
aws logs describe-log-groups \
  --region eu-west-1 \
  --log-group-name-prefix /aws/lambda/NeuroBank

# Verificar ECR images
aws ecr list-images \
  --repository-name neurobank-fastapi \
  --region eu-west-1
```

#### **4.2 Rollback Plan**

```bash
# Ver versiones del stack
aws cloudformation list-stack-sets \
  --region eu-west-1

# Rollback a versión anterior (si necesario)
aws cloudformation cancel-update-stack \
  --stack-name neurobank-api \
  --region eu-west-1
```

---

## 🎯 **URLs y Referencias Importantes**

### **🔗 Links Rápidos**
- **GitHub Actions**: https://github.com/Neiland85/NeuroBank-FastAPI-Toolkit/actions
- **AWS Console**: https://console.aws.amazon.com/cloudformation/home?region=eu-west-1
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=eu-west-1#logsV2:log-groups

### **📊 Métricas de Éxito**
- ✅ **Stack Status**: `UPDATE_COMPLETE` o `CREATE_COMPLETE`
- ✅ **Health Check**: HTTP 200 con timestamp UTC
- ✅ **API Endpoints**: Respuestas JSON válidas
- ✅ **CloudWatch**: Logs sin errores críticos

### **🚨 Criterios de Rollback**
- ❌ Stack Status: `UPDATE_FAILED`
- ❌ Health Check: HTTP 5xx errors
- ❌ Lambda Errors: > 1% error rate
- ❌ API Gateway: Timeout > 10 segundos

---

## 🎉 **Post-Deployment Checklist**

- [ ] Stack deployado exitosamente
- [ ] Health check respondiendo
- [ ] API endpoints funcionales
- [ ] Logs de CloudWatch limpios
- [ ] Métricas de X-Ray activas
- [ ] Rate limiting configurado
- [ ] Monitoreo establecido

**¡Deployment Completado! 🚀**
