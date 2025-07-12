# PyMemTrace - Memory Profiler for Game Development

PyMemTrace is a specialized memory profiling tool designed for game developers working with Python game engines. It provides real-time memory tracking during gameplay, asset lifecycle management, and performance optimization to ensure smooth gaming experiences without memory-related stutters or crashes.

## Features

### 1. Frame Memory Profiler
- **Per-frame memory tracking**: Monitor memory allocation/deallocation for each game frame
- **Spike detection**: Automatically detect and alert on memory spikes
- **Frame drop correlation**: Identify memory-related frame drops
- **Minimal overhead**: Less than 0.5ms per frame profiling overhead

### 2. Asset Memory Manager
- **Lifecycle tracking**: Monitor assets from load to unload
- **Memory heatmaps**: Visualize memory usage by asset type
- **Leak detection**: Identify orphaned assets and circular dependencies
- **Reference counting**: Track asset usage across game systems

### 3. Object Pool Analyzer
- **Pool efficiency metrics**: Measure allocation savings and GC impact
- **Automatic sizing**: Get pool size recommendations based on usage patterns
- **Allocation pattern analysis**: Understand object allocation behavior
- **Cross-pool comparison**: Compare efficiency across different pools

### 4. Memory Budget System
- **Hierarchical budgets**: Create parent-child budget relationships
- **Automatic eviction**: Configurable strategies (LRU, LFU, Priority, Size, Age, Hybrid)
- **Violation alerts**: Get notified when approaching or exceeding limits
- **Platform-aware**: Respect platform-specific memory constraints

### 5. Platform Memory Monitor
- **Multi-platform support**: PC (Windows/Linux/Mac), Mobile (iOS/Android), Consoles, Web
- **Platform-specific recommendations**: Get optimization suggestions for each platform
- **Memory bank management**: Console-specific memory bank tracking
- **Compatibility estimation**: Check if your game fits on different platforms

## Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
uv pip install -e .
```

## Usage Examples

### Basic Frame Profiling

```python
from pymemtrace import FrameMemoryProfiler

# Initialize profiler
profiler = FrameMemoryProfiler(max_frame_history=1000, spike_threshold=0.1)
profiler.start_profiling()

# Profile game frames
for frame_num in range(100):
    with profiler.frame():
        # Your game frame logic here
        render_scene()
        update_physics()
        process_input()

# Get frame statistics
stats = profiler.get_frame_stats()
print(f"Frame {stats.frame_number}: {stats.frame_duration*1000:.2f}ms, {stats.peak_memory/1024/1024:.1f}MB")

# Detect frame drops
dropped = profiler.detect_frame_drops(target_fps=60)
print(f"Dropped frames: {dropped}")
```

### Asset Memory Management

```python
from pymemtrace import AssetMemoryManager
from pymemtrace.asset_manager import AssetType

# Initialize manager
asset_manager = AssetMemoryManager()

# Register game assets
texture_data = load_texture("player.png")
asset_manager.register_asset(
    asset_id="player_texture",
    asset_type=AssetType.TEXTURE,
    asset_object=texture_data,
    metadata={"width": 1024, "height": 1024, "format": "RGBA"}
)

# Track asset lifecycle
asset_manager.update_asset_state("player_texture", AssetState.IN_USE)

# Get memory heatmap
heatmap = asset_manager.get_memory_heatmap(top_n=10)
print(f"Total asset memory: {heatmap.total_memory/1024/1024:.1f}MB")
print(f"Top memory users: {heatmap.hotspots}")

# Detect memory leaks
leaks = asset_manager.detect_memory_leaks()
if leaks:
    print(f"Potential memory leaks detected: {leaks}")
```

### Object Pooling

```python
from pymemtrace import ObjectPoolAnalyzer

# Create analyzer
analyzer = ObjectPoolAnalyzer()

# Create pools for game objects
particle_pool = analyzer.create_pool(
    Particle,
    initial_size=100,
    max_size=500,
    name="ParticlePool"
)

enemy_pool = analyzer.create_pool(
    Enemy,
    initial_size=20,
    max_size=50,
    name="EnemyPool"
)

# Use pools in game loop
for _ in range(10):
    particle = particle_pool.acquire()
    # Use particle
    particle_pool.release(particle)

# Analyze efficiency
efficiency = analyzer.analyze_efficiency("ParticlePool")
print(f"Allocation reduction: {efficiency['allocation_reduction']:.1%}")
print(f"GC impact reduction: {efficiency['gc_impact_reduction']:.2f}")

# Get pool size suggestions
suggestion = analyzer.suggest_pool_size("ParticlePool")
print(f"Suggested pool size: {suggestion['suggested_size']} (current: {suggestion['current_size']})")
```

### Memory Budget Management

```python
from pymemtrace import MemoryBudgetSystem
from pymemtrace.budget_system import EvictionStrategy

# Initialize budget system
budget_system = MemoryBudgetSystem()
budget_system.set_eviction_strategy(EvictionStrategy.HYBRID)

# Create hierarchical budgets
budget_system.create_budget("total_game", max_bytes=512*1024*1024)  # 512MB
budget_system.create_budget("graphics", max_bytes=256*1024*1024, parent="total_game")
budget_system.create_budget("audio", max_bytes=128*1024*1024, parent="total_game")
budget_system.create_budget("gameplay", max_bytes=128*1024*1024, parent="total_game")

# Register assets with budgets
budget_system.register_asset("level_texture", "graphics", size=50*1024*1024, priority=10)
budget_system.register_asset("bg_music", "audio", size=20*1024*1024, priority=5)

# Add violation callback
def on_budget_violation(violation):
    print(f"Budget violation: {violation.budget_name} - {violation.message}")

budget_system.add_violation_callback(on_budget_violation)

# Get budget status
status = budget_system.get_budget_status("graphics")
print(f"Graphics budget: {status['usage_percentage']:.1f}% used")
```

### Platform-Specific Monitoring

```python
from pymemtrace import PlatformMemoryMonitor

# Initialize monitor
monitor = PlatformMemoryMonitor()

# Get current platform status
status = monitor.get_current_status()
print(f"Platform: {status.platform.value}")
print(f"Memory usage: {status.memory_percentage:.1f}%")
print(f"Critical: {status.is_critical}")

# Get platform-specific recommendations
if status.recommendations:
    print("Recommendations:")
    for rec in status.recommendations:
        print(f"  - {rec}")

# Check compatibility with other platforms
compatibility = monitor.estimate_platform_compatibility(status.process_memory)
for platform, compat in compatibility.items():
    if not compat["meets_recommended"]:
        print(f"{platform}: Optimization needed")

# Get optimization guide
guide = monitor.get_platform_optimization_guide()
print(f"Recommended texture formats: {guide['texture_formats']}")
print(f"Memory techniques: {guide['memory_techniques']}")
```

## Running Tests

```bash
# Install test dependencies
uv pip install pytest pytest-json-report

# Run all tests with JSON report
pytest --json-report --json-report-file=pytest_results.json

# Run specific test module
pytest tests/test_frame_profiler.py -v

# Run with coverage
pytest --cov=pymemtrace --cov-report=html
```

## Performance Considerations

- **Frame profiling overhead**: < 0.5ms per frame at 60 FPS
- **Asset tracking**: Supports 10,000+ game objects efficiently
- **Pool monitoring**: < 0.1ms overhead per allocation
- **Memory snapshots**: < 5ms generation time
- **Platform monitoring**: Minimal impact with 1-second update intervals

## Best Practices

1. **Start profiling early**: Enable profiling during development to catch issues early
2. **Set appropriate budgets**: Use platform-specific memory limits as guidelines
3. **Monitor frame drops**: Correlate memory spikes with performance issues
4. **Use object pooling**: Especially for frequently created/destroyed objects
5. **Regular leak checks**: Run leak detection after major gameplay sessions
6. **Platform testing**: Test on target platforms with their specific constraints

## License

This project is part of PyMemTrace for game development optimization.