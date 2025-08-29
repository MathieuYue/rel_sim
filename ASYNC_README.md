# Async Simulation Pipeline

This document describes the new asynchronous functionality that allows you to run multiple simulation pipelines concurrently.

## Overview

The simulation pipeline has been updated to support asynchronous execution, enabling you to run multiple simulations simultaneously. This is particularly useful for:

- Running multiple agent combinations in parallel
- Conducting large-scale relationship simulations
- Reducing total execution time when running multiple scenarios
- Batch processing of different personality combinations

## Key Changes

### 1. Async LLM Utilities (`utils/llm_utils.py`)

New async versions of LLM call functions:
- `model_call_structured_async()` - Async version of structured model calls
- `model_call_unstructured_async()` - Async version of unstructured model calls
- `get_text_embedding_async()` - Async version of text embedding calls

### 2. Async Relationship Agent (`relationship_agent/relationship_agent.py`)

New async methods:
- `make_choices_async()` - Async version of agent choice making
- `act_async()` - Async version of agent actions
- `reflect_async()` - Async version of agent reflection
- `appraise_async()` - Async version of emotion appraisal
- `batch_appraise_memory_async()` - Async version of batch memory appraisal

### 3. Async Scene Master (`scene_master/scene_master.py`)

New async methods:
- `initialize_async()` - Async scene initialization
- `generate_context_async()` - Async context generation
- `progress_async()` - Async scene progression
- `summarize_async()` - Async scene summarization
- `commitment_score_async()` - Async commitment scoring
- `next_scene_async()` - Async scene transition

### 4. Async Simulation (`simulation/simulation.py`)

New async methods:
- `run_auto_async()` - Async automatic simulation execution
- `run_scene_async()` - Async single scene execution

## Retry Logic for JSON Parsing

All LLM-calling functions now include robust retry logic to handle cases where the LLM output doesn't match the expected JSON schema format:

### How It Works

1. **Automatic Retries**: Each function will retry up to 3 times if the LLM response cannot be parsed as valid JSON
2. **Error Handling**: If parsing fails after 3 attempts, the function will either:
   - Raise an exception (for critical operations)
   - Return a fallback value (for non-critical operations like `appraise()`)
3. **Detailed Logging**: Each retry attempt is logged with the specific error message
4. **Raw Response Logging**: If all retries fail, the raw LLM response is logged for debugging

### Functions with Retry Logic

**RelationshipAgent:**
- `make_choices()` / `make_choices_async()`
- `act()` / `act_async()`
- `reflect()` / `reflect_async()`
- `appraise()` / `appraise_async()`
- `batch_appraise_memory()` / `batch_appraise_memory_async()`

**SceneMaster:**
- `initialize()` / `initialize_async()`
- `generate_context()` / `generate_context_async()`
- `progress()` / `progress_async()`
- `summarize()` / `summarize_async()`
- `commitment_score()` / `commitment_score_async()`
- `next_scene()` / `next_scene_async()`

### Example Retry Behavior

```python
# If the LLM returns malformed JSON, the system will retry:
# Attempt 1: Parse failed, retrying...
# Attempt 2: Parse failed, retrying...
# Attempt 3: Parse failed, retrying...
# Failed to parse LLM response after 3 attempts: [error details]
# Raw response: [malformed JSON response]
```

## Usage Examples

### Running a Single Async Simulation

```python
import asyncio
from relationship_agent.relationship_agent import RelationshipAgent
from scene_master.scene_master import SceneMaster
from simulation.simulation import Simulation

async def run_single_simulation():
    # Create agents
    agent1 = RelationshipAgent("Alice", "A thoughtful introvert who values deep conversations.")
    agent2 = RelationshipAgent("Bob", "An outgoing extrovert who loves socializing.")
    
    # Create scene master and simulation
    scene_master = SceneMaster(agent1, agent2)
    simulation = Simulation(scene_master, agent1, agent2)
    
    # Run simulation asynchronously
    commitment_log = await simulation.run_auto_async(num_interactions_per_scene=3)
    return commitment_log

# Run the simulation
results = asyncio.run(run_single_simulation())
```

### Running Multiple Simulations Concurrently

```python
import asyncio
from relationship_agent.relationship_agent import RelationshipAgent
from scene_master.scene_master import SceneMaster
from simulation.simulation import Simulation

async def run_single_simulation(simulation_id, agent1_name, agent1_persona, agent2_name, agent2_persona):
    agent1 = RelationshipAgent(agent1_name, agent1_persona)
    agent2 = RelationshipAgent(agent2_name, agent2_persona)
    scene_master = SceneMaster(agent1, agent2)
    simulation = Simulation(scene_master, agent1, agent2)
    
    commitment_log = await simulation.run_auto_async(num_interactions_per_scene=2)
    return {"simulation_id": simulation_id, "commitment_log": commitment_log}

async def run_multiple_simulations():
    # Define multiple agent configurations
    configs = [
        {
            "simulation_id": "sim_1",
            "agent1_name": "Alex",
            "agent1_persona": "A thoughtful introvert who values deep conversations.",
            "agent2_name": "Jordan",
            "agent2_persona": "An outgoing extrovert who loves socializing."
        },
        {
            "simulation_id": "sim_2",
            "agent1_name": "Maya",
            "agent1_persona": "A career-driven professional who prioritizes work-life balance.",
            "agent2_name": "Sam",
            "agent2_persona": "A creative artist who lives in the moment."
        }
    ]
    
    # Create tasks for all simulations
    tasks = [
        run_single_simulation(**config) for config in configs
    ]
    
    # Run all simulations concurrently
    results = await asyncio.gather(*tasks)
    return results

# Run multiple simulations
results = asyncio.run(run_multiple_simulations())
```

### Using the Provided Scripts

1. **Test the async functionality:**
   ```bash
   python test_async_functionality.py
   ```

2. **Test the retry logic:**
   ```bash
   python test_retry_logic.py
   ```

3. **Run multiple simulations concurrently:**
   ```bash
   python run_multiple_simulations.py
   ```

## Performance Benefits

- **Concurrent Execution**: Multiple simulations can run simultaneously instead of sequentially
- **Reduced Total Time**: When running multiple simulations, the total time is significantly reduced
- **Better Resource Utilization**: CPU and network resources are used more efficiently
- **Scalability**: Easy to scale up to run dozens or hundreds of simulations
- **Robustness**: Retry logic ensures simulations continue even with occasional malformed LLM responses

## Backward Compatibility

All existing synchronous methods remain unchanged and functional:
- `RelationshipAgent.make_choices()`
- `RelationshipAgent.appraise()`
- `SceneMaster.initialize()`
- `SceneMaster.progress()`
- `Simulation.run_auto()`

You can continue using the existing synchronous API while gradually migrating to the async version.

## Error Handling

The async methods include comprehensive error handling:
- **Retry Logic**: Automatic retries for malformed JSON responses
- **Exception Isolation**: Exceptions in individual simulations don't affect other concurrent simulations
- **Failed Simulation Reporting**: Failed simulations are reported separately from successful ones
- **Graceful Degradation**: Non-critical functions return fallback values instead of crashing

## Best Practices

1. **Resource Management**: Be mindful of API rate limits when running many concurrent simulations
2. **Memory Usage**: Each simulation instance uses memory, so monitor usage with large numbers of concurrent simulations
3. **Error Handling**: The retry logic handles most JSON parsing issues automatically
4. **Testing**: Use the provided test scripts to verify functionality before running large-scale simulations
5. **Monitoring**: Watch for retry messages in logs to identify potential prompt or schema issues

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're importing the async functions correctly
2. **Runtime Errors**: Make sure you're using `await` with async functions
3. **Memory Issues**: Reduce the number of concurrent simulations if you encounter memory problems
4. **JSON Parsing Failures**: Check logs for retry messages and raw responses

### Debugging

- Use the test scripts to verify basic functionality
- Check that your API keys are properly configured
- Monitor network requests and responses for API-related issues
- Look for retry messages in logs to identify problematic prompts or schemas
- Examine raw responses when all retries fail to understand the issue
