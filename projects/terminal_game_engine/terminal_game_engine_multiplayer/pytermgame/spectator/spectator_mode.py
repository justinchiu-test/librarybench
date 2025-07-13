"""Spectator mode implementation"""

from typing import Dict, List, Optional, Set, Any, Callable
from pydantic import BaseModel, Field
from enum import Enum
import time
import asyncio

from ..network import Packet, PacketType
from .replay_recorder import ReplayRecorder


class ViewMode(Enum):
    """Spectator view modes"""
    FREE_CAMERA = "free_camera"
    FOLLOW_PLAYER = "follow_player"
    OVERVIEW = "overview"
    REPLAY = "replay"


class SpectatorView(BaseModel):
    """Spectator view configuration"""
    spectator_id: str
    view_mode: ViewMode = Field(ViewMode.FREE_CAMERA)
    target_player_id: Optional[str] = Field(None)
    camera_position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    zoom_level: float = Field(1.0)
    delay_seconds: float = Field(3.0, description="Delay to prevent cheating")
    joined_at: float = Field(default_factory=time.time)
    
    def update_position(self, position: Dict[str, float]):
        """Update camera position"""
        self.camera_position = position
    
    def follow_player(self, player_id: str):
        """Switch to following a player"""
        self.view_mode = ViewMode.FOLLOW_PLAYER
        self.target_player_id = player_id
    
    def free_camera(self):
        """Switch to free camera mode"""
        self.view_mode = ViewMode.FREE_CAMERA
        self.target_player_id = None


class SpectatorMode:
    """Manages spectator functionality"""
    
    def __init__(self, game_id: str, enable_replay: bool = True):
        self.game_id = game_id
        self.spectators: Dict[str, SpectatorView] = {}
        self.game_state_buffer: List[Dict[str, Any]] = []
        self.buffer_duration = 10.0  # Keep 10 seconds of states
        self.max_spectators = 100
        
        # Replay recording
        self.enable_replay = enable_replay
        self.replay_recorder: Optional[ReplayRecorder] = None
        if enable_replay:
            self.replay_recorder = ReplayRecorder(game_id=game_id)
        
        # Callbacks
        self.spectator_join_callbacks: List[Callable] = []
        self.spectator_leave_callbacks: List[Callable] = []
        
        self.running = False
    
    async def start(self):
        """Start spectator mode"""
        self.running = True
        asyncio.create_task(self._cleanup_buffer_loop())
    
    async def stop(self):
        """Stop spectator mode"""
        self.running = False
        if self.replay_recorder:
            self.replay_recorder.stop_recording()
    
    def add_spectator(self, spectator_id: str, delay_seconds: float = 3.0) -> bool:
        """Add a spectator"""
        if len(self.spectators) >= self.max_spectators:
            return False
        
        if spectator_id in self.spectators:
            return False
        
        spectator = SpectatorView(
            spectator_id=spectator_id,
            delay_seconds=delay_seconds
        )
        
        self.spectators[spectator_id] = spectator
        
        # Notify callbacks
        for callback in self.spectator_join_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(spectator_id))
                else:
                    callback(spectator_id)
            except Exception:
                pass
        
        return True
    
    def remove_spectator(self, spectator_id: str) -> bool:
        """Remove a spectator"""
        if spectator_id not in self.spectators:
            return False
        
        del self.spectators[spectator_id]
        
        # Notify callbacks
        for callback in self.spectator_leave_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(spectator_id))
                else:
                    callback(spectator_id)
            except Exception:
                pass
        
        return True
    
    def update_game_state(self, tick: int, game_state: Dict[str, Any], events: Optional[List[Dict[str, Any]]] = None):
        """Update game state for spectators"""
        timestamped_state = {
            "timestamp": time.time(),
            "tick": tick,
            "state": game_state,
            "events": events or []
        }
        
        self.game_state_buffer.append(timestamped_state)
        
        # Record to replay if enabled
        if self.replay_recorder and self.replay_recorder.recording:
            self.replay_recorder.record_frame(tick, game_state, events)
    
    def get_delayed_state(self, spectator_id: str) -> Optional[Dict[str, Any]]:
        """Get game state with appropriate delay for spectator"""
        if spectator_id not in self.spectators:
            return None
        
        spectator = self.spectators[spectator_id]
        current_time = time.time()
        target_time = current_time - spectator.delay_seconds
        
        # Find appropriate state from buffer
        for state in reversed(self.game_state_buffer):
            if state["timestamp"] <= target_time:
                return self._create_spectator_state(state, spectator)
        
        return None
    
    def _create_spectator_state(self, state: Dict[str, Any], spectator: SpectatorView) -> Dict[str, Any]:
        """Create state packet for spectator"""
        spectator_state = {
            "timestamp": state["timestamp"],
            "tick": state["tick"],
            "state": state["state"],
            "events": state["events"],
            "spectator_info": {
                "view_mode": spectator.view_mode.value,
                "camera_position": spectator.camera_position,
                "zoom_level": spectator.zoom_level,
                "target_player_id": spectator.target_player_id,
                "delay": spectator.delay_seconds
            }
        }
        
        # Apply view mode modifications
        if spectator.view_mode == ViewMode.FOLLOW_PLAYER and spectator.target_player_id:
            # Center camera on target player
            players = state["state"].get("players", {})
            if spectator.target_player_id in players:
                player_pos = players[spectator.target_player_id].get("position", {"x": 0, "y": 0})
                spectator.camera_position = player_pos.copy()
                spectator_state["spectator_info"]["camera_position"] = player_pos
        
        return spectator_state
    
    def set_view_mode(self, spectator_id: str, view_mode: ViewMode, target_player_id: Optional[str] = None) -> bool:
        """Set spectator view mode"""
        if spectator_id not in self.spectators:
            return False
        
        spectator = self.spectators[spectator_id]
        spectator.view_mode = view_mode
        
        if view_mode == ViewMode.FOLLOW_PLAYER and target_player_id:
            spectator.target_player_id = target_player_id
        else:
            spectator.target_player_id = None
        
        return True
    
    def update_camera(self, spectator_id: str, position: Dict[str, float], zoom: float = 1.0) -> bool:
        """Update spectator camera"""
        if spectator_id not in self.spectators:
            return False
        
        spectator = self.spectators[spectator_id]
        spectator.camera_position = position
        spectator.zoom_level = max(0.5, min(2.0, zoom))  # Clamp zoom
        
        return True
    
    async def _cleanup_buffer_loop(self):
        """Clean up old states from buffer"""
        while self.running:
            current_time = time.time()
            cutoff_time = current_time - self.buffer_duration
            
            # Remove old states
            self.game_state_buffer = [
                state for state in self.game_state_buffer
                if state["timestamp"] > cutoff_time
            ]
            
            await asyncio.sleep(1.0)
    
    def get_spectator_count(self) -> int:
        """Get number of spectators"""
        return len(self.spectators)
    
    def get_spectator_list(self) -> List[Dict[str, Any]]:
        """Get list of spectators"""
        return [
            {
                "spectator_id": spec.spectator_id,
                "view_mode": spec.view_mode.value,
                "target_player": spec.target_player_id,
                "joined_at": spec.joined_at
            }
            for spec in self.spectators.values()
        ]
    
    def on_spectator_join(self, callback: Callable):
        """Register spectator join callback"""
        self.spectator_join_callbacks.append(callback)
    
    def on_spectator_leave(self, callback: Callable):
        """Register spectator leave callback"""
        self.spectator_leave_callbacks.append(callback)
    
    def get_replay(self) -> Optional[ReplayRecorder]:
        """Get replay recorder"""
        return self.replay_recorder
    
    def save_replay(self) -> Optional[bytes]:
        """Save replay data"""
        if self.replay_recorder:
            return self.replay_recorder.save_to_bytes()
        return None