PY=python
PIP=pip

.PHONY: install dev-install lint format type-check security complexity dead-code docstring-coverage dependency-check architecture-check mutation-test profile load-test sonar docs docker-up docker-down migrate run run-prod all-checks ci

install:
	$(PIP) install -r requirements.txt

dev-install:
	$(PIP) install -r requirements.txt && $(PIP) install -r requirements-dev.txt

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy --install-types --non-interactive

security:
	bandit -r app -f screen || true
	semgrep scan --config auto || true
	pip-audit || true
	safety check || true

complexity:
	radon cc app -s -a
	radon mi app -s

dead-code:
	vulture app --min-confidence 80

docstring-coverage:
	interrogate -v -f 80 app

dependency-check:
	deptry . || true
	pipdeptree -w silence

architecture-check:
	import-linter --config pyproject.toml

mutation-test:
	mutmut run --paths-to-mutate app --tests-dir app/tests --use-coverage
	mutmut results

profile:
	python -m scalene -m app.main

load-test:
	locust -f tests/locustfile.py --headless -u 50 -r 10 -t 2m --host http://localhost:8000

sonar:
	sonar-scanner

docs:
	mkdocs build --strict

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

migrate:
	alembic upgrade head

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

all-checks: lint type-check security complexity dead-code docstring-coverage dependency-check architecture-check

ci: install lint type-check security

.PHONY: help install dev-install test coverage lint format type-check security complexity dead-code docs clean docker-up docker-down migrate profile load-test mutation-test all-checks ci dependency-check architecture-check pydeps sonar docs-serve docker-logs migrate-create run run-prod

PYTHON := python3.11
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := ruff
MYPY := mypy
BANDIT := bandit

help: ## Mostrar este mensaje de ayuda
	@echo "NeuroBank FastAPI Toolkit - Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $${1}, $${2}}'

install: ## Instalar dependencias de producción
	$(PIP) install -r requirements.txt

dev-install: ## Instalar dependencias de desarrollo
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test: ## Ejecutar tests
	$(PYTEST) app/tests/ -v

coverage: ## Ejecutar tests con coverage
	$(PYTEST) app/tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report: htmlcov/index.html"

lint: ## Ejecutar linting con Ruff
	$(RUFF) check app/

format: ## Formatear código con Ruff
	$(RUFF) format app/
	$(RUFF) check --fix app/

type-check: ## Verificar tipos con MyPy
	$(MYPY) app/

security: ## Análisis de seguridad
	$(BANDIT) -r app/ -c .bandit
	safety check
	pip-audit || true
	semgrep --config auto app/ || true

complexity: ## Análisis de complejidad
	radon cc app/ -a -s
	radon mi app/ -s

dead-code: ## Detectar código muerto
	vulture app/ --min-confidence 60

docstring-coverage: ## Verificar cobertura de docstrings
	interrogate app/ --fail-under 80

dependency-check: ## Análisis de dependencias
	pipdeptree
	deptry app/ || true

architecture-check: ## Validar arquitectura
	import-linter

pydeps: ## Visualizar dependencias
	pydeps app/ --max-bacon 2 --cluster

mutation-test: ## Mutation testing (lento)
	mutmut run --paths-to-mutate app/ --tests-dir app/tests/
	mutmut results

profile: ## Profiling de performance
	py-spy record -o profile.svg --duration 60 -- $(PYTHON) -m uvicorn app.main:app
	@echo "Profile saved: profile.svg"

load-test: ## Load testing con Locust
	locust -f tests/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 2m --host http://localhost:8000

sonar: ## Análisis con SonarQube
	sonar-scanner

docs: ## Generar documentación
	mkdocs build
	@echo "Docs: site/index.html"

docs-serve: ## Servir documentación localmente
	mkdocs serve

clean: ## Limpiar archivos generados
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf htmlcov/ .coverage coverage.xml test-results.xml
	rm -rf dist/ build/ *.egg-info

docker-up: ## Iniciar servicios Docker
	docker-compose up -d
	@echo "Services started. API: http://localhost:8000, Adminer: http://localhost:8080"

docker-down: ## Detener servicios Docker
	docker-compose down

docker-logs: ## Ver logs de Docker
	docker-compose logs -f api

migrate: ## Ejecutar migraciones de base de datos
	alembic upgrade head

migrate-create: ## Crear nueva migración
	alembic revision --autogenerate -m "$(msg)"

run: ## Ejecutar servidor de desarrollo
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Ejecutar servidor de producción
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop

all-checks: lint type-check security complexity dead-code docstring-coverage dependency-check architecture-check ## Ejecutar todos los checks
	@echo "✅ All checks completed!"

ci: all-checks test coverage ## Simular pipeline CI localmente
	@echo "✅ CI checks completed!"

.DEFAULT_GOAL := help
