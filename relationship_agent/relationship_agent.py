import os, json
from utils.llm_utils import model_call_unstructured, model_call_structured
import utils.general_utils as general_utils
import relationship_agent.agent_utils as agent_utils
from relationship_agent.schemas import AgentActionSchema
import uuid

class RelationshipAgent():
    def __init__(self, agent_json_path) -> None:
        with open(agent_json_path, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)

        self.name = agent_data.get("first_name") + " " + agent_data.get("last_name")
        self.agent_id = str(uuid.uuid4())
        agent_data["agent_id"] = self.agent_id
        
        info_path = os.path.join(os.path.dirname(__file__), "prompts", "agent_info.txt")
        # with open(info_path, "r", encoding="utf-8") as f:
        #     info = f.read()
        # self.description = info.replace("{{agent_name}}", self.)
        # self.description = self.description.replace("{{agent_personality}}", personality)
        # self.description = self.description.replace("{{agent_id}}", str(self.agent_id))
        self.agent_state = agent_data
        self.update_description()
        

    def act(self, scene_history, action_question, action_options):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "action.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt_filled = prompt.replace("{{agent_description}}", self.description)
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
        self.agent_state["goal"] = goal
        self.update_description()

    def update_description(self):
        self.description = json.dumps(self.agent_state)