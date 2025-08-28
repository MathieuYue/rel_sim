from pydantic import BaseModel

class SceneSchema(BaseModel):
    theme: str
    setting: str
    NPC: list[str]
    current_scene: str
    previous_summary: str
    character_1_goal: str
    character_2_goal: str
    scene_conflict: str

class ActionSchema(BaseModel):
    narrative: str
    character_uuid: str

class ConversationSchema(BaseModel):
    narrative: str
    first_character_to_speak: str

class SceneSummarySchema(BaseModel):
    summary: str