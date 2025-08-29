# Simulation Concurrency Guide

This guide helps you determine the optimal number of concurrent simulations to run based on your system resources, API limits, and use case.

## Quick Recommendations

### Based on System Type

| System Type | Recommended Concurrent Simulations | Notes |
|-------------|-----------------------------------|-------|
| **Laptop (8GB RAM, 4 cores)** | 2-4 | Conservative approach for stability |
| **Desktop (16GB RAM, 8 cores)** | 4-8 | Good balance of performance and stability |
| **Workstation (32GB+ RAM, 16+ cores)** | 8-16 | Can handle higher concurrency |
| **Server/Cloud Instance** | 16-32+ | Depends on instance size and API limits |

### Based on Use Case

| Use Case | Recommended Concurrent Simulations | Reasoning |
|----------|-----------------------------------|-----------|
| **Development/Testing** | 2-4 | Fast iteration, easy debugging |
| **Research/Experimentation** | 4-8 | Good throughput for data collection |
| **Production/Batch Processing** | 8-16+ | Maximum efficiency, monitor carefully |
| **Large-scale Studies** | 16-32+ | Requires robust infrastructure |

## Factors to Consider

### 1. **System Resources**

**CPU:**
- Each simulation uses CPU for JSON parsing and data processing
- Recommended: 1-2 simulations per CPU core
- Monitor with: `htop` or Task Manager

**Memory:**
- Each simulation instance uses ~100-500MB RAM
- Recommended: Ensure 2-4GB free RAM for other processes
- Monitor with: `free -h` or Task Manager

**Storage:**
- Simulations generate logs and save files
- Ensure sufficient disk space for your batch size

### 2. **API Limits**

**Lambda API (Primary):**
- Rate limits vary by plan
- Monitor for 429 (Too Many Requests) errors
- Consider implementing exponential backoff

**OpenAI API (Embeddings):**
- Separate rate limits for embeddings
- Usually higher limits than chat completions

### 3. **Network Bandwidth**

- Each LLM call requires network I/O
- High concurrency = more network requests
- Consider your internet connection speed

## Testing Your Optimal Concurrency

### Step 1: Run the Analysis Script

```bash
# Install psutil if not already installed
pip install psutil

# Run the concurrency analysis
python simulation_limits_guide.py
```

This script will:
- Analyze your system resources
- Test different concurrency levels
- Find the optimal number for your setup

### Step 2: Manual Testing

```python
import asyncio
from run_multiple_simulations import run_single_simulation

async def test_concurrency_level(num_simulations):
    configs = [
        {
            "simulation_id": f"test_{i}",
            "agent1_name": f"Agent1_{i}",
            "agent1_persona": "A test agent for concurrency testing.",
            "agent2_name": f"Agent2_{i}",
            "agent2_persona": "Another test agent for concurrency testing."
        }
        for i in range(num_simulations)
    ]
    
    tasks = [run_single_simulation(**config) for config in configs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = len([r for r in results if isinstance(r, dict) and r.get("status") == "completed"])
    print(f"Success rate: {successful}/{num_simulations} ({successful/num_simulations*100:.1f}%)")
    
    return successful == num_simulations

# Test different levels
for level in [2, 4, 8, 16]:
    print(f"\nTesting {level} concurrent simulations...")
    success = await test_concurrency_level(level)
    if not success:
        print(f"Stopping at {level} - too many failures")
        break
```

## Practical Guidelines

### Starting Point

1. **Begin Conservative**: Start with 2-4 concurrent simulations
2. **Monitor Resources**: Watch CPU, memory, and network usage
3. **Check for Errors**: Look for API rate limits or timeouts
4. **Gradually Increase**: If stable, try doubling the number

### Warning Signs

**Reduce concurrency if you see:**
- High CPU usage (>90%)
- High memory usage (>85%)
- API rate limit errors (429)
- Network timeouts
- Failed simulations (>10% failure rate)
- System becoming unresponsive

**Good indicators:**
- CPU usage: 60-80%
- Memory usage: 70-85%
- <5% simulation failures
- Consistent completion times

### Optimization Tips

1. **Batch Size**: Run simulations in batches rather than all at once
2. **Monitoring**: Use the retry logic logs to identify issues
3. **Scheduling**: Run heavy batches during off-peak hours
4. **Caching**: Consider caching common LLM responses if applicable

## Example Configurations

### Development Setup (Laptop)
```python
# Conservative development setup
concurrent_simulations = 2
batch_size = 10
```

### Research Setup (Desktop)
```python
# Balanced research setup
concurrent_simulations = 6
batch_size = 50
```

### Production Setup (Server)
```python
# High-throughput production setup
concurrent_simulations = 16
batch_size = 100
```

## Cost Considerations

### API Costs
- Each simulation makes multiple LLM calls
- Higher concurrency = faster completion = same total cost
- Monitor API usage to stay within budget

### Infrastructure Costs
- Higher concurrency may require better hardware
- Consider cloud instances for large-scale runs
- Balance between speed and cost

## Troubleshooting

### Common Issues

**High Failure Rate:**
- Reduce concurrency
- Check API rate limits
- Verify network connectivity
- Monitor system resources

**Slow Performance:**
- Check if CPU/memory is saturated
- Verify API response times
- Consider reducing batch size

**API Errors:**
- Implement exponential backoff
- Check API key validity
- Monitor rate limits
- Consider API plan upgrades

### Monitoring Commands

```bash
# Monitor system resources
htop
free -h
df -h

# Monitor network
iftop
netstat -i

# Monitor processes
ps aux | grep python
```

## Advanced Configuration

### Custom Concurrency Control

```python
import asyncio
import aiohttp

# Custom semaphore for API rate limiting
api_semaphore = asyncio.Semaphore(10)  # Max 10 concurrent API calls

async def rate_limited_simulation(config):
    async with api_semaphore:
        return await run_single_simulation(**config)

# Use with your simulation runner
tasks = [rate_limited_simulation(config) for config in configs]
results = await asyncio.gather(*tasks)
```

### Adaptive Concurrency

```python
async def adaptive_concurrency_runner(configs):
    """Dynamically adjust concurrency based on success rate."""
    base_concurrency = 4
    max_concurrency = 16
    
    current_concurrency = base_concurrency
    
    for batch_start in range(0, len(configs), current_concurrency):
        batch = configs[batch_start:batch_start + current_concurrency]
        
        tasks = [run_single_simulation(**config) for config in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_rate = len([r for r in results if isinstance(r, dict) and r.get("status") == "completed"]) / len(results)
        
        # Adjust concurrency based on success rate
        if success_rate > 0.95 and current_concurrency < max_concurrency:
            current_concurrency = min(current_concurrency * 2, max_concurrency)
        elif success_rate < 0.8 and current_concurrency > base_concurrency:
            current_concurrency = max(current_concurrency // 2, base_concurrency)
        
        print(f"Success rate: {success_rate:.2f}, Concurrency: {current_concurrency}")
```

## Summary

The optimal number of concurrent simulations depends on your specific setup, but here are the key principles:

1. **Start conservative** (2-4 simulations)
2. **Monitor resources** (CPU, memory, network)
3. **Watch for errors** (API limits, failures)
4. **Gradually optimize** (increase until you hit limits)
5. **Consider costs** (API usage, infrastructure)

Use the provided analysis script to find the optimal configuration for your specific system and use case.
