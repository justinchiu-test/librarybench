"""Tests for cross_platform module."""

import pytest
from src.cross_platform import (
    CrossPlatformPredictor, Architecture, PlatformProfile, 
    MemoryPrediction, CrossPlatformReport
)


class TestCrossPlatformPredictor:
    """Test suite for CrossPlatformPredictor."""
    
    def test_initialization(self):
        """Test predictor initialization."""
        predictor = CrossPlatformPredictor()
        assert predictor.host_profile is not None
        assert isinstance(predictor.host_profile, PlatformProfile)
        
    def test_platform_profiles(self):
        """Test platform profiles are properly defined."""
        predictor = CrossPlatformPredictor()
        
        # Check key platforms exist
        assert Architecture.ARM32 in predictor.PLATFORM_PROFILES
        assert Architecture.ARM64 in predictor.PLATFORM_PROFILES
        assert Architecture.ESP32 in predictor.PLATFORM_PROFILES
        assert Architecture.AVR in predictor.PLATFORM_PROFILES
        
        # Check profile properties
        arm32_profile = predictor.PLATFORM_PROFILES[Architecture.ARM32]
        assert arm32_profile.word_size == 4
        assert arm32_profile.pointer_size == 4
        assert arm32_profile.alignment == 4
        
    def test_predict_memory_simple(self):
        """Test simple memory prediction."""
        predictor = CrossPlatformPredictor()
        
        allocations = [
            ("list", 1000),
            ("dict", 2000),
            ("string", 500),
        ]
        
        report = predictor.predict_memory(allocations, [Architecture.ARM32, Architecture.ARM64])
        
        assert len(report.predictions) == 2
        assert Architecture.ARM32 in report.predictions
        assert Architecture.ARM64 in report.predictions
        
        # ARM64 should use more memory due to larger pointers
        arm32_pred = report.predictions[Architecture.ARM32]
        arm64_pred = report.predictions[Architecture.ARM64]
        assert arm64_pred.heap_usage >= arm32_pred.heap_usage
        
    def test_memory_translation(self):
        """Test memory size translation between platforms."""
        predictor = CrossPlatformPredictor()
        
        # Test list translation (contains pointers)
        host_size = 1000
        arm32_profile = predictor.PLATFORM_PROFILES[Architecture.ARM32]
        translated = predictor._translate_size("list", host_size, arm32_profile)
        assert translated > 0
        
        # Test simple type translation
        simple_size = 100
        translated_simple = predictor._translate_size("int", simple_size, arm32_profile)
        assert translated_simple > 0
        
    def test_alignment_calculation(self):
        """Test memory alignment calculation."""
        predictor = CrossPlatformPredictor()
        
        # Test alignment
        assert predictor._align_size(10, 4) == 12
        assert predictor._align_size(16, 4) == 16
        assert predictor._align_size(15, 8) == 16
        assert predictor._align_size(24, 8) == 24
        
    def test_alignment_waste_detection(self):
        """Test detection of alignment waste."""
        predictor = CrossPlatformPredictor()
        
        allocations = [
            ("small_obj", 17),  # Will need padding
            ("aligned_obj", 32),  # Already aligned
            ("odd_size", 123),  # Will need padding
        ]
        
        report = predictor.predict_memory(allocations, [Architecture.ARM32])
        
        assert len(report.alignment_issues) > 0
        
        # Check waste is calculated correctly
        total_waste = sum(waste for _, waste in report.alignment_issues)
        assert total_waste > 0
        
    def test_constrained_platform_warnings(self):
        """Test warnings for constrained platforms."""
        predictor = CrossPlatformPredictor()
        
        # Large allocations
        allocations = [
            ("large_buffer", 100000),
            ("huge_array", 200000),
        ]
        
        report = predictor.predict_memory(allocations, [Architecture.AVR, Architecture.ESP32])
        
        # Should have warnings for AVR
        avr_pred = report.predictions[Architecture.AVR]
        assert len(avr_pred.warnings) > 0
        assert any("exceeds" in w for w in avr_pred.warnings)
        
    def test_optimization_suggestions(self):
        """Test generation of optimization suggestions."""
        predictor = CrossPlatformPredictor()
        
        allocations = [
            ("buffer", 50000),
            ("cache", 100000),
        ]
        
        report = predictor.predict_memory(allocations, 
                                       [Architecture.STM32, Architecture.ESP32])
        
        assert len(report.optimization_suggestions) > 0
        
        # Should suggest optimization for constrained platforms
        assert any("optimization" in s.lower() for s in report.optimization_suggestions)
        
    def test_validation_against_limits(self):
        """Test validation against platform memory limits."""
        predictor = CrossPlatformPredictor()
        
        # Allocations that exceed AVR limits
        allocations = [("huge", 10000)]
        
        report = predictor.predict_memory(allocations, [Architecture.AVR])
        
        assert Architecture.AVR in report.validation_results
        assert not report.validation_results[Architecture.AVR]  # Should fail
        
    def test_model_allocation_patterns(self):
        """Test modeling of allocation patterns."""
        predictor = CrossPlatformPredictor()
        
        # Sequential pattern
        seq_allocs = predictor.model_allocation_pattern("sequential", 10, 100)
        assert len(seq_allocs) == 10
        assert all(size == 100 for _, size in seq_allocs)
        
        # Random pattern
        rand_allocs = predictor.model_allocation_pattern("random", 10, 100)
        assert len(rand_allocs) == 10
        
        # Burst pattern
        burst_allocs = predictor.model_allocation_pattern("burst", 20, 100)
        assert len(burst_allocs) == 20
        
    def test_compare_platforms(self):
        """Test platform comparison."""
        predictor = CrossPlatformPredictor()
        
        allocations = [
            ("obj1", 1000),
            ("obj2", 2000),
            ("obj3", 500),
        ]
        
        comparison = predictor.compare_platforms(allocations)
        
        assert comparison['most_efficient'] is not None
        assert comparison['least_efficient'] is not None
        assert len(comparison['platform_rankings']) > 0
        assert comparison['memory_range'][0] <= comparison['memory_range'][1]
        
    def test_platform_specific_overhead(self):
        """Test platform-specific overhead calculations."""
        predictor = CrossPlatformPredictor()
        
        allocations = [("data", 1000)]
        
        # Compare different platforms
        report = predictor.predict_memory(allocations, 
                                        [Architecture.X86, Architecture.AVR])
        
        x86_pred = report.predictions[Architecture.X86]
        avr_pred = report.predictions[Architecture.AVR]
        
        # AVR has higher overhead factor
        avr_profile = predictor.PLATFORM_PROFILES[Architecture.AVR]
        x86_profile = predictor.PLATFORM_PROFILES[Architecture.X86]
        assert avr_profile.overhead_factor > x86_profile.overhead_factor
        
    def test_cross_platform_report_structure(self):
        """Test the structure of cross-platform report."""
        predictor = CrossPlatformPredictor()
        
        allocations = [("test", 1000)]
        report = predictor.predict_memory(allocations, [Architecture.ARM32])
        
        assert hasattr(report, 'predictions')
        assert hasattr(report, 'alignment_issues')
        assert hasattr(report, 'portability_issues')
        assert hasattr(report, 'optimization_suggestions')
        assert hasattr(report, 'validation_results')
        
    def test_unknown_platform_handling(self):
        """Test handling of unknown platforms."""
        predictor = CrossPlatformPredictor()
        
        # Create a fake architecture
        fake_arch = Architecture.ARM32  # Use existing for test
        allocations = [("test", 1000)]
        
        # Remove platform profile temporarily
        original_profile = predictor.PLATFORM_PROFILES.pop(fake_arch, None)
        
        try:
            report = predictor.predict_memory(allocations, [fake_arch])
            assert len(report.portability_issues) > 0
        finally:
            if original_profile:
                predictor.PLATFORM_PROFILES[fake_arch] = original_profile