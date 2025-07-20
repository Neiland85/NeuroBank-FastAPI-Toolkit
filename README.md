# Operator API (FASE 2)

Backend en FastAPI para consultar estados de pedidos y generar facturas.

## Requisitos

- Python 3.10+
- macOS Sonoma 14.7.6 (compatible)
- Poetry o pip + virtualenv

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Ajusta la API_KEY si lo deseas
```

## Ejecución

```bash
uvicorn app.main:app --reload
# Visita http://localhost:8000/docs
```

## Tests

```bash
pytest
```

## Despliegue

- Contenedor Docker (opcional)
- AWS ECS/Fargate o EC2 + Systemd
- Observabilidad: CloudWatch, Prometheus + Grafana, etc.

---

## Cómo levantar el proyecto

1. **Crear entorno virtual**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar .env**
   ```bash
   cp .env.example .env
   # Edita API_KEY si lo deseas
   ```

4. **Ejecutar servidor**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Probar endpoints** (con la API Key en cabecera X-API-Key)
   - `GET /operator/order_status/123`
   - `POST /operator/generate_invoice` con body `{"order_id": "123"}`

6. **Ejecutar tests**
   ```bash
   pytest
   ```NeuroBank-FastAPI-Toolkit
Senior‑grade FastAPI microservice blueprint for AI‑driven banking. Python 3.10+, Pydantic v2, Docker &amp; AWS stack (Lambda, AppRunner, CloudWatch, X‑Ray) with CI/CD via GitHub Actions.  Incluye clean code, tests completos, observabilidad y módulos listos para estado de pedidos, facturación y analítica.
