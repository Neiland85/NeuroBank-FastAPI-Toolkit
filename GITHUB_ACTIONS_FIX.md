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

## 🔍 **Type Checking con MyPy**

### Configuración de MyPy

MyPy está configurado para ejecutarse automáticamente en los workflows de CI/CD:

#### `.github/workflows/ci.yml`

```yaml
- name: 🧼 Code Quality Checks
  run: |
    echo "Running Ruff and Mypy checks..."
    ruff check .
    ruff format --check .
    echo "Running MyPy type checking on app/ directory with pyproject.toml configuration..."
    mypy app/
    echo "✅ Code Quality stage completed."
```

#### `.github/workflows/ci-cd-pipeline.yml`
```yaml
- name: Run MyPy
  run: |
    echo "Running MyPy type checking on app/ directory with pyproject.toml configuration..."
    mypy app/ --junit-xml mypy-report.xml
```

### Configuración de MyPy en `pyproject.toml`

MyPy está configurado con reglas estrictas incluyendo `no_implicit_optional`:

```toml
[tool.mypy]
python_version = "3.11"
files = ["app"]
exclude = ["^alembic/.*", "^api/.*"]
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true  # ✅ Previene regresiones de tipado
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
ignore_missing_imports = true
plugins = ["sqlalchemy.ext.mypy.plugin"]
```

### Ejecución Local

Para ejecutar MyPy localmente:

```bash
# Usando make
make type-check

# Directamente
mypy app/
```

### Jenkins

El `Jenkinsfile` también ejecuta MyPy:

```groovy
stage('Type Checking') {
    steps {
        sh '''
            echo "Running MyPy type checking on app/ directory with pyproject.toml configuration..."
            mypy app/
        '''
    }
}
```

---

## 📝 **Spell Checking con Codespell**

### Configuración de Codespell

Codespell está configurado para ejecutarse automáticamente en los workflows de CI/CD:

#### `.github/workflows/ci.yml`
```yaml
- name: 🧼 Code Quality Checks
  run: |
    echo "Running Ruff and Mypy checks..."
    ruff check .
    ruff format --check .
    echo "Running MyPy type checking on app/ directory with pyproject.toml configuration..."
    mypy app/
    echo "Running codespell checks..."
    codespell -q 2 -I .codespell-ignore-words.txt app README.md docs/
    echo "✅ Code Quality stage completed."
```

### Archivo de Exclusiones

El archivo `.codespell-ignore-words.txt` contiene términos en español y técnicos:
- Palabras en español válidas (administrativo, componentes, etc.)
- Términos técnicos (selectin)
- Evita falsos positivos en documentación bilingüe

### Ejecución Local

Para ejecutar codespell localmente:

```bash
# Usando make
make spellcheck

# Directamente
codespell -q 2 -I .codespell-ignore-words.txt app README.md docs/
```

### Jenkins

El `Jenkinsfile` también ejecuta codespell:

```groovy
echo "Running codespell checks..."
codespell -q 2 -I .codespell-ignore-words.txt app README.md docs/
```

---

**🔧 Aplica cualquiera de estas opciones a tu workflow y el CI/CD funcionará perfectamente.**
