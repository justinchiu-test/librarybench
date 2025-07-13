"""Micro-allocation tracking with byte-level precision."""

import gc
import sys
import time
import traceback
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable, Any
from enum import Enum
import weakref


class AllocationSize(Enum):
    """Size classes for memory allocations."""
    TINY = (0, 64)          # 0-64 bytes
    SMALL = (64, 512)       # 64-512 bytes
    MEDIUM = (512, 4096)    # 512-4KB
    LARGE = (4096, float('inf'))  # 4KB+

    @classmethod
    def classify(cls, size: int) -> 'AllocationSize':
        """Classify allocation by size."""
        for size_class in cls:
            min_size, max_size = size_class.value
            if min_size <= size < max_size:
                return size_class
        return cls.LARGE


@dataclass
class AllocationEvent:
    """Represents a memory allocation event."""
    obj_id: int
    size: int
    size_class: AllocationSize
    timestamp: float
    stack_trace: List[str]
    object_type: str
    thread_id: int
    
    
@dataclass
class AllocationStats:
    """Statistics for allocations."""
    total_count: int = 0
    total_size: int = 0
    by_size_class: Dict[AllocationSize, int] = field(default_factory=lambda: defaultdict(int))
    by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    peak_memory: int = 0
    current_memory: int = 0


class MicroTracker:
    """Track memory allocations with byte-level precision."""
    
    def __init__(self, max_events: int = 10000):
        """Initialize the micro tracker.
        
        Args:
            max_events: Maximum number of events to store in history
        """
        self.max_events = max_events
        self._tracking = False
        self._events: deque = deque(maxlen=max_events)
        self._live_objects: Dict[int, AllocationEvent] = {}
        self._stats = AllocationStats()
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[AllocationEvent], None]] = []
        self._tracked_objects: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        
    def start_tracking(self) -> None:
        """Start tracking memory allocations."""
        if self._tracking:
            return
            
        self._tracking = True
        
        # Track a sample of existing objects to avoid timeout
        try:
            sample_size = min(1000, len(gc.get_objects()))
            for i, obj in enumerate(gc.get_objects()):
                if i >= sample_size:
                    break
                self._track_object(obj)
        except Exception:
            pass
            
    def stop_tracking(self) -> None:
        """Stop tracking memory allocations."""
        if not self._tracking:
            return
            
        self._tracking = False
            
    def add_callback(self, callback: Callable[[AllocationEvent], None]) -> None:
        """Add a callback for allocation events.
        
        Args:
            callback: Function to call on each allocation event
        """
        self._callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[AllocationEvent], None]) -> None:
        """Remove a callback.
        
        Args:
            callback: Callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            
    def get_allocation_events(self, limit: Optional[int] = None) -> List[AllocationEvent]:
        """Get allocation events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of allocation events
        """
        with self._lock:
            events = list(self._events)
            if limit:
                events = events[-limit:]
            return events
            
    def get_live_objects(self) -> Dict[int, AllocationEvent]:
        """Get currently live objects.
        
        Returns:
            Dictionary of live object IDs to allocation events
        """
        with self._lock:
            return self._live_objects.copy()
            
    def get_stats(self) -> AllocationStats:
        """Get allocation statistics.
        
        Returns:
            Allocation statistics
        """
        with self._lock:
            return self._stats
            
    def get_allocation_by_size_class(self) -> Dict[AllocationSize, List[AllocationEvent]]:
        """Get allocations grouped by size class.
        
        Returns:
            Dictionary mapping size classes to allocation events
        """
        by_class: Dict[AllocationSize, List[AllocationEvent]] = defaultdict(list)
        
        with self._lock:
            for event in self._events:
                by_class[event.size_class].append(event)
                
        return dict(by_class)
        
    def stream_allocations(self, size_filter: Optional[AllocationSize] = None,
                          type_filter: Optional[str] = None) -> None:
        """Stream allocation events in real-time.
        
        Args:
            size_filter: Only show allocations of this size class
            type_filter: Only show allocations of this type
        """
        def print_event(event: AllocationEvent) -> None:
            if size_filter and event.size_class != size_filter:
                return
            if type_filter and event.object_type != type_filter:
                return
                
            print(f"[{event.timestamp:.6f}] {event.object_type} "
                  f"({event.size} bytes, {event.size_class.name})")
                  
        self.add_callback(print_event)
        
    def _track_object(self, obj: Any) -> None:
        """Track a single object."""
        if not self._tracking:
            return
            
        try:
            obj_id = id(obj)
            if obj_id in self._live_objects:
                return
                
            size = sys.getsizeof(obj)
            size_class = AllocationSize.classify(size)
            
            # Get stack trace
            stack = []
            for frame_info in traceback.extract_stack()[:-2]:
                stack.append(f"{frame_info.filename}:{frame_info.lineno} {frame_info.name}")
                
            event = AllocationEvent(
                obj_id=obj_id,
                size=size,
                size_class=size_class,
                timestamp=time.time(),
                stack_trace=stack[-10:],  # Keep last 10 frames
                object_type=type(obj).__name__,
                thread_id=threading.get_ident()
            )
            
            with self._lock:
                self._events.append(event)
                self._live_objects[obj_id] = event
                self._tracked_objects[obj_id] = obj
                
                # Update stats
                self._stats.total_count += 1
                self._stats.total_size += size
                self._stats.current_memory += size
                self._stats.peak_memory = max(self._stats.peak_memory, 
                                             self._stats.current_memory)
                self._stats.by_size_class[size_class] += 1
                self._stats.by_type[event.object_type] += 1
                
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(event)
                except Exception:
                    pass
                    
        except Exception:
            # Ignore tracking errors
            pass
            
    def _cleanup_dead_objects(self) -> None:
        """Clean up dead objects from tracking."""
        with self._lock:
            dead_ids = []
            for obj_id in list(self._live_objects.keys()):
                if obj_id not in self._tracked_objects:
                    event = self._live_objects[obj_id]
                    self._stats.current_memory -= event.size
                    dead_ids.append(obj_id)
                    
            for obj_id in dead_ids:
                del self._live_objects[obj_id]
                    
    def clear(self) -> None:
        """Clear all tracking data."""
        with self._lock:
            self._events.clear()
            self._live_objects.clear()
            self._stats = AllocationStats()
            self._tracked_objects.clear()
            
    def __enter__(self) -> 'MicroTracker':
        """Context manager entry."""
        self.start_tracking()
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self._cleanup_dead_objects()
        self.stop_tracking()