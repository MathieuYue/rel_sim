from scene_master.schemas.scene_schema import SceneSchema, ActionSchema, ConversationSchema, SceneSummarySchema
import utils.general_utils as general_utils
from utils.llm_utils import model_call_structured, model_call_unstructured, parse_model_json, model_call_structured_async, model_call_unstructured_async
import json
import json5
import os
import scene_master.scene_utils as scene_utils
from relationship_agent.agent_utils import render_j2_template


class SceneMaster():
    def __init__(self, agent_1, agent_2) -> None:

        turningpoint_order_path = os.path.join(os.path.dirname(__file__), "turningpoint_order.txt")
        with open(turningpoint_order_path, "r", encoding="utf-8") as f:
            self.turningpoint_order = [line.strip() for line in f if line.strip()]

        self.json_schemas = {}

        self.prompts = general_utils.read_all_j2_prompts(os.path.join(os.path.dirname(__file__), "prompts"))

        schemas_dir = os.path.join(os.path.dirname(__file__), "json_schemas")
        if os.path.isdir(schemas_dir):
            for filename in os.listdir(schemas_dir):
                if filename.endswith(".json"):
                    schema_path = os.path.join(schemas_dir, filename)
                    with open(schema_path, "r", encoding="utf-8") as f:
                        try:
                            self.json_schemas[filename] = json5.load(f)
                        except Exception as e:
                            print(f"Error loading {filename}: {e}")

        self.scene_state = SceneSchema(
            theme="relationship_development",
            setting="",
            NPC=[],
            current_scene="",
            previous_summary="",
            character_1_goal="",
            character_2_goal="",
            scene_conflict=""
        )

        self.scene_history = []
        self.progression = 0
        # if scene_template_path:
        #     if os.path.isdir(scene_template_path):
        #         ledger_path = os.path.join(scene_template_path, "initial_state.json")
        #         scenes_path = os.path.join(scene_template_path, "scenes.json")
        #     else:
        #         ledger_path = scene_template_path
        #         scenes_path = scene_template_path
        #     with open(ledger_path, encoding="utf-8") as json_file:
        #         self.scene_state = SceneSchema(**json5.load(json_file))
        #     with open(scenes_path, encoding="utf-8") as json_file:
        #         scenes = json5.load(json_file)
        #         self.scenes_array = scene_utils.scenes_to_array(scenes)
        # self.total_scenes = len(self.scenes_array)
        self.total_scenes = len(self.turningpoint_order)
        self.agent_1 = agent_1
        self.agent_2 = agent_2
        

    def initialize(self):
        # INSERT_YOUR_CODE
        turning_points_path = os.path.join(os.path.dirname(__file__), "turing_points.json")
        with open(turning_points_path, "r", encoding="utf-8") as f:
            turning_points = json5.load(f)
        
        template_content = self.prompts['initialize.j2']

        state = self.scene_state.model_dump_json(indent=2)

        # eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        tp_type = self.turningpoint_order[self.progression]

        eligible_scenes = scene_utils.find_scenarios_by_category(turning_points, tp_type)

        context_dict = {
            "scene_state": state,
            "eligible_scenes": eligible_scenes,
            "partner_1": self.agent_1.description,
            "partner_2": self.agent_2.description
        }

        prompt = render_j2_template(template_content, context_dict)
        response = model_call_unstructured('', user_message=prompt)
        response_json = parse_model_json(response)
        if isinstance(response_json, dict):
            self.scene_state = SceneSchema(**response_json)
            self.agent_1.set_goal(self.scene_state.character_1_goal)
            self.agent_2.set_goal(self.scene_state.character_2_goal)
            return self.scene_state
        else:
            raise ValueError("Response could not be converted to SceneSchema")

    async def initialize_async(self):
        # INSERT_YOUR_CODE
        turning_points_path = os.path.join(os.path.dirname(__file__), "turing_points.json")
        with open(turning_points_path, "r", encoding="utf-8") as f:
            turning_points = json5.load(f)
        
        template_content = self.prompts['initialize.j2']

        state = self.scene_state.model_dump_json(indent=2)

        # eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        tp_type = self.turningpoint_order[self.progression]

        eligible_scenes = scene_utils.find_scenarios_by_category(turning_points, tp_type)

        context_dict = {
            "scene_state": state,
            "eligible_scenes": eligible_scenes,
            "partner_1": self.agent_1.description,
            "partner_2": self.agent_2.description
        }

        prompt = render_j2_template(template_content, context_dict)
        response = await model_call_unstructured_async('', user_message=prompt)
        response_json = parse_model_json(response)
        if isinstance(response_json, dict):
            self.scene_state = SceneSchema(**response_json)
            self.agent_1.set_goal(self.scene_state.character_1_goal)
            self.agent_2.set_goal(self.scene_state.character_2_goal)
            return self.scene_state
        else:
            raise ValueError("Response could not be converted to SceneSchema")

    
    def generate_context(self):
    # INSERT_YOUR_CODE
        template_path = os.path.join(os.path.dirname(__file__), "prompts", "next_context.j2")
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        context = {
            "agent_1_information": self.agent_1.agent_state,
            "agent_1_emotion_state": self.agent_1.emotion_state,
            "agent_2_information": self.agent_2.agent_state,
            "agent_2_emotion_state": self.agent_2.emotion_state,
            "conversation_history": self.scene_history,
            "setting": self.scene_state
        }

        prompt = render_j2_template(template_str, context)

        response = model_call_unstructured('', prompt)
        return response

    async def generate_context_async(self):
    # INSERT_YOUR_CODE
        template_path = os.path.join(os.path.dirname(__file__), "prompts", "next_context.j2")
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        context = {
            "agent_1_information": self.agent_1.agent_state,
            "agent_1_emotion_state": self.agent_1.emotion_state,
            "agent_2_information": self.agent_2.agent_state,
            "agent_2_emotion_state": self.agent_2.emotion_state,
            "conversation_history": self.scene_history,
            "setting": self.scene_state
        }

        prompt = render_j2_template(template_str, context)

        response = await model_call_unstructured_async('', prompt)
        return response

    def progress(self):
        template_content = self.prompts['progress_narrative.j2']

        state = self.scene_state.model_dump_json(indent=2)

        context_dict = {
            "partner_1": self.agent_1.description,
            "partner_2": self.agent_2.description,
            "scene_history": general_utils.history_to_str(self.scene_history),
            "scene_conflict": self.scene_state.scene_conflict
        }

        prompt = render_j2_template(template_content, context_dict)
        response = model_call_unstructured('', prompt)
        try:
            response_json = parse_model_json(response)
        except json.JSONDecodeError as e:
            print(prompt)
            print(response)
            raise ValueError(f"Failed to parse model response as JSON: {e}\nRaw response:\n{response}")
        try:
            return ActionSchema(**response_json)
        except Exception as e:
            print(f"Error creating ActionSchema: {e}")
            print(f"Raw response_json: {response_json}")
            raise

    async def progress_async(self):
        template_content = self.prompts['progress_narrative.j2']

        state = self.scene_state.model_dump_json(indent=2)

        context_dict = {
            "partner_1": self.agent_1.description,
            "partner_2": self.agent_2.description,
            "scene_history": general_utils.history_to_str(self.scene_history),
            "scene_conflict": self.scene_state.scene_conflict
        }

        prompt = render_j2_template(template_content, context_dict)
        response = await model_call_unstructured_async('', prompt)
        try:
            response_json = parse_model_json(response)
        except json.JSONDecodeError as e:
            print(prompt)
            print(response)
            raise ValueError(f"Failed to parse model response as JSON: {e}\nRaw response:\n{response}")
        try:
            return ActionSchema(**response_json)
        except Exception as e:
            print(f"Error creating ActionSchema: {e}")
            print(f"Raw response_json: {response_json}")
            raise

    def append_to_history(self, type, action):
        source = ""
        if type == 0:
            source = "Narrative"
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
        
        # response = model_call_structured(user_message=prompt_filled, output_format=self.json_schemas["summary_schema.json"], model = 'qwen3-32b-fp8')
        response = model_call_unstructured('', prompt_filled)
        response_json = parse_model_json(response)
        if isinstance(response_json, dict):
            return SceneSummarySchema(**response_json)
        else:
            raise ValueError("Response could not be converted to SummarySchema")

    async def summarize_async(self):
        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "update_state.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        state = self.scene_state.model_dump_json(indent=2)
        prompt_filled = prompt.replace("{{scene_state}}", state)
        scene_hist_str = general_utils.history_to_str(self.scene_history)
        prompt_filled = prompt_filled.replace("{{scene_history}}", scene_hist_str)
        
        # response = model_call_structured(user_message=prompt_filled, output_format=self.json_schemas["summary_schema.json"], model = 'qwen3-32b-fp8')
        response = await model_call_unstructured_async('', prompt_filled)
        response_json = parse_model_json(response)
        if isinstance(response_json, dict):
            return SceneSummarySchema(**response_json)
        else:
            raise ValueError("Response could not be converted to SummarySchema")
        
    def commitment_score(self, summary):
        template_content = self.prompts['commitment.j2']
        context_dict = {
            "relationship_context": self.scene_history
        }
        prompt = render_j2_template(template_content, context_dict)
        response = model_call_unstructured('', prompt)
        print(response)
        response_json = parse_model_json(response)
        return response_json

    async def commitment_score_async(self, summary):
        template_content = self.prompts['commitment.j2']
        context_dict = {
            "relationship_context": self.scene_history
        }
        prompt = render_j2_template(template_content, context_dict)
        response = await model_call_unstructured_async('', prompt)
        print(response)
        response_json = parse_model_json(response)
        return response_json

    # def next_scene(self):
    #     self.scene_state.current_scene = ''
    #     self.scene_state.scene_conflict = ''
    #     self.scene_state.character_1_goal = ''
    #     self.scene_state.character_2_goal = ''
    #     self.scene_history = []
    #     self.progression += 1
    #     prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "next_scene.txt")
    #     with open(prompt_path, "r", encoding="utf-8") as f:
    #         prompt = f.read()
    #     state = self.scene_state.model_dump_json(indent=2)
    #     prompt_filled = prompt.replace("{{scene_state}}", state)
    #     prompt_filled = prompt_filled.replace("{{agent_1}}", self.agent_1.description)
    #     prompt_filled = prompt_filled.replace("{{agent_2}}", self.agent_2.description)
    #     eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
    #     prompt_filled = prompt_filled.replace("{{eligible_scenes}}", eligible_scenes)

    #     response = model_call_structured(user_message=prompt_filled, output_format=self.json_schemas["scene_schema.json"], model = 'qwen3-32b-fp8')
    #     response_json = json5.loads(response)
    #     if isinstance(response_json, dict):
    #         self.scene_state = SceneSchema(**response_json)
    #         self.agent_1.set_goal(self.scene_state.character_1_goal)
    #         self.agent_2.set_goal(self.scene_state.character_2_goal)
    #         return self.scene_state
    #     else:
    #         raise ValueError("Response could not be converted to SummarySchema")


    def next_scene(self):
        self.scene_state.current_scene = ''
        self.scene_state.scene_conflict = ''
        self.scene_state.character_1_goal = ''
        self.scene_state.character_2_goal = ''
        self.scene_history = []
        self.progression += 1

        turning_points_path = os.path.join(os.path.dirname(__file__), "turing_points.json")
        with open(turning_points_path, "r", encoding="utf-8") as f:
            turning_points = json5.load(f)
        
        template_content = self.prompts['next_scene.j2']

        state = self.scene_state.model_dump_json(indent=2)

        # eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        tp_type = self.turningpoint_order[self.progression]

        eligible_scenes = scene_utils.find_scenarios_by_category(turning_points, tp_type)

        context_dict = {
            "scene_state": state,
            "eligible_scenes": eligible_scenes,
            "partner_1": self.agent_1.description,
            "partner_2": self.agent_2.description
        }

        prompt = render_j2_template(template_content, context_dict)

        print(prompt)

        response = model_call_unstructured('', user_message=prompt)
        print(response)
        response_json = parse_model_json(response)
        if isinstance(response_json, dict):
            self.scene_state = SceneSchema(**response_json)
            self.agent_1.set_goal(self.scene_state.character_1_goal)
            self.agent_2.set_goal(self.scene_state.character_2_goal)
            return self.scene_state
        else:
            raise ValueError("Response could not be converted to SceneSchema")

    async def next_scene_async(self):
        self.scene_state.current_scene = ''
        self.scene_state.scene_conflict = ''
        self.scene_state.character_1_goal = ''
        self.scene_state.character_2_goal = ''
        self.scene_history = []
        self.progression += 1

        turning_points_path = os.path.join(os.path.dirname(__file__), "turing_points.json")
        with open(turning_points_path, "r", encoding="utf-8") as f:
            turning_points = json5.load(f)
        
        template_content = self.prompts['next_scene.j2']

        state = self.scene_state.model_dump_json(indent=2)

        # eligible_scenes = scene_utils.list_to_string(self.scenes_array[self.progression])
        tp_type = self.turningpoint_order[self.progression]

        eligible_scenes = scene_utils.find_scenarios_by_category(turning_points, tp_type)

        context_dict = {
            "scene_state": state,
            "eligible_scenes": eligible_scenes,
            "partner_1": self.agent_1.description,
            "partner_2": self.agent_2.description
        }

        prompt = render_j2_template(template_content, context_dict)

        print(prompt)

        response = await model_call_unstructured_async('', user_message=prompt)
        print(response)
        response_json = parse_model_json(response)
        if isinstance(response_json, dict):
            self.scene_state = SceneSchema(**response_json)
            self.agent_1.set_goal(self.scene_state.character_1_goal)
            self.agent_2.set_goal(self.scene_state.character_2_goal)
            return self.scene_state
        else:
            raise ValueError("Response could not be converted to SceneSchema")
