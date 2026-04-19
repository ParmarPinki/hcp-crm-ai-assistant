from typing import List, Optional

from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    id: Optional[int] = None
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[str] = None
    interaction_time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    materials_shared: List[str] = Field(default_factory=list)
    samples_distributed: List[str] = Field(default_factory=list)
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)


class InteractionResponse(InteractionCreate):
    id: int
    saved_at: str
