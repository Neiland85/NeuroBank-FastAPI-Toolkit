"""
🔐 JWT Authentication Module for NeuroBank FastAPI Toolkit
Handles JWT token generation, validation, and management
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, cast

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError

from ..config import get_settings


class JWTManager:
    """JWT token management class"""

    def __init__(self):
        self.settings = get_settings()
        # Use API key as secret key or fallback to environment variable or default
        self.secret_key = (
            self.settings.api_key or 
            os.getenv("SECRET_KEY") or 
            os.getenv("JWT_SECRET_KEY") or 
            "your-secret-key-change-in-production"
        )
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def create_access_token(
        self, 
        data: Dict[str, Union[str, int]], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a new JWT access token
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        
        # Fix for ruff TC006: Add quotes to type expression in typing.cast()
        encoded_jwt = cast("str", jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm))
        
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Union[str, int]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dict: Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Fix for ruff TC006: Add quotes to type expression in typing.cast()
            payload = cast("Dict[str, Union[str, int]]", jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            ))
            return payload
            
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def create_refresh_token(self, data: Dict[str, Union[str, int]]) -> str:
        """
        Create a refresh token with longer expiration
        
        Args:
            data: Payload data to encode in the token
            
        Returns:
            str: Encoded refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh token
        to_encode.update({"exp": expire, "type": "refresh"})
        
        # Fix for ruff TC006: Add quotes to type expression in typing.cast()
        encoded_jwt = cast("str", jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm))
        
        return encoded_jwt

    def verify_refresh_token(self, token: str) -> Dict[str, Union[str, int]]:
        """
        Verify and decode a refresh token
        
        Args:
            token: Refresh token to verify
            
        Returns:
            Dict: Decoded token payload
            
        Raises:
            HTTPException: If token is invalid, expired, or not a refresh token
        """
        try:
            # Fix for ruff TC006: Add quotes to type expression in typing.cast()
            payload = cast("Dict[str, Union[str, int]]", jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            ))
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return payload
            
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global JWT manager instance
jwt_manager = JWTManager()


def create_access_token(data: Dict[str, Union[str, int]]) -> str:
    """Convenience function to create access token"""
    return jwt_manager.create_access_token(data)


def verify_token(token: str) -> Dict[str, Union[str, int]]:
    """Convenience function to verify token"""
    return jwt_manager.verify_token(token)


def create_refresh_token(data: Dict[str, Union[str, int]]) -> str:
    """Convenience function to create refresh token"""
    return jwt_manager.create_refresh_token(data)


def verify_refresh_token(token: str) -> Dict[str, Union[str, int]]:
    """Convenience function to verify refresh token"""
    return jwt_manager.verify_refresh_token(token)