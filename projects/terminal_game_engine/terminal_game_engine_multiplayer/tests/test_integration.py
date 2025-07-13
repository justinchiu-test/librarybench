"""Integration tests for PyTermGame"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock

from pytermgame import (
    NetworkClient, NetworkServer, GameServer, LobbySystem,
    SpectatorMode, ChatManager, LagCompensator, MatchmakingEngine
)
from pytermgame.network import PacketType, ProtocolType
from pytermgame.lobby import RoomSettings
from pytermgame.chat import ChatChannel
from pytermgame.server.game_state import PlayerStatus


@pytest.mark.asyncio
async def test_full_game_flow():
    """Test complete game flow from matchmaking to gameplay"""
    # Initialize systems
    lobby = LobbySystem()
    matchmaking = MatchmakingEngine()
    
    await lobby.start()
    
    # Register players
    player_ids = []
    for i in range(4):
        player_id = f"player{i}"
        player_ids.append(player_id)
        matchmaking.register_player(player_id, 1000 + i * 50)
    
    # Players join matchmaking
    for player_id in player_ids:
        success = lobby.join_matchmaking(
            player_id,
            matchmaking.player_profiles[player_id].skill_rating
        )
        assert success is True
    
    # Wait for match to be found
    await asyncio.sleep(2.5)
    
    # Check that a room was created
    assert len(lobby.rooms) > 0
    room = list(lobby.rooms.values())[0]
    assert room.status.value == "ready"
    assert len(room.players) == 4
    
    # Start game server
    game_server = GameServer(tick_rate=30)
    await game_server.start()
    
    # Add players to game
    for player_id in room.players:
        await game_server.add_player(player_id, f"client_{player_id}")
    
    # Start the game
    lobby.start_game(room.room_id, "game_server_1")
    
    # Simulate some gameplay
    for i in range(5):
        # Players send input
        for j, player_id in enumerate(room.players):
            input_data = {
                "position": {"x": j * 10 + i, "y": j * 5 + i},
                "velocity": {"x": 1, "y": 0}
            }
            game_server.game_state.update_player_position(
                player_id,
                input_data["position"],
                input_data.get("velocity")
            )
        
        await asyncio.sleep(0.1)
    
    # Check game state
    assert game_server.get_player_count() == 4
    assert game_server.game_state.tick > 0
    
    # Clean up
    await game_server.stop()
    await lobby.stop()


@pytest.mark.asyncio
async def test_spectator_and_chat_integration():
    """Test spectator mode and chat system integration"""
    # Create game server with spectator mode
    game_server = GameServer()
    spectator_mode = SpectatorMode("game123", enable_replay=True)
    chat_manager = ChatManager()
    
    await game_server.start()
    await spectator_mode.start()
    
    # Add players
    for i in range(2):
        await game_server.add_player(f"player{i}", f"client{i}")
        chat_manager.set_player_team(f"player{i}", "team1")
    
    # Add spectators
    spectator_mode.add_spectator("spectator1", delay_seconds=1.0)
    spectator_mode.add_spectator("spectator2", delay_seconds=2.0)
    
    # Players chat
    msg1 = chat_manager.process_message("player0", "Hello team!", ChatChannel.TEAM)
    assert msg1 is not None
    assert len(msg1.recipients) == 2
    
    # Spectator tries to chat (should work through different system)
    msg2 = chat_manager.process_message("spectator1", "Great game!", ChatChannel.ALL)
    assert msg2 is not None
    
    # Simulate game updates
    for i in range(10):
        game_state = {
            "tick": i,
            "players": {
                "player0": {"position": {"x": i * 10, "y": 0}},
                "player1": {"position": {"x": 0, "y": i * 10}}
            }
        }
        
        # Update spectator mode
        spectator_mode.update_game_state(i, game_state)
        
        # Update game server
        game_server.game_state.advance_tick()
        
        await asyncio.sleep(0.1)
    
    # Check spectator delayed states
    delayed1 = spectator_mode.get_delayed_state("spectator1")
    delayed2 = spectator_mode.get_delayed_state("spectator2")
    
    # spectator2 should see older state due to longer delay
    if delayed1 and delayed2:
        assert delayed2["tick"] <= delayed1["tick"]
    
    # Check replay
    assert spectator_mode.replay_recorder is not None
    assert len(spectator_mode.replay_recorder.frames) > 0
    
    # Save replay
    replay_data = spectator_mode.save_replay()
    assert replay_data is not None
    
    # Clean up
    await game_server.stop()
    await spectator_mode.stop()


@pytest.mark.asyncio
async def test_lag_compensation_gameplay():
    """Test lag compensation during gameplay"""
    # Create systems
    game_server = GameServer()
    lag_compensator = LagCompensator()
    
    await game_server.start()
    
    # Add players
    await game_server.add_player("player1", "client1")
    await game_server.add_player("player2", "client2")
    
    # Simulate gameplay with prediction and lag compensation
    for i in range(20):
        # Player 1 predicts movement
        predicted_pos = lag_compensator.predict_client_movement(
            "player1",
            {"x": i * 10, "y": 0},
            {"x": 10, "y": 0},
            {"move_x": 2},
            0.016  # 16ms frame time
        )
        
        # Server processes input (with some delay)
        if i % 3 == 0:  # Simulate periodic server updates
            # Server confirms position (with small correction)
            server_pos = {"x": predicted_pos["x"] - 0.5, "y": 0}
            lag_compensator.confirm_client_state(
                "player1",
                i + 1,
                server_pos,
                {"x": 10, "y": 0}
            )
            
            # Record server state for hit detection
            lag_compensator.record_server_state(
                "player1",
                i + 1,
                server_pos,
                {"x": 10, "y": 0},
                {"width": 20, "height": 20}
            )
        
        # Player 2 position (for hit detection)
        player2_pos = {"x": 50 + i * 5, "y": 0}
        lag_compensator.record_server_state(
            "player2",
            i + 1,
            player2_pos,
            {"x": 5, "y": 0},
            {"width": 20, "height": 20}
        )
        
        # Update interpolation
        lag_compensator.update_entity_for_interpolation(
            "player2",
            player2_pos,
            {"x": 5, "y": 0}
        )
        
        await asyncio.sleep(0.016)
    
    # Test hit verification
    current_time = time.time()
    hit, _ = lag_compensator.verify_hit(
        "player1",
        "player2",
        {"x": 100, "y": 0},
        current_time - 0.05  # 50ms ago
    )
    
    # Get metrics
    metrics = lag_compensator.get_metrics()
    assert metrics["total_hit_checks"] > 0
    assert "average_prediction_error" in metrics
    
    # Clean up
    await game_server.stop()


@pytest.mark.asyncio
async def test_network_resilience():
    """Test network resilience and reconnection"""
    server = NetworkServer(port=0)  # Random port
    client = NetworkClient("player1")
    
    # Mock network layer
    connected = False
    disconnected = False
    
    def on_connect(packet, client_id):
        nonlocal connected
        connected = True
    
    def on_disconnect(packet, client_id):
        nonlocal disconnected
        disconnected = True
    
    server.register_handler(PacketType.CONNECT, on_connect)
    server.register_handler(PacketType.DISCONNECT, on_disconnect)
    
    # Start server
    await server.start()
    
    # Simulate connection
    await server._handle_packet_data(
        b'{"packet_id": "1", "packet_type": "connect", "data": {"client_id": "player1"}, "timestamp": 0, "sequence_number": 0, "requires_ack": false}',
        "client1"
    )
    
    assert connected is True
    
    # Simulate disconnection
    await server._handle_packet_data(
        b'{"packet_id": "2", "packet_type": "disconnect", "data": {"reason": "test"}, "timestamp": 0, "sequence_number": 0, "requires_ack": false}',
        "client1"
    )
    
    assert disconnected is True
    
    # Clean up
    await server.stop()


@pytest.mark.asyncio
async def test_performance_under_load():
    """Test system performance with multiple players"""
    # Create systems
    game_server = GameServer(tick_rate=60)
    chat_manager = ChatManager()
    lag_compensator = LagCompensator()
    
    await game_server.start()
    
    # Add many players
    num_players = 50
    for i in range(num_players):
        await game_server.add_player(f"player{i}", f"client{i}")
    
    # Simulate concurrent activity
    start_time = time.time()
    
    # Run for a short duration
    for tick in range(30):  # 0.5 seconds at 60 Hz
        # All players send input
        for i in range(num_players):
            player_id = f"player{i}"
            
            # Update position
            game_server.game_state.update_player_position(
                player_id,
                {"x": i * 10 + tick, "y": i * 5 + tick},
                {"x": 1, "y": 0}
            )
            
            # Occasionally send chat
            if tick % 10 == 0:
                chat_manager.process_message(
                    player_id,
                    f"Message from {player_id}",
                    ChatChannel.ALL
                )
        
        # Advance game state
        game_server.game_state.advance_tick()
        
        await asyncio.sleep(0.016)  # ~60 FPS
    
    elapsed = time.time() - start_time
    
    # Check performance
    assert elapsed < 1.0  # Should complete in under 1 second
    assert game_server.get_player_count() == num_players
    assert game_server.game_state.tick >= 30
    
    # Get tick stats
    tick_stats = game_server.tick_manager.get_tick_stats()
    assert tick_stats["current_tick"] > 0
    
    # Clean up
    await game_server.stop()


@pytest.mark.asyncio
async def test_error_recovery():
    """Test error recovery and edge cases"""
    lobby = LobbySystem()
    game_server = GameServer()
    
    await lobby.start()
    await game_server.start()
    
    # Test invalid operations
    # Try to join non-existent room
    success = lobby.join_room("invalid_room_id", "player1")
    assert success is False
    
    # Try to start game without enough players
    room = lobby.create_room("host", "Test Room", RoomSettings(min_players=4))
    success = room.start_game("game_server_1")
    assert success is False
    
    # Add players and make ready
    for i in range(4):
        if i > 0:  # Host already in room
            lobby.join_room(room.room_id, f"player{i}")
        lobby.set_ready(f"player{i}" if i > 0 else "host", True)
    
    # Now should be able to start
    success = room.start_game("game_server_1")
    assert success is True
    
    # Test duplicate player operations
    success = await game_server.add_player("player1", "client1")
    assert success is True
    
    # Try to add same player again
    success = await game_server.add_player("player1", "client2")
    assert success is False
    
    # Test removing non-existent player
    await game_server.remove_player("non_existent_player")  # Should not crash
    
    # Clean up
    await lobby.stop()
    await game_server.stop()


def test_data_consistency():
    """Test data consistency across systems"""
    # Create interconnected systems
    matchmaking = MatchmakingEngine()
    lobby = LobbySystem()
    chat = ChatManager()
    
    # Register players in matchmaking
    player_ids = ["alice", "bob", "charlie", "david"]
    for i, pid in enumerate(player_ids):
        matchmaking.register_player(pid, 1000 + i * 100)
    
    # Create room in lobby
    room = lobby.create_room("alice", "Test Match")
    for pid in player_ids[1:]:
        lobby.join_room(room.room_id, pid)
    
    # Set up teams in chat
    chat.set_player_team("alice", "red")
    chat.set_player_team("bob", "red")
    chat.set_player_team("charlie", "blue")
    chat.set_player_team("david", "blue")
    
    # Verify consistency
    assert len(room.players) == 4
    assert all(pid in room.players for pid in player_ids)
    assert all(pid in matchmaking.player_profiles for pid in player_ids)
    
    # Test team chat recipients
    msg = chat.process_message("alice", "Go red team!", ChatChannel.TEAM)
    assert "alice" in msg.recipients
    assert "bob" in msg.recipients
    assert "charlie" not in msg.recipients
    assert "david" not in msg.recipients