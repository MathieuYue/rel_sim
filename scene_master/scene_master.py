from scene_master.schemas.scene_schema import SceneSchema, ActionSchema, ConversationSchema, SceneSummarySchema
import utils.general_utils as general_utils
from utils.llm_utils import model_call_unstructured, model_call_structured
import json
import os
import scene_master.scene_utils as scene_utils


class SceneMaster():
    def __init__(self, scene_template_path, agent_1, agent_2) -> None:
        self.scene_history = []
        self.progression = 0
        if scene_template_path:
            if os.path.isdir(scene_template_path):
                ledger_path = os.path.join(scene_template_path, "initial_state.json")
                scenes_path = os.path.join(scene_template_path, "scenes.json")
            else:
                ledger_path = scene_template_path
                scenes_path = scene_template_path
            with open(ledger_path, encoding="utf-8") as json_file:
                self.scene_state = SceneSchema(**json.load(json_file))
            with open(scenes_path, encoding="utf-8") as json_file:
                scenes = json.load(json_file)
                self.scenes_array = scene_utils.scenes_to_array(scenes)
        self.total_scenes = len(self.scenes_array)
        self.agent_1 = agent_1
        self.agent_2 = agent_2

    def initialize(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "initialize.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()

        state = self.scene_state.model_dump_json(indent=2)
        eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        prompt_filled = prompt.replace("{{scene_state}}", state).replace("{{eligible_scenes}}", eligible_scenes)
        prompt_filled = prompt_filled.replace("{{partner_1}}", self.agent_1.description).replace("{{partner_2}}", self.agent_2.description)
        response = model_call_structured(prompt_filled, "", SceneSchema)
        if response is not None:
            self.scene_state = response
        else:
            print("Error: model_call_structured returned None")
        # self.append_to_history(0, self.scene_state.current_scene)
        self.agent_1.set_goal(self.scene_state.character_1_goal)
        self.agent_2.set_goal(self.scene_state.character_2_goal)
        return self.scene_state

    def progress(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "next_action.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        scene_hist_str = general_utils.history_to_str(self.scene_history)
        prompt_filled = prompt.replace("{{scene_history}}", scene_hist_str)
        prompt_filled = prompt_filled.replace("{{partner_1}}", self.agent_1.description).replace("{{partner_2}}", self.agent_2.description)
        response = model_call_structured(prompt_filled, '', ActionSchema)
        if isinstance(response, ActionSchema):
            return response
        elif isinstance(response, dict):
            return ActionSchema(**response)
        else:
            raise ValueError("Response could not be converted to ActionSchema")

    def append_to_history(self, type, action):
        source = ""
        if type == 0:
            source = "Scene Master"
        else:
            source = type.name
        self.scene_history.append([source, action])
        return [source, action]
    
    def summarize(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "update_state.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        state = self.scene_state.model_dump_json(indent=2)
        prompt_filled = prompt.replace("{{scene_state}}", state)
        scene_hist_str = general_utils.history_to_str(self.scene_history)
        prompt_filled = prompt_filled.replace("{{scene_history}}", scene_hist_str)
        
        response = model_call_structured(prompt_filled, '', SceneSummarySchema)
        if isinstance(response, SceneSummarySchema):
            self.scene_state.previous_summary = response.summmary
            return response
        elif isinstance(response, dict):
            return SceneSummarySchema(**response)
        else:
            raise ValueError("Response could not be converted to SceneSummarySchema")
        

    def next_scene(self):
        self.scene_state.current_scene = ''
        self.scene_history = []
        self.progression += 1
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "next_scene.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        state = self.scene_state.model_dump_json(indent=2)
        prompt_filled = prompt.replace("{{scene_state}}", state)
        prompt_filled = prompt_filled.replace("{{agent_1}}", self.agent_1.description)
        prompt_filled = prompt_filled.replace("{{agent_2}}", self.agent_2.description)
        eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        prompt_filled = prompt_filled.replace("{{eligible_scenes}}", eligible_scenes)
        response = model_call_structured(prompt_filled, '', SceneSchema)
        if isinstance(response, SceneSchema):
            self.scene_state = response
            self.agent_1.set_goal(self.scene_state.character_1_goal)
            self.agent_2.set_goal(self.scene_state.character_2_goal)
            return response
        else:
            raise ValueError("Response could not be converted to SceneSchema")
