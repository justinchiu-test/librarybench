"""Performance Regression Tracker for comparing performance metrics across code versions."""

import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .complexity_analyzer import ComplexityAnalyzer, ComplexityClass, ComplexityResult


class RegressionType(Enum):
    """Types of performance regressions."""
    
    COMPLEXITY_INCREASE = "Complexity Increased"
    NEW_INEFFICIENCY = "New Inefficiency Introduced"
    REMOVED_OPTIMIZATION = "Optimization Removed"
    RESOURCE_USAGE_INCREASE = "Resource Usage Increased"
    CONCURRENCY_DEGRADATION = "Concurrency Performance Degraded"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a function."""
    
    function_name: str
    module_path: str
    time_complexity: str
    space_complexity: str
    loop_depth: int
    is_recursive: bool
    has_database_ops: bool
    has_concurrency: bool
    line_count: int
    cyclomatic_complexity: int
    memory_allocations: int
    function_hash: str
    timestamp: str


@dataclass
class PerformanceRegression:
    """Represents a detected performance regression."""
    
    regression_type: RegressionType
    function_name: str
    module_path: str
    old_metrics: PerformanceMetrics
    new_metrics: PerformanceMetrics
    severity: str  # "high", "medium", "low"
    description: str
    recommendation: str
    impact_estimate: Optional[str] = None


class PerformanceRegressionTracker:
    """Tracks performance metrics over time and identifies regressions."""
    
    def __init__(self, baseline_file: Optional[str] = None):
        self.baseline_file = baseline_file or ".performance_baseline.json"
        self.baseline_metrics: Dict[str, PerformanceMetrics] = {}
        self.current_metrics: Dict[str, PerformanceMetrics] = {}
        self._load_baseline()
    
    def analyze_codebase(self, directory: str) -> List[PerformanceRegression]:
        """Analyze entire codebase and compare with baseline.
        
        Args:
            directory: Root directory of codebase to analyze
            
        Returns:
            List of detected performance regressions
        """
        # Collect current metrics
        self.current_metrics.clear()
        self._collect_metrics(directory)
        
        # Compare with baseline
        regressions = self._compare_metrics()
        
        return regressions
    
    def update_baseline(self, directory: str) -> None:
        """Update the performance baseline with current metrics.
        
        Args:
            directory: Root directory of codebase to analyze
        """
        self.current_metrics.clear()
        self._collect_metrics(directory)
        self.baseline_metrics = self.current_metrics.copy()
        self._save_baseline()
    
    def get_performance_trends(self, function_name: str) -> Dict[str, Any]:
        """Get performance trend data for a specific function.
        
        Args:
            function_name: Name of the function to get trends for
            
        Returns:
            Dictionary containing trend information
        """
        # Check both exact name and module::name patterns
        baseline_key = None
        current_key = None
        
        for key in self.baseline_metrics:
            if key.endswith(f"::{function_name}") or key == function_name:
                baseline_key = key
                break
        
        for key in self.current_metrics:
            if key.endswith(f"::{function_name}") or key == function_name:
                current_key = key
                break
        
        trends = {
            'function_name': function_name,
            'has_baseline': baseline_key is not None,
            'has_current': current_key is not None,
        }
        
        if baseline_key:
            baseline = self.baseline_metrics[baseline_key]
            trends['baseline'] = {
                'time_complexity': baseline.time_complexity,
                'space_complexity': baseline.space_complexity,
                'timestamp': baseline.timestamp,
            }
        
        if current_key:
            current = self.current_metrics[current_key]
            trends['current'] = {
                'time_complexity': current.time_complexity,
                'space_complexity': current.space_complexity,
                'timestamp': current.timestamp,
            }
        
        return trends
    
    def _collect_metrics(self, directory: str) -> None:
        """Collect performance metrics from all Python files in directory."""
        path = Path(directory)
        complexity_analyzer = ComplexityAnalyzer()
        
        for py_file in path.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            
            try:
                module_path = str(py_file.relative_to(path))
                
                # Analyze complexity
                complexity_results = complexity_analyzer.analyze_file(str(py_file))
                
                # Analyze other metrics
                with open(py_file, 'r') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                
                # Collect metrics for each function
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        metrics = self._extract_function_metrics(
                            node, module_path, complexity_results, source
                        )
                        key = f"{module_path}::{metrics.function_name}"
                        self.current_metrics[key] = metrics
            
            except Exception:
                # Skip files that can't be analyzed
                continue
    
    def _extract_function_metrics(
        self,
        node: ast.FunctionDef,
        module_path: str,
        complexity_results: List[ComplexityResult],
        source: str
    ) -> PerformanceMetrics:
        """Extract performance metrics for a function."""
        # Find matching complexity result
        complexity_result = next(
            (r for r in complexity_results if r.function_name == node.name),
            None
        )
        
        # If no complexity result, analyze this function directly
        if not complexity_result:
            from .complexity_analyzer import ComplexityAnalyzer
            temp_analyzer = ComplexityAnalyzer()
            temp_results = temp_analyzer._analyze_function(node, {node.name: node})
            if temp_results:
                complexity_result = temp_results
        
        # Calculate additional metrics
        analyzer = FunctionMetricsAnalyzer()
        analyzer.visit(node)
        
        # Generate function hash
        function_source = ast.unparse(node) if hasattr(ast, 'unparse') else ""
        function_hash = hashlib.md5(function_source.encode()).hexdigest()[:8]
        
        return PerformanceMetrics(
            function_name=node.name,
            module_path=module_path,
            time_complexity=complexity_result.time_complexity.value if complexity_result else "O(1)",
            space_complexity=complexity_result.space_complexity.value if complexity_result else "O(1)",
            loop_depth=complexity_result.loop_depth if complexity_result else 0,
            is_recursive=complexity_result.recursive if complexity_result else False,
            has_database_ops=analyzer.has_database_ops,
            has_concurrency=analyzer.has_concurrency,
            line_count=node.end_lineno - node.lineno + 1 if node.end_lineno else 1,
            cyclomatic_complexity=analyzer.cyclomatic_complexity,
            memory_allocations=analyzer.memory_allocations,
            function_hash=function_hash,
            timestamp=datetime.now().isoformat()
        )
    
    def _compare_metrics(self) -> List[PerformanceRegression]:
        """Compare current metrics with baseline to find regressions."""
        regressions = []
        
        # Check for complexity increases
        for key, current in self.current_metrics.items():
            if key in self.baseline_metrics:
                baseline = self.baseline_metrics[key]
                
                # Compare complexity classes
                if self._is_complexity_worse(baseline.time_complexity, current.time_complexity):
                    regressions.append(PerformanceRegression(
                        regression_type=RegressionType.COMPLEXITY_INCREASE,
                        function_name=current.function_name,
                        module_path=current.module_path,
                        old_metrics=baseline,
                        new_metrics=current,
                        severity="high",
                        description=f"Time complexity increased from {baseline.time_complexity} to {current.time_complexity}",
                        recommendation="Review algorithm changes and optimize if possible",
                        impact_estimate=self._estimate_impact(baseline.time_complexity, current.time_complexity)
                    ))
                
                # Check for new inefficiencies
                if not baseline.has_database_ops and current.has_database_ops:
                    regressions.append(PerformanceRegression(
                        regression_type=RegressionType.NEW_INEFFICIENCY,
                        function_name=current.function_name,
                        module_path=current.module_path,
                        old_metrics=baseline,
                        new_metrics=current,
                        severity="medium",
                        description="Database operations added to function",
                        recommendation="Ensure database queries are optimized and necessary"
                    ))
                
                # Check for increased loop depth
                if current.loop_depth > baseline.loop_depth:
                    regressions.append(PerformanceRegression(
                        regression_type=RegressionType.COMPLEXITY_INCREASE,
                        function_name=current.function_name,
                        module_path=current.module_path,
                        old_metrics=baseline,
                        new_metrics=current,
                        severity="medium",
                        description=f"Loop nesting increased from {baseline.loop_depth} to {current.loop_depth}",
                        recommendation="Consider refactoring to reduce nested loops"
                    ))
                
                # Check for concurrency degradation
                if baseline.has_concurrency and not current.has_concurrency:
                    regressions.append(PerformanceRegression(
                        regression_type=RegressionType.CONCURRENCY_DEGRADATION,
                        function_name=current.function_name,
                        module_path=current.module_path,
                        old_metrics=baseline,
                        new_metrics=current,
                        severity="medium",
                        description="Concurrent execution capability removed",
                        recommendation="Consider if parallelization can be restored"
                    ))
        
        # Check for removed optimizations
        for key, baseline in self.baseline_metrics.items():
            if key not in self.current_metrics:
                # Function was removed - this might be okay
                continue
        
        return regressions
    
    def _is_complexity_worse(self, old: str, new: str) -> bool:
        """Check if new complexity is worse than old."""
        complexity_order = {
            "O(1)": 1,
            "O(log n)": 2,
            "O(n)": 3,
            "O(n log n)": 4,
            "O(n^2)": 5,
            "O(n^3)": 6,
            "O(2^n)": 7,
            "O(n!)": 8,
        }
        
        old_rank = complexity_order.get(old, 0)
        new_rank = complexity_order.get(new, 0)
        
        return new_rank > old_rank
    
    def _estimate_impact(self, old_complexity: str, new_complexity: str) -> str:
        """Estimate performance impact of complexity change."""
        impact_map = {
            ("O(1)", "O(n)"): "Linear slowdown with data size",
            ("O(1)", "O(n^2)"): "Quadratic slowdown - severe impact on large datasets",
            ("O(n)", "O(n^2)"): "Performance degrades from linear to quadratic",
            ("O(n)", "O(n log n)"): "Moderate slowdown, typically acceptable",
            ("O(n log n)", "O(n^2)"): "Significant performance degradation",
            ("O(n^2)", "O(n^3)"): "Severe performance impact - review immediately",
        }
        
        return impact_map.get((old_complexity, new_complexity), "Performance impact varies with input size")
    
    def _load_baseline(self) -> None:
        """Load baseline metrics from file."""
        try:
            with open(self.baseline_file, 'r') as f:
                data = json.load(f)
                for key, metrics_dict in data.items():
                    self.baseline_metrics[key] = PerformanceMetrics(**metrics_dict)
        except FileNotFoundError:
            # No baseline exists yet
            pass
        except Exception:
            # Corrupted baseline file - start fresh
            self.baseline_metrics.clear()
    
    def _save_baseline(self) -> None:
        """Save baseline metrics to file."""
        data = {
            key: asdict(metrics)
            for key, metrics in self.baseline_metrics.items()
        }
        
        with open(self.baseline_file, 'w') as f:
            json.dump(data, f, indent=2)


class FunctionMetricsAnalyzer(ast.NodeVisitor):
    """Analyzes additional metrics within a function."""
    
    def __init__(self):
        self.has_database_ops = False
        self.has_concurrency = False
        self.cyclomatic_complexity = 1
        self.memory_allocations = 0
        self.condition_count = 0
    
    def visit_Call(self, node: ast.Call):
        # Check for database operations
        if isinstance(node.func, ast.Attribute):
            db_methods = {'execute', 'query', 'filter', 'all', 'get', 'save', 'create', 'update', 'delete'}
            if node.func.attr in db_methods:
                self.has_database_ops = True
        
        # Check for concurrency operations
        if isinstance(node.func, ast.Name):
            if node.func.id in ['Thread', 'Process', 'async', 'await']:
                self.has_concurrency = True
        
        # Count memory allocations
        if isinstance(node.func, ast.Name):
            if node.func.id in ['list', 'dict', 'set', 'tuple']:
                self.memory_allocations += 1
        
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.has_concurrency = True
        self.generic_visit(node)
    
    def visit_ListComp(self, node: ast.ListComp):
        self.memory_allocations += 1
        self.generic_visit(node)
    
    def visit_DictComp(self, node: ast.DictComp):
        self.memory_allocations += 1
        self.generic_visit(node)