# PyTermGame - Multiplayer Game Engine

## Overview
A terminal-based game engine designed for creating competitive multiplayer games with robust networking, matchmaking systems, and real-time gameplay synchronization in terminal environments.

## Persona Description
A developer creating competitive terminal games who needs networking and lobby systems. She wants to enable real-time multiplayer gameplay in terminal environments.

## Key Requirements
1. **Client-server architecture for multiplayer games** - Essential for reliable multiplayer experiences with authoritative server logic, client prediction, state synchronization, connection management, and support for both TCP and UDP protocols for different game requirements.

2. **Lobby system with matchmaking support** - Critical for player engagement through game room creation, skill-based matchmaking, queue management, ready-up mechanisms, and automatic host migration to ensure smooth multiplayer sessions.

3. **Spectator mode with live game viewing** - Provides community features by allowing non-players to watch ongoing matches, delayed viewing to prevent cheating, multiple camera perspectives, and replay recording for later analysis.

4. **Chat system with command integration** - Enables player communication through in-game messaging, team chat channels, admin commands, profanity filtering, and rate limiting to maintain positive community interactions.

5. **Lag compensation for smooth gameplay** - Ensures fair competition by implementing client-side prediction, server reconciliation, interpolation for smooth movement, latency hiding techniques, and fair timestamp-based hit detection.

## Technical Requirements
- **Testability requirements**: Network code must be testable with mock connections, matchmaking algorithms must be deterministic, lag compensation must be verifiable, chat filtering must be comprehensive
- **Performance expectations**: Support 100+ concurrent players per server, sub-50ms round-trip time handling, 60 updates per second for smooth gameplay, efficient bandwidth usage under 10KB/s per player
- **Integration points**: Pluggable network transport layer, external matchmaking services, community moderation tools, tournament system APIs
- **Key constraints**: Must handle unreliable network conditions gracefully, work through common firewalls, no external networking libraries, support both LAN and internet play

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive multiplayer features including:
- Network manager handling client connections, packet serialization, and protocol abstraction
- Game server with authoritative state management, tick rate control, and client validation
- Lobby system supporting room creation, player matching, and session management
- Spectator framework with view synchronization, camera controls, and replay recording
- Chat manager with channels, moderation tools, and command processing
- Lag compensator implementing prediction, reconciliation, and fair hit detection
- Matchmaking engine with skill ratings, queue management, and balanced team creation

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Client-server communication maintains synchronization
  - Matchmaking creates balanced games within time constraints
  - Spectator views accurately reflect game state
  - Chat system filters inappropriate content
  - Lag compensation provides fair gameplay

- **Critical user scenarios that should be tested**:
  - Multiple players joining and leaving mid-game
  - Matchmaking with various skill levels
  - Network interruption and reconnection
  - Spectator joining ongoing match
  - Chat during active gameplay

- **Performance benchmarks that must be met**:
  - Handle 100 concurrent connections
  - Process 1000 messages per second
  - Matchmake 10 players in under 5 seconds
  - Synchronize game state in under 16ms
  - Compress network packets by 50%+

- **Edge cases and error conditions that must be handled properly**:
  - Network packet loss and reordering
  - Malicious client behavior
  - Server overload conditions
  - Disconnection during critical operations
  - Time synchronization issues

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - Network protocol fully tested
  - All matchmaking scenarios covered
  - Lag compensation edge cases
  - Security vulnerability tests

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria
Clear metrics indicating successful implementation:
- Client-server architecture supports stable multiplayer gameplay with 100+ concurrent players
- Lobby system efficiently matches players and manages game sessions
- Spectator mode provides smooth, synchronized viewing of live games
- Chat system enables communication while preventing abuse
- Lag compensation ensures fair and responsive gameplay across various network conditions

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
Use `uv venv` to setup virtual environments. From within the project directory, the environment can be activated with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```