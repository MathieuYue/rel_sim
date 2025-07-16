from simulation.simulation import Simulation
from scene_master.scene_master import SceneMaster
from relationship_agent.relationship_agent import RelationshipAgent
import os

# setup agents  
agent_1_path = os.path.join("sample_agents", "ryan_reynolds", "basics.json")
agent_2_path = os.path.join("sample_agents", "blake_lively", "basics.json")
agent_1 = RelationshipAgent(agent_1_path)
agent_2 = RelationshipAgent(agent_2_path)

# setup scene master
sm = SceneMaster("scene_templates/vacation", agent_1, agent_2)

# run simulation
if __name__=="__main__":
    sim = Simulation(sm, agent_1, agent_2)
    
    sim.run_auto(3)