"""ASCII sprite editor with drawing tools"""

from typing import Optional, List, Tuple, Dict, Any, Callable
from enum import Enum
import math
from pydantic import BaseModel, Field

from .models import Sprite, Layer, Pixel, Color, Palette
from .tools import DrawingTool, PencilTool, BrushTool, LineTool, RectangleTool, CircleTool, FillTool


class EditMode(str, Enum):
    """Editor mode"""
    
    DRAW = "draw"
    ERASE = "erase"
    PICK = "pick"
    SELECT = "select"


class EditorState(BaseModel):
    """Editor state"""
    
    sprite: Sprite
    active_layer: int = 0
    active_tool: str = "pencil"
    primary_color: Color = Field(default_factory=lambda: Color(r=255, g=255, b=255))
    secondary_color: Color = Field(default_factory=lambda: Color(r=0, g=0, b=0))
    mode: EditMode = EditMode.DRAW
    palette: Optional[Palette] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    history_index: int = -1
    max_history: int = 100


class SpriteEditor:
    """ASCII sprite editor"""
    
    def __init__(self, sprite: Optional[Sprite] = None):
        """Initialize editor"""
        if sprite is None:
            sprite = Sprite(name="New Sprite", width=32, height=32)
            sprite.add_layer("Background")
        
        self.state = EditorState(sprite=sprite)
        self.tools: Dict[str, DrawingTool] = {
            "pencil": PencilTool(),
            "brush": BrushTool(),
            "line": LineTool(),
            "rectangle": RectangleTool(),
            "circle": CircleTool(),
            "fill": FillTool(),
        }
        
        # Initialize default palette
        self.state.palette = Palette(name="Default")
        for r in [0, 128, 255]:
            for g in [0, 128, 255]:
                for b in [0, 128, 255]:
                    self.state.palette.add_color(Color(r=r, g=g, b=b))
    
    @property
    def sprite(self) -> Sprite:
        """Get current sprite"""
        return self.state.sprite
    
    @property
    def active_layer(self) -> Optional[Layer]:
        """Get active layer"""
        if 0 <= self.state.active_layer < len(self.sprite.layers):
            return self.sprite.layers[self.state.active_layer]
        return None
    
    def set_tool(self, tool_name: str) -> None:
        """Set active drawing tool"""
        if tool_name in self.tools:
            self.state.active_tool = tool_name
    
    def set_primary_color(self, color: Color) -> None:
        """Set primary color"""
        self.state.primary_color = color
    
    def set_secondary_color(self, color: Color) -> None:
        """Set secondary color"""
        self.state.secondary_color = color
    
    def swap_colors(self) -> None:
        """Swap primary and secondary colors"""
        self.state.primary_color, self.state.secondary_color = \
            self.state.secondary_color, self.state.primary_color
    
    def set_mode(self, mode: EditMode) -> None:
        """Set editor mode"""
        self.state.mode = mode
    
    def add_layer(self, name: str, index: Optional[int] = None) -> Layer:
        """Add new layer"""
        layer = self.sprite.add_layer(name, index)
        if index is not None and index <= self.state.active_layer:
            self.state.active_layer += 1
        self._save_history("add_layer", {"name": name, "index": index})
        return layer
    
    def remove_layer(self, index: int) -> None:
        """Remove layer"""
        if len(self.sprite.layers) > 1:
            self.sprite.remove_layer(index)
            if self.state.active_layer >= len(self.sprite.layers):
                self.state.active_layer = len(self.sprite.layers) - 1
            self._save_history("remove_layer", {"index": index})
    
    def set_active_layer(self, index: int) -> None:
        """Set active layer"""
        if 0 <= index < len(self.sprite.layers):
            self.state.active_layer = index
    
    def draw_pixel(self, x: int, y: int, char: Optional[str] = None) -> None:
        """Draw single pixel"""
        layer = self.active_layer
        if layer is None:
            return
        
        if self.state.mode == EditMode.DRAW:
            pixel = Pixel(
                char=char or '#',
                color=self.state.primary_color
            )
            layer.set_pixel(x, y, pixel)
        elif self.state.mode == EditMode.ERASE:
            layer.set_pixel(x, y, None)
        elif self.state.mode == EditMode.PICK:
            pixel = layer.get_pixel(x, y)
            if pixel:
                self.state.primary_color = pixel.color
    
    def draw_with_tool(self, start_x: int, start_y: int, end_x: int, end_y: int,
                      char: Optional[str] = None) -> None:
        """Draw using active tool"""
        layer = self.active_layer
        if layer is None or self.state.mode not in [EditMode.DRAW, EditMode.ERASE]:
            return
        
        tool = self.tools.get(self.state.active_tool)
        if tool is None:
            return
        
        color = self.state.primary_color if self.state.mode == EditMode.DRAW else None
        points = tool.get_points(start_x, start_y, end_x, end_y)
        
        for x, y in points:
            if self.state.mode == EditMode.DRAW:
                pixel = Pixel(char=char or tool.default_char, color=color)
                layer.set_pixel(x, y, pixel)
            else:
                layer.set_pixel(x, y, None)
        
        self._save_history("draw", {
            "tool": self.state.active_tool,
            "start": (start_x, start_y),
            "end": (end_x, end_y),
            "mode": self.state.mode.value
        })
    
    def fill_area(self, x: int, y: int, char: Optional[str] = None) -> None:
        """Fill connected area"""
        layer = self.active_layer
        if layer is None or self.state.mode != EditMode.DRAW:
            return
        
        tool = self.tools.get("fill")
        if not isinstance(tool, FillTool):
            return
        
        points = tool.get_fill_points(layer, x, y)
        color = self.state.primary_color
        
        for px, py in points:
            pixel = Pixel(char=char or '#', color=color)
            layer.set_pixel(px, py, pixel)
        
        self._save_history("fill", {"x": x, "y": y})
    
    def clear_layer(self) -> None:
        """Clear active layer"""
        layer = self.active_layer
        if layer:
            layer.clear()
            self._save_history("clear_layer", {"layer_index": self.state.active_layer})
    
    def resize_sprite(self, width: int, height: int) -> None:
        """Resize sprite and all layers"""
        old_width = self.sprite.width
        old_height = self.sprite.height
        
        self.sprite.width = width
        self.sprite.height = height
        
        for layer in self.sprite.layers:
            layer.resize(width, height)
        
        self._save_history("resize", {
            "old_size": (old_width, old_height),
            "new_size": (width, height)
        })
    
    def undo(self) -> bool:
        """Undo last action"""
        if self.state.history_index > 0:
            self.state.history_index -= 1
            # In a real implementation, we would restore the state
            return True
        return False
    
    def redo(self) -> bool:
        """Redo action"""
        if self.state.history_index < len(self.state.history) - 1:
            self.state.history_index += 1
            # In a real implementation, we would restore the state
            return True
        return False
    
    def _save_history(self, action: str, data: Dict[str, Any]) -> None:
        """Save action to history"""
        # Remove any history after current index
        self.state.history = self.state.history[:self.state.history_index + 1]
        
        # Add new action
        self.state.history.append({
            "action": action,
            "data": data,
            "sprite_state": self.sprite.model_dump()
        })
        
        # Limit history size
        if len(self.state.history) > self.state.max_history:
            self.state.history.pop(0)
        else:
            self.state.history_index += 1
    
    def export_sprite(self) -> Dict[str, Any]:
        """Export sprite data"""
        return self.sprite.model_dump()
    
    def import_sprite(self, data: Dict[str, Any]) -> None:
        """Import sprite data"""
        self.state.sprite = Sprite(**data)
        self.state.active_layer = 0
        self.state.history = []
        self.state.history_index = -1