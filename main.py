from scene_master.scene_master import SceneMaster
from relationship_agent.relationship_agent import RelationshipAgent
import uuid
import utils.general_utils as utils
import os

agent_1_path = os.path.join("sample_agents", "ryan_reynolds", "basics.json")
agent_2_path = os.path.join("sample_agents", "blake_lively", "basics.json")


agent_1 = RelationshipAgent(agent_1_path)
agent_2 = RelationshipAgent(agent_2_path)

sm = SceneMaster("scene_templates/vacation", agent_1, agent_2)
sys_action = sm.initialize()
sm.append_to_history(0, sys_action.current_scene)
for scene_index in range(sm.total_scenes):
    print("[Scene Master]:")
    print(sys_action.current_scene)
    for action_index in range(2):
        print("------------------------------------------------------")
        sys_action = sm.progress()
        sm.append_to_history(0, sys_action.narrative)
        print("[Scene Master:]")
        print(sys_action.narrative)
        print("Options: ")
        print(utils.list_to_indexed_string_1_based(sys_action.choices))
        print("------------------------------------------------------")
        if sys_action.character_uuid == agent_1.agent_id:
            curr_agent = agent_1
        elif sys_action.character_uuid == agent_2.agent_id:
            curr_agent = agent_2
        agent_action = curr_agent.act(sm.scene_history, sys_action.narrative, sys_action.choices)
        sm.append_to_history(curr_agent, agent_action.line)
        print("[" + curr_agent.name + "]")
        print("Chosen Action: " + sys_action.choices[agent_action.action_index])
        print("Dialogue: " + agent_action.line)
    sm.summarize()
    sys_action = sm.generate_next()


# def get_info():
#     print("-----------------------------------------------------SCENE HISTORY-----------------------------------------------------")
#     print(utils.history_to_str(sm.scene_history))
#     print("-----------------------------------------------------SCENE STATE-----------------------------------------------------")
#     print(sm.scene_state)
#     print("-----------------------------------------------------AGENT 1-----------------------------------------------------")
#     print(agent_1.description)
#     print("-----------------------------------------------------AGENT 2-----------------------------------------------------")
#     print(agent_2.description)

# get_info()

# while True:
#     res = sm.progress()


# 
# while(True):
