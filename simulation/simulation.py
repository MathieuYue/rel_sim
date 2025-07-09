from openai.types.responses.response_code_interpreter_tool_call import Output
from scene_master.scene_master import SceneMaster
from relationship_agent.relationship_agent import RelationshipAgent
import utils.general_utils as utils
from simulation_utils import print_separator, print_formatted, print_scene_separator
import os

class Simulation():
    def __init__(self, scene_master, agent_1, agent_2) -> None:
        self.scene_master = scene_master
        self.agent_1 = agent_1
        self.agent_2 = agent_2

    def run_auto(self, num_interactions_per_scene):
        # Setup
        sm_action = self.scene_master.initialize()
        self.scene_master.append_to_history(0, sm_action.current_scene)
        for scene_index in range(self.scene_master.total_scenes):
            print_scene_separator(scene_index + 1)
            self.run_scene(num_interactions_per_scene, sm_action)

    def run_scene(self, num_interactions, sm_action):
        print_formatted(0, "[Scene Master]")
        print_formatted(0, sm_action.current_scene)
        for action_index in range(num_interactions):
            print_separator()
            sm_action = self.scene_master.progress()
            self.scene_master.append_to_history(0, sm_action.narrative)
            # print("[Scene Master:]")
            print_formatted(0, "[Scene Master:]")
            # print(sm_action.narrative)
            print_formatted(0, sm_action.narrative)
            # print("Options: ")
            print_formatted(0, "Options: ")
            # print(utils.list_to_indexed_string_1_based(sm_action.choices))
            print_formatted(0, utils.list_to_indexed_string_1_based(sm_action.choices))
            print_separator()
            if sm_action.character_uuid == self.agent_1.agent_id:
                curr_agent = self.agent_1
                agent_ind = 1
            elif sm_action.character_uuid == self.agent_2.agent_id:
                curr_agent = self.agent_2
                agent_ind = 2
            agent_action = curr_agent.act(self.scene_master.scene_history, sm_action.narrative, sm_action.choices)
            self.scene_master.append_to_history(curr_agent, agent_action.line)
            print_formatted(agent_ind, "[" + curr_agent.name + "]")
            # print("[" + curr_agent.name + "]")
            print_formatted(agent_ind, "Chosen Action: " + sm_action.choices[agent_action.action_index])
            # print("Chosen Action: " + sm_action.choices[agent_action.action_index])
            print_formatted(agent_ind, agent_action.line)
            # print("Dialogue: " + agent_action.line)
    
