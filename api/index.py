import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for production
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault(
    "SECRET_KEY", os.environ.get("SECRET_KEY", "vercel-production-key-change-in-env")
)

# Import the FastAPI app
from app.main import app

# Vercel expects the app to be named 'app'
# If your FastAPI app is named differently, change this
app = app


# Optional: Add Vercel-specific middleware or configuration
@app.middleware("http")
async def add_vercel_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Vercel-Cache"] = "MISS"
    return response


# Health check endpoint for Vercel
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "platform": "vercel", "app": "NeuroBank FastAPI"}


# For local development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
