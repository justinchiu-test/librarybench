"""Tests for lobby system"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock

from pytermgame.lobby import (
    LobbySystem, GameRoom, RoomStatus, RoomSettings,
    QueueManager
)


class TestGameRoom:
    """Test GameRoom class"""
    
    def test_room_creation(self):
        """Test creating a game room"""
        settings = RoomSettings(max_players=4, min_players=2)
        room = GameRoom(
            name="Test Room",
            host_id="player1",
            settings=settings
        )
        
        assert room.name == "Test Room"
        assert room.host_id == "player1"
        assert room.status == RoomStatus.WAITING
        assert room.settings.max_players == 4
        assert len(room.players) == 0
    
    def test_add_remove_players(self):
        """Test adding and removing players"""
        room = GameRoom(name="Test", host_id="host", settings=RoomSettings(max_players=2))
        
        # Add host
        success = room.add_player("host")
        assert success is True
        assert "host" in room.players
        
        # Add another player
        success = room.add_player("player2")
        assert success is True
        assert len(room.players) == 2
        
        # Try to add when full
        success = room.add_player("player3")
        assert success is False
        
        # Remove player
        success = room.remove_player("player2")
        assert success is True
        assert len(room.players) == 1
    
    def test_ready_status(self):
        """Test player ready status"""
        room = GameRoom(name="Test", host_id="host", settings=RoomSettings(min_players=2))
        room.add_player("host")
        room.add_player("player2")
        
        # Set players ready
        room.set_player_ready("host", True)
        assert "host" in room.ready_players
        assert room.status == RoomStatus.WAITING
        
        room.set_player_ready("player2", True)
        assert room.all_players_ready() is True
        assert room.status == RoomStatus.READY
        assert room.can_start() is True
        
        # Unready a player
        room.set_player_ready("player2", False)
        assert room.status == RoomStatus.WAITING
        assert room.can_start() is False
    
    def test_host_migration(self):
        """Test host migration when host leaves"""
        room = GameRoom(name="Test", host_id="host", settings=RoomSettings())
        room.add_player("host")
        room.add_player("player2")
        room.add_player("player3")
        
        # Remove host
        room.remove_player("host")
        
        # Host should migrate to next player
        assert room.host_id == "player2"
        assert len(room.players) == 2
    
    def test_room_privacy(self):
        """Test private room functionality"""
        settings = RoomSettings(private=True, password="secret123")
        room = GameRoom(name="Private", host_id="host", settings=settings)
        
        # Can join with correct password
        can_join = room.can_join("player1", "secret123")
        assert can_join is True
        
        # Cannot join with wrong password
        can_join = room.can_join("player2", "wrong")
        assert can_join is False
        
        # Cannot join without password
        can_join = room.can_join("player3", None)
        assert can_join is False
    
    def test_start_end_game(self):
        """Test starting and ending a game"""
        room = GameRoom(name="Test", host_id="host", settings=RoomSettings(min_players=1))
        room.add_player("host")
        room.set_player_ready("host", True)
        
        # Start game
        success = room.start_game("game_server_123")
        assert success is True
        assert room.status == RoomStatus.IN_GAME
        assert room.game_server_id == "game_server_123"
        assert room.started_at is not None
        
        # End game
        room.end_game()
        assert room.status == RoomStatus.FINISHED
        assert room.game_server_id is None
        assert len(room.ready_players) == 0


class TestQueueManager:
    """Test QueueManager class"""
    
    def test_add_remove_players(self):
        """Test adding and removing players from queue"""
        queue = QueueManager()
        
        # Add players
        success = queue.add_player("player1", 1000.0)
        assert success is True
        assert len(queue.queues["default"]) == 1
        
        # Try to add same player again
        success = queue.add_player("player1", 1000.0)
        assert success is False
        
        # Remove player
        success = queue.remove_player("player1")
        assert success is True
        assert len(queue.queues["default"]) == 0
    
    def test_matchmaking_basic(self):
        """Test basic matchmaking"""
        queue = QueueManager(team_size=2)
        
        # Add 4 players with similar skills
        queue.add_player("player1", 1000.0)
        queue.add_player("player2", 1050.0)
        queue.add_player("player3", 1100.0)
        queue.add_player("player4", 1150.0)
        
        # Find match
        match = queue.find_match()
        assert match is not None
        assert len(match.players) == 4
        assert match.average_skill == 1100.0
        
        # Players should be removed from queue
        assert len(queue.queues["default"]) == 0
    
    def test_matchmaking_skill_tolerance(self):
        """Test skill-based matchmaking with tolerance"""
        queue = QueueManager(team_size=1, skill_tolerance=100.0)
        
        # Add players with varying skills
        queue.add_player("player1", 1000.0)
        queue.add_player("player2", 1500.0)  # Too high skill difference
        queue.add_player("player3", 1050.0)
        
        # Should only match players within tolerance
        match = queue.find_match()
        assert match is not None
        assert len(match.players) == 2
        assert all(p.player_id in ["player1", "player3"] for p in match.players)
    
    def test_balanced_teams(self):
        """Test balanced team creation"""
        queue = QueueManager(team_size=2)
        
        # Add players
        queue.add_player("player1", 2000.0)  # Highest skill
        queue.add_player("player2", 1500.0)
        queue.add_player("player3", 1200.0)
        queue.add_player("player4", 1000.0)  # Lowest skill
        
        match = queue.find_match()
        team1, team2 = queue.create_balanced_teams(match)
        
        # Teams should be balanced (highest + lowest vs middle two)
        assert len(team1) == 2
        assert len(team2) == 2
        
        # Check team balance
        team1_skills = [p.skill_rating for p in match.players if p.player_id in team1]
        team2_skills = [p.skill_rating for p in match.players if p.player_id in team2]
        
        team1_avg = sum(team1_skills) / len(team1_skills)
        team2_avg = sum(team2_skills) / len(team2_skills)
        
        # Teams should be relatively balanced
        assert abs(team1_avg - team2_avg) < 200
    
    def test_queue_statistics(self):
        """Test queue statistics"""
        queue = QueueManager()
        
        # Empty queue stats
        stats = queue.get_queue_stats()
        assert stats["players_in_queue"] == 0
        
        # Add players
        queue.add_player("player1", 1000.0)
        queue.add_player("player2", 1200.0)
        
        stats = queue.get_queue_stats()
        assert stats["players_in_queue"] == 2
        assert stats["average_skill_rating"] == 1100.0
        assert stats["skill_range"] == 200.0
    
    def test_player_position(self):
        """Test getting player position in queue"""
        queue = QueueManager()
        
        queue.add_player("player1", 1000.0)
        queue.add_player("player2", 1100.0)
        queue.add_player("player3", 1200.0)
        
        position = queue.get_player_position("player2")
        assert position == 2  # Second in queue


class TestLobbySystem:
    """Test LobbySystem class"""
    
    @pytest.mark.asyncio
    async def test_lobby_initialization(self):
        """Test lobby system initialization"""
        lobby = LobbySystem()
        
        assert len(lobby.rooms) == 0
        assert lobby.max_rooms == 1000
        assert lobby.running is False
    
    def test_create_room(self):
        """Test room creation"""
        lobby = LobbySystem()
        
        # Create room
        room = lobby.create_room("host1", "My Room")
        assert room is not None
        assert room.name == "My Room"
        assert room.host_id == "host1"
        assert room.room_id in lobby.rooms
        assert lobby.player_rooms["host1"] == room.room_id
        
        # Try to create another room while in one
        room2 = lobby.create_room("host1", "Another Room")
        assert room2 is None
    
    def test_join_leave_room(self):
        """Test joining and leaving rooms"""
        lobby = LobbySystem()
        
        # Create room
        room = lobby.create_room("host", "Test Room")
        room_id = room.room_id
        
        # Join room
        success = lobby.join_room(room_id, "player2")
        assert success is True
        assert "player2" in room.players
        assert lobby.player_rooms["player2"] == room_id
        
        # Try to join non-existent room
        success = lobby.join_room("invalid_id", "player3")
        assert success is False
        
        # Leave room
        success = lobby.leave_room("player2")
        assert success is True
        assert "player2" not in room.players
        assert "player2" not in lobby.player_rooms
    
    def test_ready_status_management(self):
        """Test managing ready status through lobby"""
        lobby = LobbySystem()
        
        room = lobby.create_room("host", "Test Room")
        lobby.join_room(room.room_id, "player2")
        
        # Set ready
        success = lobby.set_ready("host", True)
        assert success is True
        assert "host" in room.ready_players
        
        success = lobby.set_ready("player2", True)
        assert success is True
        assert room.status == RoomStatus.READY
    
    def test_matchmaking_integration(self):
        """Test matchmaking integration"""
        lobby = LobbySystem()
        
        # Join matchmaking
        success = lobby.join_matchmaking("player1", 1000.0)
        assert success is True
        
        # Cannot join matchmaking while in it
        success = lobby.join_matchmaking("player1", 1000.0)
        assert success is False
        
        # Cannot join matchmaking while in room
        room = lobby.create_room("player2", "Room")
        success = lobby.join_matchmaking("player2", 1000.0)
        assert success is False
        
        # Leave matchmaking
        success = lobby.leave_matchmaking("player1")
        assert success is True
    
    def test_room_list(self):
        """Test getting room list"""
        lobby = LobbySystem()
        
        # Create rooms
        public_room = lobby.create_room("host1", "Public Room")
        
        private_settings = RoomSettings(private=True, password="secret")
        private_room = lobby.create_room("host2", "Private Room", private_settings)
        
        full_room = lobby.create_room("host3", "Full Room", RoomSettings(max_players=1))
        
        # Get all rooms
        rooms = lobby.get_room_list(include_private=True, include_full=True)
        assert len(rooms) == 3
        
        # Exclude private
        rooms = lobby.get_room_list(include_private=False, include_full=True)
        assert len(rooms) == 2
        assert all(r["name"] != "Private Room" for r in rooms)
        
        # Exclude full
        rooms = lobby.get_room_list(include_private=True, include_full=False)
        assert len(rooms) == 2
        assert all(r["name"] != "Full Room" for r in rooms)
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping lobby system"""
        lobby = LobbySystem()
        
        await lobby.start()
        assert lobby.running is True
        
        await lobby.stop()
        assert lobby.running is False
    
    def test_callbacks(self):
        """Test lobby callbacks"""
        lobby = LobbySystem()
        
        created_rooms = []
        updated_rooms = []
        
        lobby.on_room_created(lambda room: created_rooms.append(room.room_id))
        lobby.on_room_updated(lambda room: updated_rooms.append(room.room_id))
        
        # Create room (triggers created callback)
        room = lobby.create_room("host", "Test")
        assert len(created_rooms) == 1
        assert created_rooms[0] == room.room_id
        
        # Join room (triggers updated callback)
        lobby.join_room(room.room_id, "player2")
        assert len(updated_rooms) == 1
        assert updated_rooms[0] == room.room_id


@pytest.mark.asyncio
async def test_lobby_matchmaking_integration():
    """Test integrated lobby and matchmaking functionality"""
    lobby = LobbySystem()
    await lobby.start()
    
    match_results = []
    
    def on_match_found(room, team1, team2):
        match_results.append((room, team1, team2))
    
    lobby.on_match_found(on_match_found)
    
    # Add players to matchmaking
    for i in range(4):
        lobby.join_matchmaking(f"player{i}", 1000 + i * 50)
    
    # Wait for matchmaking
    await asyncio.sleep(2.5)  # Slightly more than matchmaking interval
    
    # Check match was found
    assert len(match_results) == 1
    room, team1, team2 = match_results[0]
    
    assert room is not None
    assert len(team1) == 2
    assert len(team2) == 2
    assert room.status == RoomStatus.READY
    
    await lobby.stop()