"""Server reconciliation for lag compensation"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import time
from collections import deque


class PlayerSnapshot(BaseModel):
    """Snapshot of player state at a specific time"""
    player_id: str
    timestamp: float
    sequence_number: int
    position: Dict[str, float]
    velocity: Dict[str, float]
    hitbox: Dict[str, float] = Field(default_factory=lambda: {"width": 1.0, "height": 1.0})


class ServerReconciliation:
    """Handles server-side reconciliation and rewind"""
    
    def __init__(self, history_duration: float = 1.0):
        self.history_duration = history_duration
        self.player_history: Dict[str, deque[PlayerSnapshot]] = {}
        self.max_rewind_time = 0.5  # Maximum rewind time in seconds
    
    def record_player_state(self, player_id: str, sequence_number: int,
                           position: Dict[str, float], velocity: Dict[str, float],
                           hitbox: Optional[Dict[str, float]] = None):
        """Record player state for history"""
        if player_id not in self.player_history:
            self.player_history[player_id] = deque()
        
        snapshot = PlayerSnapshot(
            player_id=player_id,
            timestamp=time.time(),
            sequence_number=sequence_number,
            position=position.copy(),
            velocity=velocity.copy(),
            hitbox=hitbox or {"width": 1.0, "height": 1.0}
        )
        
        self.player_history[player_id].append(snapshot)
        
        # Clean old history
        self._cleanup_history(player_id)
    
    def _cleanup_history(self, player_id: str):
        """Remove old snapshots"""
        if player_id not in self.player_history:
            return
        
        current_time = time.time()
        cutoff_time = current_time - self.history_duration
        
        history = self.player_history[player_id]
        while history and history[0].timestamp < cutoff_time:
            history.popleft()
    
    def get_player_at_time(self, player_id: str, timestamp: float) -> Optional[PlayerSnapshot]:
        """Get player state at specific timestamp"""
        if player_id not in self.player_history or not self.player_history[player_id]:
            return None
        
        history = self.player_history[player_id]
        
        # Check bounds
        if timestamp < history[0].timestamp:
            return history[0]
        if timestamp > history[-1].timestamp:
            return history[-1]
        
        # Find closest snapshots
        prev_snapshot = None
        next_snapshot = None
        
        for snapshot in history:
            if snapshot.timestamp <= timestamp:
                prev_snapshot = snapshot
            else:
                next_snapshot = snapshot
                break
        
        # Interpolate if we have both snapshots
        if prev_snapshot and next_snapshot:
            return self._interpolate_snapshots(prev_snapshot, next_snapshot, timestamp)
        
        return prev_snapshot or next_snapshot
    
    def _interpolate_snapshots(self, prev: PlayerSnapshot, next: PlayerSnapshot, 
                             timestamp: float) -> PlayerSnapshot:
        """Interpolate between two snapshots"""
        # Calculate interpolation factor
        total_time = next.timestamp - prev.timestamp
        if total_time <= 0:
            return prev
        
        t = (timestamp - prev.timestamp) / total_time
        t = max(0, min(1, t))  # Clamp to [0, 1]
        
        # Interpolate position
        position = {
            "x": prev.position["x"] + (next.position["x"] - prev.position["x"]) * t,
            "y": prev.position["y"] + (next.position["y"] - prev.position["y"]) * t
        }
        
        # Interpolate velocity
        velocity = {
            "x": prev.velocity["x"] + (next.velocity["x"] - prev.velocity["x"]) * t,
            "y": prev.velocity["y"] + (next.velocity["y"] - prev.velocity["y"]) * t
        }
        
        return PlayerSnapshot(
            player_id=prev.player_id,
            timestamp=timestamp,
            sequence_number=prev.sequence_number,
            position=position,
            velocity=velocity,
            hitbox=prev.hitbox
        )
    
    def verify_hit(self, shooter_id: str, target_id: str, shot_position: Dict[str, float],
                   shot_timestamp: float) -> Tuple[bool, Optional[Dict[str, float]]]:
        """Verify if a hit was valid based on historical data"""
        # Limit how far back we can rewind
        current_time = time.time()
        if shot_timestamp < current_time - self.max_rewind_time:
            return False, None
        
        # Get target position at shot time
        target_snapshot = self.get_player_at_time(target_id, shot_timestamp)
        if not target_snapshot:
            return False, None
        
        # Check if shot hit the target's hitbox
        hit = self._check_hit(shot_position, target_snapshot.position, target_snapshot.hitbox)
        
        if hit:
            return True, target_snapshot.position
        
        return False, None
    
    def _check_hit(self, shot_pos: Dict[str, float], target_pos: Dict[str, float], 
                   hitbox: Dict[str, float]) -> bool:
        """Check if shot position intersects with target hitbox"""
        # Simple AABB collision detection
        half_width = hitbox["width"] / 2
        half_height = hitbox["height"] / 2
        
        return (
            shot_pos["x"] >= target_pos["x"] - half_width and
            shot_pos["x"] <= target_pos["x"] + half_width and
            shot_pos["y"] >= target_pos["y"] - half_height and
            shot_pos["y"] <= target_pos["y"] + half_height
        )
    
    def get_world_state_at_time(self, timestamp: float) -> Dict[str, PlayerSnapshot]:
        """Get all player states at specific timestamp"""
        world_state = {}
        
        for player_id in self.player_history:
            snapshot = self.get_player_at_time(player_id, timestamp)
            if snapshot:
                world_state[player_id] = snapshot
        
        return world_state
    
    def validate_player_input(self, player_id: str, input_sequence: int, 
                            input_timestamp: float, claimed_position: Dict[str, float]) -> bool:
        """Validate player input against historical data"""
        # Get player state at input time
        snapshot = self.get_player_at_time(player_id, input_timestamp)
        if not snapshot:
            return True  # Allow if no history
        
        # Check if claimed position is reasonable
        max_deviation = 10.0  # Maximum allowed deviation
        dx = abs(claimed_position["x"] - snapshot.position["x"])
        dy = abs(claimed_position["y"] - snapshot.position["y"])
        
        return dx <= max_deviation and dy <= max_deviation