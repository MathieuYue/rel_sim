import os, json
from utils.llm_utils import model_call_unstructured, model_call_structured
import utils.general_utils as general_utils
import relationship_agent.agent_utils as agent_utils
from relationship_agent.schemas import AgentActionSchema

class RelationshipAgent():
    def __init__(self, name, personality, agent_id) -> None:
        info_path = os.path.join(os.path.dirname(__file__), "prompts", "agent_info.txt")
        with open(info_path, "r", encoding="utf-8") as f:
            info = f.read()
        self.description = info.replace("{{agent_name}}", name)
        self.description = self.description.replace("{{agent_personality}}", personality)
        self.description = self.description.replace("{{agent_id}}", str(agent_id))

        self.name = name
        self.personality = personality
        self.agent_id = agent_id

    def act(self, scene_history, action_question, action_options):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "action.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt_filled = prompt.replace("{{agent_name}}", self.name)
        prompt_filled = prompt_filled.replace("{{agent_personality}}", self.personality)
        scene_hist_str = general_utils.history_to_str(scene_history)
        prompt_filled = prompt_filled.replace("{{scene_history}}", scene_hist_str)
        prompt_filled = prompt_filled.replace("{{action_question}}", action_question)

        options_str = general_utils.list_to_indexed_string(action_options)
        prompt_filled = prompt_filled.replace("{{action_options}}", options_str)

        response = model_call_structured(prompt_filled, "", AgentActionSchema)
        if isinstance(response, AgentActionSchema):
            return response
        elif isinstance(response, dict):
            return AgentActionSchema(**response)
        else:
            raise ValueError("Response could not be converted to ActionSchema")

    def set_goal(self, goal):
        self.description = self.description + "\n\nScene Goal:\n" + goal