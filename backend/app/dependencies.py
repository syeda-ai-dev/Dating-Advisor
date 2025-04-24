from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

from .config import get_settings
from .networks.exceptions import AuthenticationException, RateLimitException

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simple in-memory rate limiting store
rate_limit_store: Dict[str, Dict] = {}

def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on IP address."""
    return request.client.host if request.client else "unknown"

async def check_rate_limit(request: Request):
    """Rate limiting middleware."""
    key = get_rate_limit_key(request)
    now = time.time()
    
    if key in rate_limit_store:
        # Clean old requests
        rate_limit_store[key]["requests"] = [
            req_time for req_time in rate_limit_store[key]["requests"]
            if now - req_time < settings.RATE_LIMIT_PERIOD
        ]
        
        # Check limit
        if len(rate_limit_store[key]["requests"]) >= settings.RATE_LIMIT_REQUESTS:
            raise RateLimitException()
        
        rate_limit_store[key]["requests"].append(now)
    else:
        rate_limit_store[key] = {"requests": [now]}

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Validate JWT token and return user_id."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationException()
    except JWTError:
        raise AuthenticationException()
        
    return user_id

# Common dependencies for routes
async def common_params(
    request: Request,
    current_user: str = Depends(get_current_user)
) -> Dict:
    """Common parameters and checks for routes."""
    await check_rate_limit(request)
    return {"user_id": current_user}