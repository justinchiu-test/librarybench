# PyTermGame - ASCII Art Game Engine

A terminal-based game engine focused on creating visually stunning games using advanced ASCII art rendering techniques. PyTermGame pushes the boundaries of terminal graphics with sophisticated visual effects and animations.

## Overview

PyTermGame provides a comprehensive set of tools for creating rich ASCII art games in the terminal, including:

- **Advanced Sprite Editor** - Create and edit multi-layered ASCII sprites with drawing tools
- **Animation System** - Frame-based animation with onion skinning support
- **Layered Rendering** - Composite multiple layers with transparency and blend modes
- **Particle Effects** - Dynamic ASCII particle systems with physics
- **Dynamic Lighting** - Real-time lighting with shadows and ambient occlusion
- **Sprite Compression** - Efficient storage for large ASCII artworks

## Installation

```bash
# Install with pip
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Creating a Sprite

```python
from pytermgame.sprites import SpriteEditor, Color

# Create a new sprite editor
editor = SpriteEditor()

# Set drawing color
editor.set_primary_color(Color(r=255, g=0, b=0))

# Draw with various tools
editor.set_tool("rectangle")
editor.draw_with_tool(5, 5, 15, 15)

editor.set_tool("circle")
editor.draw_with_tool(10, 10, 15, 15)

# Add layers
editor.add_layer("Foreground")
editor.set_active_layer(1)

# Export sprite
sprite_data = editor.export_sprite()
```

### Creating Animations

```python
from pytermgame.animation import Animator

# Create animator
animator = Animator()
animation = animator.create_animation("Walk", width=32, height=32)

# Add frames
for i in range(8):
    if i > 0:
        animator.add_frame()
    
    # Edit current frame
    editor = animator.sprite_editor
    if editor:
        editor.draw_pixel(10 + i, 10, '*')

# Enable onion skinning
animator.state.onion_skin.enabled = True

# Play preview
animator.play_preview()
```

### Rendering Scenes

```python
from pytermgame.rendering import Renderer, RenderLayer
from pytermgame.sprites import Pixel, Color

# Create renderer
renderer = Renderer(width=80, height=25)

# Create layers
background = RenderLayer(name="bg", width=80, height=25, z_order=0)
sprites = RenderLayer(name="sprites", width=80, height=25, z_order=10)

# Add content to layers
for x in range(80):
    background.set_pixel(x, 20, Pixel(char='-', color=Color(r=100, g=100, b=100)))

# Add layers to renderer
renderer.add_layer(background)
renderer.add_layer(sprites)

# Render to ANSI string
output = renderer.render_to_string()
print(output)
```

### Particle Effects

```python
from pytermgame.particles import ParticleSystem, Vector2D

# Create particle system
particles = ParticleSystem(width=100, height=50)

# Create explosion effect
particles.create_explosion(Vector2D(x=50.0, y=25.0))

# Create fire effect
particles.create_fire(Vector2D(x=30.0, y=40.0))

# Update particles
particles.update(0.016)  # 60 FPS

# Render particles
particle_layer = particles.render_to_layer()
```

### Dynamic Lighting

```python
from pytermgame.lighting import LightingProcessor, LightSource, LightType
from pytermgame.particles import Vector2D

# Create lighting processor
lighting = LightingProcessor(width=100, height=50)

# Add light sources
torch = lighting.create_torch_light(Vector2D(x=20.0, y=25.0))

# Set time of day
lighting.set_time_of_day(20.0)  # 8 PM

# Calculate lighting
lighting.calculate_lighting()

# Apply to render layer
lit_layer = lighting.apply_lighting_to_layer(sprite_layer)
```

### Sprite Compression

```python
from pytermgame.compression import SpriteCompressor

# Create compressor
compressor = SpriteCompressor()

# Compress sprite
compressed = compressor.compress(sprite)
print(f"Compression ratio: {compressed.compression_stats.compression_ratio:.2f}")

# Save to file
compressor.compress_to_file(sprite, "sprite.ptz")

# Load from file
loaded_sprite = compressor.decompress_from_file("sprite.ptz")
```

## Features

### Sprite Editor
- Multiple drawing tools (pencil, brush, line, rectangle, circle, fill)
- Layer support with opacity and blend modes
- Color palette management
- Undo/redo functionality
- Import/export capabilities

### Animation System
- Frame-based animation sequencing
- Onion skinning for smooth animation creation
- Variable frame durations
- Animation sets for organizing multiple animations
- Real-time preview playback

### Rendering Engine
- Efficient layer compositing
- Multiple blend modes (normal, add, multiply, screen)
- Viewport scrolling and clipping
- Effects system (blur, glow)
- ANSI color output

### Particle System
- Physics-based particle movement
- Multiple emitter shapes (point, line, circle, rectangle)
- Predefined effects (explosion, fire, sparkle)
- Particle pooling for performance
- Collision detection

### Lighting System
- Multiple light types (point, directional, spot, ambient)
- Real-time shadow casting
- Ambient occlusion approximation
- Day/night cycle simulation
- Light color and intensity control

### Compression
- Pattern recognition for repeated elements
- Run-length encoding
- Color palette optimization
- Lossless compression
- File I/O support

## Performance

PyTermGame is designed to meet the following performance targets:

- Render 30+ layers at 30 FPS
- Animate 100+ sprites simultaneously
- Support 500+ particles
- Compress sprites by 70%+
- Maintain smooth scrolling

## Testing

Run the test suite with:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pytermgame

# Run specific test file
pytest tests/test_sprites.py

# Generate JSON report (required)
pytest --json-report --json-report-file=pytest_results.json
```

## Architecture

PyTermGame is organized into modular components:

- `sprites/` - Core sprite data structures and editor
- `animation/` - Animation sequencing and frame management
- `rendering/` - Layer compositing and output generation
- `particles/` - Particle physics and effects
- `lighting/` - Dynamic lighting calculations
- `compression/` - Sprite data compression

Each module is designed to work independently while integrating seamlessly with the others.

## Examples

See the `examples/` directory for more detailed usage examples:

- `sprite_editor_demo.py` - Interactive sprite creation
- `animation_demo.py` - Creating smooth animations
- `particle_demo.py` - Particle effects showcase
- `lighting_demo.py` - Dynamic lighting examples
- `game_scene_demo.py` - Complete game scene

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. Code follows PEP 8 style guidelines
3. Type hints are included
4. New features include tests
5. Documentation is updated

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with ❤️ for ASCII art enthusiasts and terminal game developers.