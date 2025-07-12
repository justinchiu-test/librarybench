"""Import profiler for measuring import times and building performance trees."""

import sys
import time
import importlib
import importlib.util
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import timedelta
from contextlib import contextmanager
from collections import defaultdict
import threading

from .models import ImportMetrics


class ImportProfiler:
    """Profiles import times and builds a performance tree."""

    def __init__(self) -> None:
        self._import_times: Dict[str, float] = {}
        self._import_tree: Dict[str, List[str]] = defaultdict(list)
        self._import_stack: List[str] = []
        self._original_import = None
        self._is_profiling = False
        self._import_depths: Dict[str, int] = {}
        self._import_start_times: Dict[str, float] = {}
        self._lock = threading.Lock()

    def start_profiling(self) -> None:
        """Start profiling imports."""
        if self._is_profiling:
            return

        self._is_profiling = True
        import builtins
        self._original_import = builtins.__import__
        builtins.__import__ = self._profiled_import

    def stop_profiling(self) -> None:
        """Stop profiling imports."""
        if not self._is_profiling:
            return

        self._is_profiling = False
        if self._original_import:
            import builtins
            builtins.__import__ = self._original_import

    @contextmanager
    def profile(self):
        """Context manager for profiling imports."""
        self.start_profiling()
        try:
            yield self
        finally:
            self.stop_profiling()

    def _profiled_import(self, name: str, *args, **kwargs) -> Any:
        """Wrapper around __import__ to measure timing."""
        with self._lock:
            start_time = time.perf_counter()
            parent = self._import_stack[-1] if self._import_stack else None
            
            self._import_stack.append(name)
            self._import_depths[name] = len(self._import_stack) - 1
            self._import_start_times[name] = start_time
            
            if parent:
                self._import_tree[parent].append(name)

        try:
            result = self._original_import(name, *args, **kwargs)
        finally:
            with self._lock:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                
                if name in self._import_times:
                    self._import_times[name] += elapsed
                else:
                    self._import_times[name] = elapsed
                
                self._import_stack.pop()

        return result

    def get_import_metrics(self) -> List[ImportMetrics]:
        """Get detailed import metrics for all profiled modules."""
        metrics = []
        
        cumulative_times = self._calculate_cumulative_times()
        bottlenecks = self._identify_bottlenecks(cumulative_times)
        
        for module_name, import_time in self._import_times.items():
            metrics.append(ImportMetrics(
                module_name=module_name,
                import_time=timedelta(seconds=import_time),
                cumulative_time=timedelta(seconds=cumulative_times.get(module_name, import_time)),
                parent_module=self._find_parent(module_name),
                children=self._import_tree.get(module_name, []),
                is_bottleneck=module_name in bottlenecks,
                import_depth=self._import_depths.get(module_name, 0)
            ))
        
        return sorted(metrics, key=lambda m: m.cumulative_time, reverse=True)

    def _calculate_cumulative_times(self) -> Dict[str, float]:
        """Calculate cumulative times including all dependencies."""
        cumulative_times = {}
        
        def calculate_time(module: str, visited: Set[str]) -> float:
            if module in cumulative_times:
                return cumulative_times[module]
            
            if module in visited:
                return 0.0
            
            visited.add(module)
            time = self._import_times.get(module, 0.0)
            
            for child in self._import_tree.get(module, []):
                time += calculate_time(child, visited.copy())
            
            cumulative_times[module] = time
            return time
        
        for module in self._import_times:
            calculate_time(module, set())
        
        return cumulative_times

    def _identify_bottlenecks(self, cumulative_times: Dict[str, float], 
                            threshold_percentile: float = 0.8) -> Set[str]:
        """Identify modules that are bottlenecks."""
        if not cumulative_times:
            return set()
        
        sorted_times = sorted(cumulative_times.values(), reverse=True)
        threshold_index = int(len(sorted_times) * (1 - threshold_percentile))
        threshold_time = sorted_times[threshold_index] if threshold_index < len(sorted_times) else 0
        
        return {module for module, time in cumulative_times.items() 
                if time >= threshold_time}

    def _find_parent(self, module: str) -> Optional[str]:
        """Find the parent module that imported this module."""
        for parent, children in self._import_tree.items():
            if module in children:
                return parent
        return None

    def get_slowest_imports(self, top_n: int = 10) -> List[Tuple[str, timedelta]]:
        """Get the slowest importing modules."""
        sorted_imports = sorted(self._import_times.items(), 
                              key=lambda x: x[1], reverse=True)
        return [(name, timedelta(seconds=time)) 
                for name, time in sorted_imports[:top_n]]

    def get_import_tree_visualization(self) -> str:
        """Get a text visualization of the import tree."""
        lines = []
        
        def build_tree(module: str, indent: int = 0, path: List[str] = None) -> None:
            if path is None:
                path = []
            
            if module in path:
                lines.append("  " * indent + f"{module} (circular)")
                return
            
            path = path + [module]
            time = self._import_times.get(module, 0.0)
            lines.append("  " * indent + f"{module} ({time:.3f}s)")
            
            for child in sorted(self._import_tree.get(module, [])):
                build_tree(child, indent + 1, path)
        
        root_modules = set(self._import_times.keys()) - set(
            child for children in self._import_tree.values() for child in children
        )
        
        # If no root modules, just start with all modules
        if not root_modules:
            root_modules = set(self._import_times.keys())
        
        for module in sorted(root_modules):
            build_tree(module)
        
        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all profiling data."""
        with self._lock:
            self._import_times.clear()
            self._import_tree.clear()
            self._import_stack.clear()
            self._import_depths.clear()
            self._import_start_times.clear()