import os, json
from utils.llm_utils import model_call_unstructured, model_call_structured
import utils.general_utils as general_utils
import relationship_agent.agent_utils as agent_utils
from relationship_agent.schemas import AgentActionSchema
import uuid
from relationship_agent.agent_utils import render_j2_template
from relationship_agent.memory import Memory

class RelationshipAgent():
    def __init__(self, agent_path) -> None:

        self.json_schemas = {}

        self.prompts = general_utils.read_all_j2_prompts(os.path.join(os.path.dirname(__file__), "prompts"))

        schemas_dir = os.path.join(os.path.dirname(__file__), "json_schemas")
        if os.path.isdir(schemas_dir):
            for filename in os.listdir(schemas_dir):
                if filename.endswith(".json"):
                    schema_path = os.path.join(schemas_dir, filename)
                    with open(schema_path, "r", encoding="utf-8") as f:
                        try:
                            self.json_schemas[filename] = json.load(f)
                        except Exception as e:
                            print(f"Error loading {filename}: {e}")

        with open(os.path.join(agent_path, "basics.json"), 'r', encoding='utf-8') as f:
            agent_data = json.load(f)

        self.memory = Memory()

        memory_path = os.path.join(agent_path, "memories.json")
        if os.path.exists(memory_path):
            self.memory.load_memory_store(memory_path)

        self.name = agent_data.get("first_name") + " " + agent_data.get("last_name")

        self.agent_id = str(uuid.uuid4())

        agent_data["agent_id"] = self.agent_id
        
        self.agent_state = agent_data
        self.emotion_state = []
        self.update_description()

    def add_to_working_memory(self, text, emotion_embedding=None, inner_thoughts=None, memory_type=None, agent=None):
        """
        Adds a memory item to the agent's working memory using all parameters of the Memory class.
        """
        self.memory.add_to_working_memory(
            text=text,
            emotion_embedding=emotion_embedding,
            inner_thoughts=inner_thoughts,
            memory_type=memory_type,
            agent=agent
        )

    def make_choices(self, current_narrative, inner_thoughts):
        template_content = self.prompts['make_choice.j2']

        # Prepare context for the template
        context_dict = {
            "agent_name": self.name,
            "internal_thought": inner_thoughts,
            "agent_persona": self.agent_state,
            "previous_narrative": self.memory.format_working_memory(),
            "current_narrative": current_narrative
        }

        prompt = render_j2_template(template_content, context_dict)
        response = model_call_unstructured('', prompt)
        self.emotion_state = json.loads(response)
        return self.emotion_state

    def act(self, scene_history, action_question, action_options):
        with open(os.path.join(os.path.dirname(__file__), "json_schemas", "agent_action_schema.json"), "r", encoding="utf-8") as f:
            agent_action_schema_json = json.load(f)
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "action.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt_filled = prompt.replace("{{agent_description}}", self.description)
        scene_hist_str = general_utils.history_to_str(scene_history)
        prompt_filled = prompt_filled.replace("{{scene_history}}", scene_hist_str)
        prompt_filled = prompt_filled.replace("{{action_question}}", action_question)

        options_str = general_utils.list_to_indexed_string(action_options)
        prompt_filled = prompt_filled.replace("{{action_options}}", options_str)
        prompt_filled = prompt_filled.replace("{{emotion_state}}", json.dumps(self.emotion_state))

        response = model_call_structured(user_message=prompt_filled, output_format=self.json_schemas["agent_action_schema.json"])
        response_json = json.loads(response)
        if isinstance(response_json, dict):
            return AgentActionSchema(**response_json)
        else:
            raise ValueError("Response could not be converted to AgentActionSchema")


    def reflect(self, scene_history):
        # Use the render_j2_template function to fill the reflection.j2 template with scene history
        template_content = self.prompts['reflection.j2']

        # Prepare context for the template
        context_dict = {
            "agent_information": self.agent_state,
            "context": "",  # You may want to add more context here if available
            "conversation_history": general_utils.history_to_str(scene_history)
        }

        prompt = render_j2_template(template_content, context_dict)
        
        response = model_call_unstructured('', prompt)
        self.emotion_state = json.loads(response)
        return self.emotion_state

    def appraise(self, scene_history):
        template_content = self.prompts['emotion_appraisal.j2']

        context_dict = {
            "agent_information": self.agent_state,
            "context": "",
            "conversation_history": general_utils.history_to_str(scene_history)
        }

        prompt = render_j2_template(template_content, context_dict)

        response = model_call_unstructured('', prompt)
        self.emotion_state = json.loads(response)
        return self.emotion_state

    def set_goal(self, goal):
        self.agent_state["goal"] = goal
        self.update_description()

    def update_description(self):
        self.description = json.dumps(self.agent_state)