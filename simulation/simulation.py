from openai.types.responses.response_code_interpreter_tool_call import Output
from scene_master.scene_master import SceneMaster
from relationship_agent.relationship_agent import RelationshipAgent
from simulation import simulation_utils
import utils.general_utils as utils
from simulation.simulation_utils import print_separator, print_formatted, print_scene_separator
import os
import json

class Simulation():
    def __init__(self, scene_master, agent_1, agent_2) -> None:
        # Initialize the Simulation with a scene master and two agents
        self.scene_master = scene_master
        self.agent_1 = agent_1
        self.agent_2 = agent_2

        # Flag to indicate if simulation is loaded from a save file
        self.from_save = False

    def run_auto(self, num_interactions_per_scene):
        """
        Runs the simulation automatically for all scenes, with a fixed number of interactions per scene.
        """
        
        print_formatted(0, "Theme: " + simulation_utils.snake_to_title(self.scene_master.scene_state.theme))

        # Setup: initialize or restore the scene master action
        if not self.from_save:
            self.sm_action = self.scene_master.initialize()
        else:
            self.sm_action = self.scene_master.scene_state
            
        # Main loop over scenes
        start_ind = self.scene_master.progression

        for scene_index in range(start_ind, self.scene_master.total_scenes):
            print_scene_separator(scene_index + 1)
            print_formatted(0, "Scene Conflict: " + self.scene_master.scene_state.scene_conflict)
            self.run_scene(num_interactions_per_scene)
            if scene_index == self.scene_master.total_scenes:
                print("Simulation Ended")
                break
            self.scene_master.summarize()
            commit_score = self.scene_master.commitment_score(self.scene_master.summarize())
            print(commit_score)
            self.sm_action = self.scene_master.next_scene()

    def run_scene(self, num_interactions):
        """
        Runs a single scene with a specified number of agent interactions.
        """
        # Add the scene conflict to both agents' working memory
        self.agent_1.add_to_working_memory(text = self.scene_master.scene_state.scene_conflict, memory_type = "Scene Conflict")
        self.agent_2.add_to_working_memory(text = self.scene_master.scene_state.scene_conflict, memory_type = "Scene Conflict")
        # Add the current scene to the scene history and agents' memory
        self.scene_master.append_to_history(0, self.sm_action.current_scene)
        self.agent_1.add_to_working_memory(text = self.sm_action.current_scene, memory_type = "Narrative")
        self.agent_2.add_to_working_memory(text = self.sm_action.current_scene, memory_type = "Narrative")
        print_formatted(0, "[Scene Master]")
        print_formatted(0, self.sm_action.current_scene)
        # Loop for each interaction in the scene
        for action_index in range(num_interactions):
            print_separator()
            # Progress the scene and get the next narrative/action
            self.sm_action = self.scene_master.progress()
            self.scene_master.append_to_history(0, self.sm_action.narrative)
            print_formatted(0, "[Scene Master:]")
            print_formatted(0, self.sm_action.narrative)
            print_separator()
            # Determine which agent acts next based on character_uuid
            if self.sm_action.character_uuid == self.agent_1.agent_id:
                curr_agent = self.agent_1
                other_agent = self.agent_2
                agent_ind = 1
            elif self.sm_action.character_uuid == self.agent_2.agent_id:
                curr_agent = self.agent_2
                other_agent = self.agent_1
                agent_ind = 2
            # Agent appraises the current scene history
            agent_appraisal = curr_agent.appraise(self.scene_master.scene_history)
            # Add the narrative and agent's reflection to working memory
            # curr_agent.add_to_working_memory(
            #     text=self.sm_action.narrative,
            #     emotion_embedding=agent_reflection["emotion_scores"],
            #     inner_thoughts=agent_reflection["inner_thoughts"],
            #     memory_type = "Narrative"
            # )
            # other_agent.add_to_working_memory(text=self.sm_action.narrative, memory_type = "Narrative")
            # Agent makes a choice/action
            agent_action = curr_agent.make_choices(self.sm_action.narrative, appraisal=agent_appraisal)
            # Add the agent's action to both agents' working memory
            narrative_with_action = simulation_utils.combine_narrative_action(self.sm_action.narrative, agent_name=curr_agent.name, action=agent_action['action'])
            curr_agent.add_to_working_memory(text=narrative_with_action, memory_type="Memory", emotion_embedding=agent_appraisal["emotion_scores"], inner_thoughts=agent_appraisal["inner_thoughts"])
            other_agent.add_to_working_memory(text=narrative_with_action, memory_type="Memory")
            # Append the agent's action to the scene history
            self.scene_master.append_to_history(curr_agent, agent_action["action"])
            print_formatted(agent_ind, "[" + curr_agent.name + "]")
            print_formatted(agent_ind, agent_action["action"])

    def run_scene_by_scene(self):
        """
        Runs the simulation interactively, prompting the user for the number of interactions per scene.
        """
        # Setup: initialize or restore the scene master action
        if not self.from_save:
            self.sm_action = self.scene_master.initialize()
        else:
            self.sm_action = self.scene_master.scene_state
        # Main loop over scenes
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

        # Prepare data to save: includes scene state, history, agent info, and progression
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

        # Save to file as JSON
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

        # Restore scene state (using model_validate if available, e.g., for pydantic models)
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