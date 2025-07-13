"""Tests for animation system"""

import pytest
import time
from pytermgame.animation import (
    Frame, Animation, AnimationSet,
    Animator, OnionSkinSettings
)
from pytermgame.sprites import Sprite, Layer, Pixel, Color


class TestFrame:
    """Test Frame model"""
    
    def test_frame_creation(self):
        """Test frame creation"""
        sprite = Sprite(name="Test", width=10, height=10)
        frame = Frame(sprite=sprite, duration=0.1)
        
        assert frame.sprite == sprite
        assert frame.duration == 0.1
        assert frame.metadata == {}


class TestAnimation:
    """Test Animation functionality"""
    
    def test_animation_creation(self):
        """Test animation creation"""
        animation = Animation(name="Walk", fps=10.0)
        
        assert animation.name == "Walk"
        assert animation.fps == 10.0
        assert animation.loop is True
        assert len(animation.frames) == 0
    
    def test_frame_management(self):
        """Test adding/removing frames"""
        animation = Animation(name="Test")
        sprite1 = Sprite(name="Frame1", width=10, height=10)
        sprite2 = Sprite(name="Frame2", width=10, height=10)
        
        # Add frames
        frame1 = animation.add_frame(sprite1)
        frame2 = animation.add_frame(sprite2, duration=0.2)
        
        assert len(animation.frames) == 2
        assert frame1.duration == 0.1  # Default from fps
        assert frame2.duration == 0.2
        
        # Remove frame
        animation.remove_frame(0)
        assert len(animation.frames) == 1
        assert animation.frames[0].sprite.name == "Frame2"
    
    def test_frame_duplication(self):
        """Test frame duplication"""
        animation = Animation(name="Test")
        sprite = Sprite(name="Original", width=10, height=10)
        
        animation.add_frame(sprite)
        new_frame = animation.duplicate_frame(0)
        
        assert new_frame is not None
        assert len(animation.frames) == 2
        assert animation.frames[1].sprite.name == "Original"
        assert animation.frames[1].sprite != animation.frames[0].sprite
    
    def test_frame_movement(self):
        """Test moving frames"""
        animation = Animation(name="Test")
        
        for i in range(3):
            sprite = Sprite(name=f"Frame{i}", width=10, height=10)
            animation.add_frame(sprite)
        
        # Move first to last
        animation.move_frame(0, 2)
        
        assert animation.frames[0].sprite.name == "Frame1"
        assert animation.frames[1].sprite.name == "Frame2"
        assert animation.frames[2].sprite.name == "Frame0"
    
    def test_animation_playback(self):
        """Test animation play/pause/stop"""
        animation = Animation(name="Test")
        sprite = Sprite(name="Frame", width=10, height=10)
        animation.add_frame(sprite)
        
        # Play
        animation.play()
        assert animation.playing is True
        
        # Pause
        animation.pause()
        assert animation.playing is False
        
        # Stop
        animation.play()
        animation.stop()
        assert animation.playing is False
        assert animation.current_frame == 0
    
    def test_animation_update(self):
        """Test animation frame advancement"""
        animation = Animation(name="Test", fps=10.0)
        
        for i in range(3):
            sprite = Sprite(name=f"Frame{i}", width=10, height=10)
            animation.add_frame(sprite, duration=0.1)
        
        animation.play()
        
        # Simulate time passing
        animation.last_update = time.time() - 0.15
        changed = animation.update()
        
        assert changed is True
        assert animation.current_frame == 1
    
    def test_animation_looping(self):
        """Test loop behavior"""
        animation = Animation(name="Test", loop=True)
        
        for i in range(2):
            sprite = Sprite(name=f"Frame{i}", width=10, height=10)
            animation.add_frame(sprite, duration=0.1)
        
        animation.play()
        animation.current_frame = 1
        
        # Force update past last frame
        animation.last_update = time.time() - 0.2
        animation.update()
        
        assert animation.current_frame == 0  # Looped back
        assert animation.playing is True
    
    def test_animation_no_loop(self):
        """Test non-looping animation"""
        animation = Animation(name="Test", loop=False)
        
        for i in range(2):
            sprite = Sprite(name=f"Frame{i}", width=10, height=10)
            animation.add_frame(sprite, duration=0.1)
        
        animation.play()
        animation.current_frame = 1
        
        # Force update past last frame
        animation.last_update = time.time() - 0.2
        animation.update()
        
        assert animation.current_frame == 1  # Stayed at last
        assert animation.playing is False
    
    def test_total_duration(self):
        """Test total duration calculation"""
        animation = Animation(name="Test")
        
        for i in range(3):
            sprite = Sprite(name=f"Frame{i}", width=10, height=10)
            animation.add_frame(sprite, duration=0.5)
        
        total = animation.get_total_duration()
        assert total == 1.5


class TestAnimationSet:
    """Test AnimationSet functionality"""
    
    def test_animation_set_creation(self):
        """Test animation set creation"""
        anim_set = AnimationSet(name="Character")
        
        assert anim_set.name == "Character"
        assert len(anim_set.animations) == 0
        assert anim_set.current_animation is None
    
    def test_animation_management(self):
        """Test adding/removing animations"""
        anim_set = AnimationSet(name="Character")
        
        anim1 = Animation(name="Walk")
        anim2 = Animation(name="Run")
        
        anim_set.add_animation(anim1)
        anim_set.add_animation(anim2)
        
        assert len(anim_set.animations) == 2
        assert anim_set.current_animation == "Walk"
        
        # Remove animation
        anim_set.remove_animation("Walk")
        assert len(anim_set.animations) == 1
        assert anim_set.current_animation == "Run"
    
    def test_current_animation(self):
        """Test current animation management"""
        anim_set = AnimationSet(name="Character")
        
        anim1 = Animation(name="Idle")
        anim2 = Animation(name="Walk")
        
        anim_set.add_animation(anim1)
        anim_set.add_animation(anim2)
        
        # Get current
        current = anim_set.get_current_animation()
        assert current is not None
        assert current.name == "Idle"
        
        # Set current
        success = anim_set.set_current_animation("Walk")
        assert success is True
        assert anim_set.current_animation == "Walk"
    
    def test_animation_control(self):
        """Test play/pause/stop propagation"""
        anim_set = AnimationSet(name="Character")
        animation = Animation(name="Test")
        anim_set.add_animation(animation)
        
        # Play
        anim_set.play()
        assert animation.playing is True
        
        # Pause
        anim_set.pause()
        assert animation.playing is False
        
        # Stop
        anim_set.play()
        anim_set.stop()
        assert animation.playing is False
        assert animation.current_frame == 0


class TestAnimator:
    """Test Animator functionality"""
    
    def test_animator_creation(self):
        """Test animator initialization"""
        animator = Animator()
        
        assert animator.animation_set is not None
        assert animator.state.active_animation is None
        assert animator.state.onion_skin.enabled is True
    
    def test_animation_creation(self):
        """Test creating animations through animator"""
        animator = Animator()
        
        animation = animator.create_animation("Walk", width=32, height=32)
        
        assert animation.name == "Walk"
        assert len(animation.frames) == 1
        assert animator.state.active_animation == "Walk"
        assert animator.state.active_frame == 0
    
    def test_frame_management(self):
        """Test frame operations through animator"""
        animator = Animator()
        animator.create_animation("Test")
        
        # Add frame
        frame = animator.add_frame()
        assert frame is not None
        
        animation = animator.current_animation
        assert len(animation.frames) == 2
        assert animator.state.active_frame == 1
        
        # Duplicate frame
        dup_frame = animator.duplicate_frame(0)
        assert dup_frame is not None
        assert len(animation.frames) == 3
        
        # Delete frame
        animator.delete_frame(1)
        assert len(animation.frames) == 2
    
    def test_frame_navigation(self):
        """Test frame navigation"""
        animator = Animator()
        animator.create_animation("Test")
        
        for _ in range(3):
            animator.add_frame()
        
        assert animator.state.active_frame == 3
        
        # Previous
        animator.previous_frame()
        assert animator.state.active_frame == 2
        
        # Next
        animator.next_frame()
        assert animator.state.active_frame == 3
        
        # Can't go beyond bounds
        animator.next_frame()
        assert animator.state.active_frame == 3
    
    def test_onion_skinning(self):
        """Test onion skin frame calculation"""
        animator = Animator()
        animator.create_animation("Test")
        
        # Create multiple frames
        for _ in range(5):
            animator.add_frame()
        
        animator.state.active_frame = 2
        
        # Get onion skin frames
        onion_frames = animator.get_onion_skin_frames()
        
        # Should have previous and next frames
        assert len(onion_frames) > 0
        
        # Check opacity decreases with distance
        for i, (frame, opacity, color) in enumerate(onion_frames):
            assert 0.0 < opacity <= animator.state.onion_skin.opacity_before
    
    def test_onion_skin_rendering(self):
        """Test rendering with onion skinning"""
        animator = Animator()
        animator.create_animation("Test", width=5, height=5)
        
        # Add frames with different content
        for i in range(3):
            animator.add_frame()
            editor = animator.sprite_editor
            if editor:
                editor.draw_pixel(i, i, str(i))
        
        animator.state.active_frame = 1
        
        # Render with onion skin
        result = animator.render_with_onion_skin()
        
        assert len(result) == 5
        assert len(result[0]) == 5
        
        # Current frame pixel should be visible
        assert result[1][1] is not None
        assert result[1][1].char == '1'
    
    def test_onion_skin_settings(self):
        """Test onion skin configuration"""
        animator = Animator()
        
        settings = OnionSkinSettings(
            enabled=True,
            frames_before=3,
            frames_after=2,
            opacity_before=0.5,
            opacity_after=0.3
        )
        
        animator.set_onion_skin_settings(settings)
        
        assert animator.state.onion_skin.frames_before == 3
        assert animator.state.onion_skin.frames_after == 2
        
        # Toggle
        animator.toggle_onion_skin()
        assert animator.state.onion_skin.enabled is False
    
    def test_preview_playback(self):
        """Test animation preview"""
        animator = Animator()
        animator.create_animation("Test")
        
        for _ in range(3):
            animator.add_frame()
        
        # Start preview
        animator.play_preview()
        assert animator.state.preview_playing is True
        
        animation = animator.current_animation
        assert animation.playing is True
        
        # Stop preview
        animator.stop_preview()
        assert animator.state.preview_playing is False
        assert animation.playing is False
        assert animator.state.active_frame == 0
    
    def test_frame_duration_setting(self):
        """Test setting frame duration"""
        animator = Animator()
        animator.create_animation("Test")
        
        animator.set_frame_duration(0.5)
        
        frame = animator.current_frame
        assert frame is not None
        assert frame.duration == 0.5
    
    def test_export_import(self):
        """Test animation export/import"""
        animator = Animator()
        animator.create_animation("Test", width=16, height=16)
        
        # Export
        exported = animator.export_animation()
        assert exported is not None
        assert exported["name"] == "Test"
        
        # Import
        new_animator = Animator()
        imported_anim = new_animator.import_animation(exported)
        
        assert imported_anim.name == "Test"
        assert len(new_animator.animation_set.animations) == 1