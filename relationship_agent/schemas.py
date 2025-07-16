from pydantic import BaseModel

from pydantic import BaseModel, Field
from typing import List, Optional


class AgentActionSchema(BaseModel):
    action_index: int
    line: str

class ReflectionSchema(BaseModel):
    emotional_reaction_summary: str
    change_in_trust: int
    change_in_resentment: int
    mood_change: List[str] = Field(..., description="The agent's current emotional tone or general affective state.")
    memory_log_entry: List[str] = Field(..., description="New emotionally salient moments (positive or negative) that influence future trust, resentment, and decisions.")