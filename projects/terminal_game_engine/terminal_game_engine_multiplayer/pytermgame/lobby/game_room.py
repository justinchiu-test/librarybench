"""Game room implementation"""

from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import time


class RoomStatus(Enum):
    """Room status enumeration"""
    WAITING = "waiting"
    READY = "ready"
    IN_GAME = "in_game"
    FINISHED = "finished"


class RoomSettings(BaseModel):
    """Room configuration settings"""
    max_players: int = Field(4, ge=2, le=100)
    min_players: int = Field(2, ge=1)
    private: bool = Field(False)
    password: Optional[str] = Field(None)
    game_mode: str = Field("default")
    map_name: Optional[str] = Field(None)
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    score_limit: Optional[int] = Field(None)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class GameRoom(BaseModel):
    """Game room for player lobbies"""
    room_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field("Unnamed Room")
    host_id: str = Field(description="Player ID of the room host")
    players: List[str] = Field(default_factory=list)
    ready_players: Set[str] = Field(default_factory=set)
    status: RoomStatus = Field(RoomStatus.WAITING)
    settings: RoomSettings = Field(default_factory=RoomSettings)
    created_at: float = Field(default_factory=time.time)
    started_at: Optional[float] = Field(None)
    game_server_id: Optional[str] = Field(None)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_player(self, player_id: str) -> bool:
        """Add a player to the room"""
        if len(self.players) >= self.settings.max_players:
            return False
        
        if player_id not in self.players:
            self.players.append(player_id)
            return True
        return False
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the room"""
        if player_id in self.players:
            self.players.remove(player_id)
            self.ready_players.discard(player_id)
            
            # Handle host migration
            if player_id == self.host_id and self.players:
                self.host_id = self.players[0]
            
            return True
        return False
    
    def set_player_ready(self, player_id: str, ready: bool = True) -> bool:
        """Set player ready status"""
        if player_id not in self.players:
            return False
        
        if ready:
            self.ready_players.add(player_id)
        else:
            self.ready_players.discard(player_id)
        
        # Check if room is ready to start
        if self.all_players_ready() and len(self.players) >= self.settings.min_players:
            self.status = RoomStatus.READY
        else:
            self.status = RoomStatus.WAITING
        
        return True
    
    def all_players_ready(self) -> bool:
        """Check if all players are ready"""
        return len(self.ready_players) == len(self.players)
    
    def can_start(self) -> bool:
        """Check if the game can start"""
        return (
            self.status == RoomStatus.READY and
            len(self.players) >= self.settings.min_players and
            self.all_players_ready()
        )
    
    def start_game(self, game_server_id: str) -> bool:
        """Start the game"""
        if not self.can_start():
            return False
        
        self.status = RoomStatus.IN_GAME
        self.started_at = time.time()
        self.game_server_id = game_server_id
        return True
    
    def end_game(self):
        """End the game"""
        self.status = RoomStatus.FINISHED
        self.game_server_id = None
        # Reset ready status for all players
        self.ready_players.clear()
    
    def is_full(self) -> bool:
        """Check if room is full"""
        return len(self.players) >= self.settings.max_players
    
    def is_empty(self) -> bool:
        """Check if room is empty"""
        return len(self.players) == 0
    
    def can_join(self, player_id: str, password: Optional[str] = None) -> bool:
        """Check if a player can join"""
        if self.is_full():
            return False
        
        if player_id in self.players:
            return False
        
        if self.settings.private and self.settings.password != password:
            return False
        
        if self.status != RoomStatus.WAITING:
            return False
        
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get room information"""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "host_id": self.host_id,
            "players": self.players,
            "ready_players": list(self.ready_players),
            "player_count": len(self.players),
            "max_players": self.settings.max_players,
            "status": self.status.value,
            "settings": self.settings.model_dump(),
            "can_start": self.can_start(),
            "created_at": self.created_at,
            "started_at": self.started_at
        }