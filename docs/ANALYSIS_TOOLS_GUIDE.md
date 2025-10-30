# 📊 Guía de Herramientas de Análisis y Ejecución

## 1. Análisis de Calidad de Código

### 1.1 Ruff (Linting y Formateo)
Comandos:
```bash
ruff check app/
ruff format app/
ruff check --fix app/
```

### 1.2 Radon (Complejidad Ciclomática)
```bash
radon cc app/ -a -s
radon mi app/ -s
radon raw app/ -s
radon hal app/
```

### 1.3 Vulture (Dead Code)
```bash
vulture app/ --min-confidence 60
```

### 1.4 Interrogate (Docstring Coverage)
```bash
interrogate app/
interrogate app/ --fail-under 80
```

### 1.5 SonarQube/SonarCloud
```bash
sonar-scanner
```

---

## 2. Type Checking

### 2.1 MyPy
```bash
mypy app/
mypy app/ --strict
```

---

## 3. Security Scanning

### 3.1 Bandit / Safety / pip-audit / Semgrep
```bash
bandit -r app/ -c .bandit
safety check
pip-audit
semgrep --config auto app/
```

---

## 4. Dependency Analysis

```bash
pipdeptree
deptry app/
```

---

## 5. Architecture Analysis

```bash
import-linter
pydeps app/ --max-bacon 2 --cluster
```

---

## 6. Testing Avanzado

Mutmut (mutation testing):
```bash
mutmut run
mutmut results
```

Hypothesis (property-based):
```python
from hypothesis import given, strategies as st

@given(st.text(), st.integers())
def test_example(a, b):
    pass
```

Syrupy (snapshot testing):
```python
def test_api_response(snapshot):
    assert {"ok": True} == snapshot
```

---

## 7. Performance

```bash
py-spy record -o profile.svg -- python -m uvicorn app.main:app
scalene --html --outfile report.html app/main.py
locust -f tests/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m
```

---

## 8. CI/CD Workflows
- .github/workflows/ci-cd-pipeline.yml
- .github/workflows/mutation-testing.yml
- .github/workflows/performance-testing.yml

---

## 9. Docker Compose
```bash
docker-compose up -d
docker-compose logs -f api
docker-compose exec api alembic upgrade head
```

---

## 10. Makefile
```bash
make dev-install
make all-checks
make ci
```
