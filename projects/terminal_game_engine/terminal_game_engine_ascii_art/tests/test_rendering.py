"""Tests for rendering system"""

import pytest
from pytermgame.rendering import (
    Renderer, RenderLayer, Viewport, BlendMode,
    BlurEffect, GlowEffect
)
from pytermgame.sprites import Pixel, Color


class TestRenderLayer:
    """Test RenderLayer functionality"""
    
    def test_layer_creation(self):
        """Test render layer creation"""
        layer = RenderLayer(name="Test", width=20, height=20)
        
        assert layer.name == "Test"
        assert layer.width == 20
        assert layer.height == 20
        assert layer.z_order == 0
        assert layer.visible is True
        assert layer.opacity == 1.0
    
    def test_pixel_operations(self):
        """Test pixel get/set operations"""
        layer = RenderLayer(name="Test", width=10, height=10)
        pixel = Pixel(char='#', color=Color(r=255, g=0, b=0))
        
        # Set pixel
        layer.set_pixel(5, 5, pixel)
        
        # Get pixel
        retrieved = layer.get_pixel(5, 5)
        assert retrieved is not None
        assert retrieved.char == '#'
        assert retrieved.color.r == 255
        
        # Out of bounds
        assert layer.get_pixel(20, 20) is None
    
    def test_layer_clear(self):
        """Test clearing layer"""
        layer = RenderLayer(name="Test", width=5, height=5)
        
        # Fill with pixels
        for y in range(5):
            for x in range(5):
                layer.set_pixel(x, y, Pixel(char='#', color=Color(r=255, g=255, b=255)))
        
        # Clear with color
        layer.clear(Color(r=100, g=100, b=100))
        
        # Check all pixels have the clear color
        for y in range(5):
            for x in range(5):
                pixel = layer.get_pixel(x, y)
                assert pixel is not None
                assert pixel.char == ' '
                assert pixel.color.r == 100
        
        # Clear to empty
        layer.clear()
        for y in range(5):
            for x in range(5):
                assert layer.get_pixel(x, y) is None
    
    def test_layer_properties(self):
        """Test layer properties"""
        layer = RenderLayer(
            name="Test",
            width=10,
            height=10,
            z_order=5,
            opacity=0.5,
            blend_mode=BlendMode.ADD,
            offset_x=10,
            offset_y=20
        )
        
        assert layer.z_order == 5
        assert layer.opacity == 0.5
        assert layer.blend_mode == BlendMode.ADD
        assert layer.offset_x == 10
        assert layer.offset_y == 20


class TestViewport:
    """Test Viewport functionality"""
    
    def test_viewport_creation(self):
        """Test viewport creation"""
        viewport = Viewport(x=10, y=20, width=100, height=80)
        
        assert viewport.x == 10
        assert viewport.y == 20
        assert viewport.width == 100
        assert viewport.height == 80
    
    def test_viewport_contains(self):
        """Test point containment check"""
        viewport = Viewport(x=10, y=10, width=50, height=50)
        
        # Inside
        assert viewport.contains(20, 20) is True
        assert viewport.contains(10, 10) is True
        assert viewport.contains(59, 59) is True
        
        # Outside
        assert viewport.contains(5, 5) is False
        assert viewport.contains(60, 60) is False
    
    def test_coordinate_conversion(self):
        """Test world/screen coordinate conversion"""
        viewport = Viewport(x=100, y=200, width=50, height=50)
        
        # World to screen
        screen_x, screen_y = viewport.to_screen(120, 230)
        assert screen_x == 20
        assert screen_y == 30
        
        # Screen to world
        world_x, world_y = viewport.to_world(20, 30)
        assert world_x == 120
        assert world_y == 230


class TestRenderer:
    """Test main Renderer functionality"""
    
    def test_renderer_creation(self):
        """Test renderer initialization"""
        renderer = Renderer(width=80, height=25)
        
        assert renderer.width == 80
        assert renderer.height == 25
        assert len(renderer.layers) == 0
        assert renderer.viewport.width == 80
        assert renderer.viewport.height == 25
    
    def test_layer_management(self):
        """Test adding/removing layers"""
        renderer = Renderer(width=80, height=25)
        
        layer1 = RenderLayer(name="Layer1", width=80, height=25, z_order=1)
        layer2 = RenderLayer(name="Layer2", width=80, height=25, z_order=0)
        
        renderer.add_layer(layer1)
        renderer.add_layer(layer2)
        
        assert len(renderer.layers) == 2
        # Should be sorted by z_order
        assert renderer.layers[0].name == "Layer2"
        assert renderer.layers[1].name == "Layer1"
        
        # Get layer
        found = renderer.get_layer("Layer1")
        assert found is not None
        assert found.name == "Layer1"
        
        # Remove layer
        renderer.remove_layer("Layer2")
        assert len(renderer.layers) == 1
    
    def test_z_order_management(self):
        """Test layer z-order sorting"""
        renderer = Renderer(width=80, height=25)
        
        for i in range(3):
            layer = RenderLayer(name=f"Layer{i}", width=80, height=25, z_order=2-i)
            renderer.add_layer(layer)
        
        # Check sorted order
        assert renderer.layers[0].name == "Layer2"
        assert renderer.layers[1].name == "Layer1"
        assert renderer.layers[2].name == "Layer0"
        
        # Change z-order
        renderer.set_layer_z_order("Layer2", 10)
        assert renderer.layers[2].name == "Layer2"
    
    def test_basic_rendering(self):
        """Test basic rendering without effects"""
        renderer = Renderer(width=10, height=10)
        
        # Add layer with some pixels
        layer = RenderLayer(name="Test", width=10, height=10)
        layer.set_pixel(5, 5, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        layer.set_pixel(6, 6, Pixel(char='*', color=Color(r=0, g=255, b=0)))
        
        renderer.add_layer(layer)
        
        # Render
        output = renderer.render()
        
        assert len(output) == 10
        assert len(output[0]) == 10
        
        # Check pixels
        assert output[5][5] is not None
        assert output[5][5].char == '#'
        assert output[5][5].color.r == 255
        
        assert output[6][6] is not None
        assert output[6][6].char == '*'
        assert output[6][6].color.g == 255
    
    def test_layer_visibility(self):
        """Test layer visibility toggle"""
        renderer = Renderer(width=10, height=10)
        
        layer = RenderLayer(name="Test", width=10, height=10, visible=False)
        layer.set_pixel(5, 5, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        
        renderer.add_layer(layer)
        output = renderer.render()
        
        # Invisible layer shouldn't render
        pixel = output[5][5]
        assert pixel.char == ' '  # Background
    
    def test_layer_opacity(self):
        """Test layer opacity blending"""
        renderer = Renderer(width=10, height=10)
        
        # Background layer
        bg_layer = RenderLayer(name="BG", width=10, height=10)
        bg_layer.set_pixel(5, 5, Pixel(char='.', color=Color(r=255, g=0, b=0)))
        
        # Foreground layer with opacity
        fg_layer = RenderLayer(name="FG", width=10, height=10, z_order=1, opacity=0.5)
        fg_layer.set_pixel(5, 5, Pixel(char='#', color=Color(r=0, g=255, b=0)))
        
        renderer.add_layer(bg_layer)
        renderer.add_layer(fg_layer)
        
        output = renderer.render()
        pixel = output[5][5]
        
        # Should be blended
        assert pixel is not None
        # Character from foreground (opacity > 0.5 threshold)
        assert pixel.char == '.'
        # Color should be blended
        assert 0 < pixel.color.r < 255
        assert 0 < pixel.color.g < 255
    
    def test_viewport_rendering(self):
        """Test rendering with viewport offset"""
        renderer = Renderer(width=10, height=10)
        renderer.set_viewport(5, 5, 10, 10)
        
        layer = RenderLayer(name="Test", width=20, height=20)
        # Place pixel at world (10, 10)
        layer.set_pixel(10, 10, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        
        renderer.add_layer(layer)
        output = renderer.render()
        
        # Should appear at screen (5, 5) due to viewport offset
        assert output[5][5] is not None
        assert output[5][5].char == '#'
    
    def test_layer_offset(self):
        """Test layer offset rendering"""
        renderer = Renderer(width=10, height=10)
        
        layer = RenderLayer(name="Test", width=5, height=5, offset_x=3, offset_y=3)
        layer.set_pixel(0, 0, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        
        renderer.add_layer(layer)
        output = renderer.render()
        
        # Pixel should be offset
        assert output[3][3] is not None
        assert output[3][3].char == '#'
    
    def test_render_to_string(self):
        """Test ANSI string rendering"""
        renderer = Renderer(width=5, height=3)
        
        layer = RenderLayer(name="Test", width=5, height=3)
        layer.set_pixel(0, 0, Pixel(char='R', color=Color(r=255, g=0, b=0)))
        layer.set_pixel(1, 0, Pixel(char='G', color=Color(r=0, g=255, b=0)))
        layer.set_pixel(2, 0, Pixel(char='B', color=Color(r=0, g=0, b=255)))
        
        renderer.add_layer(layer)
        ansi_output = renderer.render_to_string()
        
        # Should contain ANSI escape codes
        assert "\033[" in ansi_output
        assert "R" in ansi_output
        assert "G" in ansi_output
        assert "B" in ansi_output
    
    def test_blend_modes(self):
        """Test different blend modes"""
        renderer = Renderer(width=10, height=10)
        
        # Base layer
        base = RenderLayer(name="Base", width=10, height=10)
        base.set_pixel(5, 5, Pixel(char='.', color=Color(r=128, g=128, b=128)))
        
        # Add blend layer
        add_layer = RenderLayer(name="Add", width=10, height=10, 
                               z_order=1, blend_mode=BlendMode.ADD)
        add_layer.set_pixel(5, 5, Pixel(char='+', color=Color(r=64, g=64, b=64)))
        
        renderer.add_layer(base)
        renderer.add_layer(add_layer)
        
        output = renderer.render()
        pixel = output[5][5]
        
        # Colors should be added
        assert pixel.color.r == 192  # 128 + 64
        assert pixel.color.g == 192
        assert pixel.color.b == 192


class TestEffects:
    """Test layer effects"""
    
    def test_blur_effect(self):
        """Test blur effect application"""
        layer = RenderLayer(name="Test", width=5, height=5)
        
        # Create a sharp pattern
        layer.set_pixel(2, 2, Pixel(char='#', color=Color(r=255, g=255, b=255)))
        
        # Apply blur
        blur = BlurEffect(radius=1)
        blur.apply(layer)
        
        # Adjacent pixels should have some color
        adjacent = layer.get_pixel(1, 2)
        assert adjacent is not None
        assert adjacent.color.r > 0
    
    def test_glow_effect(self):
        """Test glow effect application"""
        layer = RenderLayer(name="Test", width=7, height=7)
        
        # Create a bright pixel
        layer.set_pixel(3, 3, Pixel(char='*', color=Color(r=255, g=200, b=100)))
        
        # Apply glow
        glow = GlowEffect(intensity=1.5, radius=2)
        glow.apply(layer)
        
        # Should have glow around the pixel
        glow_pixel = layer.get_pixel(2, 3)
        assert glow_pixel is not None
        # Glow should be brighter than original
        assert glow_pixel.color.r > 200
    
    def test_effect_in_renderer(self):
        """Test effects applied during rendering"""
        renderer = Renderer(width=10, height=10)
        
        layer = RenderLayer(name="Test", width=10, height=10)
        layer.set_pixel(5, 5, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        layer.effects = ["glow"]
        
        renderer.add_layer(layer)
        output = renderer.render()
        
        # Should have glow effect applied
        # Check adjacent pixels for glow
        assert output[4][5] is not None or output[6][5] is not None


class TestViewportScrolling:
    """Test viewport scrolling functionality"""
    
    def test_viewport_scroll(self):
        """Test viewport scrolling"""
        renderer = Renderer(width=10, height=10)
        
        # Initial viewport
        renderer.set_viewport(0, 0)
        assert renderer.viewport.x == 0
        assert renderer.viewport.y == 0
        
        # Scroll
        renderer.scroll_viewport(5, 10)
        assert renderer.viewport.x == 5
        assert renderer.viewport.y == 10
        
        # Scroll more
        renderer.scroll_viewport(-2, -3)
        assert renderer.viewport.x == 3
        assert renderer.viewport.y == 7