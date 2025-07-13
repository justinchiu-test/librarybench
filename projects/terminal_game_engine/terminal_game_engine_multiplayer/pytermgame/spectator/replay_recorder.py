"""Replay recording functionality"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time
import json
import gzip
from io import BytesIO


class ReplayFrame(BaseModel):
    """Single frame of replay data"""
    frame_number: int
    timestamp: float
    tick: int
    game_state: Dict[str, Any]
    events: List[Dict[str, Any]] = Field(default_factory=list)
    
    def compress(self) -> bytes:
        """Compress frame data"""
        data = json.dumps(self.model_dump()).encode('utf-8')
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
            gz.write(data)
        return buffer.getvalue()
    
    @classmethod
    def decompress(cls, data: bytes) -> "ReplayFrame":
        """Decompress frame data"""
        buffer = BytesIO(data)
        with gzip.GzipFile(fileobj=buffer, mode='rb') as gz:
            json_data = gz.read().decode('utf-8')
        return cls(**json.loads(json_data))


class ReplayRecorder(BaseModel):
    """Records game replays"""
    game_id: str
    started_at: float = Field(default_factory=time.time)
    frames: List[ReplayFrame] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    max_frames: int = Field(10000, description="Maximum frames to store")
    recording: bool = Field(True)
    compression_enabled: bool = Field(True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def record_frame(self, tick: int, game_state: Dict[str, Any], events: Optional[List[Dict[str, Any]]] = None):
        """Record a game frame"""
        if not self.recording:
            return
        
        frame = ReplayFrame(
            frame_number=len(self.frames),
            timestamp=time.time(),
            tick=tick,
            game_state=game_state,
            events=events or []
        )
        
        self.frames.append(frame)
        
        # Limit frame count
        if len(self.frames) > self.max_frames:
            self.frames.pop(0)
    
    def add_event(self, event: Dict[str, Any]):
        """Add event to current frame"""
        if self.frames and self.recording:
            self.frames[-1].events.append(event)
    
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        self.metadata["ended_at"] = time.time()
        self.metadata["duration"] = self.metadata["ended_at"] - self.started_at
        self.metadata["total_frames"] = len(self.frames)
    
    def get_frame(self, frame_number: int) -> Optional[ReplayFrame]:
        """Get specific frame"""
        if 0 <= frame_number < len(self.frames):
            return self.frames[frame_number]
        return None
    
    def get_frame_at_time(self, timestamp: float) -> Optional[ReplayFrame]:
        """Get frame closest to timestamp"""
        if not self.frames:
            return None
        
        # Binary search for closest frame
        left, right = 0, len(self.frames) - 1
        
        while left < right:
            mid = (left + right) // 2
            if self.frames[mid].timestamp < timestamp:
                left = mid + 1
            else:
                right = mid
        
        # Find closest frame
        if left > 0:
            if abs(self.frames[left - 1].timestamp - timestamp) < abs(self.frames[left].timestamp - timestamp):
                return self.frames[left - 1]
        
        return self.frames[left]
    
    def get_frame_range(self, start_frame: int, end_frame: int) -> List[ReplayFrame]:
        """Get range of frames"""
        start = max(0, start_frame)
        end = min(len(self.frames), end_frame + 1)
        return self.frames[start:end]
    
    def save_to_bytes(self) -> bytes:
        """Save replay to bytes"""
        data = {
            "game_id": self.game_id,
            "started_at": self.started_at,
            "metadata": self.metadata,
            "frames": []
        }
        
        # Compress frames if enabled
        if self.compression_enabled:
            for frame in self.frames:
                data["frames"].append(frame.compress())
        else:
            data["frames"] = [f.model_dump() for f in self.frames]
        
        # Compress entire replay
        json_data = json.dumps(data).encode('utf-8')
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
            gz.write(json_data)
        
        return buffer.getvalue()
    
    @classmethod
    def load_from_bytes(cls, data: bytes) -> "ReplayRecorder":
        """Load replay from bytes"""
        buffer = BytesIO(data)
        with gzip.GzipFile(fileobj=buffer, mode='rb') as gz:
            json_data = gz.read().decode('utf-8')
        
        replay_data = json.loads(json_data)
        
        # Decompress frames
        frames = []
        if replay_data.get("frames"):
            if isinstance(replay_data["frames"][0], bytes):
                # Compressed frames
                for frame_data in replay_data["frames"]:
                    frames.append(ReplayFrame.decompress(frame_data))
            else:
                # Uncompressed frames
                for frame_data in replay_data["frames"]:
                    frames.append(ReplayFrame(**frame_data))
        
        return cls(
            game_id=replay_data["game_id"],
            started_at=replay_data["started_at"],
            frames=frames,
            metadata=replay_data["metadata"],
            recording=False
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get replay summary"""
        return {
            "game_id": self.game_id,
            "started_at": self.started_at,
            "duration": self.metadata.get("duration", time.time() - self.started_at),
            "total_frames": len(self.frames),
            "recording": self.recording,
            "metadata": self.metadata
        }