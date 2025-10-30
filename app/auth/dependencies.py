import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models.user import User

# Configuración del esquema de seguridad
security = HTTPBearer(auto_error=False)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_api_key() -> str:
    """Obtiene la API key desde la configuración centralizada"""
    settings = get_settings()
    if not settings.api_key:
        raise ValueError("API_KEY environment variable is required")
    return settings.api_key


def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
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
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar la API key
    if provided_api_key != expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return provided_api_key


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token (should include user_id and role)
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token
    
    Extracts and validates JWT token from Authorization header,
    then retrieves the user from the database with their role information.
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
    
    Returns:
        User object with role information
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control
    
    Creates a dependency that checks if the current user has one of the allowed roles.
    
    Args:
        allowed_roles: Variable number of role names that are allowed
    
    Returns:
        Dependency function that validates user role
    
    Example:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint():
            return {"message": "Admin access granted"}
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


# Convenient role-specific dependencies
def admin_only(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires admin role"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def customer_only(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires customer role"""
    if current_user.role.name != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required"
        )
    return current_user


def auditor_only(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires auditor role"""
    if current_user.role.name != "auditor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditor access required"
        )
    return current_user
