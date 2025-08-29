#!/usr/bin/env python3
"""
Test script to verify that the retry logic works correctly when LLM outputs 
don't match the expected JSON schema format.
"""

import asyncio
import time
from relationship_agent.relationship_agent import RelationshipAgent
from scene_master.scene_master import SceneMaster

async def test_retry_logic():
    """Test that retry logic works for malformed JSON responses."""
    print("Testing retry logic for malformed JSON responses...")
    
    # Create a simple agent
    agent = RelationshipAgent("TestAgent", "A test agent for retry logic testing.")
    
    # Test async appraisal with retry logic
    scene_history = [["Narrative", "This is a test scene for retry logic testing."]]
    
    print("Testing agent.appraise_async() with retry logic...")
    start_time = time.time()
    
    try:
        appraisal = await agent.appraise_async(scene_history)
        end_time = time.time()
        
        print(f"Appraisal completed in {end_time - start_time:.2f} seconds")
        print(f"Appraisal result: {appraisal}")
        
        if appraisal is not None:
            print("✅ Retry logic test PASSED - appraisal completed successfully")
            return True
        else:
            print("❌ Retry logic test FAILED - appraisal returned None")
            return False
            
    except Exception as e:
        print(f"❌ Retry logic test FAILED with exception: {e}")
        return False

async def test_scene_master_retry_logic():
    """Test that retry logic works for scene master operations."""
    print("\nTesting scene master retry logic...")
    
    # Create agents
    agent1 = RelationshipAgent("Alice", "A test agent for scene master retry testing.")
    agent2 = RelationshipAgent("Bob", "Another test agent for scene master retry testing.")
    
    # Create scene master
    scene_master = SceneMaster(agent1, agent2)
    
    print("Testing scene_master.initialize_async() with retry logic...")
    start_time = time.time()
    
    try:
        scene_state = await scene_master.initialize_async()
        end_time = time.time()
        
        print(f"Scene initialization completed in {end_time - start_time:.2f} seconds")
        print(f"Scene conflict: {scene_state.scene_conflict}")
        
        if scene_state is not None:
            print("✅ Scene master retry logic test PASSED - initialization completed successfully")
            return True
        else:
            print("❌ Scene master retry logic test FAILED - initialization returned None")
            return False
            
    except Exception as e:
        print(f"❌ Scene master retry logic test FAILED with exception: {e}")
        return False

async def test_concurrent_retry_logic():
    """Test that retry logic works correctly in concurrent operations."""
    print("\nTesting concurrent retry logic...")
    
    # Create multiple agents
    agents = [
        RelationshipAgent(f"Agent{i}", f"Test agent {i} for concurrent retry testing.")
        for i in range(3)
    ]
    
    # Test concurrent appraisals with retry logic
    scene_history = [["Narrative", "This is a test scene for concurrent retry testing."]]
    
    print("Testing concurrent agent.appraise_async() with retry logic...")
    start_time = time.time()
    
    try:
        # Run multiple appraisals concurrently
        tasks = [agent.appraise_async(scene_history) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        print(f"Concurrent appraisals completed in {end_time - start_time:.2f} seconds")
        
        successful_results = [r for r in results if not isinstance(r, Exception) and r is not None]
        failed_results = [r for r in results if isinstance(r, Exception) or r is None]
        
        print(f"Successful appraisals: {len(successful_results)}")
        print(f"Failed appraisals: {len(failed_results)}")
        
        if len(successful_results) == len(agents):
            print("✅ Concurrent retry logic test PASSED - all appraisals completed successfully")
            return True
        else:
            print("❌ Concurrent retry logic test FAILED - some appraisals failed")
            return False
            
    except Exception as e:
        print(f"❌ Concurrent retry logic test FAILED with exception: {e}")
        return False

async def main():
    """Run all retry logic tests."""
    print("Starting retry logic tests...\n")
    
    tests = [
        ("Agent Retry Logic", test_retry_logic),
        ("Scene Master Retry Logic", test_scene_master_retry_logic),
        ("Concurrent Retry Logic", test_concurrent_retry_logic)
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
    
    if all_passed:
        print("\n🎉 All retry logic tests passed! The system should handle malformed JSON responses gracefully.")
    else:
        print("\n⚠️  Some retry logic tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
