FROM python:3.11-slim

# Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  POETRY_VERSION=1.8.2

# Sistema
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copiar proyecto
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --only main

# Copiar código
COPY . /app

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
