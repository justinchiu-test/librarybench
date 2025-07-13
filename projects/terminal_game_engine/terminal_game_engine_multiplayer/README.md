# PyTermGame - Multiplayer Terminal Game Engine

A robust, feature-rich multiplayer game engine designed for creating competitive terminal-based games with real-time networking, matchmaking, and lag compensation.

## Overview

PyTermGame provides a comprehensive framework for building multiplayer terminal games with:
- Client-server architecture with authoritative game state
- Skill-based matchmaking and lobby systems
- Real-time spectator mode with replay recording
- Integrated chat with moderation and commands
- Advanced lag compensation for smooth gameplay
- Support for both TCP and UDP protocols

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd terminal_game_engine_multiplayer

# Create virtual environment
uv venv
source .venv/bin/activate

# Install the package
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Quick Start

### Creating a Game Server

```python
import asyncio
from pytermgame import GameServer

async def main():
    # Create game server
    server = GameServer(host="0.0.0.0", port=8888, tick_rate=60)
    
    # Register callbacks
    server.on_player_join(lambda player_id: print(f"Player {player_id} joined"))
    server.on_player_leave(lambda player_id: print(f"Player {player_id} left"))
    
    # Start server
    await server.start()
    print("Game server running on port 8888")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await server.stop()

asyncio.run(main())
```

### Creating a Game Client

```python
import asyncio
from pytermgame import NetworkClient

async def main():
    # Create client
    client = NetworkClient("player123")
    
    # Connect to server
    if await client.connect("localhost", 8888):
        print("Connected to server!")
        
        # Send player input
        await client.send_input({"move": "forward", "jump": True})
        
        # Send chat message
        await client.send_chat_message("Hello everyone!")
        
        # Handle game state updates
        client.on_game_state(lambda packet: print(f"Game update: {packet.data}"))
        
        # Keep running
        await asyncio.sleep(60)
        
        # Disconnect
        await client.disconnect()

asyncio.run(main())
```

### Setting Up Matchmaking

```python
from pytermgame import LobbySystem, MatchmakingEngine

# Initialize systems
lobby = LobbySystem()
matchmaking = MatchmakingEngine()

# Register players
for i in range(4):
    player_id = f"player{i}"
    matchmaking.register_player(player_id, skill_rating=1000 + i * 50)
    
# Join matchmaking queue
await lobby.start()
for player_id in players:
    lobby.join_matchmaking(player_id, matchmaking.player_profiles[player_id].skill_rating)

# Matches will be created automatically based on skill
```

## Core Features

### 1. Network Architecture

- **Protocol Support**: Both TCP (reliable) and UDP (fast) protocols
- **Packet System**: Type-safe packet definitions with automatic serialization
- **Connection Management**: Automatic reconnection and timeout handling
- **Rate Limiting**: Built-in protection against network flooding

### 2. Game Server

- **Authoritative State**: Server maintains the true game state
- **Tick-Based Updates**: Configurable tick rate (default 60 Hz)
- **Physics Simulation**: Basic physics with position and velocity
- **Input Validation**: Server validates all player inputs

### 3. Lobby & Matchmaking

- **Room System**: Create public/private game rooms
- **Skill-Based Matchmaking**: ELO-based rating system
- **Queue Management**: Dynamic skill tolerance for faster matches
- **Team Balancing**: Automatic creation of balanced teams

### 4. Spectator Mode

- **Live Viewing**: Watch ongoing games with configurable delay
- **Multiple Views**: Free camera, player follow, or overview modes
- **Replay Recording**: Automatic recording with compression
- **Anti-Cheat**: Built-in delay to prevent ghosting

### 5. Chat System

- **Multiple Channels**: All, team, and private messages
- **Moderation**: Profanity filter, spam detection, rate limiting
- **Commands**: Built-in command system with permissions
- **Admin Tools**: Mute, ban, and warning systems

### 6. Lag Compensation

- **Client Prediction**: Smooth movement without waiting for server
- **Server Reconciliation**: Authoritative correction of predictions
- **Entity Interpolation**: Smooth rendering of other players
- **Hit Verification**: Fair hit detection with latency compensation

## Usage Examples

### Creating a Custom Game Mode

```python
from pytermgame import GameServer, GameState

class CaptureTheFlagServer(GameServer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flags = {"red": {"x": 100, "y": 100}, "blue": {"x": 900, "y": 900}}
        
    async def on_player_input(self, player_id: str, input_data: dict):
        # Handle flag capture logic
        player = self.game_state.players.get(player_id)
        if not player:
            return
            
        # Check if player is near enemy flag
        team = self.get_player_team(player_id)
        enemy_flag = self.flags["blue" if team == "red" else "red"]
        
        distance = ((player.position["x"] - enemy_flag["x"]) ** 2 + 
                   (player.position["y"] - enemy_flag["y"]) ** 2) ** 0.5
                   
        if distance < 50:  # Capture radius
            await self.broadcast_event({
                "type": "flag_captured",
                "player": player_id,
                "team": team
            })
```

### Implementing Custom Chat Commands

```python
from pytermgame.chat import Command, CommandPermission

# Create custom command
def handle_stats(player_id: str, args: str):
    stats = get_player_stats(player_id)
    return {
        "type": "stats",
        "data": {
            "kills": stats.kills,
            "deaths": stats.deaths,
            "score": stats.score
        }
    }

# Register command
chat_manager.command_processor.register_command(Command(
    name="stats",
    description="Show your game statistics",
    usage="/stats",
    permission=CommandPermission.ALL,
    handler=handle_stats
))
```

### Advanced Lag Compensation

```python
from pytermgame import LagCompensator

# Initialize lag compensation
lag_comp = LagCompensator()

# Client-side prediction
def update_player_position(player_id: str, input: dict, delta_time: float):
    current_pos = get_player_position(player_id)
    current_vel = get_player_velocity(player_id)
    
    # Predict next position
    predicted_pos = lag_comp.predict_client_movement(
        player_id, current_pos, current_vel, input, delta_time
    )
    
    # Apply prediction locally
    set_player_position(player_id, predicted_pos)

# Server-side hit verification
def verify_shot(shooter_id: str, target_id: str, shot_data: dict):
    # Verify hit with lag compensation
    hit, target_pos = lag_comp.verify_hit(
        shooter_id, target_id,
        shot_data["position"],
        shot_data["timestamp"]
    )
    
    if hit:
        apply_damage(target_id, shot_data["damage"])
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pytermgame

# Run specific test module
pytest tests/test_network.py

# Generate JSON report (required)
pytest --json-report --json-report-file=pytest_results.json
```

## Performance Optimization

### Server Configuration

```python
# Optimize for high player count
server = GameServer(
    tick_rate=30,  # Lower tick rate for more players
    max_players=200,
    protocol_type=ProtocolType.UDP  # Use UDP for lower latency
)

# Configure lag compensation
server.lag_compensator.max_extrapolation_time = 0.1  # 100ms max
server.lag_compensator.enable_interpolation = True
```

### Network Optimization

```python
# Reduce bandwidth usage
server.network_server.packet_compression = True
server.broadcast_interval = 0.05  # 20 Hz state updates

# Prioritize important packets
packet.requires_ack = True  # For critical packets only
```

## Architecture

```
pytermgame/
├── network/          # Network layer (client/server, protocols, packets)
├── server/           # Game server (state management, tick system)
├── lobby/            # Lobby and matchmaking systems
├── spectator/        # Spectator mode and replay recording
├── chat/             # Chat system with moderation
├── lag_compensation/ # Client prediction and lag compensation
└── matchmaking/      # Skill-based matchmaking engine
```

## API Reference

### Key Classes

- `GameServer`: Main game server class
- `NetworkClient`: Client network interface
- `GameState`: Authoritative game state
- `LobbySystem`: Room and matchmaking management
- `SpectatorMode`: Spectator functionality
- `ChatManager`: Chat and command system
- `LagCompensator`: Lag compensation system
- `MatchmakingEngine`: Skill-based matchmaking

### Events and Callbacks

- `on_player_join(player_id)`: Player joined game
- `on_player_leave(player_id)`: Player left game
- `on_game_update(state, delta_time)`: Game tick update
- `on_message(message)`: Chat message received
- `on_match_found(room, team1, team2)`: Match created

## Best Practices

1. **Always validate input on the server** - Never trust client data
2. **Use appropriate tick rates** - 60 Hz for competitive, 30 Hz for casual
3. **Implement rate limiting** - Prevent spam and DoS attacks
4. **Enable lag compensation** - Essential for good player experience
5. **Monitor performance metrics** - Track latency, packet loss, and FPS
6. **Use replay recording sparingly** - Can consume significant memory
7. **Test with simulated latency** - Ensure game feels good at 100ms+

## Troubleshooting

### Common Issues

1. **High latency**: Switch to UDP protocol, reduce tick rate
2. **Desync issues**: Ensure all game logic runs on server
3. **Chat spam**: Adjust rate limiting parameters
4. **Matchmaking delays**: Increase skill tolerance over time
5. **Memory usage**: Limit replay buffer size, reduce history

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get performance metrics
metrics = game_server.get_server_stats()
print(f"Players: {metrics['player_count']}")
print(f"Tick rate: {metrics['tick_stats']['actual_tick_rate']}")

# Monitor lag compensation
lag_metrics = lag_compensator.get_metrics()
print(f"Prediction error: {lag_metrics['average_prediction_error']}")
```

## Contributing

Contributions are welcome! Please ensure:
- All tests pass with `pytest`
- Code follows PEP 8 style guidelines
- Type hints are included for all functions
- New features include comprehensive tests

## License

This project is provided as-is for educational and development purposes.