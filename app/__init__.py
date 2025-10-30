# NeuroBank FastAPI Toolkit

# Import models to ensure they are registered with SQLAlchemy metadata
# This must be done before database operations that use Base.metadata
from app import models  # noqa: F401
