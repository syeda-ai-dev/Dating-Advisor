import httpx
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables in development
if os.getenv("APP_ENV") == "development":
    load_dotenv()

class APIClient:
    """Client for communicating with the backend API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to API with error handling."""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                error_msg = f"API request failed: {str(e)}"
                if response := getattr(e, "response", None):
                    try:
                        error_msg = response.json().get("detail", error_msg)
                    except:
                        pass
                raise APIError(error_msg)

    # Chat endpoints
    async def chat_with_advisor(self, message: str, user_id: str) -> Dict:
        """Send message to chat advisor."""
        return await self._make_request(
            "POST",
            "/api/chat/advisor",
            data={"message": message, "user_id": user_id, "chat_mode": "advisor"}
        )

    async def chat_with_partner(self, message: str, user_id: str) -> Dict:
        """Send message to partner simulation."""
        return await self._make_request(
            "POST",
            "/api/chat/partner",
            data={"message": message, "user_id": user_id, "chat_mode": "partner"}
        )

    # Profile endpoints
    async def get_profile(self, user_id: str) -> Dict:
        """Get user profile."""
        return await self._make_request("GET", f"/api/profile/{user_id}")

    async def update_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """Update user profile."""
        return await self._make_request(
            "PUT",
            f"/api/profile/{user_id}",
            data=profile_data
        )

    # Matches endpoints
    async def get_matches(
        self,
        user_id: str,
        min_score: float = 50.0,
        limit: int = 10
    ) -> List[Dict]:
        """Get potential matches for user."""
        return await self._make_request(
            "GET",
            f"/api/matches/{user_id}",
            params={"min_score": min_score, "limit": limit}
        )

class APIError(Exception):
    """Custom exception for API-related errors."""
    pass