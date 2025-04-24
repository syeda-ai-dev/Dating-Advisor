from fastapi import HTTPException
from typing import Any, Optional

class BaseAPIException(HTTPException):
    """Base exception for API errors."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = "ERROR",
        headers: Optional[dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code

class ChatException(BaseAPIException):
    """Exception for chat-related errors."""
    def __init__(self, detail: str, code: str = "CHAT_ERROR"):
        super().__init__(status_code=400, detail=detail, code=code)

class ProfileException(BaseAPIException):
    """Exception for profile-related errors."""
    def __init__(self, detail: str, code: str = "PROFILE_ERROR"):
        super().__init__(status_code=400, detail=detail, code=code)

class ConfigException(BaseAPIException):
    """Exception for configuration-related errors."""
    def __init__(self, detail: str, code: str = "CONFIG_ERROR"):
        super().__init__(status_code=500, detail=detail, code=code)

class AuthenticationException(BaseAPIException):
    """Exception for authentication-related errors."""
    def __init__(self, detail: str = "Not authenticated", code: str = "AUTH_ERROR"):
        super().__init__(status_code=401, detail=detail, code=code)

class RateLimitException(BaseAPIException):
    """Exception for rate limiting errors."""
    def __init__(self, detail: str = "Rate limit exceeded", code: str = "RATE_LIMIT_ERROR"):
        super().__init__(status_code=429, detail=detail, code=code)