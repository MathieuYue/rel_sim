import json
import os
from jinja2 import Template

def load_name_and_personality(agent_json_path):
    """
    Loads the first name and personality from a sample_agents json file.

    Args:
        agent_json_path (str): Path to the agent's basics.json file.

    Returns:
        tuple: (name, personality) where name is the first name from the file.
    """
    with open(agent_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    name = data.get("first_name")
    personality = data.get("personality")
    return (name, personality)

def render_j2_template(template_content, context_dict):
    template = Template(template_content)
    return template.render(**context_dict)

