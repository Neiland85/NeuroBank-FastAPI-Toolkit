#!/usr/bin/env python3
"""
Script simple para probar el servidor FastAPI
"""

import uvicorn
import sys
import os

# Añadir el directorio actual al PATH
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    print("🚀 Iniciando NeuroBank FastAPI Server...")
    print("📡 URL: http://localhost:8000")
    print("📊 Dashboard: http://localhost:8000/backoffice/")
    print("📖 Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)
