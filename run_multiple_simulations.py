#!/usr/bin/env python3
"""
Example script demonstrating how to run multiple simulation pipelines concurrently
using the new async methods.
"""

import asyncio
import json
from relationship_agent.relationship_agent import RelationshipAgent
from scene_master.scene_master import SceneMaster
from simulation.simulation import Simulation
import os

async def run_single_simulation(simulation_id, agent1_name, agent1_persona, agent2_name, agent2_persona, num_interactions=3):
    """
    Run a single simulation pipeline asynchronously.
    
    Args:
        simulation_id: Unique identifier for this simulation
        agent1_name: Name of the first agent
        agent1_persona: Persona description of the first agent
        agent2_name: Name of the second agent
        agent2_persona: Persona description of the second agent
        num_interactions: Number of interactions per scene
    
    Returns:
        dict: Results of the simulation including commitment log
    """
    print(f"Starting simulation {simulation_id}: {agent1_name} & {agent2_name}")
    
    # Create agents
    agent1 = RelationshipAgent(agent1_name, agent1_persona)
    agent2 = RelationshipAgent(agent2_name, agent2_persona)
    
    # Create scene master
    scene_master = SceneMaster(agent1, agent2)
    
    # Create simulation
    simulation = Simulation(scene_master, agent1, agent2)
    
    try:
        # Run the simulation asynchronously
        commitment_log = await simulation.run_auto_async(num_interactions)
        
        print(f"Completed simulation {simulation_id}")
        return {
            "simulation_id": simulation_id,
            "agent1_name": agent1_name,
            "agent2_name": agent2_name,
            "commitment_log": commitment_log,
            "status": "completed"
        }
    except Exception as e:
        print(f"Error in simulation {simulation_id}: {e}")
        return {
            "simulation_id": simulation_id,
            "agent1_name": agent1_name,
            "agent2_name": agent2_name,
            "error": str(e),
            "status": "failed"
        }

async def run_multiple_simulations_concurrently():
    """
    Run multiple simulation pipelines concurrently.
    """
    # Define different agent configurations for multiple simulations
    simulation_configs = [
        {
            "simulation_id": "sim_1",
            "agent1_name": "Alex",
            "agent1_persona": "A thoughtful introvert who values deep conversations and personal space. Alex is analytical and prefers to think before speaking.",
            "agent2_name": "Jordan",
            "agent2_persona": "An outgoing extrovert who loves socializing and spontaneous adventures. Jordan is expressive and acts on intuition."
        },
        {
            "simulation_id": "sim_2", 
            "agent1_name": "Maya",
            "agent1_persona": "A career-driven professional who prioritizes work-life balance. Maya is organized and values clear communication.",
            "agent2_name": "Sam",
            "agent2_persona": "A creative artist who lives in the moment and values emotional expression. Sam is spontaneous and follows their heart."
        },
        {
            "simulation_id": "sim_3",
            "agent1_name": "Taylor",
            "agent1_persona": "A practical realist who focuses on facts and logical solutions. Taylor is reliable and values stability.",
            "agent2_name": "Casey",
            "agent2_persona": "An idealistic dreamer who believes in possibilities and emotional connections. Casey is optimistic and values authenticity."
        }
    ]
    
    # Create tasks for all simulations
    tasks = []
    for config in simulation_configs:
        task = run_single_simulation(
            simulation_id=config["simulation_id"],
            agent1_name=config["agent1_name"],
            agent1_persona=config["agent1_persona"],
            agent2_name=config["agent2_name"],
            agent2_persona=config["agent2_persona"],
            num_interactions=2  # Reduced for faster execution
        )
        tasks.append(task)
    
    print(f"Starting {len(tasks)} simulations concurrently...")
    
    # Run all simulations concurrently and wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_results = []
    failed_results = []
    
    for result in results:
        if isinstance(result, Exception):
            print(f"Simulation failed with exception: {result}")
            failed_results.append({"error": str(result)})
        elif result.get("status") == "completed":
            successful_results.append(result)
        else:
            failed_results.append(result)
    
    print(f"\nSimulation Results:")
    print(f"Successful: {len(successful_results)}")
    print(f"Failed: {len(failed_results)}")
    
    # Save results to file
    output_data = {
        "successful_simulations": successful_results,
        "failed_simulations": failed_results,
        "total_simulations": len(simulation_configs)
    }
    
    # Ensure output directory exists
    os.makedirs("simulation_results", exist_ok=True)
    
    with open("simulation_results/concurrent_simulation_results.json", "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"Results saved to simulation_results/concurrent_simulation_results.json")
    
    return output_data

async def run_simulations_with_custom_configs():
    """
    Example of running simulations with custom configurations.
    """
    # You can customize this function to run specific agent combinations
    # or load configurations from files
    
    custom_configs = [
        {
            "simulation_id": "custom_1",
            "agent1_name": "Blake",
            "agent1_persona": "A compassionate caregiver who puts others first. Blake is nurturing and values emotional support.",
            "agent2_name": "Riley", 
            "agent2_persona": "An independent adventurer who values freedom and new experiences. Riley is self-reliant and seeks excitement."
        }
    ]
    
    tasks = []
    for config in custom_configs:
        task = run_single_simulation(
            simulation_id=config["simulation_id"],
            agent1_name=config["agent1_name"],
            agent1_persona=config["agent1_persona"],
            agent2_name=config["agent2_name"],
            agent2_persona=config["agent2_persona"],
            num_interactions=3
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    # Run the concurrent simulations
    asyncio.run(run_multiple_simulations_concurrently())
