"""Tests for the platform memory monitor module."""

import pytest
from unittest.mock import Mock, patch
from pymemtrace.platform_monitor import (
    PlatformMemoryMonitor, GamePlatform, PlatformMemoryStatus
)


class TestPlatformMemoryMonitor:
    """Test suite for PlatformMemoryMonitor."""
    
    def test_initialization(self):
        """Test monitor initialization."""
        monitor = PlatformMemoryMonitor()
        assert monitor.current_platform in GamePlatform
        assert monitor.memory_limits is not None
        assert monitor._monitoring_enabled is False
    
    def test_platform_detection(self):
        """Test platform detection."""
        monitor = PlatformMemoryMonitor()
        
        # Should detect current platform
        platform = monitor._detect_platform()
        assert platform in GamePlatform
        
        # On most test systems, should be PC platform
        assert platform in [
            GamePlatform.PC_WINDOWS,
            GamePlatform.PC_LINUX,
            GamePlatform.PC_MAC
        ]
    
    def test_platform_limits(self):
        """Test platform memory limits."""
        monitor = PlatformMemoryMonitor()
        limits = monitor._get_platform_limits()
        
        assert limits.platform == monitor.current_platform
        assert limits.total_memory > 0
        assert limits.recommended_limit > 0
        assert limits.critical_limit > limits.recommended_limit
        assert limits.reserved_system > 0
    
    def test_current_status(self):
        """Test getting current memory status."""
        monitor = PlatformMemoryMonitor()
        status = monitor.get_current_status()
        
        assert isinstance(status, PlatformMemoryStatus)
        assert status.platform == monitor.current_platform
        assert status.process_memory > 0
        assert status.available_memory > 0
        assert status.total_memory > 0
        assert 0 <= status.memory_percentage <= 100
        assert isinstance(status.is_critical, bool)
        assert isinstance(status.recommendations, list)
    
    def test_recommendations_generation(self):
        """Test platform-specific recommendations."""
        monitor = PlatformMemoryMonitor()
        
        # Test with high memory usage
        recommendations = monitor._generate_recommendations(
            process_memory=monitor.memory_limits.recommended_limit + 1,
            available_memory=100 * 1024 * 1024,
            memory_percentage=85
        )
        
        assert len(recommendations) > 0
        assert any("exceeds platform recommendation" in r for r in recommendations)
    
    def test_mobile_recommendations(self):
        """Test mobile platform recommendations."""
        monitor = PlatformMemoryMonitor()
        monitor.current_platform = GamePlatform.MOBILE_IOS
        
        # Test iOS critical memory
        recommendations = monitor._generate_recommendations(
            process_memory=500 * 1024 * 1024,
            available_memory=50 * 1024 * 1024,  # Less than 100MB
            memory_percentage=75
        )
        
        assert any("iOS may terminate" in r for r in recommendations)
        assert any("texture resolution" in r for r in recommendations)
    
    def test_console_recommendations(self):
        """Test console platform recommendations."""
        monitor = PlatformMemoryMonitor()
        monitor.current_platform = GamePlatform.CONSOLE_PLAYSTATION
        monitor.memory_limits = monitor._get_platform_limits()
        
        recommendations = monitor._generate_recommendations(
            process_memory=monitor.memory_limits.recommended_limit + 1,
            available_memory=1024 * 1024 * 1024,
            memory_percentage=80
        )
        
        assert any("console memory banks" in r for r in recommendations)
        assert any("platform-specific texture" in r for r in recommendations)
    
    def test_platform_optimization_guide(self):
        """Test platform optimization guidelines."""
        monitor = PlatformMemoryMonitor()
        guide = monitor.get_platform_optimization_guide()
        
        assert "platform" in guide
        assert "texture_formats" in guide
        assert "audio_formats" in guide
        assert "memory_techniques" in guide
        assert len(guide["texture_formats"]) > 0
    
    def test_platform_comparison(self):
        """Test comparing platforms."""
        monitor = PlatformMemoryMonitor()
        
        platforms = [
            GamePlatform.PC_WINDOWS,
            GamePlatform.MOBILE_IOS,
            GamePlatform.CONSOLE_PLAYSTATION
        ]
        
        comparison = monitor.compare_platforms(platforms)
        
        assert len(comparison) == 3
        for platform in platforms:
            assert platform.value in comparison
            platform_data = comparison[platform.value]
            assert "min_memory_mb" in platform_data
            assert "recommended_mb" in platform_data
            assert "crash_threshold" in platform_data
    
    def test_platform_compatibility(self):
        """Test platform compatibility estimation."""
        monitor = PlatformMemoryMonitor()
        
        # Test with 500MB usage
        memory_usage = 500 * 1024 * 1024
        compatibility = monitor.estimate_platform_compatibility(memory_usage)
        
        # Should be compatible with PC platforms
        assert compatibility[GamePlatform.PC_WINDOWS.value]["meets_minimum"]
        
        # May not be compatible with mobile
        mobile_compat = compatibility[GamePlatform.MOBILE_IOS.value]
        assert "optimization_needed" in mobile_compat
    
    def test_memory_bank_usage(self):
        """Test console memory bank usage."""
        monitor = PlatformMemoryMonitor()
        
        # Test non-console platform
        if monitor.current_platform not in [
            GamePlatform.CONSOLE_PLAYSTATION,
            GamePlatform.CONSOLE_XBOX
        ]:
            assert monitor.get_memory_bank_usage() is None
        
        # Simulate console platform
        monitor.current_platform = GamePlatform.CONSOLE_PLAYSTATION
        monitor.memory_limits = monitor._get_platform_limits()
        
        bank_usage = monitor.get_memory_bank_usage()
        if bank_usage:
            assert "main" in bank_usage
            assert "video" in bank_usage
            assert bank_usage["main"] > 0
    
    def test_monitoring_start_stop(self):
        """Test starting and stopping monitoring."""
        monitor = PlatformMemoryMonitor()
        
        # Start monitoring
        monitor.start_monitoring(interval=0.1)
        assert monitor._monitoring_enabled is True
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert monitor._monitoring_enabled is False
    
    def test_status_callbacks(self):
        """Test status callbacks."""
        monitor = PlatformMemoryMonitor()
        callback_called = False
        received_status = None
        
        def status_callback(status: PlatformMemoryStatus):
            nonlocal callback_called, received_status
            callback_called = True
            received_status = status
        
        monitor.add_status_callback(status_callback)
        
        # Manually trigger callback with critical status
        status = monitor.get_current_status()
        status.is_critical = True
        
        for callback in monitor._callbacks:
            callback(status)
        
        assert callback_called
        assert received_status.is_critical
    
    def test_web_platform_config(self):
        """Test web platform configuration."""
        monitor = PlatformMemoryMonitor()
        
        config = monitor.PLATFORM_CONFIGS[GamePlatform.WEB]
        assert config["min_memory"] == 256
        assert config["crash_threshold"] == 0.95
        
        # Test web recommendations
        monitor.current_platform = GamePlatform.WEB
        recommendations = monitor._generate_recommendations(
            process_memory=400 * 1024 * 1024,
            available_memory=100 * 1024 * 1024,
            memory_percentage=82
        )
        
        assert any("WebGL" in r for r in recommendations)
        assert any("progressive asset loading" in r for r in recommendations)
    
    def test_switch_platform_config(self):
        """Test Nintendo Switch platform configuration."""
        monitor = PlatformMemoryMonitor()
        monitor.current_platform = GamePlatform.CONSOLE_SWITCH
        
        recommendations = monitor._generate_recommendations(
            process_memory=2500 * 1024 * 1024,
            available_memory=500 * 1024 * 1024,
            memory_percentage=76
        )
        
        assert any("handheld mode" in r for r in recommendations)
        assert any("dynamic resolution" in r for r in recommendations)
    
    def test_last_status_tracking(self):
        """Test that last status is tracked."""
        monitor = PlatformMemoryMonitor()
        
        assert monitor._last_status is None
        
        status = monitor.get_current_status()
        assert monitor._last_status is not None
        assert monitor._last_status.platform == status.platform