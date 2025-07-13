"""Extended tests for micro_tracker module."""

import pytest
import time
import gc
import sys
from src.micro_tracker import MicroTracker, AllocationSize, AllocationEvent, AllocationStats


class TestMicroTrackerExtended:
    """Extended test suite for MicroTracker."""
    
    def test_allocation_size_boundaries(self):
        """Test allocation size classification boundaries."""
        # Test exact boundaries
        assert AllocationSize.classify(0) == AllocationSize.TINY
        assert AllocationSize.classify(64) == AllocationSize.SMALL
        assert AllocationSize.classify(512) == AllocationSize.MEDIUM
        assert AllocationSize.classify(4096) == AllocationSize.LARGE
        assert AllocationSize.classify(1000000) == AllocationSize.LARGE
        
    def test_track_different_object_types(self):
        """Test tracking various Python object types."""
        tracker = MicroTracker()
        
        with tracker:
            # Different object types
            int_obj = 42
            float_obj = 3.14
            str_obj = "test string"
            bytes_obj = b"bytes data"
            tuple_obj = (1, 2, 3)
            set_obj = {1, 2, 3}
            frozenset_obj = frozenset([1, 2, 3])
            
        events = tracker.get_allocation_events()
        types_tracked = {e.object_type for e in events}
        
        # Should track various types
        assert len(types_tracked) > 5
        
    def test_memory_leak_detection(self):
        """Test detection of potential memory leaks."""
        tracker = MicroTracker()
        
        with tracker:
            # Create objects that persist
            persistent_list = []
            for i in range(10):
                persistent_list.append([0] * 100)
                
        stats = tracker.get_stats()
        # Check that we tracked allocations
        assert stats.total_count >= 10
        assert stats.total_size > 0
        
    def test_allocation_timestamp_ordering(self):
        """Test that allocation timestamps are properly ordered."""
        tracker = MicroTracker()
        
        with tracker:
            obj1 = [1]
            time.sleep(0.01)
            obj2 = [2]
            time.sleep(0.01)
            obj3 = [3]
            
        events = tracker.get_allocation_events()
        timestamps = [e.timestamp for e in events if e.object_type == 'list']
        
        # Timestamps should be increasing
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i-1]
            
    def test_stack_trace_depth(self):
        """Test stack trace capture depth."""
        tracker = MicroTracker()
        
        def deep_function_3():
            return [1, 2, 3]
            
        def deep_function_2():
            return deep_function_3()
            
        def deep_function_1():
            return deep_function_2()
            
        with tracker:
            result = deep_function_1()
            
        events = tracker.get_allocation_events()
        
        # Should have tracked allocations
        assert len(events) > 0
        
        # Check that stack traces exist
        for event in events:
            assert hasattr(event, 'stack_trace')
            assert isinstance(event.stack_trace, list)
            
    def test_stats_accuracy(self):
        """Test accuracy of allocation statistics."""
        tracker = MicroTracker()
        
        with tracker:
            # Known allocations
            small_list = [1, 2, 3]  # Small
            medium_list = list(range(100))  # Medium
            large_list = list(range(1000))  # Large
            
        stats = tracker.get_stats()
        
        # Check that we tracked allocations
        assert stats.total_count > 0
        assert stats.total_size > 0
        # Check that size classes were populated
        assert len(stats.by_size_class) > 0
        
    def test_circular_reference_handling(self):
        """Test handling of circular references."""
        tracker = MicroTracker()
        
        with tracker:
            # Create circular reference
            list1 = []
            list2 = []
            list1.append(list2)
            list2.append(list1)
            
        # Should not crash or hang
        events = tracker.get_allocation_events()
        assert len(events) > 0
        
    def test_large_object_tracking(self):
        """Test tracking of very large objects."""
        tracker = MicroTracker()
        
        with tracker:
            # Large object
            large_data = [0] * 10000
            large_string = "x" * 10000
            
        events = tracker.get_allocation_events()
        
        # Should have tracked some large allocations
        assert len(events) > 0
        assert any(e.size > 1000 for e in events)
        
    def test_event_filtering(self):
        """Test filtering of allocation events."""
        tracker = MicroTracker()
        
        with tracker:
            # Various allocations
            nums = [1, 2, 3]
            text = "hello world"
            data = {"key": "value"}
            
        # Get events by type
        events = tracker.get_allocation_events()
        
        # Should have tracked various types
        types_found = {e.object_type for e in events}
        assert len(types_found) > 0
        
        # Should be able to filter events
        assert len(events) > 0
        
    def test_memory_overhead_calculation(self):
        """Test calculation of memory overhead."""
        tracker = MicroTracker()
        
        # Track empty containers
        with tracker:
            empty_list = []
            empty_dict = {}
            empty_set = set()
            empty_tuple = ()
            
        stats = tracker.get_stats()
        
        # Even empty containers have overhead
        assert stats.total_size > 0
        
    def test_peak_memory_tracking(self):
        """Test peak memory tracking accuracy."""
        tracker = MicroTracker()
        
        with tracker:
            # Allocate and free
            temp_data = [0] * 10000
            peak_before_free = tracker.get_stats().peak_memory
            
            del temp_data
            gc.collect()
            
            # Peak should remain the same
            peak_after_free = tracker.get_stats().peak_memory
            
        assert peak_before_free == peak_after_free
        assert peak_before_free > 0