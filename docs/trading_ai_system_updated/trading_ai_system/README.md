# Crypto Trading AI System

This repository provides a **starter template** for building a modular, compliant,
and scalable crypto‑trading system powered by AI.  The goal is to give you a
professional foundation that you can extend into a fully fledged algorithmic
trading platform ready for competitions such as **Alpha Arena** or **Hyperliquid**.

## Repository structure

```text
trading_ai_system/
├── docker-compose.yml      # Orchestration for local development
├── Makefile                # Helper targets for common tasks
├── .env.example            # Environment variables template (do not commit real secrets)
├── ingestion_service/      # Service that ingests live market data into Kafka
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── inference_service/      # Service that performs inference using RL/NLP models
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── control_service/        # Service that executes trades based on model output
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── .devcontainer/
│   └── devcontainer.json   # VS Code container definition for reproducible dev
└── .github/workflows/
    └── ci.yml              # Example GitHub Actions workflow
```

## Key features

- **Microservices architecture**: Each component (ingestion, inference,
  control) is isolated behind its own container.  Services communicate via
  Kafka topics, enabling horizontal scaling and independent deployments.
- **Observability**: Prometheus metrics and OpenTelemetry tracing are
  instrumented in each service.  Metrics can be scraped by Prometheus and
  visualised in Grafana to monitor latencies, throughput and errors.
- **Modularity**: The `inference_service` uses a pluggable model layer.  By
  default it implements a stub that always returns “hold”; replace it with
  your own **LSTM**, **Transformer** or **reinforcement learning** policy
  implemented with `torch`, `stable‑baselines3` or `ray[rllib]`.
- **Compliance hooks**: The system includes optional integration points for
  Merkle logging (immutable audit logs), explainability through SHAP/LIME and
  rate‑limiting middleware to satisfy MiCA and AI Act requirements.

## Prerequisites

1. **macOS Sonoma 14.7.6** with command line tools installed.
2. **Homebrew** for package management (`/bin/bash -c "$(curl -fsSL
   https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`).
3. **Docker Desktop for Mac** and **Docker Compose v2**.  Make sure Docker
   Desktop is granted access to the default network and file system.
4. **GitHub CLI** (`brew install gh`) and **Git** for cloning and committing
   code.
5. **Python 3.11+** installed via `pyenv` or the system installer.  This
   repository uses [`poetry`](https://python-poetry.org) for dependency
   management, but plain `pip` and virtualenv will also work.

## Getting started

1. **Clone the template**

   ```bash
   gh repo clone your‑username/crypto‑trading‑ai
   cd crypto‑trading‑ai
   ```

2. **Copy environment variables**

   Create a `.env` file based on the example and fill in secrets such as API
   keys for exchanges, Kafka credentials and monitoring endpoints.  Never
   commit real secrets to version control; use GitHub Secrets for CI/CD and
   Docker secrets in production.

   ```bash
   cp .env.example .env
   # then edit with your own values
   ```

3. **Build and run locally**

   Use Docker Compose to spin up Kafka, Zookeeper and the three services.

   ```bash
   docker compose up --build
   ```

   This command builds each service and starts them together with Kafka and
   Zookeeper.  Once running, you should see log output indicating the
   ingestion service is consuming price feeds and publishing messages.

4. **Development inside a dev container**

   Visual Studio Code can attach to the `.devcontainer` configuration for
   reproducible development.  Press `F1` → *Dev Containers: Reopen in
   Container* to start a container with all Python and Node dependencies
   installed.  The dev container uses `poetry` for Python dependencies and
   includes the GitHub Copilot extension by default (if installed locally).

5. **Testing**

   Each service includes a `tests/` directory where you can add unit tests.
   Integrate `pytest`, `pylint` and `mypy` into your CI workflow.  The
   `Makefile` contains shortcuts (`make test`, `make lint`) to run these
   locally.

## Services

### Ingestion Service

This microservice connects to external data sources (e.g. Hyperliquid
WebSocket or CCXT exchange API) and publishes normalised tick data to Kafka.
It is intentionally simple – replace `main.py` with your own ingestion logic.

### Inference Service

The inference service subscribes to the `market_data` topic, loads an AI
model and outputs trading signals (e.g. 1 for buy, −1 for sell) on a
`trade_signals` topic.  Initially it implements a dummy policy.  You can
integrate any model: LSTM for time series, transformers for sentiment or
reinforcement learning agents trained with `stable‑baselines3` or `ray[rllib]`.

### Control Service

This service listens to `trade_signals`, performs sanity checks (rate limits,
position sizing via Kelly criterion) and places orders on the exchange via
`ccxt` or the native Hyperliquid SDK.  It is the only service that holds
private keys; secure them via environment variables and never log them.

## Security and compliance

- **KYC/AML**: If handling client funds, integrate KYC/AML checks in your
  onboarding and ensure your code operates through regulated exchanges only.
- **Auditability**: Use Merkle trees or append‑only logs to track every
  decision and executed trade.  This is essential for MiCA/AI Act compliance.
- **Explainability**: Integrate `shap` or `lime` in the inference service to
  produce human‑readable explanations of model outputs.  Persist these with
  each trade to support audits.
- **Geo‑fencing**: Avoid placing trades in prohibited jurisdictions.  Implement
  IP or time‑zone checks and respect FATF guidelines.

## Extending the template

This template is a starting point.  To achieve competitive performance,
consider the following enhancements:

1. **Distributed RL training**: Use `ray[rllib]` to train multi‑agent
   reinforcement learning policies on historical tick data.  Combine
   adversarial training with synthetic crash scenarios.
2. **Sentiment analysis**: Ingest social‑media data (X/Twitter) with a
   transformer model fine‑tuned on crypto sentiment.  Fuse this with price
   features in the RL state.
3. **Backtesting**: Integrate `backtrader` or `zipline` for offline
   evaluation.  Use Monte‑Carlo simulation and cross‑validation to assess
   risk.  Target a Sharpe ratio above 1.5 and drawdowns below 20 %.
4. **Deployment**: For production, deploy services on Kubernetes (EKS/GKE) or
   serverless platforms (AWS AppRunner).  Use GitHub Actions to build,
   test and push Docker images, and Terraform to manage infrastructure.

## License

This template is provided under the MIT License.  See [LICENSE](LICENSE)
for details.