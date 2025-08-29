#!/usr/bin/env python3
"""
Guide for determining optimal number of concurrent simulations.
This script helps you find the right balance between performance and resource usage.
"""

import asyncio
import time
import psutil
import os
from relationship_agent.relationship_agent import RelationshipAgent
from scene_master.scene_master import SceneMaster
from simulation.simulation import Simulation

async def measure_single_simulation_time():
    """Measure how long a single simulation takes to complete."""
    print("Measuring single simulation performance...")
    
    # Create a simple test simulation
    agent1 = RelationshipAgent("TestAgent1", "A test agent for performance measurement.")
    agent2 = RelationshipAgent("TestAgent2", "Another test agent for performance measurement.")
    scene_master = SceneMaster(agent1, agent2)
    simulation = Simulation(scene_master, agent1, agent2)
    
    start_time = time.time()
    try:
        # Run a short simulation (1 interaction per scene, 2 scenes)
        await simulation.run_auto_async(num_interactions_per_scene=1)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Single simulation completed in {duration:.2f} seconds")
        return duration
    except Exception as e:
        print(f"Error measuring single simulation: {e}")
        return None

async def test_concurrent_load(num_simulations):
    """Test how the system performs with a specific number of concurrent simulations."""
    print(f"\nTesting {num_simulations} concurrent simulations...")
    
    async def run_test_simulation(sim_id):
        agent1 = RelationshipAgent(f"Agent1_{sim_id}", f"Test agent 1 for simulation {sim_id}")
        agent2 = RelationshipAgent(f"Agent2_{sim_id}", f"Test agent 2 for simulation {sim_id}")
        scene_master = SceneMaster(agent1, agent2)
        simulation = Simulation(scene_master, agent1, agent2)
        
        try:
            await simulation.run_auto_async(num_interactions_per_scene=1)
            return {"sim_id": sim_id, "status": "success"}
        except Exception as e:
            return {"sim_id": sim_id, "status": "failed", "error": str(e)}
    
    # Record system resources before
    cpu_before = psutil.cpu_percent(interval=1)
    memory_before = psutil.virtual_memory().percent
    
    start_time = time.time()
    
    # Run concurrent simulations
    tasks = [run_test_simulation(i) for i in range(num_simulations)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Record system resources after
    cpu_after = psutil.cpu_percent(interval=1)
    memory_after = psutil.virtual_memory().percent
    
    # Count successes and failures
    successful = len([r for r in results if isinstance(r, dict) and r.get("status") == "success"])
    failed = len(results) - successful
    
    print(f"Results for {num_simulations} concurrent simulations:")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  CPU usage: {cpu_before:.1f}% -> {cpu_after:.1f}%")
    print(f"  Memory usage: {memory_before:.1f}% -> {memory_after:.1f}%")
    
    return {
        "num_simulations": num_simulations,
        "total_time": total_time,
        "successful": successful,
        "failed": failed,
        "cpu_increase": cpu_after - cpu_before,
        "memory_increase": memory_after - memory_before
    }

def get_system_info():
    """Get information about the current system."""
    print("=== System Information ===")
    print(f"CPU cores: {psutil.cpu_count()}")
    print(f"CPU cores (logical): {psutil.cpu_count(logical=True)}")
    print(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"Available memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    
    # Check for API rate limits (if environment variables are set)
    lambda_api_key = os.getenv("LAMBDA_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if lambda_api_key:
        print("Lambda API key: Configured")
    if openai_api_key:
        print("OpenAI API key: Configured")
    
    print()

def calculate_recommendations(single_sim_time, system_info):
    """Calculate recommended simulation limits based on system capabilities."""
    print("=== Recommendations ===")
    
    # Conservative recommendations (safe for most systems)
    conservative_cpu = min(psutil.cpu_count(), 4)  # Max 4 concurrent or CPU cores
    conservative_memory = max(1, int(psutil.virtual_memory().available / (1024**3) / 2))  # 2GB per sim
    
    # Aggressive recommendations (for high-performance systems)
    aggressive_cpu = psutil.cpu_count(logical=True)  # Use all logical cores
    aggressive_memory = max(1, int(psutil.virtual_memory().available / (1024**3) / 1))  # 1GB per sim
    
    print(f"Conservative approach: {min(conservative_cpu, conservative_memory)} simulations")
    print(f"Aggressive approach: {min(aggressive_cpu, aggressive_memory)} simulations")
    
    if single_sim_time:
        print(f"Estimated time for 10 simulations:")
        print(f"  Sequential: {single_sim_time * 10:.1f} seconds")
        print(f"  Concurrent (conservative): {single_sim_time * 10 / min(conservative_cpu, conservative_memory):.1f} seconds")
        print(f"  Concurrent (aggressive): {single_sim_time * 10 / min(aggressive_cpu, aggressive_memory):.1f} seconds")
    
    print()
    return min(conservative_cpu, conservative_memory), min(aggressive_cpu, aggressive_memory)

async def find_optimal_concurrency():
    """Find the optimal number of concurrent simulations through testing."""
    print("=== Finding Optimal Concurrency ===")
    
    # Test different concurrency levels, starting with 4
    test_levels = [4, 8, 16, 32]
    results = []
    
    for level in test_levels:
        if level > 16:  # Skip very high levels unless specifically testing
            continue
            
        result = await test_concurrent_load(level)
        results.append(result)
        
        # Stop if we're seeing too many failures
        if result["failed"] > result["successful"] * 0.5:  # More than 50% failure rate
            print(f"Stopping at {level} simulations due to high failure rate")
            break
    
    # Find the sweet spot
    best_result = None
    best_efficiency = 0
    
    for result in results:
        if result["successful"] > 0:
            # Calculate efficiency (successful simulations per second)
            efficiency = result["successful"] / result["total_time"]
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_result = result
    
    if best_result:
        print(f"\nOptimal concurrency: {best_result['num_simulations']} simulations")
        print(f"Efficiency: {best_efficiency:.2f} successful simulations/second")
    
    return best_result

async def main():
    """Main function to determine optimal simulation limits."""
    print("Simulation Concurrency Guide")
    print("=" * 50)
    
    # Get system information
    get_system_info()
    
    # Measure single simulation performance
    single_sim_time = await measure_single_simulation_time()
    
    # Calculate recommendations
    conservative, aggressive = calculate_recommendations(single_sim_time, None)
    
    # Test to find optimal concurrency
    optimal = await find_optimal_concurrency()
    
    print("=== Final Recommendations ===")
    print(f"1. Start with {conservative} concurrent simulations (conservative)")
    print(f"2. If successful, try up to {aggressive} concurrent simulations (aggressive)")
    if optimal:
        print(f"3. Based on testing, optimal appears to be {optimal['num_simulations']} simulations")
    
    print("\n=== Guidelines ===")
    print("- Monitor CPU and memory usage during runs")
    print("- Watch for API rate limit errors")
    print("- Reduce concurrency if you see high failure rates")
    print("- Increase concurrency if system resources are underutilized")
    print("- Consider API costs when scaling up")

if __name__ == "__main__":
    asyncio.run(main())
