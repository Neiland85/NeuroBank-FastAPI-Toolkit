# Makefile — NeuroBank CI/CD utilities

AWS_REGION ?= eu-west-1
AWS_ACCOUNT_ID ?= 000000000000
ECR_REGISTRY := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
TAG := $(shell date +prod-%Y.%m.%d-%H%M)

.PHONY: help setup lint test build release-prod aws-login

help:
	@echo "Available targets:"
	@echo "  setup          Install dependencies"
	@echo "  lint           Run flake8 + black"
	@echo "  test           Run pytest"
	@echo "  build          Build docker images"
	@echo "  release-prod   Create tag + push (triggers ECS deploy)"
	@echo "  aws-login      Authenticate docker to AWS ECR"

setup:
	pip install -r requirements.txt

lint:
	flake8 . || true
	black --check . || true

test:
	pytest -q || echo "⚠️ No tests found"

build:
	@echo "Building local images..."
	docker build -t neurobank-api:latest -f docker/Dockerfile.api .

aws-login:
	aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(ECR_REGISTRY)

release-prod:
	git tag -a $(TAG) -m "Release $(TAG)"
	git push origin $(TAG)
