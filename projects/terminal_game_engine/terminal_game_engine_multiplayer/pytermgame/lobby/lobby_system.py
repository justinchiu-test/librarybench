"""Main lobby system implementation"""

from typing import Dict, List, Optional, Set, Callable, Any
import asyncio
import uuid
import time

from ..network import Packet, PacketType
from .game_room import GameRoom, RoomStatus, RoomSettings
from .queue_manager import QueueManager


class LobbySystem:
    """Manages game rooms and matchmaking"""
    
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}
        self.player_rooms: Dict[str, str] = {}  # player_id -> room_id
        self.queue_manager = QueueManager()
        
        # Callbacks
        self.room_created_callbacks: List[Callable] = []
        self.room_updated_callbacks: List[Callable] = []
        self.match_found_callbacks: List[Callable] = []
        
        # Settings
        self.max_rooms = 1000
        self.room_timeout = 3600  # 1 hour
        self.matchmaking_interval = 2.0  # Check for matches every 2 seconds
        
        self.running = False
    
    async def start(self):
        """Start the lobby system"""
        self.running = True
        asyncio.create_task(self._matchmaking_loop())
        asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop the lobby system"""
        self.running = False
    
    def create_room(self, host_id: str, name: str, settings: Optional[RoomSettings] = None) -> Optional[GameRoom]:
        """Create a new game room"""
        if len(self.rooms) >= self.max_rooms:
            return None
        
        # Check if player is already in a room
        if host_id in self.player_rooms:
            return None
        
        room = GameRoom(
            name=name,
            host_id=host_id,
            settings=settings or RoomSettings()
        )
        
        room.add_player(host_id)
        self.rooms[room.room_id] = room
        self.player_rooms[host_id] = room.room_id
        
        # Notify callbacks
        for callback in self.room_created_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(room))
                else:
                    callback(room)
            except Exception:
                pass
        
        return room
    
    def join_room(self, room_id: str, player_id: str, password: Optional[str] = None) -> bool:
        """Join an existing room"""
        if room_id not in self.rooms:
            return False
        
        # Check if player is already in a room
        if player_id in self.player_rooms:
            return False
        
        room = self.rooms[room_id]
        if room.can_join(player_id, password):
            if room.add_player(player_id):
                self.player_rooms[player_id] = room_id
                self._notify_room_update(room)
                return True
        
        return False
    
    def leave_room(self, player_id: str) -> bool:
        """Leave current room"""
        if player_id not in self.player_rooms:
            return False
        
        room_id = self.player_rooms[player_id]
        if room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        if room.remove_player(player_id):
            del self.player_rooms[player_id]
            
            # Delete room if empty
            if room.is_empty():
                del self.rooms[room_id]
            else:
                self._notify_room_update(room)
            
            return True
        
        return False
    
    def set_ready(self, player_id: str, ready: bool = True) -> bool:
        """Set player ready status"""
        if player_id not in self.player_rooms:
            return False
        
        room_id = self.player_rooms[player_id]
        if room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        if room.set_player_ready(player_id, ready):
            self._notify_room_update(room)
            return True
        
        return False
    
    def start_game(self, room_id: str, game_server_id: str) -> bool:
        """Start a game for a room"""
        if room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        if room.start_game(game_server_id):
            self._notify_room_update(room)
            return True
        
        return False
    
    def end_game(self, room_id: str):
        """End a game for a room"""
        if room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        room.end_game()
        self._notify_room_update(room)
    
    def join_matchmaking(self, player_id: str, skill_rating: float = 1000.0, 
                        queue_type: str = "default", preferences: Optional[Dict[str, Any]] = None) -> bool:
        """Join matchmaking queue"""
        # Check if player is in a room
        if player_id in self.player_rooms:
            return False
        
        return self.queue_manager.add_player(player_id, skill_rating, queue_type, preferences)
    
    def leave_matchmaking(self, player_id: str) -> bool:
        """Leave matchmaking queue"""
        return self.queue_manager.remove_player(player_id)
    
    def get_room_list(self, include_private: bool = False, include_full: bool = True) -> List[Dict[str, Any]]:
        """Get list of available rooms"""
        room_list = []
        
        for room in self.rooms.values():
            if room.status != RoomStatus.WAITING:
                continue
            
            if not include_private and room.settings.private:
                continue
            
            if not include_full and room.is_full():
                continue
            
            room_list.append(room.get_info())
        
        return room_list
    
    def get_room(self, room_id: str) -> Optional[GameRoom]:
        """Get a specific room"""
        return self.rooms.get(room_id)
    
    def get_player_room(self, player_id: str) -> Optional[GameRoom]:
        """Get the room a player is in"""
        if player_id in self.player_rooms:
            room_id = self.player_rooms[player_id]
            return self.rooms.get(room_id)
        return None
    
    def _notify_room_update(self, room: GameRoom):
        """Notify callbacks of room update"""
        for callback in self.room_updated_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(room))
                else:
                    callback(room)
            except Exception:
                pass
    
    async def _matchmaking_loop(self):
        """Process matchmaking queue"""
        while self.running:
            # Check each queue type
            for queue_type in list(self.queue_manager.queues.keys()):
                match_group = self.queue_manager.find_match(queue_type)
                
                if match_group:
                    # Create teams
                    team1, team2 = self.queue_manager.create_balanced_teams(match_group)
                    
                    # Create a room for the match
                    host_id = team1[0]  # First player is host
                    room = self.create_room(
                        host_id,
                        f"Ranked Match {match_group.group_id[:8]}",
                        RoomSettings(
                            max_players=len(match_group.players),
                            min_players=len(match_group.players),
                            private=True,
                            game_mode="ranked"
                        )
                    )
                    
                    if room:
                        # Add all players to room
                        for player in match_group.players[1:]:  # Skip host
                            self.join_room(room.room_id, player.player_id)
                        
                        # Set all players as ready
                        for player in match_group.players:
                            self.set_ready(player.player_id, True)
                        
                        # Notify match found
                        for callback in self.match_found_callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(room, team1, team2)
                                else:
                                    callback(room, team1, team2)
                            except Exception:
                                pass
            
            await asyncio.sleep(self.matchmaking_interval)
    
    async def _cleanup_loop(self):
        """Clean up old/inactive rooms"""
        while self.running:
            current_time = time.time()
            rooms_to_remove = []
            
            for room_id, room in self.rooms.items():
                # Remove finished games after timeout
                if room.status == RoomStatus.FINISHED:
                    if current_time - room.created_at > self.room_timeout:
                        rooms_to_remove.append(room_id)
                
                # Remove empty rooms
                elif room.is_empty():
                    rooms_to_remove.append(room_id)
            
            # Remove rooms
            for room_id in rooms_to_remove:
                # Remove all players from room
                room = self.rooms[room_id]
                for player_id in list(room.players):
                    if player_id in self.player_rooms:
                        del self.player_rooms[player_id]
                
                del self.rooms[room_id]
            
            await asyncio.sleep(60)  # Check every minute
    
    def on_room_created(self, callback: Callable):
        """Register room created callback"""
        self.room_created_callbacks.append(callback)
    
    def on_room_updated(self, callback: Callable):
        """Register room updated callback"""
        self.room_updated_callbacks.append(callback)
    
    def on_match_found(self, callback: Callable):
        """Register match found callback"""
        self.match_found_callbacks.append(callback)