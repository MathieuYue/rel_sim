#!/usr/bin/env python3
"""
Simple test script to verify that the async functionality works correctly.
"""

import asyncio
import time
from relationship_agent.relationship_agent import RelationshipAgent
from scene_master.scene_master import SceneMaster
from simulation.simulation import Simulation

async def test_async_llm_calls():
    """Test that async LLM calls work correctly."""
    print("Testing async LLM calls...")
    
    # Create a simple agent
    agent = RelationshipAgent("TestAgent", "A test agent for async functionality testing.")
    
    # Test async appraisal
    scene_history = [["Narrative", "This is a test scene for async functionality."]]
    start_time = time.time()
    appraisal = await agent.appraise_async(scene_history)
    end_time = time.time()
    
    print(f"Async appraisal completed in {end_time - start_time:.2f} seconds")
    print(f"Appraisal result: {appraisal}")
    
    return appraisal is not None

async def test_async_simulation():
    """Test that async simulation works correctly."""
    print("Testing async simulation...")
    
    # Create agents
    agent1 = RelationshipAgent("Alice", "A test agent for async simulation testing.")
    agent2 = RelationshipAgent("Bob", "Another test agent for async simulation testing.")
    
    # Create scene master
    scene_master = SceneMaster(agent1, agent2)
    
    # Create simulation
    simulation = Simulation(scene_master, agent1, agent2)
    
    # Test async initialization
    start_time = time.time()
    scene_state = await scene_master.initialize_async()
    end_time = time.time()
    
    print(f"Async initialization completed in {end_time - start_time:.2f} seconds")
    print(f"Scene state: {scene_state.scene_conflict}")
    
    return scene_state is not None

async def test_concurrent_operations():
    """Test that multiple async operations can run concurrently."""
    print("Testing concurrent operations...")
    
    # Create multiple agents
    agents = [
        RelationshipAgent(f"Agent{i}", f"Test agent {i} for concurrent testing.")
        for i in range(3)
    ]
    
    # Test concurrent appraisals
    scene_history = [["Narrative", "This is a test scene for concurrent functionality."]]
    
    start_time = time.time()
    
    # Run multiple appraisals concurrently
    tasks = [agent.appraise_async(scene_history) for agent in agents]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    print(f"Concurrent appraisals completed in {end_time - start_time:.2f} seconds")
    print(f"Number of successful appraisals: {len([r for r in results if r is not None])}")
    
    return len([r for r in results if r is not None]) == len(agents)

async def main():
    """Run all async tests."""
    print("Starting async functionality tests...\n")
    
    tests = [
        ("Async LLM Calls", test_async_llm_calls),
        ("Async Simulation", test_async_simulation),
        ("Concurrent Operations", test_concurrent_operations)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = await test_func()
            results[test_name] = result
            print(f"{test_name}: {'PASSED' if result else 'FAILED'}\n")
        except Exception as e:
            print(f"{test_name}: FAILED with error: {e}\n")
            results[test_name] = False
    
    # Summary
    print("Test Summary:")
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    asyncio.run(main())
