"""Animation models and data structures"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time

from ..sprites.models import Sprite


class Frame(BaseModel):
    """Single animation frame"""
    
    sprite: Sprite
    duration: float = Field(gt=0, default=0.1)  # Duration in seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Animation(BaseModel):
    """Sprite animation sequence"""
    
    name: str
    frames: List[Frame] = Field(default_factory=list)
    loop: bool = True
    fps: float = Field(gt=0, default=10.0)
    current_frame: int = 0
    playing: bool = False
    last_update: float = 0.0
    
    def add_frame(self, sprite: Sprite, duration: Optional[float] = None) -> Frame:
        """Add frame to animation"""
        if duration is None:
            duration = 1.0 / self.fps
        
        frame = Frame(sprite=sprite, duration=duration)
        self.frames.append(frame)
        return frame
    
    def remove_frame(self, index: int) -> None:
        """Remove frame by index"""
        if 0 <= index < len(self.frames):
            self.frames.pop(index)
            if self.current_frame >= len(self.frames) and len(self.frames) > 0:
                self.current_frame = len(self.frames) - 1
    
    def duplicate_frame(self, index: int) -> Optional[Frame]:
        """Duplicate frame at index"""
        if 0 <= index < len(self.frames):
            original = self.frames[index]
            # Deep copy the sprite
            new_sprite = Sprite(**original.sprite.model_dump())
            new_frame = Frame(sprite=new_sprite, duration=original.duration)
            self.frames.insert(index + 1, new_frame)
            return new_frame
        return None
    
    def move_frame(self, from_index: int, to_index: int) -> None:
        """Move frame to new position"""
        if (0 <= from_index < len(self.frames) and 
            0 <= to_index < len(self.frames)):
            frame = self.frames.pop(from_index)
            self.frames.insert(to_index, frame)
            
            # Update current frame if needed
            if self.current_frame == from_index:
                self.current_frame = to_index
            elif from_index < self.current_frame <= to_index:
                self.current_frame -= 1
            elif to_index <= self.current_frame < from_index:
                self.current_frame += 1
    
    def get_current_frame(self) -> Optional[Frame]:
        """Get current frame"""
        if 0 <= self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None
    
    def play(self) -> None:
        """Start playing animation"""
        self.playing = True
        self.last_update = time.time()
    
    def pause(self) -> None:
        """Pause animation"""
        self.playing = False
    
    def stop(self) -> None:
        """Stop animation and reset"""
        self.playing = False
        self.current_frame = 0
    
    def update(self) -> bool:
        """Update animation state, returns True if frame changed"""
        if not self.playing or len(self.frames) == 0:
            return False
        
        current_time = time.time()
        current_frame_obj = self.get_current_frame()
        
        if current_frame_obj is None:
            return False
        
        # Check if enough time has passed
        if current_time - self.last_update >= current_frame_obj.duration:
            self.last_update = current_time
            self.current_frame += 1
            
            # Handle looping
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False
            
            return True
        
        return False
    
    def set_frame(self, index: int) -> None:
        """Set current frame"""
        if 0 <= index < len(self.frames):
            self.current_frame = index
    
    def get_total_duration(self) -> float:
        """Get total animation duration"""
        return sum(frame.duration for frame in self.frames)


class AnimationSet(BaseModel):
    """Collection of animations"""
    
    name: str
    animations: Dict[str, Animation] = Field(default_factory=dict)
    current_animation: Optional[str] = None
    
    def add_animation(self, animation: Animation) -> None:
        """Add animation to set"""
        self.animations[animation.name] = animation
        if self.current_animation is None:
            self.current_animation = animation.name
    
    def remove_animation(self, name: str) -> None:
        """Remove animation by name"""
        if name in self.animations:
            del self.animations[name]
            if self.current_animation == name:
                self.current_animation = next(iter(self.animations), None)
    
    def get_current_animation(self) -> Optional[Animation]:
        """Get current animation"""
        if self.current_animation:
            return self.animations.get(self.current_animation)
        return None
    
    def set_current_animation(self, name: str) -> bool:
        """Set current animation"""
        if name in self.animations:
            self.current_animation = name
            return True
        return False
    
    def play(self, animation_name: Optional[str] = None) -> None:
        """Play animation"""
        if animation_name:
            self.set_current_animation(animation_name)
        
        animation = self.get_current_animation()
        if animation:
            animation.play()
    
    def pause(self) -> None:
        """Pause current animation"""
        animation = self.get_current_animation()
        if animation:
            animation.pause()
    
    def stop(self) -> None:
        """Stop current animation"""
        animation = self.get_current_animation()
        if animation:
            animation.stop()
    
    def update(self) -> bool:
        """Update current animation"""
        animation = self.get_current_animation()
        if animation:
            return animation.update()
        return False