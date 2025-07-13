"""Lighting system models"""

from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import math

from ..sprites.models import Color
from ..particles.models import Vector2D


class LightType(str, Enum):
    """Light source types"""
    
    POINT = "point"
    DIRECTIONAL = "directional"
    SPOT = "spot"
    AMBIENT = "ambient"


class LightSource(BaseModel):
    """Light source definition"""
    
    name: str
    type: LightType
    position: Vector2D
    color: Color = Field(default_factory=lambda: Color(r=255, g=255, b=255))
    intensity: float = Field(ge=0.0, le=10.0, default=1.0)
    enabled: bool = True
    
    # Point/spot light properties
    radius: float = Field(gt=0.0, default=10.0)
    falloff: float = Field(ge=0.0, le=2.0, default=1.0)  # 0=constant, 1=linear, 2=quadratic
    
    # Directional/spot light properties
    direction: Vector2D = Field(default_factory=lambda: Vector2D(x=0, y=1))
    
    # Spot light properties
    cone_angle: float = Field(ge=0.0, le=180.0, default=45.0)  # Degrees
    cone_softness: float = Field(ge=0.0, le=1.0, default=0.1)
    
    # Shadow properties
    cast_shadows: bool = True
    shadow_softness: float = Field(ge=0.0, le=1.0, default=0.2)
    
    def get_intensity_at(self, point: Vector2D) -> float:
        """Calculate light intensity at a point"""
        if not self.enabled:
            return 0.0
        
        if self.type == LightType.AMBIENT:
            return self.intensity
        
        elif self.type == LightType.POINT:
            distance = point.subtract(self.position).magnitude()
            if distance > self.radius:
                return 0.0
            
            # Apply falloff
            if self.falloff == 0:
                return self.intensity
            elif self.falloff == 1:
                return self.intensity * (1.0 - distance / self.radius)
            else:
                return self.intensity * (1.0 - (distance / self.radius) ** 2)
        
        elif self.type == LightType.DIRECTIONAL:
            return self.intensity
        
        elif self.type == LightType.SPOT:
            # Check if point is within radius
            to_point = point.subtract(self.position)
            distance = to_point.magnitude()
            if distance > self.radius:
                return 0.0
            
            # Check if point is within cone
            if distance > 0:
                to_point_norm = to_point.normalize()
                direction_norm = self.direction.normalize()
                
                dot = to_point_norm.dot(direction_norm)
                angle = math.degrees(math.acos(max(-1, min(1, dot))))
                
                if angle > self.cone_angle / 2:
                    return 0.0
                
                # Apply cone softness
                cone_factor = 1.0
                if self.cone_softness > 0:
                    soft_angle = self.cone_angle / 2 * (1 - self.cone_softness)
                    if angle > soft_angle:
                        cone_factor = 1.0 - (angle - soft_angle) / (self.cone_angle / 2 - soft_angle)
                
                # Apply distance falloff
                distance_factor = 1.0
                if self.falloff == 1:
                    distance_factor = 1.0 - distance / self.radius
                elif self.falloff == 2:
                    distance_factor = 1.0 - (distance / self.radius) ** 2
                
                return self.intensity * cone_factor * distance_factor
        
        return 0.0
    
    def get_color_at(self, point: Vector2D) -> Color:
        """Get light color at a point"""
        intensity = self.get_intensity_at(point)
        return Color(
            r=int(self.color.r * intensity),
            g=int(self.color.g * intensity),
            b=int(self.color.b * intensity),
            a=self.color.a
        )


class Shadow(BaseModel):
    """Shadow information for a point"""
    
    occlusion: float = Field(ge=0.0, le=1.0, default=0.0)
    source: Optional[str] = None  # Light source name
    
    def apply_to_color(self, color: Color) -> Color:
        """Apply shadow to color"""
        factor = 1.0 - self.occlusion
        return Color(
            r=int(color.r * factor),
            g=int(color.g * factor),
            b=int(color.b * factor),
            a=color.a
        )


class LightMap(BaseModel):
    """Precomputed light map for performance"""
    
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    scale: int = Field(gt=0, default=1)  # Resolution scale (1 = full res)
    data: List[List[Color]] = Field(default_factory=list)
    shadow_data: List[List[float]] = Field(default_factory=list)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.data:
            # Initialize with black
            self.data = [[Color(r=0, g=0, b=0) for _ in range(self.width // self.scale)] 
                        for _ in range(self.height // self.scale)]
            self.shadow_data = [[0.0 for _ in range(self.width // self.scale)] 
                               for _ in range(self.height // self.scale)]
    
    def get_light_at(self, x: int, y: int) -> Color:
        """Get interpolated light color at position"""
        # Convert to light map coordinates
        lx = x // self.scale
        ly = y // self.scale
        
        if 0 <= lx < len(self.data[0]) and 0 <= ly < len(self.data):
            return self.data[ly][lx]
        
        return Color(r=0, g=0, b=0)
    
    def get_shadow_at(self, x: int, y: int) -> float:
        """Get shadow occlusion at position"""
        lx = x // self.scale
        ly = y // self.scale
        
        if 0 <= lx < len(self.shadow_data[0]) and 0 <= ly < len(self.shadow_data):
            return self.shadow_data[ly][lx]
        
        return 0.0
    
    def set_light_at(self, x: int, y: int, color: Color) -> None:
        """Set light color at position"""
        lx = x // self.scale
        ly = y // self.scale
        
        if 0 <= lx < len(self.data[0]) and 0 <= ly < len(self.data):
            self.data[ly][lx] = color
    
    def set_shadow_at(self, x: int, y: int, occlusion: float) -> None:
        """Set shadow occlusion at position"""
        lx = x // self.scale
        ly = y // self.scale
        
        if 0 <= lx < len(self.shadow_data[0]) and 0 <= ly < len(self.shadow_data):
            self.shadow_data[ly][lx] = occlusion
    
    def clear(self) -> None:
        """Clear light map"""
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                self.data[y][x] = Color(r=0, g=0, b=0)
                self.shadow_data[y][x] = 0.0


class TimeOfDay(BaseModel):
    """Time of day settings for day/night cycle"""
    
    hour: float = Field(ge=0.0, lt=24.0, default=12.0)
    
    # Light colors at different times
    dawn_color: Color = Field(default_factory=lambda: Color(r=255, g=200, b=150))
    noon_color: Color = Field(default_factory=lambda: Color(r=255, g=255, b=255))
    dusk_color: Color = Field(default_factory=lambda: Color(r=255, g=150, b=100))
    night_color: Color = Field(default_factory=lambda: Color(r=50, g=50, b=100))
    
    # Ambient light levels
    dawn_ambient: float = Field(ge=0.0, le=1.0, default=0.3)
    noon_ambient: float = Field(ge=0.0, le=1.0, default=0.7)
    dusk_ambient: float = Field(ge=0.0, le=1.0, default=0.3)
    night_ambient: float = Field(ge=0.0, le=1.0, default=0.1)
    
    # Sun angle
    sunrise_hour: float = Field(default=6.0)
    sunset_hour: float = Field(default=18.0)
    
    def get_sun_angle(self) -> float:
        """Get sun angle in degrees (0 = horizon, 90 = zenith)"""
        if self.hour < self.sunrise_hour or self.hour > self.sunset_hour:
            return -30.0  # Below horizon
        
        day_progress = (self.hour - self.sunrise_hour) / (self.sunset_hour - self.sunrise_hour)
        return math.sin(day_progress * math.pi) * 90.0
    
    def get_ambient_light(self) -> Tuple[Color, float]:
        """Get ambient light color and intensity for current time"""
        if self.hour < 6:  # Night to dawn
            t = self.hour / 6
            color = self._interpolate_color(self.night_color, self.dawn_color, t)
            intensity = self.night_ambient + (self.dawn_ambient - self.night_ambient) * t
        
        elif self.hour < 12:  # Dawn to noon
            t = (self.hour - 6) / 6
            color = self._interpolate_color(self.dawn_color, self.noon_color, t)
            intensity = self.dawn_ambient + (self.noon_ambient - self.dawn_ambient) * t
        
        elif self.hour < 18:  # Noon to dusk
            t = (self.hour - 12) / 6
            color = self._interpolate_color(self.noon_color, self.dusk_color, t)
            intensity = self.noon_ambient + (self.dusk_ambient - self.noon_ambient) * t
        
        else:  # Dusk to night
            t = (self.hour - 18) / 6
            color = self._interpolate_color(self.dusk_color, self.night_color, t)
            intensity = self.dusk_ambient + (self.night_ambient - self.dusk_ambient) * t
        
        return color, intensity
    
    def _interpolate_color(self, c1: Color, c2: Color, t: float) -> Color:
        """Interpolate between two colors"""
        return Color(
            r=int(c1.r + (c2.r - c1.r) * t),
            g=int(c1.g + (c2.g - c1.g) * t),
            b=int(c1.b + (c2.b - c1.b) * t),
            a=c1.a + (c2.a - c1.a) * t
        )
    
    def advance_time(self, hours: float) -> None:
        """Advance time by hours"""
        self.hour = (self.hour + hours) % 24.0