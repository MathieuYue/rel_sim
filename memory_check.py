#!/usr/bin/env python3
"""
Memory usage analysis script to help identify what's consuming RAM
and provide recommendations for freeing up memory for simulations.
"""

import psutil
import os
import subprocess
import platform

def get_memory_info():
    """Get detailed memory information."""
    memory = psutil.virtual_memory()
    
    print("=== Memory Usage Analysis ===")
    print(f"Total RAM: {memory.total / (1024**3):.1f} GB")
    print(f"Available RAM: {memory.available / (1024**3):.1f} GB")
    print(f"Used RAM: {memory.used / (1024**3):.1f} GB")
    print(f"Memory Usage: {memory.percent:.1f}%")
    
    if hasattr(memory, 'cached'):
        print(f"Cached: {memory.cached / (1024**3):.1f} GB")
    if hasattr(memory, 'buffers'):
        print(f"Buffers: {memory.buffers / (1024**3):.1f} GB")
    
    print()

def get_top_memory_processes():
    """Get the top memory-consuming processes."""
    print("=== Top Memory-Consuming Processes ===")
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'memory_mb': proc.info['memory_info'].rss / (1024**2),
                'memory_percent': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Sort by memory usage
    processes.sort(key=lambda x: x['memory_mb'], reverse=True)
    
    print(f"{'PID':<8} {'Memory (MB)':<12} {'Memory %':<10} {'Process Name'}")
    print("-" * 50)
    
    for proc in processes[:15]:  # Top 15 processes
        print(f"{proc['pid']:<8} {proc['memory_mb']:<12.1f} {proc['memory_percent']:<10.1f} {proc['name']}")
    
    print()

def get_system_info():
    """Get system information."""
    print("=== System Information ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print(f"CPU Cores: {psutil.cpu_count()}")
    print(f"CPU Usage: {psutil.cpu_percent(interval=1):.1f}%")
    print()

def get_recommendations():
    """Provide memory optimization recommendations."""
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    
    print("=== Memory Optimization Recommendations ===")
    
    if available_gb < 2:
        print("⚠️  CRITICAL: Very low available memory!")
        print("   - Close all unnecessary applications immediately")
        print("   - Restart your computer if possible")
        print("   - Consider running simulations later")
    elif available_gb < 4:
        print("⚠️  WARNING: Low available memory")
        print("   - Close web browsers and other large applications")
        print("   - Restart your IDE/editor")
        print("   - Use smaller batch sizes for simulations")
    else:
        print("✅ Good available memory for simulations")
    
    print()
    print("General recommendations:")
    print("1. Close web browsers (especially Chrome/Firefox)")
    print("2. Close unused applications and terminal windows")
    print("3. Restart your IDE/editor")
    print("4. Clear system cache (see commands below)")
    print("5. Use smaller simulation batch sizes")
    print("6. Monitor memory usage during simulations")
    print()

def get_optimization_commands():
    """Provide system-specific optimization commands."""
    system = platform.system()
    
    print("=== System-Specific Commands ===")
    
    if system == "Darwin":  # macOS
        print("macOS optimization commands:")
        print("  # Clear system cache")
        print("  sudo purge")
        print("  # Clear DNS cache")
        print("  sudo dscacheutil -flushcache")
        print("  sudo killall -HUP mDNSResponder")
        print("  # Check memory pressure")
        print("  memory_pressure")
        
    elif system == "Linux":
        print("Linux optimization commands:")
        print("  # Clear page cache, dentries, and inodes")
        print("  sudo sync && sudo echo 3 | sudo tee /proc/sys/vm/drop_caches")
        print("  # Clear swap")
        print("  sudo swapoff -a && sudo swapon -a")
        print("  # Check memory usage")
        print("  free -h")
        print("  # Monitor memory in real-time")
        print("  watch -n 1 'free -h'")
        
    elif system == "Windows":
        print("Windows optimization commands:")
        print("  # Clear memory (run as administrator)")
        print("  EmptyStandbyList.exe")
        print("  # Or use built-in tools")
        print("  # Task Manager -> Performance -> Memory -> Clear memory")
        
    print()

def check_simulation_readiness():
    """Check if the system is ready for simulations."""
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    cpu_usage = psutil.cpu_percent(interval=1)
    
    print("=== Simulation Readiness Check ===")
    
    # Memory check
    if available_gb >= 4:
        print("✅ Memory: Sufficient for multiple simulations")
        recommended_sims = min(8, int(available_gb / 0.5))  # 500MB per sim
    elif available_gb >= 2:
        print("⚠️  Memory: Limited, use small batches")
        recommended_sims = min(4, int(available_gb / 0.5))
    else:
        print("❌ Memory: Insufficient, free up memory first")
        recommended_sims = 0
    
    # CPU check
    if cpu_usage < 50:
        print("✅ CPU: Ready for concurrent processing")
    elif cpu_usage < 80:
        print("⚠️  CPU: Moderate load, monitor during simulations")
    else:
        print("❌ CPU: High load, consider waiting")
        recommended_sims = min(recommended_sims, 2)
    
    print(f"\nRecommended concurrent simulations: {recommended_sims}")
    
    if recommended_sims == 0:
        print("\n❌ System not ready for simulations. Please free up memory first.")
    elif recommended_sims <= 2:
        print("\n⚠️  System ready for limited simulations. Consider freeing up more memory.")
    else:
        print("\n✅ System ready for simulations!")
    
    print()

def main():
    """Main function to run memory analysis."""
    print("Memory Usage Analysis for Simulation Optimization")
    print("=" * 60)
    print()
    
    get_system_info()
    get_memory_info()
    get_top_memory_processes()
    get_recommendations()
    get_optimization_commands()
    check_simulation_readiness()
    
    print("=" * 60)
    print("Run this script again after optimizing to see improvements.")

if __name__ == "__main__":
    main()
