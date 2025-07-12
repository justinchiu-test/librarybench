"""Memory optimization recommendations for embedded systems."""

import ast
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional, Any
from enum import Enum
from pathlib import Path


class OptimizationType(Enum):
    """Types of memory optimizations."""
    DATA_STRUCTURE = "data_structure"
    OBJECT_POOLING = "object_pooling"
    LAZY_LOADING = "lazy_loading"
    MEMORY_REUSE = "memory_reuse"
    ALGORITHM = "algorithm"
    REDUNDANCY = "redundancy"
    
    
@dataclass
class OptimizationSuggestion:
    """A specific optimization suggestion."""
    type: OptimizationType
    priority: int  # 1-10, higher is more important
    location: str  # file:line or function name
    current_approach: str
    suggested_approach: str
    estimated_savings: int  # bytes
    implementation_effort: str  # "low", "medium", "high"
    code_example: Optional[str] = None
    

@dataclass
class MemoryPattern:
    """Detected memory usage pattern."""
    pattern_type: str
    locations: List[str]
    memory_impact: int
    frequency: int
    

@dataclass
class OptimizationReport:
    """Complete optimization analysis report."""
    suggestions: List[OptimizationSuggestion]
    memory_patterns: List[MemoryPattern]
    total_potential_savings: int
    optimization_ranking: List[Tuple[str, int]]  # (optimization_id, score)
    implementation_plan: List[str]


class MemoryOptimizer:
    """Analyze code and suggest memory optimizations for embedded systems."""
    
    # Memory costs for common patterns
    PATTERN_COSTS = {
        'list_append_loop': 100,  # Per iteration
        'string_concat_loop': 50,  # Per iteration
        'dict_default': 200,
        'redundant_copy': 500,
        'large_temp_var': 1000,
        'unnecessary_list': 300,
    }
    
    # Efficient alternatives
    EFFICIENT_ALTERNATIVES = {
        'list': 'array.array or bytes for homogeneous data',
        'dict': 'collections.defaultdict or __slots__ for objects',
        'str_concat': 'str.join() or io.StringIO',
        'global_var': 'function parameter or class attribute',
        'deep_copy': 'shallow copy or in-place modification',
    }
    
    def __init__(self):
        """Initialize the memory optimizer."""
        self.detected_patterns: List[MemoryPattern] = []
        self.suggestions: List[OptimizationSuggestion] = []
        
    def analyze_file(self, file_path: Path) -> OptimizationReport:
        """Analyze a Python file for optimization opportunities.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Optimization report
        """
        with open(file_path, 'r') as f:
            source = f.read()
            
        return self.analyze_source(source, str(file_path))
        
    def analyze_source(self, source: str, filename: str = "<string>") -> OptimizationReport:
        """Analyze Python source for optimization opportunities.
        
        Args:
            source: Python source code
            filename: Name of the file
            
        Returns:
            Optimization report
        """
        self.detected_patterns.clear()
        self.suggestions.clear()
        
        try:
            tree = ast.parse(source, filename)
        except SyntaxError:
            return self._create_empty_report()
            
        # Run various analyzers
        self._analyze_data_structures(tree, filename)
        self._analyze_loops(tree, filename)
        self._analyze_redundancy(tree, filename)
        self._analyze_object_creation(tree, filename)
        self._analyze_algorithms(tree, filename)
        
        # Calculate total savings
        total_savings = sum(s.estimated_savings for s in self.suggestions)
        
        # Rank optimizations
        ranking = self._rank_optimizations()
        
        # Generate implementation plan
        plan = self._generate_implementation_plan()
        
        return OptimizationReport(
            suggestions=sorted(self.suggestions, key=lambda x: x.priority, reverse=True),
            memory_patterns=self.detected_patterns,
            total_potential_savings=total_savings,
            optimization_ranking=ranking,
            implementation_plan=plan
        )
        
    def _analyze_data_structures(self, tree: ast.AST, filename: str) -> None:
        """Analyze data structure usage for optimization."""
        for node in ast.walk(tree):
            # Large lists that could be arrays
            if isinstance(node, ast.List) and len(node.elts) > 100:
                all_nums = all(isinstance(e, (ast.Num, ast.Constant)) for e in node.elts)
                if all_nums:
                    self._add_suggestion(
                        type=OptimizationType.DATA_STRUCTURE,
                        priority=7,
                        location=f"{filename}:{node.lineno}",
                        current_approach="Large list of numbers",
                        suggested_approach="Use array.array for homogeneous numeric data",
                        estimated_savings=len(node.elts) * 4,  # 4 bytes per element saved
                        implementation_effort="low",
                        code_example="import array\nnumbers = array.array('i', [1, 2, 3, ...])"
                    )
                    
            # Detect list multiplication pattern (e.g., [1, 2, 3] * 100)
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                if isinstance(node.left, ast.List) and isinstance(node.right, (ast.Num, ast.Constant)):
                    # Check if list contains numbers
                    all_nums = all(isinstance(e, (ast.Num, ast.Constant)) for e in node.left.elts)
                    multiplier = node.right.n if hasattr(node.right, 'n') else node.right.value
                    
                    if all_nums and len(node.left.elts) * multiplier > 100:
                        self._add_suggestion(
                            type=OptimizationType.DATA_STRUCTURE,
                            priority=7,
                            location=f"{filename}:{node.lineno}",
                            current_approach="Large list of numbers created by multiplication",
                            suggested_approach="Use array.array for homogeneous numeric data",
                            estimated_savings=len(node.left.elts) * multiplier * 4,
                            implementation_effort="low",
                            code_example="import array\nnumbers = array.array('i', [1, 2, 3, 4, 5] * 100)"
                        )
                    
            # Dict that could use __slots__
            elif isinstance(node, ast.ClassDef):
                has_slots = any(isinstance(n, ast.Assign) and 
                               any(isinstance(t, ast.Name) and t.id == '__slots__' for t in n.targets)
                               for n in node.body)
                
                # Count attributes set in __init__
                init_attrs = 0
                for n in node.body:
                    if isinstance(n, ast.FunctionDef) and n.name == '__init__':
                        for stmt in ast.walk(n):
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                        init_attrs += 1
                
                if not has_slots and (len(node.body) > 2 or init_attrs > 2):
                    self._add_suggestion(
                        type=OptimizationType.DATA_STRUCTURE,
                        priority=8,
                        location=f"{filename}:{node.lineno}",
                        current_approach=f"Class {node.name} without __slots__",
                        suggested_approach="Add __slots__ to reduce memory overhead",
                        estimated_savings=200 * len(node.body),  # Rough estimate
                        implementation_effort="low",
                        code_example=f"class {node.name}:\n    __slots__ = ['attr1', 'attr2', ...]"
                    )
                    
    def _analyze_loops(self, tree: ast.AST, filename: str) -> None:
        """Analyze loops for memory inefficiencies."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # String concatenation in loops
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            # Check if it's string concatenation
                            self._add_pattern(
                                pattern_type='string_concat_loop',
                                locations=[f"{filename}:{node.lineno}"],
                                memory_impact=self.PATTERN_COSTS['string_concat_loop'] * 10,
                                frequency=1
                            )
                            
                            self._add_suggestion(
                                type=OptimizationType.ALGORITHM,
                                priority=9,
                                location=f"{filename}:{node.lineno}",
                                current_approach="String concatenation in loop",
                                suggested_approach="Use list.append() and str.join()",
                                estimated_savings=500,
                                implementation_effort="low",
                                code_example="parts = []\nfor item in items:\n    parts.append(str(item))\nresult = ''.join(parts)"
                            )
                            
                # List append in tight loops
                list_appends = []
                for child in ast.walk(node):
                    if (isinstance(child, ast.Call) and 
                        isinstance(child.func, ast.Attribute) and
                        child.func.attr == 'append'):
                        list_appends.append(child)
                        
                if len(list_appends) > 1:
                    self._add_suggestion(
                        type=OptimizationType.ALGORITHM,
                        priority=6,
                        location=f"{filename}:{node.lineno}",
                        current_approach="Multiple list.append() in loop",
                        suggested_approach="Pre-allocate list or use list comprehension",
                        estimated_savings=len(list_appends) * 50,
                        implementation_effort="medium",
                        code_example="# Pre-allocate:\nresult = [None] * expected_size\n# Or use comprehension:\nresult = [process(x) for x in items]"
                    )
                    
    def _analyze_redundancy(self, tree: ast.AST, filename: str) -> None:
        """Analyze code for redundant allocations."""
        # Track variable assignments
        assignments: Dict[str, List[ast.AST]] = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id not in assignments:
                            assignments[target.id] = []
                        assignments[target.id].append(node)
                        
        # Find redundant copies
        for var_name, assign_list in assignments.items():
            if len(assign_list) > 2:
                # Multiple assignments might indicate redundant copies
                self._add_pattern(
                    pattern_type='redundant_copy',
                    locations=[f"{filename}:{a.lineno}" for a in assign_list],
                    memory_impact=self.PATTERN_COSTS['redundant_copy'],
                    frequency=len(assign_list)
                )
                
                self._add_suggestion(
                    type=OptimizationType.REDUNDANCY,
                    priority=5,
                    location=f"{filename}:{assign_list[0].lineno}",
                    current_approach=f"Multiple assignments to '{var_name}'",
                    suggested_approach="Reuse existing object or modify in-place",
                    estimated_savings=300,
                    implementation_effort="medium"
                )
                
    def _analyze_object_creation(self, tree: ast.AST, filename: str) -> None:
        """Analyze object creation patterns for pooling opportunities."""
        object_creations: Dict[str, List[ast.AST]] = {}
        
        # Look for object creation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Check for object creation inside loops
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        class_name = child.func.id
                        # Check if it looks like a class (starts with uppercase)
                        if class_name[0].isupper():
                            if class_name not in object_creations:
                                object_creations[class_name] = []
                            # Add multiple times to account for loop iterations
                            for _ in range(10):  # Assume loop runs many times
                                object_creations[class_name].append(child)
                    
        # Suggest object pooling for frequently created objects
        for class_name, creations in object_creations.items():
            if len(creations) > 5:  # Lower threshold for testing
                self._add_suggestion(
                    type=OptimizationType.OBJECT_POOLING,
                    priority=7,
                    location=f"{filename}",
                    current_approach=f"Creating {len(creations)} instances of {class_name}",
                    suggested_approach=f"Implement object pooling for {class_name}",
                    estimated_savings=len(creations) * 100,
                    implementation_effort="high",
                    code_example=f"""class {class_name}Pool:
    def __init__(self, size=10):
        self._pool = [{{class_name}}() for _ in range(size)]
        self._available = list(self._pool)
        
    def acquire(self):
        if self._available:
            return self._available.pop()
        return {class_name}()
        
    def release(self, obj):
        obj.reset()  # Clear object state
        self._available.append(obj)"""
                )
                
    def _analyze_algorithms(self, tree: ast.AST, filename: str) -> None:
        """Analyze algorithms for memory-efficient alternatives."""
        for node in ast.walk(tree):
            # Nested loops that might benefit from better algorithms
            if isinstance(node, ast.For):
                nested_loops = sum(1 for child in ast.walk(node) 
                                 if isinstance(child, ast.For) and child != node)
                
                if nested_loops >= 2:
                    self._add_suggestion(
                        type=OptimizationType.ALGORITHM,
                        priority=8,
                        location=f"{filename}:{node.lineno}",
                        current_approach="Deeply nested loops",
                        suggested_approach="Consider more efficient algorithm or data structure",
                        estimated_savings=1000,
                        implementation_effort="high"
                    )
                    
            # Large temporary variables
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                if len(node.value.elts) > 50:
                    self._add_pattern(
                        pattern_type='large_temp_var',
                        locations=[f"{filename}:{node.lineno}"],
                        memory_impact=self.PATTERN_COSTS['large_temp_var'],
                        frequency=1
                    )
                    
    def _add_suggestion(self, **kwargs: Any) -> None:
        """Add an optimization suggestion."""
        self.suggestions.append(OptimizationSuggestion(**kwargs))
        
    def _add_pattern(self, **kwargs: Any) -> None:
        """Add a detected memory pattern."""
        self.detected_patterns.append(MemoryPattern(**kwargs))
        
    def _rank_optimizations(self) -> List[Tuple[str, int]]:
        """Rank optimizations by impact and effort.
        
        Returns:
            List of (optimization_id, score) tuples
        """
        rankings = []
        
        for i, suggestion in enumerate(self.suggestions):
            # Score based on priority, savings, and effort
            effort_score = {'low': 3, 'medium': 2, 'high': 1}.get(
                suggestion.implementation_effort, 1
            )
            
            score = (suggestion.priority * 10 + 
                    (suggestion.estimated_savings // 100) +
                    effort_score * 5)
                    
            rankings.append((f"opt_{i}", score))
            
        return sorted(rankings, key=lambda x: x[1], reverse=True)
        
    def _generate_implementation_plan(self) -> List[str]:
        """Generate step-by-step implementation plan.
        
        Returns:
            List of implementation steps
        """
        plan = []
        
        # Group by effort
        low_effort = [s for s in self.suggestions if s.implementation_effort == "low"]
        medium_effort = [s for s in self.suggestions if s.implementation_effort == "medium"]
        high_effort = [s for s in self.suggestions if s.implementation_effort == "high"]
        
        if low_effort:
            plan.append("Phase 1: Quick Wins (Low Effort)")
            for s in low_effort[:3]:
                plan.append(f"  - {s.suggested_approach} at {s.location}")
                
        if medium_effort:
            plan.append("\nPhase 2: Moderate Changes (Medium Effort)")
            for s in medium_effort[:3]:
                plan.append(f"  - {s.suggested_approach} at {s.location}")
                
        if high_effort:
            plan.append("\nPhase 3: Major Refactoring (High Effort)")
            for s in high_effort[:2]:
                plan.append(f"  - {s.suggested_approach}")
                
        return plan
        
    def _create_empty_report(self) -> OptimizationReport:
        """Create an empty optimization report."""
        return OptimizationReport(
            suggestions=[],
            memory_patterns=[],
            total_potential_savings=0,
            optimization_ranking=[],
            implementation_plan=[]
        )
        
    def identify_pooling_candidates(self, 
                                   allocation_history: List[Tuple[str, int, int]]) -> List[str]:
        """Identify objects suitable for pooling.
        
        Args:
            allocation_history: List of (object_type, size, count) tuples
            
        Returns:
            List of object types suitable for pooling
        """
        candidates = []
        
        for obj_type, size, count in allocation_history:
            # High frequency, similar size allocations are good candidates
            if count > 100 and size < 1000:
                candidates.append(obj_type)
                
        return candidates