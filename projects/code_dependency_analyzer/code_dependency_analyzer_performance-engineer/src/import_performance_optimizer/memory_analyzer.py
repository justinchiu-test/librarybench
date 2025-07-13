"""Memory footprint analyzer for imported modules."""

import sys
import gc
import psutil
import importlib
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict

from .models import MemoryFootprint


class MemoryAnalyzer:
    """Analyzes memory footprint of imported modules and their dependencies."""

    def __init__(self) -> None:
        self._baseline_memory: Optional[int] = None
        self._module_memory: Dict[str, int] = {}
        self._import_tree: Dict[str, List[str]] = defaultdict(list)
        self._process = psutil.Process()

    def start_analysis(self) -> None:
        """Start memory analysis by recording baseline memory."""
        gc.collect()
        self._baseline_memory = self._get_current_memory()
        self._module_memory.clear()
        self._import_tree.clear()

    def _get_current_memory(self) -> int:
        """Get current memory usage in bytes."""
        return self._process.memory_info().rss

    def measure_module_memory(self, module_name: str) -> int:
        """Measure memory footprint of a specific module."""
        # If already measured, return the cached value
        if module_name in self._module_memory:
            return self._module_memory[module_name]
            
        gc.collect()
        before_memory = self._get_current_memory()

        try:
            if module_name not in sys.modules:
                importlib.import_module(module_name)
            gc.collect()
            after_memory = self._get_current_memory()
            
            memory_used = max(0, after_memory - before_memory)
            self._module_memory[module_name] = memory_used
            
            self._analyze_submodules(module_name)
            
            return memory_used
        except ImportError:
            return 0

    def _analyze_submodules(self, module_name: str) -> None:
        """Analyze memory usage of submodules."""
        if module_name not in sys.modules:
            return

        module = sys.modules[module_name]
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name, None)
            if hasattr(attr, '__module__') and attr.__module__ != module_name:
                submodule_name = attr.__module__
                if submodule_name and submodule_name not in self._module_memory:
                    self._import_tree[module_name].append(submodule_name)

    def get_memory_footprints(self, modules: Optional[List[str]] = None) -> List[MemoryFootprint]:
        """Get memory footprint information for modules."""
        if modules is None:
            modules = list(self._module_memory.keys())

        footprints = []
        cumulative_memory = self._calculate_cumulative_memory()
        total_memory = sum(self._module_memory.values())

        for module_name in modules:
            direct_memory = self._module_memory.get(module_name, 0)
            cumulative = cumulative_memory.get(module_name, direct_memory)
            
            memory_by_child = {}
            for child in self._import_tree.get(module_name, []):
                memory_by_child[child] = self._module_memory.get(child, 0)

            percentage = (cumulative / total_memory * 100) if total_memory > 0 else 0

            footprints.append(MemoryFootprint(
                module_name=module_name,
                direct_memory=direct_memory,
                cumulative_memory=cumulative,
                memory_by_child=memory_by_child,
                percentage_of_total=percentage
            ))

        return sorted(footprints, key=lambda f: f.cumulative_memory, reverse=True)

    def _calculate_cumulative_memory(self) -> Dict[str, int]:
        """Calculate cumulative memory including all dependencies."""
        cumulative_memory = {}
        
        # Use iterative approach to avoid deep recursion
        def calculate_memory_iterative(start_module: str) -> int:
            if start_module in cumulative_memory:
                return cumulative_memory[start_module]
                
            stack = [(start_module, False)]
            temp_results = {}
            visited_in_path = set()
            
            while stack:
                module, processed = stack.pop()
                
                if processed:
                    # Calculate cumulative memory for this module
                    memory = self._module_memory.get(module, 0)
                    for child in self._import_tree.get(module, []):
                        if child in temp_results:
                            memory += temp_results[child]
                    temp_results[module] = memory
                    cumulative_memory[module] = memory
                    visited_in_path.discard(module)
                else:
                    if module in cumulative_memory:
                        continue
                    if module in visited_in_path:
                        # Circular dependency, use direct memory only
                        temp_results[module] = self._module_memory.get(module, 0)
                        cumulative_memory[module] = temp_results[module]
                        continue
                        
                    visited_in_path.add(module)
                    stack.append((module, True))
                    
                    # Add children to stack
                    for child in self._import_tree.get(module, []):
                        if child not in cumulative_memory:
                            stack.append((child, False))
            
            return cumulative_memory.get(start_module, 0)
        
        for module in self._module_memory:
            calculate_memory_iterative(module)
        
        return cumulative_memory

    def identify_memory_heavy_branches(self, threshold_mb: float = 10.0) -> List[Tuple[str, int]]:
        """Identify dependency branches consuming significant memory."""
        threshold_bytes = int(threshold_mb * 1024 * 1024)
        cumulative_memory = self._calculate_cumulative_memory()
        
        heavy_branches = [
            (module, memory) 
            for module, memory in cumulative_memory.items()
            if memory >= threshold_bytes
        ]
        
        return sorted(heavy_branches, key=lambda x: x[1], reverse=True)

    def get_memory_tree_visualization(self) -> str:
        """Get a text visualization of memory usage tree."""
        lines = []
        visited = set()

        def format_bytes(bytes_value: int) -> str:
            """Format bytes to human readable format."""
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.2f} TB"

        def build_tree(module: str, indent: int = 0) -> None:
            if module in visited:
                lines.append("  " * indent + f"{module} (circular)")
                return

            visited.add(module)
            memory = self._module_memory.get(module, 0)
            lines.append("  " * indent + f"{module} ({format_bytes(memory)})")

            for child in sorted(self._import_tree.get(module, [])):
                build_tree(child, indent + 1)

        root_modules = set(self._module_memory.keys()) - set(
            child for children in self._import_tree.values() for child in children
        )

        for module in sorted(root_modules):
            build_tree(module)

        return "\n".join(lines)

    def get_optimization_opportunities(self) -> Dict[str, Any]:
        """Identify memory optimization opportunities."""
        opportunities = {
            "large_modules": [],
            "duplicate_imports": [],
            "unused_imports": [],
            "total_potential_savings": 0
        }

        cumulative_memory = self._calculate_cumulative_memory()
        
        for module, memory in self._module_memory.items():
            if memory > 5 * 1024 * 1024:  # 5MB
                opportunities["large_modules"].append({
                    "module": module,
                    "direct_memory": memory,
                    "cumulative_memory": cumulative_memory.get(module, memory)
                })

        import_counts = defaultdict(int)
        for children in self._import_tree.values():
            for child in children:
                import_counts[child] += 1

        for module, count in import_counts.items():
            if count > 1:
                memory = self._module_memory.get(module, 0)
                opportunities["duplicate_imports"].append({
                    "module": module,
                    "import_count": count,
                    "memory_per_import": memory,
                    "potential_savings": memory * (count - 1)
                })
                opportunities["total_potential_savings"] += memory * (count - 1)

        return opportunities