from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class ChatState:
    """Chat state for managing conversations."""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: str = ""
    last_updated: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        self.last_updated = datetime.now()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the chat history."""
        return self.messages

    def clear_history(self) -> None:
        """Clear the chat history."""
        self.messages = []
        self.last_updated = datetime.now()