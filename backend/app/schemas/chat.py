from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_form: Dict[str, Any] = Field(default_factory=dict)
    chat_history: List[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    assistant_message: str
    tool_used: str
    form_patch: Dict[str, Any]
    suggestions: List[str] = Field(default_factory=list)
