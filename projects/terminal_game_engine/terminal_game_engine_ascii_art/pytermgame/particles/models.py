"""Particle system models and physics"""

from typing import List, Optional, Tuple, Dict, Any, Callable
from enum import Enum
from pydantic import BaseModel, Field
import random
import math
import time

from ..sprites.models import Color


class Vector2D(BaseModel):
    """2D vector for positions and velocities"""
    
    x: float = 0.0
    y: float = 0.0
    
    def add(self, other: 'Vector2D') -> 'Vector2D':
        """Add vectors"""
        return Vector2D(x=self.x + other.x, y=self.y + other.y)
    
    def subtract(self, other: 'Vector2D') -> 'Vector2D':
        """Subtract vectors"""
        return Vector2D(x=self.x - other.x, y=self.y - other.y)
    
    def multiply(self, scalar: float) -> 'Vector2D':
        """Multiply by scalar"""
        return Vector2D(x=self.x * scalar, y=self.y * scalar)
    
    def magnitude(self) -> float:
        """Get vector magnitude"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self) -> 'Vector2D':
        """Get normalized vector"""
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(x=self.x / mag, y=self.y / mag)
        return Vector2D(x=0, y=0)
    
    def dot(self, other: 'Vector2D') -> float:
        """Dot product"""
        return self.x * other.x + self.y * other.y


class Particle(BaseModel):
    """Individual particle"""
    
    position: Vector2D
    velocity: Vector2D = Field(default_factory=lambda: Vector2D())
    acceleration: Vector2D = Field(default_factory=lambda: Vector2D())
    char: str = Field(default='*', max_length=1)
    color: Color = Field(default_factory=lambda: Color(r=255, g=255, b=255))
    life: float = Field(ge=0.0, default=1.0)  # Remaining life (0-1)
    lifetime: float = Field(gt=0.0, default=1.0)  # Total lifetime in seconds
    size: float = Field(ge=0.0, default=1.0)
    rotation: float = 0.0  # Rotation in radians
    angular_velocity: float = 0.0  # Rotation speed
    created_at: float = Field(default_factory=time.time)
    
    def update(self, dt: float) -> None:
        """Update particle physics"""
        # Update velocity
        self.velocity = self.velocity.add(self.acceleration.multiply(dt))
        
        # Update position
        self.position = self.position.add(self.velocity.multiply(dt))
        
        # Update rotation
        self.rotation += self.angular_velocity * dt
        
        # Update life
        age = time.time() - self.created_at
        self.life = max(0.0, 1.0 - age / self.lifetime)
    
    def is_alive(self) -> bool:
        """Check if particle is still alive"""
        return self.life > 0.0
    
    def get_char_for_angle(self) -> str:
        """Get character based on velocity angle"""
        if self.velocity.magnitude() < 0.1:
            return self.char
        
        # Calculate angle from velocity
        angle = math.atan2(self.velocity.y, self.velocity.x)
        angle_deg = math.degrees(angle) % 360
        
        # Select character based on angle
        if 337.5 <= angle_deg or angle_deg < 22.5:
            return '-'
        elif 22.5 <= angle_deg < 67.5:
            return '\\'
        elif 67.5 <= angle_deg < 112.5:
            return '|'
        elif 112.5 <= angle_deg < 157.5:
            return '/'
        elif 157.5 <= angle_deg < 202.5:
            return '-'
        elif 202.5 <= angle_deg < 247.5:
            return '\\'
        elif 247.5 <= angle_deg < 292.5:
            return '|'
        else:
            return '/'


class EmitterShape(str, Enum):
    """Emitter shape types"""
    
    POINT = "point"
    LINE = "line"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    CONE = "cone"


class ParticleEmitter(BaseModel):
    """Particle emitter configuration"""
    
    name: str
    position: Vector2D
    shape: str = "point"
    shape_params: Dict[str, float] = Field(default_factory=dict)
    
    # Emission properties
    emission_rate: float = Field(gt=0, default=10.0)  # Particles per second
    burst_count: int = Field(ge=0, default=0)  # Particles in burst
    max_particles: int = Field(gt=0, default=500)
    enabled: bool = True
    
    # Particle properties
    particle_chars: List[str] = Field(default_factory=lambda: ['*', '.', 'o'])
    particle_lifetime: Tuple[float, float] = (0.5, 2.0)  # Min, max seconds
    particle_speed: Tuple[float, float] = (10.0, 50.0)  # Min, max
    particle_direction: Tuple[float, float] = (0.0, 360.0)  # Min, max degrees
    particle_size: Tuple[float, float] = (0.8, 1.2)
    particle_rotation_speed: Tuple[float, float] = (0.0, 0.0)
    
    # Colors
    start_color: Color = Field(default_factory=lambda: Color(r=255, g=255, b=255))
    end_color: Color = Field(default_factory=lambda: Color(r=128, g=128, b=128))
    color_variance: float = Field(ge=0.0, le=1.0, default=0.1)
    
    # Forces
    gravity: Vector2D = Field(default_factory=lambda: Vector2D(x=0, y=98.1))
    wind: Vector2D = Field(default_factory=lambda: Vector2D())
    
    # Internal state
    last_emission: float = Field(default=0.0)
    emission_accumulator: float = Field(default=0.0)
    
    def get_spawn_position(self) -> Vector2D:
        """Get random spawn position based on shape"""
        if self.shape == "point":
            return Vector2D(x=self.position.x, y=self.position.y)
        
        elif self.shape == "line":
            length = self.shape_params.get("length", 10.0)
            angle = self.shape_params.get("angle", 0.0)
            t = random.random()
            offset_x = math.cos(math.radians(angle)) * length * (t - 0.5)
            offset_y = math.sin(math.radians(angle)) * length * (t - 0.5)
            return Vector2D(
                x=self.position.x + offset_x,
                y=self.position.y + offset_y
            )
        
        elif self.shape == "circle":
            radius = self.shape_params.get("radius", 5.0)
            angle = random.random() * 2 * math.pi
            r = math.sqrt(random.random()) * radius
            return Vector2D(
                x=self.position.x + math.cos(angle) * r,
                y=self.position.y + math.sin(angle) * r
            )
        
        elif self.shape == "rectangle":
            width = self.shape_params.get("width", 10.0)
            height = self.shape_params.get("height", 10.0)
            return Vector2D(
                x=self.position.x + (random.random() - 0.5) * width,
                y=self.position.y + (random.random() - 0.5) * height
            )
        
        else:
            return Vector2D(x=self.position.x, y=self.position.y)
    
    def create_particle(self) -> Particle:
        """Create a new particle"""
        # Position
        pos = self.get_spawn_position()
        
        # Velocity
        angle = random.uniform(
            math.radians(self.particle_direction[0]),
            math.radians(self.particle_direction[1])
        )
        speed = random.uniform(self.particle_speed[0], self.particle_speed[1])
        velocity = Vector2D(
            x=math.cos(angle) * speed,
            y=math.sin(angle) * speed
        )
        
        # Character
        char = random.choice(self.particle_chars)
        
        # Color with variance
        def vary_color(base: int) -> int:
            variance = int(255 * self.color_variance)
            return max(0, min(255, base + random.randint(-variance, variance)))
        
        color = Color(
            r=vary_color(self.start_color.r),
            g=vary_color(self.start_color.g),
            b=vary_color(self.start_color.b),
            a=self.start_color.a
        )
        
        # Properties
        lifetime = random.uniform(self.particle_lifetime[0], self.particle_lifetime[1])
        size = random.uniform(self.particle_size[0], self.particle_size[1])
        angular_velocity = random.uniform(
            self.particle_rotation_speed[0],
            self.particle_rotation_speed[1]
        )
        
        # Acceleration (gravity + wind)
        acceleration = self.gravity.add(self.wind)
        
        return Particle(
            position=pos,
            velocity=velocity,
            acceleration=acceleration,
            char=char,
            color=color,
            lifetime=lifetime,
            size=size,
            angular_velocity=angular_velocity
        )
    
    def update(self, dt: float) -> List[Particle]:
        """Update emitter and return new particles to spawn"""
        if not self.enabled:
            return []
        
        new_particles = []
        
        # Handle burst emission
        if self.burst_count > 0:
            for _ in range(self.burst_count):
                new_particles.append(self.create_particle())
            self.burst_count = 0
        
        # Handle continuous emission
        self.emission_accumulator += self.emission_rate * dt
        
        while self.emission_accumulator >= 1.0:
            new_particles.append(self.create_particle())
            self.emission_accumulator -= 1.0
        
        return new_particles
    
    def burst(self, count: Optional[int] = None) -> None:
        """Trigger burst emission"""
        self.burst_count = count or 10


class ParticleEffect(BaseModel):
    """Predefined particle effect"""
    
    name: str
    emitters: List[ParticleEmitter]
    duration: Optional[float] = None  # None for infinite
    
    @classmethod
    def create_explosion(cls, position: Vector2D) -> 'ParticleEffect':
        """Create explosion effect"""
        emitter = ParticleEmitter(
            name="explosion",
            position=position,
            shape="circle",
            shape_params={"radius": 2.0},
            emission_rate=0,
            burst_count=50,
            particle_chars=['*', 'x', '+', '.'],
            particle_lifetime=(0.3, 0.8),
            particle_speed=(50.0, 150.0),
            particle_direction=(0.0, 360.0),
            start_color=Color(r=255, g=200, b=100),
            end_color=Color(r=255, g=0, b=0),
            gravity=Vector2D(x=0, y=50)
        )
        
        return cls(name="explosion", emitters=[emitter], duration=1.0)
    
    @classmethod
    def create_fire(cls, position: Vector2D) -> 'ParticleEffect':
        """Create fire effect"""
        emitter = ParticleEmitter(
            name="fire",
            position=position,
            shape="line",
            shape_params={"length": 5.0, "angle": 0.0},
            emission_rate=30,
            particle_chars=['^', '*', '.'],
            particle_lifetime=(0.5, 1.0),
            particle_speed=(10.0, 30.0),
            particle_direction=(260.0, 280.0),  # Mostly upward
            start_color=Color(r=255, g=200, b=0),
            end_color=Color(r=255, g=0, b=0),
            gravity=Vector2D(x=0, y=-50)  # Negative gravity for upward motion
        )
        
        return cls(name="fire", emitters=[emitter])
    
    @classmethod
    def create_sparkle(cls, position: Vector2D) -> 'ParticleEffect':
        """Create sparkle effect"""
        emitter = ParticleEmitter(
            name="sparkle",
            position=position,
            shape="point",
            emission_rate=5,
            particle_chars=['*', '+', '.'],
            particle_lifetime=(0.5, 1.5),
            particle_speed=(5.0, 15.0),
            particle_direction=(0.0, 360.0),
            start_color=Color(r=255, g=255, b=255),
            end_color=Color(r=128, g=128, b=255),
            gravity=Vector2D(x=0, y=10),
            color_variance=0.3
        )
        
        return cls(name="sparkle", emitters=[emitter])