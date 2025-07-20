import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()  # Carga variables de .env

API_KEY = os.getenv("API_KEY", "secret")

async def verify_api_key(x_api_key: str = Header(...)):
    """
    Verifica la API Key enviada en la cabecera 'X-API-Key'.
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida",
        )
