from fastapi import APIRouter, Depends
from typing import Dict
from ..models.schemas import ChatRequest, ChatResponse, ChatMessage
from ..models.chat import ChatState
from ..networks.exceptions import ChatException
from ..config import get_settings
from ..dependencies import common_params
import httpx
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])
settings = get_settings()

# In-memory storage for chat states
chat_states: Dict[str, ChatState] = {}

async def get_groq_response(messages: list, api_key: str) -> str:
    """Get response from Groq API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.groq.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise ChatException(f"Failed to get response from Groq: {str(e)}")

def get_chat_state(user_id: str) -> ChatState:
    """Get or create chat state for user."""
    if user_id not in chat_states:
        chat_states[user_id] = ChatState(user_id=user_id)
    return chat_states[user_id]

@router.post("/advisor", response_model=ChatResponse)
async def chat_with_advisor(
    request: ChatRequest,
    commons: Dict = Depends(common_params)
) -> ChatResponse:
    """Chat with the dating advisor AI."""
    chat_state = get_chat_state(commons["user_id"])
    
    # Add user message to history
    chat_state.add_message("user", request.message)
    
    # Prepare context for advisor mode
    system_message = {
        "role": "system",
        "content": "You are an expert dating advisor helping users navigate relationships and dating."
    }
    
    messages = [system_message] + chat_state.get_messages()
    
    # Get response from Groq
    response = await get_groq_response(messages, settings.GROQ_API_KEY.get_secret_value())
    
    # Add AI response to history
    chat_state.add_message("assistant", response)
    
    return ChatResponse(
        message=response,
        chat_history=[ChatMessage(**msg) for msg in chat_state.get_messages()]
    )

@router.post("/partner", response_model=ChatResponse)
async def chat_with_partner(
    request: ChatRequest,
    commons: Dict = Depends(common_params)
) -> ChatResponse:
    """Chat with an AI simulating a potential dating partner."""
    chat_state = get_chat_state(commons["user_id"])
    
    # Add user message to history
    chat_state.add_message("user", request.message)
    
    # Prepare context for partner mode
    system_message = {
        "role": "system",
        "content": "You are simulating a potential dating partner engaging in conversation."
    }
    
    messages = [system_message] + chat_state.get_messages()
    
    # Get response from Groq
    response = await get_groq_response(messages, settings.GROQ_API_KEY.get_secret_value())
    
    # Add AI response to history
    chat_state.add_message("assistant", response)
    
    return ChatResponse(
        message=response,
        chat_history=[ChatMessage(**msg) for msg in chat_state.get_messages()]
    )