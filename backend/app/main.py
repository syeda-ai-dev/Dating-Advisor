from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .routers import chat_router, profile_router, matches_router
from .networks.handlers import exception_handlers
from .networks.exceptions import (
    BaseAPIException, 
    ChatException,
    ProfileException,
    AuthenticationException,
    RateLimitException
)
from .config import get_settings
from .dependencies import check_rate_limit
import time
from starlette.middleware.base import BaseHTTPMiddleware

settings = get_settings()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        await check_rate_limit(request)
        return await call_next(request)

app = FastAPI(
    title="Date Mate API",
    description="Dating advisor and matchmaking API",
    version="1.0.0",
)

# Add middleware
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.APP_ENV == "development" else ["api.datemate.com"]
)

# Add exception handlers
for exc, handler in exception_handlers.items():
    app.add_exception_handler(exc, handler)

# Include routers
app.include_router(chat_router.router)
app.include_router(profile_router.router)
app.include_router(matches_router.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }