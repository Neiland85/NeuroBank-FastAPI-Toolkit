# Docker Configuration for NeuroBank FastAPI Toolkit

This directory contains Docker configurations for building and deploying the NeuroBank FastAPI application.

## Dockerfile.api

Production-ready multi-stage Dockerfile optimized for:
- **FastAPI** application deployment
- **Uvicorn** ASGI server with uvloop for performance
- **Non-root user** for enhanced security
- **Health checks** for container orchestration
- **Multi-stage build** for minimal image size

### Building the Image

```bash
# Build from repository root
docker build -f docker/Dockerfile.api -t neurobank-fastapi:latest .

# Build with custom tag
docker build -f docker/Dockerfile.api -t neurobank-fastapi:v1.0.0 .
```

### Running the Container

```bash
# Run with default settings (port 8000)
docker run -p 8000:8000 neurobank-fastapi:latest

# Run with custom port
docker run -p 3000:3000 -e PORT=3000 neurobank-fastapi:latest

# Run with custom workers
docker run -p 8000:8000 -e WORKERS=4 neurobank-fastapi:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e API_KEY=your-api-key \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=postgresql://... \
  neurobank-fastapi:latest
```

### Environment Variables

- `PORT` - Port to bind the application (default: 8000)
- `WORKERS` - Number of uvicorn workers (default: 1)
- `API_KEY` - API key for authentication
- `ENVIRONMENT` - Environment name (development, staging, production)
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Secret key for JWT token generation

### Health Check

The container includes a health check that tests the `/health` endpoint:
- Interval: 30 seconds
- Timeout: 10 seconds
- Start period: 10 seconds
- Retries: 3

### Image Layers

1. **Builder Stage**: Compiles and installs Python dependencies
2. **Runtime Stage**: Creates minimal production image with only runtime dependencies

### Security Features

- Non-root user execution
- Minimal base image (python:3.11-slim)
- No unnecessary packages
- Separate build and runtime stages

### Best Practices

1. Always use specific version tags in production
2. Set appropriate resource limits in container orchestration
3. Use secrets management for sensitive environment variables
4. Mount volumes for persistent data if needed
5. Configure proper logging and monitoring

## CI/CD Integration

This Dockerfile is used in the GitHub Actions workflow:
- `.github/workflows/production-pipeline.yml`

The workflow automatically builds and pushes images to Docker Hub with:
- `latest` tag for main branch
- Git SHA tag for versioning
- Build cache optimization
