from pydantic import BaseModel

class SceneSchema(BaseModel):
    theme: str
    setting: str
    NPC: list[str]
    current_scene: str
    previous_summary: str

class ActionSchema(BaseModel):
    narrative: str
    choices: list[str]
    character_name: str

class ConversationSchema(BaseModel):
    narrative: str
    first_character_to_speak: str