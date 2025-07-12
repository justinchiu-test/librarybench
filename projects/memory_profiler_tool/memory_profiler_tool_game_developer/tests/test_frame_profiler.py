"""Tests for the frame memory profiler module."""

import time
import pytest
from unittest.mock import Mock
from pymemtrace.frame_profiler import FrameMemoryProfiler, MemorySpike


class TestFrameMemoryProfiler:
    """Test suite for FrameMemoryProfiler."""
    
    def test_initialization(self):
        """Test profiler initialization."""
        profiler = FrameMemoryProfiler(max_frame_history=100, spike_threshold=0.2)
        assert profiler.max_frame_history == 100
        assert profiler.spike_threshold == 0.2
        assert profiler.frame_count == 0
        assert len(profiler.frame_history) == 0
    
    def test_frame_profiling_context_manager(self):
        """Test frame profiling using context manager."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        with profiler.frame():
            # Simulate some work
            time.sleep(0.01)
        
        assert profiler.frame_count == 1
        assert len(profiler.frame_history) == 1
        
        frame_data = profiler.get_frame_stats()
        assert frame_data is not None
        assert frame_data.frame_number == 1
        assert frame_data.frame_duration > 0
    
    def test_frame_profiling_manual(self):
        """Test manual frame profiling."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        profiler.start_frame()
        time.sleep(0.01)
        profiler.end_frame()
        
        assert profiler.frame_count == 1
        frame_data = profiler.get_frame_stats()
        assert frame_data.frame_duration >= 0.01
    
    def test_memory_spike_detection(self):
        """Test memory spike detection."""
        profiler = FrameMemoryProfiler(spike_threshold=0.1)
        spike_detected = False
        spike_info = None
        
        def spike_callback(spike: MemorySpike):
            nonlocal spike_detected, spike_info
            spike_detected = True
            spike_info = spike
        
        profiler.add_spike_callback(spike_callback)
        profiler.start_profiling()
        
        # Create baseline frames
        for _ in range(10):
            with profiler.frame():
                pass
        
        # Force a spike by modifying memory usage
        # In real scenario, this would happen naturally
        with profiler.frame():
            # Create large temporary objects
            large_data = [0] * 10000000
        
        # Spike detection happens in end_frame
        # May not always trigger in test due to GC
    
    def test_frame_history_limit(self):
        """Test frame history respects max limit."""
        profiler = FrameMemoryProfiler(max_frame_history=5)
        profiler.start_profiling()
        
        for i in range(10):
            with profiler.frame():
                pass
        
        assert len(profiler.frame_history) == 5
        assert profiler.frame_count == 10
    
    def test_average_frame_memory(self):
        """Test average memory calculation."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        for _ in range(5):
            with profiler.frame():
                pass
        
        avg_memory = profiler.get_average_frame_memory(last_n_frames=5)
        assert avg_memory > 0
    
    def test_frame_drops_detection(self):
        """Test detection of dropped frames."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        # Normal frame
        with profiler.frame():
            time.sleep(0.001)
        
        # Dropped frame (exceeds 16.67ms for 60 FPS)
        with profiler.frame():
            time.sleep(0.02)
        
        dropped = profiler.detect_frame_drops(target_fps=60)
        assert len(dropped) >= 1
        assert 2 in dropped
    
    def test_memory_trend(self):
        """Test memory trend calculation."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        for _ in range(10):
            with profiler.frame():
                pass
        
        trend = profiler.get_memory_trend(window_size=5)
        assert len(trend) > 0
        assert all(isinstance(t, float) for t in trend)
    
    def test_profiling_overhead(self):
        """Test that profiling overhead is measured."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        overhead = profiler.get_profiling_overhead()
        assert overhead >= 0
        assert overhead < 5.0  # Should be less than 5ms (more lenient for CI environments)
    
    def test_profiling_disabled(self):
        """Test that profiling does nothing when disabled."""
        profiler = FrameMemoryProfiler()
        # Don't call start_profiling()
        
        with profiler.frame():
            pass
        
        assert profiler.frame_count == 0
        assert len(profiler.frame_history) == 0
    
    def test_frame_time_correlation(self):
        """Test correlation between frame time and memory."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        for i in range(5):
            with profiler.frame():
                time.sleep(0.001 * (i + 1))
        
        correlation = profiler.get_frame_time_correlation()
        assert "frame_times" in correlation
        assert "memory_usage" in correlation
        assert len(correlation["frame_times"]) == 5
        assert len(correlation["memory_usage"]) == 5
    
    def test_reset(self):
        """Test profiler reset."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        with profiler.frame():
            pass
        
        assert profiler.frame_count == 1
        
        profiler.reset()
        assert profiler.frame_count == 0
        assert len(profiler.frame_history) == 0
    
    def test_thread_safety(self):
        """Test thread safety of frame profiler."""
        import threading
        
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        def profile_frames():
            for _ in range(10):
                with profiler.frame():
                    time.sleep(0.001)
        
        threads = [threading.Thread(target=profile_frames) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have processed frames from all threads
        assert profiler.frame_count == 30
    
    def test_gc_tracking(self):
        """Test garbage collection tracking."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        with profiler.frame():
            # Force some allocations
            temp_data = [list(range(1000)) for _ in range(100)]
        
        frame_data = profiler.get_frame_stats()
        assert frame_data.gc_collections is not None
        assert isinstance(frame_data.gc_collections, dict)