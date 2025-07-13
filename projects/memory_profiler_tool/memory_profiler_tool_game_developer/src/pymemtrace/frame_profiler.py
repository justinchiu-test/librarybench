"""Frame memory profiler for tracking per-frame memory usage in games."""

import gc
import sys
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Deque
from contextlib import contextmanager


@dataclass
class FrameMemoryData:
    """Memory data for a single frame."""
    frame_number: int
    timestamp: float
    allocated_memory: int
    deallocated_memory: int
    peak_memory: int
    gc_collections: Dict[int, int]
    allocation_count: int
    deallocation_count: int
    frame_duration: float = 0.0


@dataclass
class MemorySpike:
    """Represents a memory spike during frame rendering."""
    frame_number: int
    spike_size: int
    duration: float
    timestamp: float


class FrameMemoryProfiler:
    """Profiles memory usage on a per-frame basis for game loops."""
    
    def __init__(self, max_frame_history: int = 1000, spike_threshold: float = 0.1):
        """
        Initialize the frame memory profiler.
        
        Args:
            max_frame_history: Maximum number of frames to keep in history
            spike_threshold: Percentage threshold for spike detection (0.1 = 10%)
        """
        self.max_frame_history = max_frame_history
        self.spike_threshold = spike_threshold
        self.frame_history: Deque[FrameMemoryData] = deque(maxlen=max_frame_history)
        self.current_frame: Optional[FrameMemoryData] = None
        self.frame_count = 0
        self._lock = threading.Lock()
        self._profiling_enabled = False
        self._frame_start_time = 0.0
        self._baseline_memory = 0
        self._spike_callbacks: List[Callable[[MemorySpike], None]] = []
        self._gc_baseline = self._get_gc_counts()
        
    def _get_gc_counts(self) -> Dict[int, int]:
        """Get current garbage collection counts."""
        return {i: gc.get_count()[i] for i in range(gc.get_count().__len__())}
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        # Use a more efficient method that doesn't iterate all objects
        import psutil
        process = psutil.Process()
        return process.memory_info().rss
    
    @contextmanager
    def frame(self):
        """Context manager for profiling a single frame."""
        self.start_frame()
        try:
            yield
        finally:
            self.end_frame()
    
    def start_frame(self) -> None:
        """Start profiling a new frame."""
        if not self._profiling_enabled:
            return
            
        with self._lock:
            self.frame_count += 1
            self._frame_start_time = time.perf_counter()
            start_memory = self._get_memory_usage()
            
            self.current_frame = FrameMemoryData(
                frame_number=self.frame_count,
                timestamp=time.time(),
                allocated_memory=start_memory,
                deallocated_memory=0,
                peak_memory=start_memory,
                gc_collections=self._get_gc_counts(),
                allocation_count=0,
                deallocation_count=0
            )
    
    def end_frame(self) -> None:
        """End profiling the current frame."""
        if not self._profiling_enabled or not self.current_frame:
            return
            
        with self._lock:
            end_memory = self._get_memory_usage()
            frame_duration = time.perf_counter() - self._frame_start_time
            
            self.current_frame.frame_duration = frame_duration
            self.current_frame.deallocated_memory = max(0, self.current_frame.allocated_memory - end_memory)
            self.current_frame.peak_memory = max(self.current_frame.peak_memory, end_memory)
            
            # Check for memory spikes
            if self.frame_history:
                avg_memory = sum(f.peak_memory for f in list(self.frame_history)[-10:]) / min(10, len(self.frame_history))
                spike_size = end_memory - avg_memory
                if spike_size > avg_memory * self.spike_threshold:
                    spike = MemorySpike(
                        frame_number=self.frame_count,
                        spike_size=spike_size,
                        duration=frame_duration,
                        timestamp=time.time()
                    )
                    for callback in self._spike_callbacks:
                        callback(spike)
            
            self.frame_history.append(self.current_frame)
            self.current_frame = None
    
    def start_profiling(self) -> None:
        """Start the profiling session."""
        with self._lock:
            self._profiling_enabled = True
            self._baseline_memory = self._get_memory_usage()
            self.frame_count = 0
            self.frame_history.clear()
    
    def stop_profiling(self) -> None:
        """Stop the profiling session."""
        with self._lock:
            self._profiling_enabled = False
            if self.current_frame:
                self.end_frame()
    
    def add_spike_callback(self, callback: Callable[[MemorySpike], None]) -> None:
        """Add a callback to be called when a memory spike is detected."""
        self._spike_callbacks.append(callback)
    
    def get_frame_stats(self, frame_number: Optional[int] = None) -> Optional[FrameMemoryData]:
        """Get stats for a specific frame or the latest frame."""
        with self._lock:
            if not self.frame_history:
                return None
                
            if frame_number is None:
                return self.frame_history[-1]
                
            for frame in self.frame_history:
                if frame.frame_number == frame_number:
                    return frame
            return None
    
    def get_average_frame_memory(self, last_n_frames: int = 60) -> float:
        """Get average memory usage over the last N frames."""
        with self._lock:
            if not self.frame_history:
                return 0.0
                
            frames = list(self.frame_history)[-last_n_frames:]
            return sum(f.peak_memory for f in frames) / len(frames)
    
    def get_memory_trend(self, window_size: int = 100) -> List[float]:
        """Get memory usage trend over a sliding window."""
        with self._lock:
            if len(self.frame_history) < window_size:
                return []
                
            trend = []
            frames = list(self.frame_history)
            for i in range(len(frames) - window_size + 1):
                window = frames[i:i + window_size]
                avg = sum(f.peak_memory for f in window) / window_size
                trend.append(avg)
            return trend
    
    def get_frame_time_correlation(self) -> Dict[str, List[float]]:
        """Get correlation between frame time and memory usage."""
        with self._lock:
            if not self.frame_history:
                return {"frame_times": [], "memory_usage": []}
                
            frames = list(self.frame_history)
            return {
                "frame_times": [f.frame_duration * 1000 for f in frames],  # Convert to ms
                "memory_usage": [f.peak_memory for f in frames]
            }
    
    def detect_frame_drops(self, target_fps: int = 60) -> List[int]:
        """Detect frames that exceeded target frame time."""
        target_frame_time = 1.0 / target_fps
        
        with self._lock:
            dropped_frames = []
            for frame in self.frame_history:
                if frame.frame_duration > target_frame_time:
                    dropped_frames.append(frame.frame_number)
            return dropped_frames
    
    def get_profiling_overhead(self) -> float:
        """Get the overhead of profiling in milliseconds."""
        # Measure time to profile an empty frame
        start = time.perf_counter()
        with self.frame():
            pass
        return (time.perf_counter() - start) * 1000
    
    def reset(self) -> None:
        """Reset all profiling data."""
        with self._lock:
            self.frame_history.clear()
            self.frame_count = 0
            self.current_frame = None
            self._baseline_memory = self._get_memory_usage()