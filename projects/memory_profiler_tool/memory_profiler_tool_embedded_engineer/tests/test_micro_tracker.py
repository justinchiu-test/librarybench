"""Tests for micro_tracker module."""

import pytest
import time
import threading
from src.micro_tracker import MicroTracker, AllocationSize, AllocationEvent


class TestMicroTracker:
    """Test suite for MicroTracker."""
    
    def test_initialization(self):
        """Test tracker initialization."""
        tracker = MicroTracker(max_events=100)
        assert tracker.max_events == 100
        assert not tracker._tracking
        assert len(tracker._events) == 0
        assert len(tracker._live_objects) == 0
        
    def test_start_stop_tracking(self):
        """Test starting and stopping tracking."""
        tracker = MicroTracker()
        
        # Start tracking
        tracker.start_tracking()
        assert tracker._tracking
        
        # Stop tracking
        tracker.stop_tracking()
        assert not tracker._tracking
        
    def test_context_manager(self):
        """Test context manager usage."""
        with MicroTracker() as tracker:
            assert tracker._tracking
            # Create some objects
            test_list = [1, 2, 3, 4, 5]
            test_dict = {'a': 1, 'b': 2}
            
        assert not tracker._tracking
        
    def test_allocation_tracking(self):
        """Test basic allocation tracking."""
        tracker = MicroTracker()
        tracker.start_tracking()
        
        # Create objects
        test_list = list(range(100))
        test_dict = {i: i*2 for i in range(50)}
        test_string = "Hello" * 100
        
        # Give time for tracking
        time.sleep(0.1)
        
        tracker.stop_tracking()
        
        # Check events were recorded
        events = tracker.get_allocation_events()
        assert len(events) > 0
        
        # Check stats
        stats = tracker.get_stats()
        assert stats.total_count > 0
        assert stats.total_size > 0
        assert stats.current_memory > 0
        
    def test_size_classification(self):
        """Test allocation size classification."""
        assert AllocationSize.classify(32) == AllocationSize.TINY
        assert AllocationSize.classify(100) == AllocationSize.SMALL
        assert AllocationSize.classify(1000) == AllocationSize.MEDIUM
        assert AllocationSize.classify(5000) == AllocationSize.LARGE
        
    def test_allocation_events(self):
        """Test allocation event structure."""
        tracker = MicroTracker()
        tracker.start_tracking()
        
        # Create a specific object
        test_obj = [1, 2, 3]
        
        time.sleep(0.1)
        tracker.stop_tracking()
        
        events = tracker.get_allocation_events()
        
        # Check event properties
        for event in events:
            assert isinstance(event.obj_id, int)
            assert isinstance(event.size, int)
            assert isinstance(event.size_class, AllocationSize)
            assert isinstance(event.timestamp, float)
            assert isinstance(event.stack_trace, list)
            assert isinstance(event.object_type, str)
            assert isinstance(event.thread_id, int)
            
    def test_live_objects_tracking(self):
        """Test tracking of live objects."""
        tracker = MicroTracker()
        
        with tracker:
            # Create objects
            obj1 = [1, 2, 3]
            obj2 = {'a': 1}
            
            live_objects = tracker.get_live_objects()
            assert len(live_objects) > 0
            
            # Delete an object
            del obj1
            
            # Live objects should update eventually
            # Note: Exact timing depends on GC
            
    def test_callbacks(self):
        """Test allocation callbacks."""
        events_received = []
        
        def callback(event: AllocationEvent):
            events_received.append(event)
            
        tracker = MicroTracker()
        tracker.add_callback(callback)
        
        with tracker:
            test_list = [1, 2, 3, 4, 5]
            test_dict = {'a': 1}
            
        assert len(events_received) > 0
        
        # Remove callback
        tracker.remove_callback(callback)
        
    def test_allocation_by_size_class(self):
        """Test grouping allocations by size class."""
        tracker = MicroTracker()
        
        with tracker:
            # Create objects of different sizes
            tiny_obj = "x"  # Small string
            small_obj = [i for i in range(10)]
            medium_obj = [i for i in range(100)]
            large_obj = [i for i in range(1000)]
            
        by_class = tracker.get_allocation_by_size_class()
        
        # Should have allocations in different size classes
        assert len(by_class) > 0
        
    def test_stream_allocations(self):
        """Test allocation streaming with filters."""
        tracker = MicroTracker()
        
        # Test size filter
        tracker.stream_allocations(size_filter=AllocationSize.SMALL)
        
        # Test type filter
        tracker.stream_allocations(type_filter='list')
        
        with tracker:
            test_list = [1, 2, 3]
            test_dict = {'a': 1}
            
    def test_clear(self):
        """Test clearing tracking data."""
        tracker = MicroTracker()
        
        with tracker:
            test_list = [1, 2, 3]
            
        assert len(tracker.get_allocation_events()) > 0
        
        tracker.clear()
        
        assert len(tracker.get_allocation_events()) == 0
        assert len(tracker.get_live_objects()) == 0
        
    def test_thread_safety(self):
        """Test thread safety of tracking."""
        tracker = MicroTracker()
        results = []
        
        def allocate_in_thread():
            with tracker:
                thread_list = list(range(100))
                results.append(len(tracker.get_allocation_events()))
                
        threads = []
        for _ in range(5):
            t = threading.Thread(target=allocate_in_thread)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # Should have tracked allocations from all threads
        assert len(results) == 5
        
    def test_memory_stats(self):
        """Test memory statistics calculation."""
        tracker = MicroTracker()
        
        with tracker:
            # Create objects of known types
            int_list = [i for i in range(100)]
            str_list = ["test" * 10 for _ in range(50)]
            dict_obj = {i: str(i) for i in range(100)}
            
        stats = tracker.get_stats()
        
        assert stats.total_count > 0
        assert stats.total_size > 0
        assert stats.peak_memory >= stats.current_memory
        assert len(stats.by_size_class) > 0
        assert len(stats.by_type) > 0
        
    def test_max_events_limit(self):
        """Test max events limit is respected."""
        max_events = 10
        tracker = MicroTracker(max_events=max_events)
        
        with tracker:
            # Create more objects than max_events
            for i in range(20):
                obj = [i] * 10
                
        events = tracker.get_allocation_events()
        assert len(events) <= max_events