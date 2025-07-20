from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

# Configuración del esquema de seguridad
security = HTTPBearer(auto_error=False)

def get_api_key() -> str:
    """Obtiene la API key desde las variables de entorno"""
    if not (api_key := os.getenv("API_KEY")):
        raise ValueError("API_KEY environment variable is required")
    return api_key

def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    **Verifica que la API key proporcionada sea válida**
    
    Soporta dos métodos de autenticación:
    1. **Bearer Token**: Authorization: Bearer <api-key>  
    2. **X-API-Key Header**: X-API-Key: <api-key>
    
    Args:
        request: FastAPI request object
        credentials: Credenciales HTTP Bearer (opcional)
        
    Returns:
        str: API key válida
        
    Raises:
        HTTPException: Si la API key no es válida o está ausente
    """
    expected_api_key = get_api_key()
    provided_api_key = None
    
    # Método 1: Bearer Token
    if credentials and credentials.credentials:
        provided_api_key = credentials.credentials
    
    # Método 2: X-API-Key Header  
    elif "x-api-key" in request.headers:
        provided_api_key = request.headers["x-api-key"]
    
    # No se proporcionó API key
    if not provided_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Use 'Authorization: Bearer <key>' or 'X-API-Key: <key>'",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verificar la API key
    if provided_api_key != expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return provided_api_key
