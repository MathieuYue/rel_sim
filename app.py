from flask import Flask, render_template, request, jsonify, session, Response, stream_template
from simulation.simulation import Simulation
from scene_master.scene_master import SceneMaster
from relationship_agent.relationship_agent import RelationshipAgent
import os
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Global variable to store current simulation
current_simulation = None
simulation_thread = None
simulation_running = False

def get_available_agents():
    """Get list of available agents from sample_agents directory"""
    agents = []
    sample_agents_dir = "sample_agents"
    if os.path.exists(sample_agents_dir):
        for agent_dir in os.listdir(sample_agents_dir):
            agent_path = os.path.join(sample_agents_dir, agent_dir)
            if os.path.isdir(agent_path):
                # Try to get agent name from basics.json
                basics_path = os.path.join(agent_path, "basics.json")
                if os.path.exists(basics_path):
                    try:
                        with open(basics_path, 'r') as f:
                            basics = json.load(f)
                            name = basics.get('name', agent_dir.replace('_', ' ').title())
                    except:
                        name = agent_dir.replace('_', ' ').title()
                else:
                    name = agent_dir.replace('_', ' ').title()
                agents.append({
                    'id': agent_dir,
                    'name': name,
                    'path': agent_path
                })
    return agents

def get_available_scenarios():
    """Get list of available scenarios from scene_templates directory"""
    scenarios = []
    templates_dir = "scene_templates"
    if os.path.exists(templates_dir):
        for scenario_dir in os.listdir(templates_dir):
            scenario_path = os.path.join(templates_dir, scenario_dir)
            if os.path.isdir(scenario_path):
                scenarios.append({
                    'id': scenario_dir,
                    'name': scenario_dir.replace('_', ' ').title(),
                    'path': scenario_path
                })
    return scenarios

def get_saved_simulations():
    """Get list of saved simulations"""
    saves = []
    saves_dir = "saves"
    if os.path.exists(saves_dir):
        for file in os.listdir(saves_dir):
            if file.endswith('.json'):
                file_path = os.path.join(saves_dir, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        saves.append({
                            'filename': file,
                            'name': file.replace('simulation_', '').replace('.json', ''),
                            'agent_1': data.get('agent_1', {}).get('name', 'Unknown'),
                            'agent_2': data.get('agent_2', {}).get('name', 'Unknown'),
                            'progression': data.get('progression', 0),
                            'total_scenes': data.get('total_scenes', 0)
                        })
                except:
                    saves.append({
                        'filename': file,
                        'name': file.replace('simulation_', '').replace('.json', ''),
                        'agent_1': 'Unknown',
                        'agent_2': 'Unknown',
                        'progression': 0,
                        'total_scenes': 0
                    })
    return saves

@app.route('/')
def index():
    """Main page with simulation setup"""
    agents = get_available_agents()
    scenarios = get_available_scenarios()
    saved_simulations = get_saved_simulations()
    
    return render_template('index.html', 
                         agents=agents, 
                         scenarios=scenarios,
                         saved_simulations=saved_simulations)

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start a new simulation"""
    global current_simulation, simulation_thread, simulation_running
    
    data = request.json
    agent_1_id = data.get('agent_1')
    agent_2_id = data.get('agent_2')
    scenario_id = data.get('scenario')
    interactions_per_scene = data.get('interactions_per_scene', 5)
    
    try:
        # Setup agents
        agent_1_path = os.path.join("sample_agents", agent_1_id)
        agent_2_path = os.path.join("sample_agents", agent_2_id)
        agent_1 = RelationshipAgent(agent_1_path)
        agent_2 = RelationshipAgent(agent_2_path)
        
        # Setup scene master
        scenario_path = os.path.join("scene_templates", scenario_id)
        sm = SceneMaster(scenario_path, agent_1, agent_2)
        
        # Create simulation
        current_simulation = Simulation(sm, agent_1, agent_2)
        
        # Initialize the simulation to set up sm_action
        current_simulation.sm_action = current_simulation.scene_master.initialize()
        
        # Store simulation info in session
        session['simulation_info'] = {
            'agent_1': agent_1_id,
            'agent_2': agent_2_id,
            'scenario': scenario_id,
            'interactions_per_scene': interactions_per_scene,
            'started_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Simulation started successfully',
            'simulation_info': session['simulation_info']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting simulation: {str(e)}'
        }), 500

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    """Run the simulation and return results"""
    global current_simulation, simulation_running
    
    if not current_simulation:
        return jsonify({
            'success': False,
            'message': 'No simulation available. Please start a simulation first.'
        }), 400
    
    data = request.json
    mode = data.get('mode', 'auto')  # 'auto' or 'scene_by_scene'
    interactions_per_scene = data.get('interactions_per_scene', 5)
    
    try:
        simulation_running = True
        
        if mode == 'auto':
            # Run simulation automatically
            results = run_simulation_auto(interactions_per_scene)
        else:
            # Run scene by scene
            results = run_simulation_scene_by_scene(interactions_per_scene)
        
        simulation_running = False
        
        # Debug: Print results to console
        print(f"DEBUG: Captured {len(results)} results")
        for result in results:
            print(f"DEBUG: {result}")
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        simulation_running = False
        return jsonify({
            'success': False,
            'message': f'Error running simulation: {str(e)}'
        }), 500

@app.route('/api/run_simulation_stream', methods=['POST'])
def run_simulation_stream():
    """Run the simulation and stream results in real-time"""
    global current_simulation, simulation_running
    
    if not current_simulation:
        return jsonify({
            'success': False,
            'message': 'No simulation available. Please start a simulation first.'
        }), 400
    
    data = request.json
    mode = data.get('mode', 'auto')  # 'auto' or 'scene_by_scene'
    interactions_per_scene = data.get('interactions_per_scene', 5)
    
    def generate():
        try:
            simulation_running = True
            
            if mode == 'auto':
                # Run simulation automatically with streaming
                yield from run_simulation_auto_stream(interactions_per_scene)
            else:
                # Run scene by scene with streaming
                yield from run_simulation_scene_by_scene_stream(interactions_per_scene)
            
            simulation_running = False
            
        except Exception as e:
            simulation_running = False
            error_result = {
                'type': 'error',
                'content': f'Error during simulation: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_result)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

def run_simulation_auto(interactions_per_scene):
    """Run simulation in auto mode and capture output"""
    results = []
    
    # Ensure sm_action is initialized
    if not hasattr(current_simulation, 'sm_action') or current_simulation.sm_action is None:
        current_simulation.sm_action = current_simulation.scene_master.initialize()
    
    def add_result(content, result_type='output'):
        results.append({
            'type': result_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    try:
        # Get simulation components
        sim = current_simulation
        agent_1 = sim.agent_1
        agent_2 = sim.agent_2
        scene_master = sim.scene_master
        
        # Add the scene conflict to both agents' working memory
        add_result(f"Central Conflict of Scene: {scene_master.scene_state.scene_conflict}")
        agent_1.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        agent_2.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        
        # Add the current scene to the scene history and agents' memory
        scene_master.append_to_history(0, sim.sm_action.current_scene)
        agent_1.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        agent_2.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        add_result(sim.sm_action.current_scene, "scene-master")
        
        # Loop for each interaction in the scene
        for action_index in range(interactions_per_scene):
            
            # Progress the scene and get the next narrative/action
            sim.sm_action = scene_master.progress()
            scene_master.append_to_history(0, sim.sm_action.narrative)
            
            add_result("[Scene Master:]", "scene-master")
            add_result(sim.sm_action.narrative, "scene-master")
            
            # Determine which agent acts next based on character_uuid
            if sim.sm_action.character_uuid == agent_1.agent_id:
                curr_agent = agent_1
                other_agent = agent_2
                agent_ind = 1
                agent_name = agent_1.name
            elif sim.sm_action.character_uuid == agent_2.agent_id:
                curr_agent = agent_2
                other_agent = agent_1
                agent_ind = 2
                agent_name = agent_2.name
            else:
                add_result(f"Unknown character_uuid: {sim.sm_action.character_uuid}", "error")
                continue
            
            # Agent appraises the current scene history
            add_result(f"{agent_name} is appraising the scene...")
            agent_appraisal = curr_agent.appraise(scene_master.scene_history)
            
            # Agent makes a choice/action
            add_result(f"{agent_name} is making a choice...")
            agent_action = curr_agent.make_choices(sim.sm_action.narrative, appraisal=agent_appraisal)
            
            # Add the agent's action to both agents' working memory
            from simulation.simulation_utils import combine_narrative_action
            narrative_with_action = combine_narrative_action(
                sim.sm_action.narrative, 
                agent_name=curr_agent.name, 
                action=agent_action['action']
            )
            
            curr_agent.add_to_working_memory(
                text=narrative_with_action, 
                memory_type="Memory", 
                emotion_embedding=agent_appraisal["emotion_scores"], 
                inner_thoughts=agent_appraisal["inner_thoughts"]
            )
            other_agent.add_to_working_memory(text=narrative_with_action, memory_type="Memory")
            
            # Append the agent's action to the scene history
            scene_master.append_to_history(curr_agent, agent_action["action"])
            
            add_result(f"[{agent_name}] {agent_action['action']}", f"agent-{agent_ind}")
            
    except Exception as e:
        # Add error message to results
        add_result(f'Error during simulation: {str(e)}', 'error')
        raise e
    
    return results

def run_simulation_auto_stream(interactions_per_scene):
    """Run simulation in auto mode and stream output in real-time"""
    
    # Ensure sm_action is initialized
    if not hasattr(current_simulation, 'sm_action') or current_simulation.sm_action is None:
        current_simulation.sm_action = current_simulation.scene_master.initialize()
    
    def yield_result(content, result_type='output'):
        result = {
            'type': result_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        return f"data: {json.dumps(result)}\n\n"
    
    try:
        # Get simulation components
        sim = current_simulation
        agent_1 = sim.agent_1
        agent_2 = sim.agent_2
        scene_master = sim.scene_master
        
        # Add the scene conflict to both agents' working memory
        yield yield_result(f"Scene Conflict: {scene_master.scene_state.scene_conflict}", "scene-master")
        agent_1.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        agent_2.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        
        # Add the current scene to the scene history and agents' memory
        scene_master.append_to_history(0, sim.sm_action.current_scene)
        agent_1.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        agent_2.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")

        yield yield_result(sim.sm_action.current_scene, "scene-master")
        
        # Loop for each interaction in the scene
        for action_index in range(interactions_per_scene):
            
            # Progress the scene and get the next narrative/action
            sim.sm_action = scene_master.progress()
            print(sim.sm_action)
            scene_master.append_to_history(0, sim.sm_action.narrative)
            yield yield_result(sim.sm_action.narrative, "scene-master")
            
            # Determine which agent acts next based on character_uuid
            if sim.sm_action.character_uuid == agent_1.agent_id:
                curr_agent = agent_1
                other_agent = agent_2
                agent_ind = 1
                agent_name = agent_1.name
            elif sim.sm_action.character_uuid == agent_2.agent_id:
                curr_agent = agent_2
                other_agent = agent_1
                agent_ind = 2
                agent_name = agent_2.name
            else:
                yield yield_result(f"Unknown character_uuid: {sim.sm_action.character_uuid}", "error")
                continue
            
            # Agent appraises the current scene history
            try:
                agent_appraisal = curr_agent.appraise(scene_master.scene_history)
                yield yield_result(f"Internal monologue: {agent_appraisal['inner_thoughts']}", f"agent-{agent_ind}")
            except TimeoutError as e:
                yield yield_result(f"Timeout error during {agent_name}'s appraisal: {str(e)}", "error")
                raise e
            except Exception as e:
                yield yield_result(f"Error during {agent_name}'s appraisal: {str(e)}", "error")
                raise e

            # Agent makes a choice/action
            try:
                agent_action = curr_agent.make_choices(sim.sm_action.narrative, appraisal=agent_appraisal)
            except TimeoutError as e:
                yield yield_result(f"Timeout error during {agent_name}'s choice making: {str(e)}", "error")
                raise e
            except Exception as e:
                yield yield_result(f"Error during {agent_name}'s choice making: {str(e)}", "error")
                raise e
            
            
            # Add the agent's action to both agents' working memory
            from simulation.simulation_utils import combine_narrative_action
            narrative_with_action = combine_narrative_action(
                sim.sm_action.narrative, 
                agent_name=curr_agent.name, 
                action=agent_action['action']
            )
            
            curr_agent.add_to_working_memory(
                text=narrative_with_action, 
                memory_type="Memory", 
                emotion_embedding=agent_appraisal["emotion_scores"], 
                inner_thoughts=agent_appraisal["inner_thoughts"]
            )
            other_agent.add_to_working_memory(text=narrative_with_action, memory_type="Memory")
            
            # Append the agent's action to the scene history
            scene_master.append_to_history(curr_agent, agent_action["action"])
            
            yield yield_result(f"Action: {agent_action['action']}", f"agent-{agent_ind}")
            
    except Exception as e:
        # Add error message to results
        yield yield_result(f'Error during simulation: {str(e)}', 'error')
        raise e

def run_simulation_scene_by_scene_stream(interactions_per_scene):
    """Run simulation scene by scene and stream output in real-time"""
    
    # Ensure sm_action is initialized
    if not hasattr(current_simulation, 'sm_action') or current_simulation.sm_action is None:
        current_simulation.sm_action = current_simulation.scene_master.initialize()
    
    def yield_result(content, result_type='output'):
        result = {
            'type': result_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        return f"data: {json.dumps(result)}\n\n"
    
    try:
        # Get simulation components
        sim = current_simulation
        agent_1 = sim.agent_1
        agent_2 = sim.agent_2
        scene_master = sim.scene_master
        
        # Add the scene conflict to both agents' working memory
        yield yield_result(f"Adding scene conflict to agents: {scene_master.scene_state.scene_conflict}")
        agent_1.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        agent_2.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        
        # Add the current scene to the scene history and agents' memory
        scene_master.append_to_history(0, sim.sm_action.current_scene)
        agent_1.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        agent_2.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        
        yield yield_result("[Scene Master]", "scene-master")
        yield yield_result(sim.sm_action.current_scene, "scene-master")
        
        # Loop for each interaction in the scene
        for action_index in range(interactions_per_scene):
            
            # Progress the scene and get the next narrative/action
            sim.sm_action = scene_master.progress()
            scene_master.append_to_history(0, sim.sm_action.narrative)
            
            yield yield_result("[Scene Master:]", "scene-master")
            yield yield_result(sim.sm_action.narrative, "scene-master")
            
            # Determine which agent acts next based on character_uuid
            if sim.sm_action.character_uuid == agent_1.agent_id:
                curr_agent = agent_1
                other_agent = agent_2
                agent_ind = 1
                agent_name = agent_1.name
            elif sim.sm_action.character_uuid == agent_2.agent_id:
                curr_agent = agent_2
                other_agent = agent_1
                agent_ind = 2
                agent_name = agent_2.name
            else:
                yield yield_result(f"Unknown character_uuid: {sim.sm_action.character_uuid}", "error")
                continue
            
            # Agent appraises the current scene history
            yield yield_result(f"{agent_name} is appraising the scene...")
            try:
                agent_appraisal = curr_agent.appraise(scene_master.scene_history)
            except TimeoutError as e:
                yield yield_result(f"Timeout error during {agent_name}'s appraisal: {str(e)}", "error")
                raise e
            except Exception as e:
                yield yield_result(f"Error during {agent_name}'s appraisal: {str(e)}", "error")
                raise e
            
            # Agent makes a choice/action
            yield yield_result(f"{agent_name} is making a choice...")
            try:
                agent_action = curr_agent.make_choices(sim.sm_action.narrative, appraisal=agent_appraisal)
            except TimeoutError as e:
                yield yield_result(f"Timeout error during {agent_name}'s choice making: {str(e)}", "error")
                raise e
            except Exception as e:
                yield yield_result(f"Error during {agent_name}'s choice making: {str(e)}", "error")
                raise e
            
            # Add the agent's action to both agents' working memory
            from simulation.simulation_utils import combine_narrative_action
            narrative_with_action = combine_narrative_action(
                sim.sm_action.narrative, 
                agent_name=curr_agent.name, 
                action=agent_action['action']
            )
            
            curr_agent.add_to_working_memory(
                text=narrative_with_action, 
                memory_type="Memory", 
                emotion_embedding=agent_appraisal["emotion_scores"], 
                inner_thoughts=agent_appraisal["inner_thoughts"]
            )
            other_agent.add_to_working_memory(text=narrative_with_action, memory_type="Memory")
            
            # Append the agent's action to the scene history
            scene_master.append_to_history(curr_agent, agent_action["action"])
            
            yield yield_result(f"[{agent_name}] {agent_action['action']}", f"agent-{agent_ind}")
            
    except Exception as e:
        # Add error message to results
        yield yield_result(f'Error during simulation: {str(e)}', 'error')
        raise e

def run_simulation_scene_by_scene(interactions_per_scene):
    """Run simulation scene by scene and capture output"""
    results = []
    
    # Ensure sm_action is initialized
    if not hasattr(current_simulation, 'sm_action') or current_simulation.sm_action is None:
        current_simulation.sm_action = current_simulation.scene_master.initialize()
    
    def add_result(content, result_type='output'):
        results.append({
            'type': result_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    try:
        # Get simulation components
        sim = current_simulation
        agent_1 = sim.agent_1
        agent_2 = sim.agent_2
        scene_master = sim.scene_master
        
        # Add the scene conflict to both agents' working memory
        add_result(f"Adding scene conflict to agents: {scene_master.scene_state.scene_conflict}")
        agent_1.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        agent_2.add_to_working_memory(text=scene_master.scene_state.scene_conflict, memory_type="Scene Conflict")
        
        # Add the current scene to the scene history and agents' memory
        scene_master.append_to_history(0, sim.sm_action.current_scene)
        agent_1.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        agent_2.add_to_working_memory(text=sim.sm_action.current_scene, memory_type="Narrative")
        
        add_result("[Scene Master]", "scene-master")
        add_result(sim.sm_action.current_scene, "scene-master")
        
        # Loop for each interaction in the scene
        for action_index in range(interactions_per_scene):
            
            # Progress the scene and get the next narrative/action
            sim.sm_action = scene_master.progress()
            scene_master.append_to_history(0, sim.sm_action.narrative)
            
            add_result("[Scene Master:]", "scene-master")
            add_result(sim.sm_action.narrative, "scene-master")
            
            # Determine which agent acts next based on character_uuid
            if sim.sm_action.character_uuid == agent_1.agent_id:
                curr_agent = agent_1
                other_agent = agent_2
                agent_ind = 1
                agent_name = agent_1.name
            elif sim.sm_action.character_uuid == agent_2.agent_id:
                curr_agent = agent_2
                other_agent = agent_1
                agent_ind = 2
                agent_name = agent_2.name
            else:
                add_result(f"Unknown character_uuid: {sim.sm_action.character_uuid}", "error")
                continue
            
            # Agent appraises the current scene history
            add_result(f"{agent_name} is appraising the scene...")
            print("running make appraisal")
            agent_appraisal = curr_agent.appraise(scene_master.scene_history)
            
            # Agent makes a choice/action
            add_result(f"{agent_name} is making a choice...")
            print("running make choices")
            agent_action = curr_agent.make_choices(sim.sm_action.narrative, appraisal=agent_appraisal)
            
            # Add the agent's action to both agents' working memory
            from simulation.simulation_utils import combine_narrative_action
            narrative_with_action = combine_narrative_action(
                sim.sm_action.narrative, 
                agent_name=curr_agent.name, 
                action=agent_action['action']
            )
            
            curr_agent.add_to_working_memory(
                text=narrative_with_action, 
                memory_type="Memory", 
                emotion_embedding=agent_appraisal["emotion_scores"], 
                inner_thoughts=agent_appraisal["inner_thoughts"]
            )
            other_agent.add_to_working_memory(text=narrative_with_action, memory_type="Memory")
            
            # Append the agent's action to the scene history
            scene_master.append_to_history(curr_agent, agent_action["action"])
            
            add_result(f"[{agent_name}] {agent_action['action']}", f"agent-{agent_ind}")
            
    except Exception as e:
        # Add error message to results
        add_result(f'Error during simulation: {str(e)}', 'error')
        raise e
    
    return results

@app.route('/api/save_simulation', methods=['POST'])
def save_simulation():
    """Save current simulation"""
    global current_simulation
    
    if not current_simulation:
        return jsonify({
            'success': False,
            'message': 'No simulation to save'
        }), 400
    
    try:
        filename = request.json.get('filename')
        current_simulation.save_simulation(filename)
        
        return jsonify({
            'success': True,
            'message': 'Simulation saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving simulation: {str(e)}'
        }), 500

@app.route('/api/load_simulation', methods=['POST'])
def load_simulation():
    """Load a saved simulation"""
    global current_simulation
    
    data = request.json
    filename = data.get('filename')
    
    try:
        # Create a temporary simulation to load the save
        temp_sim = Simulation(None, None, None)
        success = temp_sim.load_simulation(filename)
        
        if success:
            current_simulation = temp_sim
            # Initialize sm_action if it doesn't exist
            if not hasattr(current_simulation, 'sm_action') or current_simulation.sm_action is None:
                current_simulation.sm_action = current_simulation.scene_master.scene_state
            return jsonify({
                'success': True,
                'message': 'Simulation loaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to load simulation'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading simulation: {str(e)}'
        }), 500

@app.route('/api/simulation_status')
def simulation_status():
    """Get current simulation status"""
    global current_simulation, simulation_running
    
    return jsonify({
        'has_simulation': current_simulation is not None,
        'is_running': simulation_running,
        'simulation_info': session.get('simulation_info', {})
    })

@app.route('/api/agents')
def get_agents():
    """Get list of available agents"""
    agents = get_available_agents()
    return jsonify(agents)

@app.route('/api/scenarios')
def get_scenarios():
    """Get list of available scenarios"""
    scenarios = get_available_scenarios()
    return jsonify(scenarios)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 