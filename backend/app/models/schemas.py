from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserProfile(BaseModel):
    name: str
    age: int = Field(..., ge=18, le=99)
    gender: str
    interested_in: List[str]
    relationship_goals: str
    hobbies: List[str]
    personality_traits: List[str]
    ideal_partner_traits: List[str]
    deal_breakers: List[str]
    love_language: str
    communication_style: str
    life_goals: List[str]
    values: List[str]
    location: str
    languages: List[str]
    education: str
    occupation: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str
    user_id: str
    chat_mode: str = Field(..., regex='^(advisor|partner)$')

class ChatResponse(BaseModel):
    message: str
    chat_history: List[ChatMessage]

class ErrorResponse(BaseModel):
    detail: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.now)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"