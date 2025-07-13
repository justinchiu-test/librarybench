# Process Resource Monitor - Game Server Administrator Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Luna, a game server admin managing multiplayer game instances. The library should monitor per-game-session resource usage to optimize server allocation and prevent lag during peak gaming hours.

## Core Requirements

### 1. Game Session Isolation with Per-Match Monitoring
- Track individual game server processes and their sessions
- Isolate resource usage per match/room/instance
- Monitor game state transitions and resource impact
- Track lobby, loading, and active gameplay phases
- Support multiple game engines (Unity, Unreal, custom)

### 2. Player Count Correlation with Resource Usage
- Monitor resource scaling with player count increases
- Track per-player resource overhead
- Identify resource usage patterns for different game modes
- Predict resource needs based on matchmaking queue
- Analyze bot vs human player resource differences

### 3. Network Latency Impact on Process Behavior
- Correlate network conditions with server resource usage
- Track packet processing overhead during high latency
- Monitor lag compensation algorithm resource cost
- Identify network-induced CPU spikes
- Measure netcode optimization effectiveness

### 4. Dynamic Server Scaling Based on Player Activity
- Predict player population peaks and valleys
- Automatically recommend server spin-up/down times
- Track server warm-up and cool-down resource usage
- Optimize instance placement for regional player bases
- Monitor cross-region server migration impact

### 5. Cheat Detection through Abnormal Resource Patterns
- Identify unusual resource consumption patterns
- Detect speed hacks via abnormal packet rates
- Monitor memory manipulation attempts
- Track suspicious process spawning patterns
- Correlate anti-cheat service resource overhead

## Technical Specifications

### Data Collection
- Direct integration with game server APIs
- Real-time packet analysis for network metrics
- Player action correlation with resource spikes
- Game state monitoring via server logs
- Memory pattern analysis for cheat detection

### API Design
```python
# Example usage
monitor = GameServerMonitor()

# Configure game server monitoring
monitor.add_game_server(
    name="minecraft-survival-01",
    type="minecraft",
    port=25565,
    max_players=100
)

# Track game session resources
session_stats = monitor.get_session_resources(
    server="minecraft-survival-01",
    session_id="abc123",
    metrics=["cpu", "memory", "network", "disk"]
)

# Analyze player count impact
player_analysis = monitor.analyze_player_scaling(
    server="minecraft-survival-01",
    time_range="24h",
    correlation_metrics=["tps", "cpu_usage", "memory_growth"]
)

# Monitor network impact
network_impact = monitor.get_network_resource_correlation(
    include_regions=True,
    latency_buckets=[0, 50, 100, 200, 500]
)

# Generate scaling recommendations
scaling = monitor.recommend_scaling(
    forecast_hours=6,
    target_player_experience="smooth",  # or "responsive" or "economical"
    include_cost_analysis=True
)

# Detect suspicious patterns
anomalies = monitor.detect_cheat_patterns(
    sensitivity="high",
    include_player_correlation=True,
    time_window="1h"
)
```

### Testing Requirements
- Simulated game session testing with bot players
- Network condition simulation (latency, packet loss)
- Load testing with varying player counts
- Cheat pattern detection validation
- Use pytest with pytest-json-report for test result formatting
- Test with multiple game server types

### Performance Targets
- Monitor 100+ concurrent game sessions
- Track 10,000+ concurrent players across all servers
- Detect anomalies within 30 seconds
- Process 1 million packets per second
- Generate scaling recommendations in <5 seconds

## Implementation Constraints
- Python 3.8+ compatibility required
- Use Python standard library plus: psutil, scapy, requests, numpy
- No GUI components - this is a backend library only
- Support multiple game server architectures
- Minimal impact on game server performance (<2% overhead)

## Deliverables
1. Core Python library with game server monitoring
2. Player impact analysis and prediction engine
3. Network correlation and optimization toolkit
4. Automatic scaling recommendation system
5. CLI tool for game server health monitoring and alerts