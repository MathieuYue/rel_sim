import os, json

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
        prompt_filled = prompt_filled.replace("{{action_options}}", action_options)
        return prompt_filled

    def info(self):
        return self.name