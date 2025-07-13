"""Game state management for server"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
import time
import uuid
from enum import Enum


class PlayerStatus(Enum):
    """Player status enumeration"""
    CONNECTED = "connected"
    PLAYING = "playing"
    SPECTATING = "spectating"
    DISCONNECTED = "disconnected"


class GameObject(BaseModel):
    """Base game object model"""
    object_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    object_type: str = Field("generic")
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    velocity: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    data: Dict[str, Any] = Field(default_factory=dict)
    last_updated: float = Field(default_factory=time.time)


class PlayerState(BaseModel):
    """Player state information"""
    player_id: str
    status: PlayerStatus = Field(PlayerStatus.CONNECTED)
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    velocity: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    score: int = Field(0)
    health: int = Field(100)
    data: Dict[str, Any] = Field(default_factory=dict)
    last_input_time: float = Field(default_factory=time.time)
    last_input_sequence: int = Field(0)
    ping: float = Field(0.0)


class GameState(BaseModel):
    """Authoritative game state"""
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tick: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
    players: Dict[str, PlayerState] = Field(default_factory=dict)
    objects: Dict[str, GameObject] = Field(default_factory=dict)
    game_data: Dict[str, Any] = Field(default_factory=dict)
    started: bool = Field(False)
    ended: bool = Field(False)
    
    def add_player(self, player_id: str) -> PlayerState:
        """Add a new player to the game"""
        if player_id not in self.players:
            player = PlayerState(player_id=player_id)
            self.players[player_id] = player
            return player
        return self.players[player_id]
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game"""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def update_player_position(self, player_id: str, position: Dict[str, float], velocity: Optional[Dict[str, float]] = None):
        """Update player position and velocity"""
        if player_id in self.players:
            self.players[player_id].position = position
            if velocity:
                self.players[player_id].velocity = velocity
            self.players[player_id].last_input_time = time.time()
    
    def add_object(self, obj: GameObject) -> str:
        """Add a game object"""
        self.objects[obj.object_id] = obj
        return obj.object_id
    
    def remove_object(self, object_id: str) -> bool:
        """Remove a game object"""
        if object_id in self.objects:
            del self.objects[object_id]
            return True
        return False
    
    def update_object(self, object_id: str, position: Optional[Dict[str, float]] = None, 
                     velocity: Optional[Dict[str, float]] = None, data: Optional[Dict[str, Any]] = None):
        """Update game object properties"""
        if object_id in self.objects:
            obj = self.objects[object_id]
            if position:
                obj.position = position
            if velocity:
                obj.velocity = velocity
            if data:
                obj.data.update(data)
            obj.last_updated = time.time()
    
    def get_active_players(self) -> List[PlayerState]:
        """Get list of active players"""
        return [p for p in self.players.values() if p.status == PlayerStatus.PLAYING]
    
    def get_spectators(self) -> List[PlayerState]:
        """Get list of spectators"""
        return [p for p in self.players.values() if p.status == PlayerStatus.SPECTATING]
    
    def advance_tick(self):
        """Advance game tick"""
        self.tick += 1
        self.timestamp = time.time()
    
    def serialize_for_client(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """Serialize state for client consumption"""
        state_data = {
            "game_id": self.game_id,
            "tick": self.tick,
            "timestamp": self.timestamp,
            "players": {pid: p.model_dump() for pid, p in self.players.items()},
            "objects": {oid: o.model_dump() for oid, o in self.objects.items()},
            "game_data": self.game_data,
            "started": self.started,
            "ended": self.ended
        }
        
        # Add player-specific data if requested
        if player_id and player_id in self.players:
            state_data["your_state"] = self.players[player_id].model_dump()
        
        return state_data
    
    def validate_player_input(self, player_id: str, input_data: Dict[str, Any], sequence: int) -> bool:
        """Validate player input"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        
        # Check if player is active
        if player.status != PlayerStatus.PLAYING:
            return False
        
        # Check sequence number (prevent replay attacks)
        if sequence <= player.last_input_sequence:
            return False
        
        # Update sequence
        player.last_input_sequence = sequence
        
        return True
    
    def apply_physics(self, delta_time: float):
        """Apply basic physics to all objects"""
        # Update player positions based on velocity
        for player in self.players.values():
            if player.status == PlayerStatus.PLAYING:
                player.position["x"] += player.velocity["x"] * delta_time
                player.position["y"] += player.velocity["y"] * delta_time
        
        # Update object positions
        for obj in self.objects.values():
            obj.position["x"] += obj.velocity["x"] * delta_time
            obj.position["y"] += obj.velocity["y"] * delta_time