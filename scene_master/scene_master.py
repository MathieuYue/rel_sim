from scene_master.schemas.scene_schema import SceneSchema, ActionSchema, ConversationSchema
from utils.llm_utils import model_call_unstructured, model_call_structured
import json
import os
import scene_master.scene_utils as scene_utils


class SceneMaster():
    def __init__(self, scene_template_path) -> None:
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

    def initialize(self, agent_1, agent_2):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "initialize.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()

        state = self.scene_state.model_dump_json(indent=2)
        eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        prompt_filled = prompt.replace("{{scene_state}}", state).replace("{{eligible_scenes}}", eligible_scenes)
        prompt_filled = prompt_filled.replace("{{partner_1}}", agent_1.info()).replace("{{partner_2}}", agent_2.info())
        response = model_call_structured(prompt_filled, "", SceneSchema)
        if response is not None:
            self.scene_state = response
        else:
            print("Error: model_call_structured returned None")
        action = ['Scene Master', self.scene_state.current_scene]
        print(action)
        self.scene_history.append(action)
        return response

    def progress(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "progress.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        scene_hist_str = scene_utils.history_to_str(self.scene_history)
        prompt_filled = prompt.replace("{{scene_history}}", scene_hist_str)

        response = model_call_structured(prompt_filled, '', ActionSchema)
        print(response)
        return response


    def get_state(self):
        return self.scene_state

