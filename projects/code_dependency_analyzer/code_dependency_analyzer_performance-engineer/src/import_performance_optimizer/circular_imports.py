"""Circular import detection and performance impact analysis."""

import sys
import time
import importlib
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import timedelta
from collections import defaultdict, deque

from .models import CircularImportInfo


class CircularImportAnalyzer:
    """Detects circular imports and measures their performance impact."""

    def __init__(self) -> None:
        self._import_graph: Dict[str, Set[str]] = defaultdict(set)
        self._circular_imports: List[List[str]] = []
        self._import_times: Dict[str, float] = {}
        self._import_memory: Dict[str, int] = {}
        self._import_stack: List[str] = []
        self._visited_modules: Set[str] = set()

    def build_import_graph(self, root_module: str) -> None:
        """Build the import dependency graph starting from a root module."""
        self._import_graph.clear()
        self._circular_imports.clear()
        self._visited_modules.clear()
        
        self._analyze_module_imports(root_module)
        self._detect_circular_imports()

    def _analyze_module_imports(self, module_name: str) -> None:
        """Recursively analyze module imports."""
        if module_name in self._visited_modules:
            return
        
        self._visited_modules.add(module_name)
        
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = importlib.import_module(module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name, None)
                if hasattr(attr, '__module__'):
                    imported_module = attr.__module__
                    if imported_module and imported_module != module_name:
                        self._import_graph[module_name].add(imported_module)
                        
                        if imported_module not in self._visited_modules:
                            self._analyze_module_imports(imported_module)
        except Exception:
            pass

    def _detect_circular_imports(self) -> None:
        """Detect all circular import cycles in the graph."""
        visited = set()
        rec_stack = set()
        cycles_found = set()
        
        def dfs(module: str, path: List[str]) -> None:
            if module in rec_stack:
                # Found a cycle
                cycle_start_idx = path.index(module)
                cycle = path[cycle_start_idx:] + [module]
                # Normalize cycle to start with the smallest module name
                min_module = min(cycle[:-1])  # Exclude the repeated module
                min_idx = cycle[:-1].index(min_module)
                normalized_cycle = cycle[min_idx:-1] + cycle[:min_idx+1]
                
                # Create a hashable key for deduplication
                cycle_key = tuple(sorted(cycle[:-1]))
                if cycle_key not in cycles_found:
                    cycles_found.add(cycle_key)
                    self._circular_imports.append(normalized_cycle)
                return
            
            if module in visited:
                return
            
            visited.add(module)
            rec_stack.add(module)
            path.append(module)
            
            for dependency in self._import_graph.get(module, []):
                dfs(dependency, path.copy())
            
            path.pop()
            rec_stack.remove(module)
        
        for module in self._import_graph:
            if module not in visited:
                dfs(module, [])

    def measure_circular_import_impact(self, 
                                     import_times: Optional[Dict[str, float]] = None,
                                     memory_usage: Optional[Dict[str, int]] = None) -> List[CircularImportInfo]:
        """Measure the performance impact of circular imports."""
        if import_times:
            self._import_times = import_times
        if memory_usage:
            self._import_memory = memory_usage
        
        circular_infos = []
        
        for cycle in self._circular_imports:
            impact_time = self._calculate_time_impact(cycle)
            memory_overhead = self._calculate_memory_overhead(cycle)
            severity = self._determine_severity(impact_time, memory_overhead, len(cycle))
            
            circular_infos.append(CircularImportInfo(
                modules_involved=cycle,
                performance_impact=timedelta(seconds=impact_time),
                memory_overhead=memory_overhead,
                import_chain=self._build_import_chain(cycle),
                severity=severity
            ))
        
        return sorted(circular_infos, 
                     key=lambda x: (self._severity_score(x.severity), x.performance_impact),
                     reverse=True)

    def _calculate_time_impact(self, cycle: List[str]) -> float:
        """Calculate the time impact of a circular import cycle."""
        total_time = 0.0
        overhead_factor = 1.2  # 20% overhead for circular dependencies
        
        for module in cycle:
            module_time = self._import_times.get(module, 0.0)
            total_time += module_time
        
        return total_time * (overhead_factor - 1)

    def _calculate_memory_overhead(self, cycle: List[str]) -> int:
        """Calculate the memory overhead of a circular import cycle."""
        total_memory = 0
        overhead_factor = 1.1  # 10% overhead for circular references
        
        for module in cycle:
            module_memory = self._import_memory.get(module, 0)
            total_memory += module_memory
        
        return int(total_memory * (overhead_factor - 1))

    def _determine_severity(self, time_impact: float, memory_overhead: int, 
                          cycle_length: int) -> str:
        """Determine the severity of a circular import."""
        score = 0
        
        if time_impact > 1.0:
            score += 3
        elif time_impact > 0.5:
            score += 2
        elif time_impact > 0.1:
            score += 1
        
        if memory_overhead > 10 * 1024 * 1024:  # 10MB
            score += 3
        elif memory_overhead > 5 * 1024 * 1024:  # 5MB
            score += 2
        elif memory_overhead > 1 * 1024 * 1024:  # 1MB
            score += 1
        
        if cycle_length > 5:
            score += 2
        elif cycle_length > 3:
            score += 1
        
        if score >= 6:
            return "critical"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"

    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting."""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(severity, 0)

    def _build_import_chain(self, cycle: List[str]) -> List[str]:
        """Build a readable import chain for the cycle."""
        chain = []
        for i, module in enumerate(cycle):
            next_module = cycle[(i + 1) % len(cycle)]
            chain.append(f"{module} -> {next_module}")
        return chain

    def find_all_circular_paths(self, start_module: str, 
                               end_module: str) -> List[List[str]]:
        """Find all circular import paths between two modules."""
        paths = []
        
        def find_paths(current: str, target: str, path: List[str], 
                      visited: Set[str]) -> None:
            if current == target and len(path) > 1:
                paths.append(path + [current])
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            for next_module in self._import_graph.get(current, []):
                if next_module not in visited or next_module == target:
                    find_paths(next_module, target, path + [current], visited.copy())
        
        find_paths(start_module, end_module, [], set())
        return paths

    def get_refactoring_suggestions(self, circular_info: CircularImportInfo) -> List[str]:
        """Generate refactoring suggestions for circular imports."""
        suggestions = []
        modules = circular_info.modules_involved
        
        suggestions.append(
            f"Consider moving shared dependencies from {modules[0]} and {modules[-1]} "
            f"to a separate common module"
        )
        
        if len(modules) > 3:
            suggestions.append(
                f"This circular dependency involves {len(modules)} modules. "
                f"Consider using dependency injection or interfaces to break the cycle"
            )
        
        suggestions.append(
            "Use conditional imports (inside functions) for imports that are only "
            "needed in specific code paths"
        )
        
        if circular_info.severity in ["high", "critical"]:
            suggestions.append(
                "URGENT: This circular import has significant performance impact. "
                "Consider immediate refactoring"
            )
        
        return suggestions

    def get_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of circular imports."""
        circular_infos = self.measure_circular_import_impact()
        
        total_cycles = len(circular_infos)
        critical_cycles = sum(1 for info in circular_infos if info.severity == "critical")
        high_cycles = sum(1 for info in circular_infos if info.severity == "high")
        
        total_time_impact = sum(
            info.performance_impact.total_seconds() 
            for info in circular_infos
        )
        
        total_memory_overhead = sum(
            info.memory_overhead 
            for info in circular_infos
        )
        
        return {
            "total_circular_imports": total_cycles,
            "critical_severity_count": critical_cycles,
            "high_severity_count": high_cycles,
            "total_time_impact_seconds": total_time_impact,
            "total_memory_overhead_bytes": total_memory_overhead,
            "most_problematic_cycles": circular_infos[:5],
            "summary": f"Found {total_cycles} circular imports "
                      f"({critical_cycles} critical, {high_cycles} high severity) "
                      f"with {total_time_impact:.2f}s total impact"
        }