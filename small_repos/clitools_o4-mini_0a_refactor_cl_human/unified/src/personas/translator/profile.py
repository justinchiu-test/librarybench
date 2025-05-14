"""
Profiler for translation operations.
Measures and reports performance metrics for translation workflows.
"""

import time
import functools
import json
import os
from typing import Any, Callable, Dict, List, Optional, Union


class Profiler:
    """
    Measures and tracks performance of translation operations.
    Provides detailed timing information for optimization.
    """
    
    def __init__(self, 
                enabled: bool = True,
                output_file: Optional[str] = None,
                print_summary: bool = False):
        """
        Initialize a new profiler.
        
        Args:
            enabled: Whether profiling is enabled
            output_file: File to output profile data to
            print_summary: Whether to print summary after profiling
        """
        self.enabled = enabled
        self.output_file = output_file
        self.print_summary = print_summary
        self.active = False
        
        # Metrics storage
        self.timings: Dict[str, List[float]] = {}
        self.call_counts: Dict[str, int] = {}
        self.start_times: Dict[str, float] = {}
        
        # For nested operations
        self.operation_stack: List[str] = []
    
    def start(self, operation: str) -> None:
        """
        Start timing an operation.
        
        Args:
            operation: Name of the operation to time
        """
        if not self.enabled:
            return
        
        self.active = True
        
        # Push to operation stack
        self.operation_stack.append(operation)
        
        # Record start time
        self.start_times[operation] = time.time()
        
        # Initialize metrics if needed
        if operation not in self.timings:
            self.timings[operation] = []
        if operation not in self.call_counts:
            self.call_counts[operation] = 0
    
    def stop(self, operation: Optional[str] = None) -> float:
        """
        Stop timing an operation and record metrics.
        
        Args:
            operation: Name of the operation (None for current operation)
            
        Returns:
            Time elapsed in seconds
        """
        if not self.enabled or not self.active:
            return 0.0
        
        # If no operation specified, use the current one
        if operation is None:
            if not self.operation_stack:
                return 0.0
            operation = self.operation_stack.pop()
        elif operation in self.operation_stack:
            # Remove from stack if found
            self.operation_stack.remove(operation)
        else:
            # Operation not started, ignore
            return 0.0
        
        # Check if we have a start time
        if operation not in self.start_times:
            return 0.0
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_times[operation]
        
        # Record metrics
        self.timings[operation].append(elapsed)
        self.call_counts[operation] += 1
        
        # Clean up
        del self.start_times[operation]
        
        # If operation stack is empty, not active anymore
        if not self.operation_stack:
            self.active = False
        
        return elapsed
    
    def reset(self) -> None:
        """Reset all profiling data."""
        self.timings.clear()
        self.call_counts.clear()
        self.start_times.clear()
        self.operation_stack.clear()
        self.active = False
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get profiling statistics.
        
        Returns:
            Dictionary of operation statistics
        """
        stats = {}
        
        for operation, times in self.timings.items():
            if not times:
                continue
                
            count = self.call_counts.get(operation, 0)
            total = sum(times)
            avg = total / count if count > 0 else 0
            
            stats[operation] = {
                'count': count,
                'total': total,
                'average': avg,
                'min': min(times) if times else 0,
                'max': max(times) if times else 0
            }
        
        return stats
    
    def print_stats(self) -> None:
        """Print profiling statistics."""
        stats = self.get_stats()
        
        if not stats:
            print("No profiling data available")
            return
        
        print("\nProfiling Statistics:")
        print("-" * 80)
        print(f"{'Operation':<30} {'Count':>10} {'Total':>10} {'Avg':>10} {'Min':>10} {'Max':>10}")
        print("-" * 80)
        
        for operation, data in sorted(stats.items()):
            print(f"{operation:<30} {data['count']:>10d} {data['total']:>10.6f} {data['average']:>10.6f} {data['min']:>10.6f} {data['max']:>10.6f}")
        
        print("-" * 80)
    
    def save_stats(self, output_file: Optional[str] = None) -> bool:
        """
        Save profiling statistics to a file.
        
        Args:
            output_file: File to save to (default: self.output_file)
            
        Returns:
            True if saved successfully, False otherwise
        """
        file_path = output_file or self.output_file
        if not file_path:
            return False
        
        try:
            stats = self.get_stats()
            
            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write stats to file
            with open(file_path, 'w') as f:
                json.dump(stats, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving profiling stats: {e}")
            return False
    
    def __enter__(self) -> 'Profiler':
        """Context manager entry."""
        # Use a generic operation name for context manager
        self.start("__context__")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop("__context__")
        
        # Print summary if requested
        if self.print_summary:
            self.print_stats()
        
        # Save to file if specified
        if self.output_file:
            self.save_stats()


def profile(func: Optional[Callable] = None, operation: Optional[str] = None, profiler: Optional[Profiler] = None) -> Callable:
    """
    Decorator for profiling functions.
    
    Args:
        func: Function to profile
        operation: Custom operation name (default: function name)
        profiler: Custom profiler to use (default: global profiler)
        
    Returns:
        Decorated function
    """
    # Allow for both @profile and @profile(...)
    if func is None:
        return lambda f: profile(f, operation, profiler)
    
    # Use global profiler if none provided
    if profiler is None:
        profiler = _global_profiler
    
    # Use function name if no operation specified
    op_name = operation or func.__qualname__
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler.start(op_name)
        try:
            return func(*args, **kwargs)
        finally:
            profiler.stop(op_name)
            
    return wrapper


# Create a global profiler for convenience
_global_profiler = Profiler()

def start(operation: str) -> None:
    """Start profiling an operation using the global profiler."""
    _global_profiler.start(operation)

def stop(operation: Optional[str] = None) -> float:
    """Stop profiling an operation using the global profiler."""
    return _global_profiler.stop(operation)

def reset() -> None:
    """Reset the global profiler."""
    _global_profiler.reset()

def get_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics from the global profiler."""
    return _global_profiler.get_stats()

def print_stats() -> None:
    """Print statistics from the global profiler."""
    _global_profiler.print_stats()

def save_stats(output_file: str) -> bool:
    """Save statistics from the global profiler."""
    return _global_profiler.save_stats(output_file)

def configure(enabled: bool = True, output_file: Optional[str] = None, print_summary: bool = False) -> None:
    """Configure the global profiler."""
    global _global_profiler
    _global_profiler = Profiler(enabled, output_file, print_summary)