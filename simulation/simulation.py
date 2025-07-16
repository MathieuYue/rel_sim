from openai.types.responses.response_code_interpreter_tool_call import Output
from scene_master.scene_master import SceneMaster
from relationship_agent.relationship_agent import RelationshipAgent
import utils.general_utils as utils
from simulation.simulation_utils import print_separator, print_formatted, print_scene_separator
import os
import json

class Simulation():
    def __init__(self, scene_master, agent_1, agent_2) -> None:
        
        self.scene_master = scene_master
        self.agent_1 = agent_1
        self.agent_2 = agent_2

        self.from_save = False

    def run_auto(self, num_interactions_per_scene):
        # setup
        if not self.from_save:
            self.sm_action = self.scene_master.initialize()
        else:
            self.sm_action = self.scene_master.scene_state
            
        # main loop
        start_ind = self.scene_master.progression
        for scene_index in range(start_ind, self.scene_master.total_scenes):
            print_scene_separator(scene_index + 1)
            self.run_scene(num_interactions_per_scene)
            if scene_index == self.scene_master.total_scenes:
                print("Simulation Ended")
                break
            self.scene_master.summarize()
            self.sm_action = self.scene_master.next_scene()

    def run_scene(self, num_interactions):
        self.scene_master.append_to_history(0, self.sm_action.current_scene)
        print_formatted(0, "[Scene Master]")
        print_formatted(0, self.sm_action.current_scene)
        for action_index in range(num_interactions):
            print_separator()
            self.sm_action = self.scene_master.progress()
            self.scene_master.append_to_history(0, self.sm_action.narrative)
            # print("[Scene Master:]")
            print_formatted(0, "[Scene Master:]")
            # print(self.sm_action.narrative)
            print_formatted(0, self.sm_action.narrative)
            # print("Options: ")
            print_formatted(0, "Options: ")
            # print(utils.list_to_indexed_string_1_based(self.sm_action.choices))
            print_formatted(0, utils.list_to_indexed_string_1_based(self.sm_action.choices))
            print_separator()
            if self.sm_action.character_uuid == self.agent_1.agent_id:
                curr_agent = self.agent_1
                agent_ind = 1
            elif self.sm_action.character_uuid == self.agent_2.agent_id:
                curr_agent = self.agent_2
                agent_ind = 2
            agent_reflection = curr_agent.reflect(self.scene_master.scene_history)
            print(json.dumps(agent_reflection))
            agent_action = curr_agent.act(self.scene_master.scene_history, self.sm_action.narrative, self.sm_action.choices)
            self.scene_master.append_to_history(curr_agent, agent_action.line)
            print_formatted(agent_ind, "[" + curr_agent.name + "]")
            # print("[" + curr_agent.name + "]")
            print_formatted(agent_ind, "Chosen Action: " + self.sm_action.choices[agent_action.action_index])
            # print("Chosen Action: " + sm_action.choices[agent_action.action_index])
            print_formatted(agent_ind, agent_action.line)
            # print("Dialogue: " + agent_action.line)

    def run_scene_by_scene(self):
        # setup 
        if not self.from_save:
            self.sm_action = self.scene_master.initialize()
        else:
            self.sm_action = self.scene_master.scene_state
        # main loop
        for scene_index in range(self.scene_master.total_scenes):
            print_scene_separator(scene_index + 1)
            usr_input = input("# of interactions(or 'quit' to stop): ")
            if usr_input == 'quit':
                self.save_simulation()
                print("Simulation Terminated")
                break            
            self.run_scene(int(usr_input))
            if scene_index == self.scene_master.total_scenes:
                break
            self.scene_master.summarize()
            self.sm_action = self.scene_master.next_scene()

    def save_simulation(self, filename=None):
        """
        Saves the current simulation state and history to the 'saves' folder.
        If filename is not provided, a default name is generated.
        """
        import os
        import json
        from datetime import datetime

        # Ensure the saves directory exists
        saves_dir = "saves"
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)

        # Generate a filename if not provided
        if filename is None:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{now}.json"
        save_path = os.path.join(saves_dir, filename)

        # Prepare data to save
        data = {
            "scene_state": self.scene_master.scene_state.model_dump() if hasattr(self.scene_master.scene_state, "model_dump") else str(self.scene_master.scene_state),
            "scene_history": self.scene_master.scene_history,
            "agent_1": {
                "name": getattr(self.agent_1, "name", ""),
                "description": getattr(self.agent_1, "description", ""),
                "goal": getattr(self.agent_1, "goal", "")
            },
            "agent_2": {
                "name": getattr(self.agent_2, "name", ""),
                "description": getattr(self.agent_2, "description", ""),
                "goal": getattr(self.agent_2, "goal", "")
            },
            "progression": getattr(self.scene_master, "progression", None),
            "total_scenes": getattr(self.scene_master, "total_scenes", None)
        }

        # Save to file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Simulation saved to {save_path}")

        # INSERT_YOUR_CODE
    def load_simulation(self, filename):
        """
        Loads a saved simulation state from the 'saves' folder and restores the simulation.
        """
        import os
        import json

        saves_dir = "saves"
        load_path = os.path.join(saves_dir, filename)
        if not os.path.exists(load_path):
            print(f"File {load_path} does not exist.")
            return False

        with open(load_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Restore scene state
        if hasattr(self.scene_master.scene_state, "model_validate"):
            # If using pydantic or similar
            self.scene_master.scene_state = self.scene_master.scene_state.__class__.model_validate(data["scene_state"])
        else:
            self.scene_master.scene_state = data["scene_state"]

        # Restore scene history
        self.scene_master.scene_history = data.get("scene_history", [])

        # Restore agents' goals (and optionally other attributes)
        if hasattr(self.agent_1, "goal"):
            self.agent_1.goal = data.get("agent_1", {}).get("goal", "")
        if hasattr(self.agent_2, "goal"):
            self.agent_2.goal = data.get("agent_2", {}).get("goal", "")

        # Set agent_id for agent_1 and agent_2 from their descriptions (which are JSON strings)
        import json as _json
        try:
            agent_1_desc = data.get("agent_1", {}).get("description", "")
            agent_1_state = _json.loads(agent_1_desc) if agent_1_desc else {}
            if hasattr(self.agent_1, "agent_id") and "agent_id" in agent_1_state:
                self.agent_1.agent_id = agent_1_state["agent_id"]
                self.agent_1.agent_state["agent_id"] = agent_1_state["agent_id"]
        except Exception:
            pass

        try:
            agent_2_desc = data.get("agent_2", {}).get("description", "")
            agent_2_state = _json.loads(agent_2_desc) if agent_2_desc else {}
            if hasattr(self.agent_2, "agent_id") and "agent_id" in agent_2_state:
                self.agent_2.agent_id = agent_2_state["agent_id"]
                self.agent_2.agent_state["agent_id"] = agent_2_state["agent_id"]
        except Exception:
            pass

        # Optionally restore agent descriptions/names if needed
        if hasattr(self.agent_1, "description"):
            self.agent_1.description = data.get("agent_1", {}).get("description", self.agent_1.description)
        if hasattr(self.agent_2, "description"):
            self.agent_2.description = data.get("agent_2", {}).get("description", self.agent_2.description)
        if hasattr(self.agent_1, "name"):
            self.agent_1.name = data.get("agent_1", {}).get("name", self.agent_1.name)
        if hasattr(self.agent_2, "name"):
            self.agent_2.name = data.get("agent_2", {}).get("name", self.agent_2.name)

        # Restore progression and total_scenes
        if hasattr(self.scene_master, "progression"):
            self.scene_master.progression = data.get("progression", 0)
        if hasattr(self.scene_master, "total_scenes"):
            self.scene_master.total_scenes = data.get("total_scenes", 0)

        print(f"Simulation loaded from {load_path}")
        self.from_save = True
        return True