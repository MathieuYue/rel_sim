def print_separator():
    print("------------------------------------------------------------------------------")

def print_formatted(source, output_str):
    if source == 0:
        color = '\033[91m'
    elif source == 1:
        color = '\033[92m'
    else:
        color = '\033[94m'
    print(f'{color}{output_str}\033[0m')

def print_scene_separator(scene_ind):
    print(f'-------------------------------- SCENE {scene_ind} --------------------------------')

    # INSERT_YOUR_CODE
def combine_narrative_action(narrative, agent_name, action):
    """
    Combines a narrative and an agent's action into a single formatted string.

    Args:
        narrative (str): The narrative string.
        agent_name (str): The name of the agent performing the action.
        action (str): The action string.

    Returns:
        str: Combined string in the format:
             "Narrative: <narrative>. <Agent_name>: <action>"
    """
    return f"Narrative: {narrative}. {agent_name}: {action}"
