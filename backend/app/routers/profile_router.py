from fastapi import APIRouter, Depends
from typing import Dict
from ..models.schemas import UserProfile
from ..networks.exceptions import ProfileException
from ..dependencies import common_params

router = APIRouter(prefix="/api/profile", tags=["profile"])

# In-memory storage for user profiles
profiles: Dict[str, UserProfile] = {}

@router.get("/{user_id}", response_model=UserProfile)
async def get_profile(
    user_id: str,
    commons: Dict = Depends(common_params)
) -> UserProfile:
    """Get user profile by ID."""
    # Verify user can only access their own profile
    if user_id != commons["user_id"]:
        raise ProfileException("You can only access your own profile")
        
    if user_id not in profiles:
        raise ProfileException(f"Profile not found for user {user_id}")
    return profiles[user_id]

@router.put("/{user_id}", response_model=UserProfile)
async def update_profile(
    user_id: str,
    profile: UserProfile,
    commons: Dict = Depends(common_params)
) -> UserProfile:
    """Update or create user profile."""
    # Verify user can only update their own profile
    if user_id != commons["user_id"]:
        raise ProfileException("You can only update your own profile")
        
    profiles[user_id] = profile
    return profile

@router.delete("/{user_id}")
async def delete_profile(
    user_id: str,
    commons: Dict = Depends(common_params)
) -> dict:
    """Delete user profile."""
    # Verify user can only delete their own profile
    if user_id != commons["user_id"]:
        raise ProfileException("You can only delete your own profile")
        
    if user_id not in profiles:
        raise ProfileException(f"Profile not found for user {user_id}")
    del profiles[user_id]
    return {"message": "Profile deleted successfully"}