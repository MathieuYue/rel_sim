from pydantic import BaseModel

class AgentActionSchema(BaseModel):
    action_index: int