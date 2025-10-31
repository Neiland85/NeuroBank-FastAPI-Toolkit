# Deploy Plan — NeuroBank + Trading AI (Vercel + Railway + ECS)

## 1) Arquitectura por entornos

- **Local Dev**: Docker Compose + Kafka local + `.env`
- **Staging (QA/Demo)**: Railway (servicios: `api_gateway` FastAPI, `ingestion_service`, `inference_service`, `control_service`)
- **Producción**: AWS ECS Fargate (mismos servicios + OTel sidecar + ALB + MSK opcional)
- **Frontend/Dashboards**: Vercel (Next.js/SvelteKit) consumiendo `API_BASE_URL`

## 2) Servicios (microservicios Python)

1. **api_gateway** (FastAPI, base NeuroBank)
2. **ingestion_service** (websockets/CCXT → Kafka topic `market_data`)
3. **inference_service** (LSTM/RL/ensemble → Kafka topic `trade_signals`, SHAP/LIME opcional)
4. **control_service** (riesgo + ejecución órdenes via exchange SDK/CCXT)
5. **otel-collector** (prod, sidecar en ECS) [opcional en staging]
6. **kafka/zookeeper** (local/staging; en prod usar MSK o Kafka gestionado)

## 3) Secrets y variables (nombres estándar)

- `SECRET_KEY` — clave app (prod: `openssl rand -hex 32`)
- `API_KEY` — token interno
- `ENVIRONMENT` — development|staging|production
- `WORKERS` — uvicorn workers (p.ej. 2–4)
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (solo ECS)
- `KAFKA_BOOTSTRAP_SERVERS`, `TOPIC_MARKET_DATA`, `TOPIC_TRADE_SIGNALS`
- Exchanges: `EXCHANGE_API_KEY`, `EXCHANGE_SECRET`
- Hyperliquid: `HYPERLIQUID_API_KEY`, `HYPERLIQUID_PRIVATE_KEY`
- OTel: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`

## 4) CI/CD

- **GH Actions - CI**: lint + tests + build cache
- **Deploy Staging (Railway)**: al merge en `main` o tag `staging-*` → `railway up`
- **Deploy Prod (ECS)**: tag con `prod-*` → build & push a ECR + update servicio ECS

## 5) Observabilidad

- **Staging**: Prometheus client en `/metrics` + logs Railway
- **Prod**: OTel SDK (trazas) → Collector sidecar (OTLP/HTTP) → Grafana/Tempo/CloudWatch

## 6) Cumplimiento (MiCA/AI Act)

- Explainability en inferencia (SHAP/LIME) adjunta a señales
- Logs inmutables (Merkle) para auditoría decisiones
- Gates en CI/CD: Trivy (seguridad), licencia, firmas de imagen (cosign) [opcional]

## 7) Rollback

- Staging: `railway deployments` → rollback one-click
- Prod: mantener 2 task defs en ECS; rollback cambiando el `taskDefinition` del servicio
