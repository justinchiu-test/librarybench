"""Animation editor with onion skinning support"""

from typing import Optional, List, Tuple, Dict, Any
from pydantic import BaseModel, Field

from .models import Animation, Frame, AnimationSet
from ..sprites.models import Sprite, Layer, Pixel, Color
from ..sprites.editor import SpriteEditor


class OnionSkinSettings(BaseModel):
    """Onion skinning configuration"""
    
    enabled: bool = True
    frames_before: int = Field(ge=0, le=5, default=2)
    frames_after: int = Field(ge=0, le=5, default=1)
    opacity_before: float = Field(ge=0.0, le=1.0, default=0.3)
    opacity_after: float = Field(ge=0.0, le=1.0, default=0.2)
    color_before: Color = Field(default_factory=lambda: Color(r=255, g=0, b=0))
    color_after: Color = Field(default_factory=lambda: Color(r=0, g=255, b=0))


class AnimatorState(BaseModel):
    """Animator state"""
    
    animation_set: AnimationSet
    active_animation: Optional[str] = None
    active_frame: int = 0
    onion_skin: OnionSkinSettings = Field(default_factory=OnionSkinSettings)
    preview_playing: bool = False
    sprite_editor: Optional[Dict[str, Any]] = None


class Animator:
    """Animation editor with frame management and onion skinning"""
    
    def __init__(self, animation_set: Optional[AnimationSet] = None):
        """Initialize animator"""
        if animation_set is None:
            animation_set = AnimationSet(name="New Animation Set")
        
        self.state = AnimatorState(animation_set=animation_set)
        self._sprite_editor: Optional[SpriteEditor] = None
    
    @property
    def animation_set(self) -> AnimationSet:
        """Get animation set"""
        return self.state.animation_set
    
    @property
    def current_animation(self) -> Optional[Animation]:
        """Get current animation"""
        if self.state.active_animation:
            return self.animation_set.animations.get(self.state.active_animation)
        return None
    
    @property
    def current_frame(self) -> Optional[Frame]:
        """Get current frame"""
        animation = self.current_animation
        if animation and 0 <= self.state.active_frame < len(animation.frames):
            return animation.frames[self.state.active_frame]
        return None
    
    @property
    def sprite_editor(self) -> Optional[SpriteEditor]:
        """Get sprite editor for current frame"""
        frame = self.current_frame
        if frame:
            if self._sprite_editor is None or self._sprite_editor.sprite != frame.sprite:
                self._sprite_editor = SpriteEditor(frame.sprite)
            return self._sprite_editor
        return None
    
    def create_animation(self, name: str, width: int = 32, height: int = 32) -> Animation:
        """Create new animation"""
        animation = Animation(name=name)
        
        # Add initial frame
        sprite = Sprite(name=f"{name}_frame_1", width=width, height=height)
        sprite.add_layer("Layer 1")
        animation.add_frame(sprite)
        
        self.animation_set.add_animation(animation)
        self.state.active_animation = name
        self.state.active_frame = 0
        
        return animation
    
    def delete_animation(self, name: str) -> None:
        """Delete animation"""
        self.animation_set.remove_animation(name)
        if self.state.active_animation == name:
            self.state.active_animation = None
            self.state.active_frame = 0
    
    def set_active_animation(self, name: str) -> bool:
        """Set active animation"""
        if name in self.animation_set.animations:
            self.state.active_animation = name
            self.state.active_frame = 0
            self._sprite_editor = None
            return True
        return False
    
    def add_frame(self, after_index: Optional[int] = None) -> Optional[Frame]:
        """Add new frame to current animation"""
        animation = self.current_animation
        if not animation:
            return None
        
        # Create new sprite based on current frame or empty
        current = self.current_frame
        if current:
            sprite = Sprite(**current.sprite.model_dump())
            sprite.name = f"{animation.name}_frame_{len(animation.frames) + 1}"
        else:
            sprite = Sprite(
                name=f"{animation.name}_frame_{len(animation.frames) + 1}",
                width=32,
                height=32
            )
            sprite.add_layer("Layer 1")
        
        # Insert frame
        frame = Frame(sprite=sprite)
        if after_index is not None and 0 <= after_index < len(animation.frames):
            animation.frames.insert(after_index + 1, frame)
            self.state.active_frame = after_index + 1
        else:
            animation.frames.append(frame)
            self.state.active_frame = len(animation.frames) - 1
        
        self._sprite_editor = None
        return frame
    
    def duplicate_frame(self, index: Optional[int] = None) -> Optional[Frame]:
        """Duplicate frame"""
        animation = self.current_animation
        if not animation:
            return None
        
        if index is None:
            index = self.state.active_frame
        
        new_frame = animation.duplicate_frame(index)
        if new_frame:
            self.state.active_frame = index + 1
            self._sprite_editor = None
        
        return new_frame
    
    def delete_frame(self, index: Optional[int] = None) -> None:
        """Delete frame"""
        animation = self.current_animation
        if not animation or len(animation.frames) <= 1:
            return
        
        if index is None:
            index = self.state.active_frame
        
        animation.remove_frame(index)
        if self.state.active_frame >= len(animation.frames):
            self.state.active_frame = len(animation.frames) - 1
        
        self._sprite_editor = None
    
    def move_frame(self, from_index: int, to_index: int) -> None:
        """Move frame to new position"""
        animation = self.current_animation
        if animation:
            animation.move_frame(from_index, to_index)
            if self.state.active_frame == from_index:
                self.state.active_frame = to_index
    
    def set_active_frame(self, index: int) -> None:
        """Set active frame"""
        animation = self.current_animation
        if animation and 0 <= index < len(animation.frames):
            self.state.active_frame = index
            self._sprite_editor = None
    
    def next_frame(self) -> None:
        """Go to next frame"""
        animation = self.current_animation
        if animation and self.state.active_frame < len(animation.frames) - 1:
            self.state.active_frame += 1
            self._sprite_editor = None
    
    def previous_frame(self) -> None:
        """Go to previous frame"""
        if self.state.active_frame > 0:
            self.state.active_frame -= 1
            self._sprite_editor = None
    
    def set_frame_duration(self, duration: float, index: Optional[int] = None) -> None:
        """Set frame duration"""
        if index is None:
            frame = self.current_frame
        else:
            animation = self.current_animation
            if animation and 0 <= index < len(animation.frames):
                frame = animation.frames[index]
            else:
                frame = None
        
        if frame and duration > 0:
            frame.duration = duration
    
    def get_onion_skin_frames(self) -> List[Tuple[Frame, float, Color]]:
        """Get frames for onion skinning with opacity and color"""
        if not self.state.onion_skin.enabled:
            return []
        
        animation = self.current_animation
        if not animation:
            return []
        
        frames = []
        current_idx = self.state.active_frame
        
        # Previous frames
        for i in range(1, self.state.onion_skin.frames_before + 1):
            idx = current_idx - i
            if idx >= 0:
                opacity = self.state.onion_skin.opacity_before * (1.0 - i / (self.state.onion_skin.frames_before + 1))
                frames.append((
                    animation.frames[idx],
                    opacity,
                    self.state.onion_skin.color_before
                ))
        
        # Future frames
        for i in range(1, self.state.onion_skin.frames_after + 1):
            idx = current_idx + i
            if idx < len(animation.frames):
                opacity = self.state.onion_skin.opacity_after * (1.0 - i / (self.state.onion_skin.frames_after + 1))
                frames.append((
                    animation.frames[idx],
                    opacity,
                    self.state.onion_skin.color_after
                ))
        
        return frames
    
    def render_with_onion_skin(self) -> List[List[Optional[Pixel]]]:
        """Render current frame with onion skinning"""
        frame = self.current_frame
        if not frame:
            return []
        
        # Start with empty canvas
        width = frame.sprite.width
        height = frame.sprite.height
        result = [[None for _ in range(width)] for _ in range(height)]
        
        # Render onion skin frames first
        for skin_frame, opacity, tint_color in self.get_onion_skin_frames():
            skin_composite = skin_frame.sprite.composite()
            
            for y in range(height):
                for x in range(width):
                    pixel = skin_composite[y][x]
                    if pixel:
                        # Apply tint and opacity
                        tinted_color = pixel.color.blend(tint_color, 0.5)
                        tinted_color.a = opacity
                        
                        if result[y][x] is None:
                            result[y][x] = Pixel(
                                char=pixel.char,
                                color=tinted_color
                            )
                        else:
                            # Blend with existing
                            result[y][x].color = result[y][x].color.blend(tinted_color, opacity)
        
        # Render current frame on top
        current_composite = frame.sprite.composite()
        for y in range(height):
            for x in range(width):
                pixel = current_composite[y][x]
                if pixel:
                    result[y][x] = pixel
        
        return result
    
    def toggle_onion_skin(self) -> None:
        """Toggle onion skinning"""
        self.state.onion_skin.enabled = not self.state.onion_skin.enabled
    
    def set_onion_skin_settings(self, settings: OnionSkinSettings) -> None:
        """Update onion skin settings"""
        self.state.onion_skin = settings
    
    def play_preview(self) -> None:
        """Start animation preview"""
        animation = self.current_animation
        if animation:
            self.state.preview_playing = True
            animation.play()
    
    def stop_preview(self) -> None:
        """Stop animation preview"""
        animation = self.current_animation
        if animation:
            self.state.preview_playing = False
            animation.stop()
            self.state.active_frame = 0
    
    def update_preview(self) -> bool:
        """Update preview animation"""
        if not self.state.preview_playing:
            return False
        
        animation = self.current_animation
        if animation and animation.update():
            self.state.active_frame = animation.current_frame
            self._sprite_editor = None
            return True
        
        return False
    
    def export_animation(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Export animation data"""
        if name:
            animation = self.animation_set.animations.get(name)
        else:
            animation = self.current_animation
        
        if animation:
            return animation.model_dump()
        return None
    
    def import_animation(self, data: Dict[str, Any]) -> Animation:
        """Import animation data"""
        animation = Animation(**data)
        self.animation_set.add_animation(animation)
        return animation