from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

# Configuración del esquema de seguridad
security = HTTPBearer()

def get_api_key() -> str:
    """Obtiene la API key desde las variables de entorno"""
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="API_KEY not configured"
        )
    return api_key

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verifica que la API key proporcionada sea válida
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        str: API key válida
        
    Raises:
        HTTPException: Si la API key no es válida
    """
    expected_api_key = get_api_key()
    
    if credentials.credentials != expected_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return credentials.credentials
