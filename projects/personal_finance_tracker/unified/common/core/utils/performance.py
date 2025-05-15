"""Performance monitoring utilities shared across implementations."""

import time
import functools
import statistics
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast
from datetime import datetime

F = TypeVar('F', bound=Callable[..., Any])


class Timer:
    """Utility for measuring execution time."""
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize the timer.
        
        Args:
            name: Optional name for the timer
        """
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __enter__(self) -> 'Timer':
        """Start the timer when entering a context."""
        self.start()
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Stop the timer when exiting a context."""
        self.stop()
    
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self) -> float:
        """
        Stop the timer.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise ValueError("Timer has not been started")
        
        self.end_time = time.time()
        return self.elapsed_time
    
    @property
    def elapsed_time(self) -> float:
        """
        Get the elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise ValueError("Timer has not been started")
        
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time
    
    @property
    def elapsed_milliseconds(self) -> float:
        """
        Get the elapsed time in milliseconds.
        
        Returns:
            Elapsed time in milliseconds
        """
        return self.elapsed_time * 1000


class PerformanceMonitor:
    """
    Monitor for tracking performance metrics of function calls.
    
    Tracks execution times, counts, and statistics for functions.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self._metrics: Dict[str, List[float]] = {}
        self._call_counts: Dict[str, int] = {}
        self._start_times: Dict[str, float] = {}
    
    def start(self, name: str) -> None:
        """
        Start timing a named operation.
        
        Args:
            name: Name of the operation
        """
        self._start_times[name] = time.time()
    
    def stop(self, name: str) -> float:
        """
        Stop timing a named operation and record the elapsed time.
        
        Args:
            name: Name of the operation
            
        Returns:
            Elapsed time in seconds
        """
        if name not in self._start_times:
            raise ValueError(f"No timing started for {name}")
        
        elapsed_time = time.time() - self._start_times[name]
        del self._start_times[name]
        
        # Record the metric
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(elapsed_time)
        
        # Update call count
        self._call_counts[name] = self._call_counts.get(name, 0) + 1
        
        return elapsed_time
    
    def record(self, name: str, value: float) -> None:
        """
        Record a metric value directly.
        
        Args:
            name: Name of the metric
            value: Value to record
        """
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)
        
        # Update call count
        self._call_counts[name] = self._call_counts.get(name, 0) + 1
    
    def get_metrics(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a named metric.
        
        Args:
            name: Name of the metric
            
        Returns:
            Dictionary with statistics
        """
        if name not in self._metrics:
            return {}
        
        values = self._metrics[name]
        
        if not values:
            return {"count": 0}
        
        # Calculate statistics
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "total": sum(values),
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all metrics.
        
        Returns:
            Dictionary mapping metric names to statistics
        """
        return {name: self.get_metrics(name) for name in self._metrics}
    
    def reset(self, name: Optional[str] = None) -> None:
        """
        Reset metrics.
        
        Args:
            name: Name of the metric to reset, or None to reset all
        """
        if name is None:
            # Reset all metrics
            self._metrics = {}
            self._call_counts = {}
            self._start_times = {}
        else:
            # Reset specific metric
            if name in self._metrics:
                del self._metrics[name]
            if name in self._call_counts:
                del self._call_counts[name]
            if name in self._start_times:
                del self._start_times[name]


def time_it(func: F) -> F:
    """
    Decorator to time function execution.
    
    Args:
        func: The function to time
        
    Returns:
        Wrapped function that logs timing information
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed_time = time.time() - start_time
            func_name = func.__qualname__
            print(f"{func_name} took {elapsed_time:.6f} seconds")
    
    return cast(F, wrapper)


def monitor_performance(
    monitor: PerformanceMonitor, name: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator to monitor function performance.
    
    Args:
        monitor: PerformanceMonitor instance
        name: Optional name for the metric (defaults to function name)
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        metric_name = name or func.__qualname__
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            monitor.start(metric_name)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.stop(metric_name)
        
        return cast(F, wrapper)
    
    return decorator


# Global performance monitor for convenience
global_monitor = PerformanceMonitor()


def global_timer(name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to time function with the global monitor.
    
    Args:
        name: Optional name for the metric (defaults to function name)
        
    Returns:
        Decorator function
    """
    return monitor_performance(global_monitor, name)