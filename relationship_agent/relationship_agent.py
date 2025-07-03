import os, json
from utils.llm_utils import model_call_unstructured, model_call_structured
import relationship_agent.agent_utils as agent_utils
from relationship_agent.schemas import AgentActionSchema

class RelationshipAgent():
    def __init__(self, name, personality) -> None:
        self.name = name
        self.personality = personality

    def act(self, scene_history, action_question, action_options):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "action.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt_filled = prompt.replace("{{agent_name}}", self.name)
        prompt_filled = prompt_filled.replace("{{agent_personality}}", self.personality)
        prompt_filled = prompt_filled.replace("{{scene_history}}", scene_history)
        prompt_filled = prompt_filled.replace("{{action_question}}", action_question)

        options_str = agent_utils.list_to_indexed_string(action_options)
        prompt_filled = prompt_filled.replace("{{action_options}}", options_str)

        response = model_call_structured(prompt_filled, "", AgentActionSchema)
        if response is not None:
            print(response)
        return prompt_filled

    def info(self):
        return self.name