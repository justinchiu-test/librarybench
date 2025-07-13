"""Integration tests for PyTermGame"""

import pytest
import time
from pytermgame.sprites import Sprite, SpriteEditor, Color, Pixel
from pytermgame.animation import Animator, Animation
from pytermgame.rendering import Renderer, RenderLayer, BlendMode
from pytermgame.particles import ParticleSystem, Vector2D
from pytermgame.lighting import LightingProcessor, LightSource, LightType
from pytermgame.compression import SpriteCompressor


class TestSpriteToAnimation:
    """Test sprite creation to animation workflow"""
    
    def test_create_animated_sprite(self):
        """Test creating and animating a sprite"""
        # Create sprite with editor
        editor = SpriteEditor()
        editor.sprite.name = "Character"
        
        # Draw first frame
        editor.set_tool("rectangle")
        editor.draw_with_tool(5, 5, 10, 10)
        
        # Create animator and animation
        animator = Animator()
        animation = animator.create_animation("Walk", width=32, height=32)
        
        # Add frames
        for i in range(3):
            if i > 0:
                animator.add_frame()
            
            # Modify sprite for each frame
            sprite_editor = animator.sprite_editor
            if sprite_editor:
                sprite_editor.draw_pixel(10 + i, 10, str(i))
        
        # Verify animation
        assert len(animation.frames) == 3
        assert animator.current_animation is not None
        
        # Test playback
        animator.play_preview()
        assert animator.state.preview_playing is True


class TestRenderingPipeline:
    """Test complete rendering pipeline"""
    
    def test_layered_scene_rendering(self):
        """Test rendering a complex scene with layers"""
        renderer = Renderer(width=50, height=25)
        
        # Background layer
        bg_layer = RenderLayer(name="background", width=50, height=25, z_order=0)
        for x in range(50):
            bg_layer.set_pixel(x, 12, Pixel(char='-', color=Color(r=50, g=50, b=50)))
        
        # Sprite layer
        sprite_layer = RenderLayer(name="sprite", width=50, height=25, z_order=10)
        # Draw a simple character
        for y in range(5, 10):
            for x in range(20, 25):
                sprite_layer.set_pixel(x, y, Pixel(char='#', color=Color(r=255, g=200, b=100)))
        
        # Particle layer
        particle_system = ParticleSystem(width=50, height=25)
        particle_system.spawn_burst(
            position=Vector2D(x=25.0, y=5.0),
            count=10,
            char='*'
        )
        particle_layer = particle_system.render_to_layer()
        particle_layer.z_order = 20
        
        # Add all layers
        renderer.add_layer(bg_layer)
        renderer.add_layer(sprite_layer)
        renderer.add_layer(particle_layer)
        
        # Render
        output = renderer.render()
        
        # Verify output
        assert len(output) == 25
        assert len(output[0]) == 50
        
        # Check layering worked
        ground_pixel = output[12][25]
        assert ground_pixel.char == '-'
        
        # Convert to string
        ansi_output = renderer.render_to_string()
        assert isinstance(ansi_output, str)
        assert len(ansi_output) > 0


class TestLightingIntegration:
    """Test lighting system integration"""
    
    def test_lit_scene(self):
        """Test scene with dynamic lighting"""
        # Create scene
        renderer = Renderer(width=40, height=20)
        lighting = LightingProcessor(width=40, height=20)
        
        # Create sprite layer
        sprite_layer = RenderLayer(name="sprites", width=40, height=20)
        
        # Add some objects
        for y in range(5, 15):
            for x in range(10, 30):
                if (x + y) % 3 == 0:
                    sprite_layer.set_pixel(x, y, 
                        Pixel(char='#', color=Color(r=200, g=200, b=200)))
        
        # Update occluders from sprite layer
        lighting.update_occluders(sprite_layer)
        
        # Add lights
        torch1 = lighting.create_torch_light(Vector2D(x=5.0, y=10.0))
        torch2 = lighting.create_torch_light(Vector2D(x=35.0, y=10.0))
        
        # Set time of day
        lighting.set_time_of_day(20.0)  # Evening
        
        # Calculate lighting
        lighting.calculate_lighting()
        
        # Apply lighting to sprite layer
        lit_layer = lighting.apply_lighting_to_layer(sprite_layer)
        
        # Add to renderer
        renderer.add_layer(lit_layer)
        
        # Render
        output = renderer.render()
        
        # Verify lighting affected the scene
        # Near torch should be brighter
        near_torch = output[10][6]
        far_from_torch = output[10][20]
        
        if near_torch and far_from_torch:
            # Rough check - exact values depend on lighting calculation
            assert near_torch.color.r >= far_from_torch.color.r


class TestAnimationWithEffects:
    """Test animation with particle effects"""
    
    def test_animated_particle_scene(self):
        """Test animation with triggered particle effects"""
        # Create animator
        animator = Animator()
        animation = animator.create_animation("Explosion", width=50, height=30)
        
        # Create particle system
        particle_system = ParticleSystem(width=50, height=30)
        
        # Create frames
        for i in range(5):
            if i > 0:
                animator.add_frame()
            
            # Add explosion effect on frame 2
            if i == 2:
                particle_system.create_explosion(Vector2D(x=25.0, y=15.0))
        
        # Simulate animation playback
        animator.play_preview()
        
        # Update particles
        particle_system.update(0.1)
        
        # Verify particles exist
        assert particle_system.get_particle_count() > 0
        
        # Render current frame with particles
        renderer = Renderer(width=50, height=30)
        
        # Get current animation frame
        if animator.current_frame:
            sprite_layer = RenderLayer(name="animation", width=50, height=30)
            composite = animator.current_frame.sprite.composite()
            
            for y in range(30):
                for x in range(50):
                    if composite[y][x]:
                        sprite_layer.set_pixel(x, y, composite[y][x])
            
            renderer.add_layer(sprite_layer)
        
        # Add particle layer
        particle_layer = particle_system.render_to_layer()
        renderer.add_layer(particle_layer)
        
        # Render composite
        output = renderer.render()
        assert len(output) == 30


class TestCompressionWorkflow:
    """Test sprite compression in workflow"""
    
    def test_compress_animated_sprite(self):
        """Test compressing an animated sprite"""
        # Create animated sprite
        animator = Animator()
        animation = animator.create_animation("Character", width=32, height=32)
        
        # Add multiple frames
        for i in range(10):
            if i > 0:
                animator.add_frame()
            
            editor = animator.sprite_editor
            if editor:
                # Draw different content in each frame
                editor.set_tool("circle")
                editor.draw_with_tool(16, 16, 16 + i, 16)
        
        # Compress each frame
        compressor = SpriteCompressor()
        compressed_frames = []
        
        for frame in animation.frames:
            compressed = compressor.compress(frame.sprite)
            compressed_frames.append(compressed)
            
            # Verify compression
            assert compressed.compression_stats.original_size > 0
            assert compressed.compression_stats.compressed_size > 0
        
        # Decompress and verify
        for i, compressed in enumerate(compressed_frames):
            decompressed = compressor.decompress(compressed)
            assert decompressed.width == 32
            assert decompressed.height == 32


class TestFullGameScene:
    """Test a complete game scene"""
    
    def test_complete_scene(self):
        """Test rendering a complete game scene with all features"""
        # Scene dimensions
        width, height = 80, 40
        
        # Initialize systems
        renderer = Renderer(width=width, height=height)
        lighting = LightingProcessor(width=width, height=height)
        particles = ParticleSystem(width=width, height=height)
        
        # Create background
        bg_layer = RenderLayer(name="background", width=width, height=height, z_order=0)
        bg_color = Color(r=20, g=20, b=40)
        for y in range(height):
            for x in range(width):
                bg_layer.set_pixel(x, y, Pixel(char=' ', color=bg_color))
        
        # Create terrain
        terrain_layer = RenderLayer(name="terrain", width=width, height=height, z_order=10)
        
        # Ground
        for x in range(width):
            for y in range(30, height):
                terrain_layer.set_pixel(x, y, Pixel(char='=', color=Color(r=100, g=80, b=60)))
        
        # Trees
        tree_positions = [(10, 25), (30, 27), (50, 26), (70, 25)]
        for tx, ty in tree_positions:
            # Trunk
            for y in range(ty, ty + 5):
                terrain_layer.set_pixel(tx, y, Pixel(char='|', color=Color(r=101, g=67, b=33)))
            # Leaves
            for dy in range(-2, 3):
                for dx in range(-3, 4):
                    if abs(dx) + abs(dy) <= 3:
                        terrain_layer.set_pixel(tx + dx, ty - 3 + dy, 
                            Pixel(char='*', color=Color(r=34, g=139, b=34)))
        
        # Update lighting occluders
        lighting.update_occluders(terrain_layer)
        
        # Add character sprite
        character_layer = RenderLayer(name="character", width=width, height=height, z_order=50)
        char_x, char_y = 40, 28
        
        # Simple character
        character_layer.set_pixel(char_x, char_y - 2, Pixel(char='o', color=Color(r=255, g=220, b=177)))
        character_layer.set_pixel(char_x, char_y - 1, Pixel(char='|', color=Color(r=100, g=100, b=200)))
        character_layer.set_pixel(char_x, char_y, Pixel(char='^', color=Color(r=100, g=100, b=200)))
        
        # Add lighting
        lighting.set_time_of_day(19.0)  # Dusk
        
        # Add torches
        for tx, _ in tree_positions:
            lighting.create_torch_light(Vector2D(x=float(tx), y=20.0))
        
        # Character has a lantern
        lantern = LightSource(
            name="lantern",
            type=LightType.POINT,
            position=Vector2D(x=float(char_x), y=float(char_y - 1)),
            color=Color(r=255, g=255, b=200),
            intensity=0.8,
            radius=15.0
        )
        lighting.add_light(lantern)
        
        # Calculate lighting
        lighting.calculate_lighting()
        
        # Apply lighting to layers
        lit_terrain = lighting.apply_lighting_to_layer(terrain_layer)
        lit_character = lighting.apply_lighting_to_layer(character_layer)
        
        # Add particle effects - fireflies
        for _ in range(3):
            x = 20 + (time.time() * 10) % 40
            y = 15 + (time.time() * 5) % 10
            particles.create_sparkle(Vector2D(x=x, y=y))
        
        particles.update(0.1)
        
        # Compose scene
        renderer.add_layer(bg_layer)
        renderer.add_layer(lit_terrain)
        renderer.add_layer(lit_character)
        renderer.add_layer(particles.render_to_layer())
        
        # Render final scene
        output = renderer.render()
        
        # Verify scene rendered
        assert len(output) == height
        assert len(output[0]) == width
        
        # Check some elements exist
        # Ground should be visible
        ground_pixel = output[35][40]
        assert ground_pixel is not None
        
        # Character should be visible
        char_pixel = output[char_y - 1][char_x]
        assert char_pixel is not None
        
        # Can render to string
        ansi_scene = renderer.render_to_string()
        assert len(ansi_scene) > 0
        assert '\033[' in ansi_scene  # Has ANSI codes


class TestPerformance:
    """Test performance requirements"""
    
    def test_rendering_performance(self):
        """Test rendering meets performance requirements"""
        renderer = Renderer(width=100, height=50)
        
        # Add 30 layers (performance requirement)
        for i in range(30):
            layer = RenderLayer(
                name=f"layer_{i}",
                width=100,
                height=50,
                z_order=i,
                opacity=0.8
            )
            
            # Add some content
            for _ in range(50):
                import random
                x = random.randint(0, 99)
                y = random.randint(0, 49)
                layer.set_pixel(x, y, Pixel(
                    char=random.choice(['#', '*', '.', '+', '-']),
                    color=Color(
                        r=random.randint(0, 255),
                        g=random.randint(0, 255),
                        b=random.randint(0, 255)
                    )
                ))
            
            renderer.add_layer(layer)
        
        # Time rendering
        start_time = time.time()
        frames_rendered = 0
        
        while time.time() - start_time < 1.0:
            renderer.render()
            frames_rendered += 1
        
        fps = frames_rendered
        
        # Should achieve at least 30 FPS
        assert fps >= 30
    
    def test_particle_performance(self):
        """Test particle system performance"""
        particles = ParticleSystem(width=100, height=100, max_particles=500)
        
        # Spawn 500 particles (performance requirement)
        for _ in range(50):
            particles.spawn_burst(
                position=Vector2D(x=50.0, y=50.0),
                count=10
            )
        
        # Time updates
        start_time = time.time()
        updates = 0
        
        while time.time() - start_time < 1.0:
            particles.update(0.016)  # ~60 FPS timing
            updates += 1
        
        # Should handle updates smoothly
        assert updates >= 60
        assert particles.get_particle_count() <= 500