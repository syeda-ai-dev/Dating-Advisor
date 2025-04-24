from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

from .exceptions import (
    BaseAPIException,
    ChatException,
    ProfileException,
    ConfigException,
    AuthenticationException,
    RateLimitException
)

async def base_exception_handler(
    request: Request,
    exc: BaseAPIException
) -> JSONResponse:
    """Handle custom API exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": exc.code,
            "timestamp": datetime.now().isoformat()
        }
    )

async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    )

# Map of exception handlers
exception_handlers: Dict[Any, Any] = {
    BaseAPIException: base_exception_handler,
    ChatException: base_exception_handler,
    ProfileException: base_exception_handler,
    ConfigException: base_exception_handler,
    AuthenticationException: base_exception_handler,
    RateLimitException: base_exception_handler,
    Exception: general_exception_handler
}