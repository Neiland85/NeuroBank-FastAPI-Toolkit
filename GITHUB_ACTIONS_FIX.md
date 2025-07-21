# 🔧 GitHub Actions Workflow Fix

## 📝 **Opción 1: Actualizar el archivo .github/workflows/ci-cd.yml**

Añade la variable `API_KEY` al workflow existente:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    # ✅ AÑADIR ESTAS VARIABLES DE ENTORNO
    env:
      API_KEY: "NeuroBankDemo2025-SecureKey-ForTestingOnly"
      ENVIRONMENT: "testing"
      CI: "true"
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest --cov=app --cov-report=xml --cov-report=html
```

## 📝 **Opción 2: Usar GitHub Secrets (Más Seguro)**

Si prefieres usar secrets:

```yaml
    env:
      API_KEY: ${{ secrets.API_KEY }}
      ENVIRONMENT: "testing"
      CI: "true"
```

Y luego en GitHub → Settings → Secrets → Actions → New repository secret:
- Name: `API_KEY`
- Value: `NeuroBankDemo2025-SecureKey-ForTestingOnly`

## 📝 **Opción 3: Variables Globales del Workflow**

Añadir al inicio del archivo workflow:

```yaml
name: CI/CD Pipeline

# ✅ VARIABLES GLOBALES PARA TODO EL WORKFLOW
env:
  API_KEY: "NeuroBankDemo2025-SecureKey-ForTestingOnly"
  ENVIRONMENT: "testing"
  CI: "true"

on:
  push:
    branches: [ main, develop ]
  # ... resto del workflow
```

## 🎯 **Recomendación**

**Usa la Opción 1** - es la más directa y funciona inmediatamente.

El código ya está preparado para detectar `CI=true` y usar automáticamente una API key de prueba, pero añadir la variable explícitamente garantiza compatibilidad total.

---

**🔧 Aplica cualquiera de estas opciones a tu workflow y el CI/CD funcionará perfectamente.**
