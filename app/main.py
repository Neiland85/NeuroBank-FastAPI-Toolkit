from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import operator
from .utils.logging import init_logging

init_logging()

app = FastAPI(
    title="Operator API",
    version="0.1.0",
    description="Backend de operadores reales (FASE 2)"
)

# CORS (ajusta origins según tu caso)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(operator.router, prefix="/operator", tags=["Operator"])

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
