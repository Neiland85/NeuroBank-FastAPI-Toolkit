#!/bin/bash
echo "Starting NeuroBank FastAPI Server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
