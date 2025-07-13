"""Entity interpolation for smooth movement"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import time
from collections import deque


class InterpolationSnapshot(BaseModel):
    """Snapshot for interpolation"""
    timestamp: float
    position: Dict[str, float]
    velocity: Dict[str, float]
    rotation: float = Field(0.0)
    data: Dict[str, Any] = Field(default_factory=dict)


class EntityBuffer(BaseModel):
    """Buffer for entity interpolation"""
    entity_id: str
    snapshots: deque[InterpolationSnapshot] = Field(default_factory=lambda: deque(maxlen=10))
    interpolation_delay: float = Field(0.1, description="Interpolation delay in seconds")
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_snapshot(self, position: Dict[str, float], velocity: Dict[str, float], 
                    rotation: float = 0.0, data: Optional[Dict[str, Any]] = None):
        """Add a new snapshot"""
        snapshot = InterpolationSnapshot(
            timestamp=time.time(),
            position=position.copy(),
            velocity=velocity.copy(),
            rotation=rotation,
            data=data or {}
        )
        self.snapshots.append(snapshot)
    
    def get_interpolated_state(self, current_time: float) -> Optional[InterpolationSnapshot]:
        """Get interpolated state at current time"""
        if len(self.snapshots) < 2:
            return self.snapshots[-1] if self.snapshots else None
        
        # Apply interpolation delay
        render_time = current_time - self.interpolation_delay
        
        # Find snapshots to interpolate between
        prev_snapshot = None
        next_snapshot = None
        
        for i in range(len(self.snapshots) - 1):
            if self.snapshots[i].timestamp <= render_time <= self.snapshots[i + 1].timestamp:
                prev_snapshot = self.snapshots[i]
                next_snapshot = self.snapshots[i + 1]
                break
        
        if not prev_snapshot or not next_snapshot:
            # Use latest snapshot if we can't interpolate
            return self.snapshots[-1]
        
        # Calculate interpolation factor
        total_time = next_snapshot.timestamp - prev_snapshot.timestamp
        if total_time <= 0:
            return next_snapshot
        
        t = (render_time - prev_snapshot.timestamp) / total_time
        t = max(0, min(1, t))  # Clamp to [0, 1]
        
        # Interpolate values
        position = {
            "x": self._lerp(prev_snapshot.position["x"], next_snapshot.position["x"], t),
            "y": self._lerp(prev_snapshot.position["y"], next_snapshot.position["y"], t)
        }
        
        velocity = {
            "x": self._lerp(prev_snapshot.velocity["x"], next_snapshot.velocity["x"], t),
            "y": self._lerp(prev_snapshot.velocity["y"], next_snapshot.velocity["y"], t)
        }
        
        rotation = self._lerp(prev_snapshot.rotation, next_snapshot.rotation, t)
        
        return InterpolationSnapshot(
            timestamp=render_time,
            position=position,
            velocity=velocity,
            rotation=rotation,
            data=next_snapshot.data  # Use latest data
        )
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation"""
        return a + (b - a) * t


class Interpolator:
    """Manages entity interpolation for smooth rendering"""
    
    def __init__(self, default_delay: float = 0.1):
        self.default_delay = default_delay
        self.entity_buffers: Dict[str, EntityBuffer] = {}
        self.smoothing_enabled = True
    
    def update_entity(self, entity_id: str, position: Dict[str, float], 
                     velocity: Dict[str, float], rotation: float = 0.0,
                     data: Optional[Dict[str, Any]] = None):
        """Update entity with new state"""
        if entity_id not in self.entity_buffers:
            self.entity_buffers[entity_id] = EntityBuffer(
                entity_id=entity_id,
                interpolation_delay=self.default_delay
            )
        
        buffer = self.entity_buffers[entity_id]
        buffer.add_snapshot(position, velocity, rotation, data)
    
    def get_interpolated_position(self, entity_id: str) -> Optional[Dict[str, float]]:
        """Get interpolated position for entity"""
        if not self.smoothing_enabled:
            # Return latest position without interpolation
            if entity_id in self.entity_buffers:
                buffer = self.entity_buffers[entity_id]
                if buffer.snapshots:
                    return buffer.snapshots[-1].position
            return None
        
        if entity_id not in self.entity_buffers:
            return None
        
        buffer = self.entity_buffers[entity_id]
        state = buffer.get_interpolated_state(time.time())
        
        return state.position if state else None
    
    def get_interpolated_state(self, entity_id: str) -> Optional[InterpolationSnapshot]:
        """Get full interpolated state for entity"""
        if entity_id not in self.entity_buffers:
            return None
        
        buffer = self.entity_buffers[entity_id]
        return buffer.get_interpolated_state(time.time())
    
    def set_interpolation_delay(self, entity_id: str, delay: float):
        """Set custom interpolation delay for entity"""
        if entity_id in self.entity_buffers:
            self.entity_buffers[entity_id].interpolation_delay = delay
    
    def remove_entity(self, entity_id: str):
        """Remove entity from interpolation"""
        if entity_id in self.entity_buffers:
            del self.entity_buffers[entity_id]
    
    def get_all_interpolated_states(self) -> Dict[str, InterpolationSnapshot]:
        """Get interpolated states for all entities"""
        current_time = time.time()
        states = {}
        
        for entity_id, buffer in self.entity_buffers.items():
            state = buffer.get_interpolated_state(current_time)
            if state:
                states[entity_id] = state
        
        return states
    
    def enable_smoothing(self, enabled: bool = True):
        """Enable or disable interpolation smoothing"""
        self.smoothing_enabled = enabled
    
    def clear(self):
        """Clear all interpolation buffers"""
        self.entity_buffers.clear()