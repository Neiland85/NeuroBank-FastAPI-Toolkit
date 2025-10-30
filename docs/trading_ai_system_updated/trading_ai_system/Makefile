# Makefile for common development tasks

PYTHON ?= python3

.PHONY: help setup build up down logs lint test format

help:
	@echo "Available commands:"
	@echo "  make setup   - Install dependencies into a virtualenv"
	@echo "  make build   - Build Docker images"
	@echo "  make up      - Start the stack with docker compose"
	@echo "  make down    - Stop the stack"
	@echo "  make logs    - Follow logs from all services"
	@echo "  make lint    - Lint Python code using flake8"
	@echo "  make test    - Run pytest if tests/ exists"

setup:
	$(PYTHON) -m venv .venv && .venv/bin/pip install -U pip
	for svc in ingestion_service inference_service control_service; do \
		if [ -f $$svc/requirements.txt ]; then \
			.venv/bin/pip install -r $$svc/requirements.txt; \
		fi; \
	done

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

lint:
	flake8 . --max-line-length=120

test:
	@if [ -d "tests" ]; then \
		pytest -q; \
	else \
		echo "No tests directory"; \
	fi

# ------------------------------------------------------------------------------
# AWS provisioning and deployment helpers
#
# Las siguientes tareas simplifican la creación de repositorios ECR, clústeres ECS
# y el proceso de construcción y subida de imágenes Docker para cada
# microservicio. Configura las variables `AWS_REGION` y `AWS_ACCOUNT_ID` al
# invocar make o define valores por defecto aquí.

AWS_REGION ?= eu-west-1
AWS_ACCOUNT_ID ?= 123456789012

ECR_REPOS = neurobank/api-gateway neurobank/ingestion-service neurobank/inference-service neurobank/control-service

# Crea todos los repositorios ECR definidos en ECR_REPOS. Si ya existen,
# ignora el error.
aws-create-ecr:
	@for repo in $(ECR_REPOS); do \
		echo "Creating ECR repository $$repo in $(AWS_REGION)..."; \
		aws ecr create-repository --repository-name $$repo --region $(AWS_REGION) --image-scanning-configuration scanOnPush=true || true; \
	done

# Crea el clúster ECS llamado neurobank-prod. Si ya existe, ignora el error.
aws-create-ecs:
	aws ecs create-cluster --cluster-name neurobank-prod --region $(AWS_REGION) || true

# Inicia sesión en ECR usando las credenciales configuradas en tu entorno.
aws-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

# Build and push rules para cada microservicio. Cada regla `build-*` compila la
# imagen Docker y la regla `push-*` la envía a ECR. Ajusta el nombre del
# Dockerfile y el contexto según tu proyecto.

# API Gateway
build-api:
	docker build -t neurobank/api-gateway:latest -f Dockerfile.dev .

push-api: build-api aws-login
	docker tag neurobank/api-gateway:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/api-gateway:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/api-gateway:latest

# Ingestion Service
build-ingestion:
	docker build -t neurobank/ingestion-service:latest -f ingestion_service/Dockerfile ingestion_service

push-ingestion: build-ingestion aws-login
	docker tag neurobank/ingestion-service:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/ingestion-service:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/ingestion-service:latest

# Inference Service
build-inference:
	docker build -t neurobank/inference-service:latest -f inference_service/Dockerfile inference_service

push-inference: build-inference aws-login
	docker tag neurobank/inference-service:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/inference-service:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/inference-service:latest

# Control Service
build-control:
	docker build -t neurobank/control-service:latest -f control_service/Dockerfile control_service

push-control: build-control aws-login
	docker tag neurobank/control-service:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/control-service:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/neurobank/control-service:latest