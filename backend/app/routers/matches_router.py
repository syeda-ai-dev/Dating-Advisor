from fastapi import APIRouter, Depends
from typing import List, Dict
from ..models.schemas import UserProfile
from ..networks.exceptions import ProfileException
from ..dependencies import common_params
from .profile_router import profiles

router = APIRouter(prefix="/api/matches", tags=["matches"])

def calculate_match_score(user_profile: UserProfile, potential_match: UserProfile) -> float:
    """Calculate compatibility score between two profiles."""
    score = 0.0
    total_weights = 0
    
    # Common interests and hobbies (weight: 3)
    common_hobbies = set(user_profile.hobbies) & set(potential_match.hobbies)
    score += len(common_hobbies) * 3
    total_weights += len(user_profile.hobbies) * 3 if user_profile.hobbies else 0
    
    # Matching relationship goals (weight: 5)
    if user_profile.relationship_goals == potential_match.relationship_goals:
        score += 5
    total_weights += 5
    
    # Common values (weight: 4)
    common_values = set(user_profile.values) & set(potential_match.values)
    score += len(common_values) * 4
    total_weights += len(user_profile.values) * 4 if user_profile.values else 0
    
    # Language match (weight: 2)
    common_languages = set(user_profile.languages) & set(potential_match.languages)
    score += len(common_languages) * 2
    total_weights += len(user_profile.languages) * 2 if user_profile.languages else 0
    
    # Communication style and love language (weight: 3)
    if user_profile.communication_style == potential_match.communication_style:
        score += 3
    if user_profile.love_language == potential_match.love_language:
        score += 3
    total_weights += 6
    
    # Normalize score to percentage
    return (score / total_weights) * 100 if total_weights > 0 else 0

@router.get("/{user_id}", response_model=List[Dict])
async def get_matches(
    user_id: str,
    min_score: float = 50.0,
    limit: int = 10,
    commons: Dict = Depends(common_params)
) -> List[Dict]:
    """Get potential matches for a user."""
    # Verify user can only get their own matches
    if user_id != commons["user_id"]:
        raise ProfileException("You can only get matches for your own profile")
    
    if user_id not in profiles:
        raise ProfileException(f"Profile not found for user {user_id}")
    
    user_profile = profiles[user_id]
    matches = []
    
    for match_id, match_profile in profiles.items():
        if match_id == user_id:
            continue
            
        # Check if the match's gender is in user's interested_in list
        if (match_profile.gender not in user_profile.interested_in or 
            user_profile.gender not in match_profile.interested_in):
            continue
            
        # Calculate match score
        score = calculate_match_score(user_profile, match_profile)
        
        if score >= min_score:
            # Filter out sensitive information
            safe_profile = match_profile.dict(
                exclude={'deal_breakers', 'values'}
            )
            matches.append({
                "user_id": match_id,
                "profile": safe_profile,
                "match_score": round(score, 2)
            })
    
    # Sort matches by score and limit results
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches[:limit]