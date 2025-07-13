"""Tests for game server module"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock

from pytermgame.server import GameServer, GameState, PlayerState, GameObject, TickManager
from pytermgame.server.game_state import PlayerStatus
from pytermgame.network import PacketType, ProtocolType


class TestGameState:
    """Test GameState class"""
    
    def test_game_state_creation(self):
        """Test creating game state"""
        state = GameState()
        
        assert state.tick == 0
        assert state.started is False
        assert state.ended is False
        assert len(state.players) == 0
        assert len(state.objects) == 0
    
    def test_add_remove_player(self):
        """Test adding and removing players"""
        state = GameState()
        
        # Add player
        player = state.add_player("player1")
        assert player.player_id == "player1"
        assert player.status == PlayerStatus.CONNECTED
        assert "player1" in state.players
        
        # Remove player
        success = state.remove_player("player1")
        assert success is True
        assert "player1" not in state.players
        
        # Remove non-existent player
        success = state.remove_player("player2")
        assert success is False
    
    def test_update_player_position(self):
        """Test updating player position"""
        state = GameState()
        state.add_player("player1")
        
        new_position = {"x": 100.0, "y": 200.0}
        new_velocity = {"x": 10.0, "y": 0.0}
        
        state.update_player_position("player1", new_position, new_velocity)
        
        assert state.players["player1"].position == new_position
        assert state.players["player1"].velocity == new_velocity
    
    def test_game_objects(self):
        """Test game object management"""
        state = GameState()
        
        # Add object
        obj = GameObject(
            object_type="powerup",
            position={"x": 50.0, "y": 50.0}
        )
        obj_id = state.add_object(obj)
        
        assert obj_id in state.objects
        assert state.objects[obj_id].object_type == "powerup"
        
        # Update object
        state.update_object(obj_id, position={"x": 60.0, "y": 60.0})
        assert state.objects[obj_id].position["x"] == 60.0
        
        # Remove object
        success = state.remove_object(obj_id)
        assert success is True
        assert obj_id not in state.objects
    
    def test_validate_player_input(self):
        """Test player input validation"""
        state = GameState()
        player = state.add_player("player1")
        player.status = PlayerStatus.PLAYING
        
        # Valid input
        valid = state.validate_player_input("player1", {"move": "left"}, 1)
        assert valid is True
        
        # Invalid - player not playing
        player.status = PlayerStatus.SPECTATING
        valid = state.validate_player_input("player1", {"move": "left"}, 2)
        assert valid is False
        
        # Invalid - old sequence number
        player.status = PlayerStatus.PLAYING
        player.last_input_sequence = 10
        valid = state.validate_player_input("player1", {"move": "left"}, 5)
        assert valid is False
    
    def test_apply_physics(self):
        """Test physics application"""
        state = GameState()
        player = state.add_player("player1")
        player.status = PlayerStatus.PLAYING
        player.position = {"x": 100.0, "y": 100.0}
        player.velocity = {"x": 10.0, "y": -5.0}
        
        # Apply physics
        delta_time = 0.1  # 100ms
        state.apply_physics(delta_time)
        
        assert player.position["x"] == 101.0  # 100 + 10 * 0.1
        assert player.position["y"] == 99.5   # 100 + (-5) * 0.1
    
    def test_serialize_for_client(self):
        """Test state serialization for clients"""
        state = GameState()
        state.add_player("player1")
        state.add_player("player2")
        
        # Serialize without specific player
        data = state.serialize_for_client()
        assert "players" in data
        assert len(data["players"]) == 2
        assert "your_state" not in data
        
        # Serialize for specific player
        data = state.serialize_for_client("player1")
        assert "your_state" in data
        assert data["your_state"]["player_id"] == "player1"


class TestTickManager:
    """Test TickManager class"""
    
    def test_tick_manager_creation(self):
        """Test creating tick manager"""
        manager = TickManager(target_tick_rate=60)
        
        assert manager.target_tick_rate == 60
        assert manager.tick_interval == 1.0 / 60
        assert manager.current_tick == 0
        assert manager.running is False
    
    @pytest.mark.asyncio
    async def test_tick_callbacks(self):
        """Test tick callbacks"""
        manager = TickManager(target_tick_rate=10)  # 10 Hz for faster testing
        
        callback_calls = []
        
        def test_callback(tick, delta_time):
            callback_calls.append((tick, delta_time))
        
        manager.add_callback(test_callback)
        
        await manager.start()
        await asyncio.sleep(0.15)  # Wait for at least 1 tick
        await manager.stop()
        
        assert len(callback_calls) > 0
        assert callback_calls[0][0] == 0  # First tick number
    
    def test_tick_stats(self):
        """Test tick statistics"""
        manager = TickManager(target_tick_rate=30)
        
        stats = manager.get_tick_stats()
        assert stats["current_tick"] == 0
        assert stats["target_tick_rate"] == 30
        assert stats["running"] is False


class TestGameServer:
    """Test GameServer class"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test game server initialization"""
        server = GameServer(host="localhost", port=8888, tick_rate=60)
        
        assert server.game_state is not None
        assert server.tick_manager.target_tick_rate == 60
        assert server.running is False
        assert server.max_players == 100
    
    @pytest.mark.asyncio
    async def test_player_management(self):
        """Test adding and removing players"""
        server = GameServer()
        
        # Add player
        success = await server.add_player("player1", "client1")
        assert success is True
        assert server.get_player_count() == 1
        assert "player1" in server.game_state.players
        assert server.client_to_player["client1"] == "player1"
        
        # Try to add too many players
        server.max_players = 1
        success = await server.add_player("player2", "client2")
        assert success is False
        
        # Remove player
        await server.remove_player("player1")
        assert server.get_player_count() == 0
        assert "player1" not in server.game_state.players
    
    @pytest.mark.asyncio
    async def test_input_handling(self):
        """Test player input handling"""
        server = GameServer()
        await server.add_player("player1", "client1")
        
        # Create mock packet
        from pytermgame.network import Packet
        packet = Packet(
            packet_id="test",
            packet_type=PacketType.PLAYER_INPUT,
            sender_id="client1",
            data={
                "input": {"position": {"x": 10, "y": 20}},
                "sequence": 1
            }
        )
        
        # Make player active
        server.game_state.players["player1"].status = PlayerStatus.PLAYING
        
        # Handle input
        await server._handle_player_input(packet, "client1")
        
        # Check input buffer
        assert "player1" in server.input_buffer
        assert len(server.input_buffer["player1"]) == 1
        assert server.input_buffer["player1"][0]["input"]["position"]["x"] == 10
    
    @pytest.mark.asyncio
    async def test_chat_handling(self):
        """Test chat message handling"""
        server = GameServer()
        await server.add_player("player1", "client1")
        
        # Mock broadcast
        server.network_server.broadcast_packet = AsyncMock(return_value={})
        
        packet = Packet(
            packet_id="test",
            packet_type=PacketType.CHAT_MESSAGE,
            data={"message": "Hello!", "channel": "all"}
        )
        
        await server._handle_chat_message(packet, "client1")
        
        # Check broadcast was called
        server.network_server.broadcast_packet.assert_called_once()
        broadcast_packet = server.network_server.broadcast_packet.call_args[0][0]
        assert broadcast_packet.data["message"] == "Hello!"
        assert broadcast_packet.data["player_id"] == "player1"
    
    @pytest.mark.asyncio
    async def test_game_tick_processing(self):
        """Test game tick processing"""
        server = GameServer()
        
        # Add callback to track ticks
        tick_count = 0
        
        def update_callback(state, delta_time):
            nonlocal tick_count
            tick_count += 1
        
        server.on_game_update(update_callback)
        
        # Manually trigger a game tick
        await server._game_tick(0, 0.016)  # 16ms delta
        
        assert tick_count == 1
        assert server.game_state.tick == 1
    
    def test_server_stats(self):
        """Test server statistics"""
        server = GameServer()
        
        stats = server.get_server_stats()
        assert stats["player_count"] == 0
        assert stats["spectator_count"] == 0
        assert stats["max_players"] == 100
        assert "tick_stats" in stats
        assert "game_id" in stats


@pytest.mark.asyncio
async def test_game_server_integration():
    """Test integrated game server functionality"""
    server = GameServer(tick_rate=30)
    
    # Track callbacks
    join_events = []
    leave_events = []
    update_events = []
    
    server.on_player_join(lambda pid: join_events.append(pid))
    server.on_player_leave(lambda pid: leave_events.append(pid))
    server.on_game_update(lambda state, dt: update_events.append((state.tick, dt)))
    
    # Add players
    await server.add_player("player1", "client1")
    await server.add_player("player2", "client2")
    
    assert len(join_events) == 2
    assert server.get_player_count() == 2
    
    # Start server components
    await server.tick_manager.start()
    
    # Let it run briefly
    await asyncio.sleep(0.1)
    
    # Stop server
    await server.tick_manager.stop()
    
    # Remove a player
    await server.remove_player("player1")
    
    assert len(leave_events) == 1
    assert leave_events[0] == "player1"
    assert server.get_player_count() == 1