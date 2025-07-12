"""Static memory usage analysis before deployment."""

import ast
import dis
import sys
import inspect
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from pathlib import Path
import importlib.util


@dataclass
class MemoryEstimate:
    """Memory estimate for a code element."""
    min_bytes: int
    max_bytes: int
    average_bytes: int
    confidence: float  # 0.0 to 1.0
    notes: List[str] = field(default_factory=list)


@dataclass
class CodePathAnalysis:
    """Analysis results for a code path."""
    path_id: str
    function_calls: List[str]
    memory_estimate: MemoryEstimate
    intensive_operations: List[str]
    allocations: List[Tuple[str, int]]  # (type, estimated_size)


@dataclass
class DeploymentReport:
    """Pre-deployment memory analysis report."""
    total_estimate: MemoryEstimate
    code_paths: List[CodePathAnalysis]
    memory_hotspots: List[Tuple[str, int]]  # (location, estimated_bytes)
    validation_errors: List[str]
    recommendations: List[str]


class StaticAnalyzer:
    """Analyze Python code for memory usage before deployment."""
    
    # Base memory sizes for common types
    TYPE_SIZES = {
        'int': 28,
        'float': 24,
        'bool': 28,
        'str': 49,  # Base size, +1 per character
        'list': 56,  # Base size, +8 per element pointer
        'dict': 232,  # Base size, varies with entries
        'tuple': 48,  # Base size, +8 per element
        'set': 216,  # Base size
        'bytes': 33,  # Base size, +1 per byte
        'bytearray': 56,  # Base size, +1 per byte
    }
    
    # Memory overhead for operations
    OPERATION_OVERHEAD = {
        'list_comprehension': 100,
        'dict_comprehension': 200,
        'generator': 80,
        'lambda': 100,
        'function_call': 50,
        'class_instance': 200,
    }
    
    def __init__(self, device_memory_limit: Optional[int] = None):
        """Initialize the static analyzer.
        
        Args:
            device_memory_limit: Memory limit of target device in bytes
        """
        self.device_memory_limit = device_memory_limit
        self._analyzed_functions: Set[str] = set()
        self._call_graph: Dict[str, Set[str]] = {}
        
    def analyze_file(self, file_path: Path) -> DeploymentReport:
        """Analyze a Python file for memory usage.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Deployment report with memory estimates
        """
        with open(file_path, 'r') as f:
            source = f.read()
            
        return self.analyze_source(source, str(file_path))
        
    def analyze_source(self, source: str, filename: str = "<string>") -> DeploymentReport:
        """Analyze Python source code for memory usage.
        
        Args:
            source: Python source code
            filename: Name of the file
            
        Returns:
            Deployment report with memory estimates
        """
        try:
            tree = ast.parse(source, filename)
        except SyntaxError as e:
            return DeploymentReport(
                total_estimate=MemoryEstimate(0, 0, 0, 0.0),
                code_paths=[],
                memory_hotspots=[],
                validation_errors=[f"Syntax error: {e}"],
                recommendations=[]
            )
            
        # Analyze AST
        code_paths = []
        memory_hotspots = []
        has_classes = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                path_analysis = self._analyze_function(node, filename)
                if path_analysis:
                    code_paths.append(path_analysis)
                    
            elif isinstance(node, ast.ClassDef):
                has_classes = True
                    
            # Find memory-intensive patterns
            hotspot = self._check_memory_hotspot(node, filename)
            if hotspot:
                memory_hotspots.append(hotspot)
                
        # Calculate total estimates
        total_min = sum(p.memory_estimate.min_bytes for p in code_paths)
        total_max = sum(p.memory_estimate.max_bytes for p in code_paths)
        total_avg = sum(p.memory_estimate.average_bytes for p in code_paths)
        
        # Validation
        validation_errors = []
        if self.device_memory_limit and total_max > self.device_memory_limit:
            validation_errors.append(
                f"Maximum memory estimate ({total_max} bytes) exceeds device limit "
                f"({self.device_memory_limit} bytes)"
            )
            
        # Generate recommendations
        recommendations = self._generate_recommendations(code_paths, memory_hotspots)
        
        # Add class-specific recommendations
        if has_classes:
            recommendations.append("Consider using __slots__ to reduce memory overhead in classes")
        
        return DeploymentReport(
            total_estimate=MemoryEstimate(
                min_bytes=total_min,
                max_bytes=total_max,
                average_bytes=total_avg,
                confidence=0.7
            ),
            code_paths=code_paths,
            memory_hotspots=sorted(memory_hotspots, key=lambda x: x[1], reverse=True)[:10],
            validation_errors=validation_errors,
            recommendations=recommendations
        )
        
    def analyze_module(self, module_name: str) -> DeploymentReport:
        """Analyze an imported module for memory usage.
        
        Args:
            module_name: Name of the module to analyze
            
        Returns:
            Deployment report
        """
        try:
            module = importlib.import_module(module_name)
            source = inspect.getsource(module)
            return self.analyze_source(source, module.__file__ or module_name)
        except Exception as e:
            return DeploymentReport(
                total_estimate=MemoryEstimate(0, 0, 0, 0.0),
                code_paths=[],
                memory_hotspots=[],
                validation_errors=[f"Failed to analyze module: {e}"],
                recommendations=[]
            )
            
    def estimate_memory_for_value(self, value: Any) -> int:
        """Estimate memory usage for a value.
        
        Args:
            value: Value to estimate
            
        Returns:
            Estimated memory in bytes
        """
        if value is None:
            return 16
            
        value_type = type(value).__name__
        base_size = self.TYPE_SIZES.get(value_type, 100)
        
        if isinstance(value, str):
            return base_size + len(value)
        elif isinstance(value, (list, tuple)):
            return base_size + 8 * len(value) + sum(self.estimate_memory_for_value(v) for v in value)
        elif isinstance(value, dict):
            return base_size + sum(self.estimate_memory_for_value(k) + self.estimate_memory_for_value(v) 
                                 for k, v in value.items())
        elif isinstance(value, (bytes, bytearray)):
            return base_size + len(value)
            
        return base_size
        
    def _analyze_function(self, node: ast.FunctionDef, filename: str) -> Optional[CodePathAnalysis]:
        """Analyze a function for memory usage."""
        path_id = f"{filename}:{node.name}:{node.lineno}"
        
        if path_id in self._analyzed_functions:
            return None
            
        self._analyzed_functions.add(path_id)
        
        # Analyze function body
        allocations = []
        intensive_operations = []
        function_calls = []
        
        for child in ast.walk(node):
            # Track allocations
            if isinstance(child, ast.List):
                size = len(child.elts) if hasattr(child, 'elts') else 10
                allocations.append(('list', self.TYPE_SIZES['list'] + 8 * size))
                
            # Track list multiplication (e.g., [0] * 10000)
            elif isinstance(child, ast.BinOp) and isinstance(child.op, ast.Mult):
                if isinstance(child.left, ast.List) and isinstance(child.right, (ast.Num, ast.Constant)):
                    multiplier = child.right.n if hasattr(child.right, 'n') else child.right.value
                    list_size = len(child.left.elts) if hasattr(child.left, 'elts') else 1
                    total_size = self.TYPE_SIZES['list'] + 8 * list_size * multiplier
                    allocations.append(('list_mult', total_size))
                
            elif isinstance(child, ast.Dict):
                size = len(child.keys) if hasattr(child, 'keys') else 10
                allocations.append(('dict', self.TYPE_SIZES['dict'] + 16 * size))
                
            elif isinstance(child, ast.ListComp):
                intensive_operations.append(f"List comprehension at line {child.lineno}")
                allocations.append(('list_comp', self.OPERATION_OVERHEAD['list_comprehension']))
                
            elif isinstance(child, ast.DictComp):
                intensive_operations.append(f"Dict comprehension at line {child.lineno}")
                allocations.append(('dict_comp', self.OPERATION_OVERHEAD['dict_comprehension']))
                
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    function_calls.append(child.func.id)
                    # Track class instantiation
                    if child.func.id[0].isupper():  # Likely a class
                        allocations.append(('class_instance', self.OPERATION_OVERHEAD['class_instance']))
                    
        # Calculate memory estimate
        min_bytes = sum(size for _, size in allocations)
        max_bytes = min_bytes * 2  # Conservative estimate
        avg_bytes = int((min_bytes + max_bytes) / 2)
        
        return CodePathAnalysis(
            path_id=path_id,
            function_calls=function_calls,
            memory_estimate=MemoryEstimate(
                min_bytes=min_bytes,
                max_bytes=max_bytes,
                average_bytes=avg_bytes,
                confidence=0.7
            ),
            intensive_operations=intensive_operations,
            allocations=allocations
        )
        
    def _check_memory_hotspot(self, node: ast.AST, filename: str) -> Optional[Tuple[str, int]]:
        """Check if a node represents a memory hotspot."""
        # Check list comprehensions
        if isinstance(node, ast.ListComp):
            # Estimate size based on comprehension
            estimated_size = 1000  # Conservative estimate
            return (f"{filename}:{node.lineno} - Large list comprehension", estimated_size)
            
        # Check dict comprehensions
        elif isinstance(node, ast.DictComp):
            estimated_size = 2000  # Conservative estimate
            return (f"{filename}:{node.lineno} - Large dict comprehension", estimated_size)
            
        # Large list/dict literals
        elif isinstance(node, ast.List) and hasattr(node, 'elts') and len(node.elts) > 100:
            size = self.TYPE_SIZES['list'] + 8 * len(node.elts)
            return (f"{filename}:{node.lineno} - Large list", size)
            
        elif isinstance(node, ast.Dict) and hasattr(node, 'keys') and len(node.keys) > 50:
            size = self.TYPE_SIZES['dict'] + 16 * len(node.keys)
            return (f"{filename}:{node.lineno} - Large dict", size)
            
        # Nested comprehensions
        elif isinstance(node, (ast.ListComp, ast.DictComp)):
            for child in ast.walk(node):
                if isinstance(child, (ast.ListComp, ast.DictComp)) and child != node:
                    return (f"{filename}:{node.lineno} - Nested comprehension", 1000)
                    
        # String concatenation in loops
        elif isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    if isinstance(child.target, ast.Name):
                        return (f"{filename}:{node.lineno} - String concatenation in loop", 500)
                        
        return None
        
    def _generate_recommendations(self, code_paths: List[CodePathAnalysis], 
                                hotspots: List[Tuple[str, int]]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Check for large allocations
        large_allocations = [cp for cp in code_paths 
                           if cp.memory_estimate.max_bytes > 10000]
        if large_allocations:
            recommendations.append(
                "Consider using generators instead of lists for large data processing"
            )
            
        # Check for string concatenation
        string_hotspots = [h for h in hotspots if "String concatenation" in h[0]]
        if string_hotspots:
            recommendations.append(
                "Use str.join() instead of string concatenation in loops"
            )
            
        # Check for nested comprehensions
        nested_comps = [h for h in hotspots if "Nested comprehension" in h[0]]
        if nested_comps:
            recommendations.append(
                "Consider breaking down nested comprehensions into separate steps"
            )
            
        # Check for classes without __slots__
        for path in code_paths:
            for alloc_type, _ in path.allocations:
                if 'class_instance' in alloc_type:
                    recommendations.append(
                        "Consider using __slots__ to reduce memory overhead in classes"
                    )
                    break
                    
        # Memory limit warnings
        if self.device_memory_limit:
            total_max = sum(cp.memory_estimate.max_bytes for cp in code_paths)
            usage_percent = (total_max / self.device_memory_limit) * 100
            
            if usage_percent > 80:
                recommendations.append(
                    f"Memory usage is at {usage_percent:.1f}% of device limit. "
                    "Consider optimizing data structures"
                )
                
        return recommendations
        
    def validate_against_device(self, report: DeploymentReport, 
                              device_profile: Dict[str, Any]) -> List[str]:
        """Validate memory usage against device constraints.
        
        Args:
            report: Deployment report
            device_profile: Device profile with memory constraints
            
        Returns:
            List of validation errors/warnings
        """
        errors = []
        
        available_memory = device_profile.get('available_memory', 0)
        memory_alignment = device_profile.get('memory_alignment', 4)
        
        if report.total_estimate.max_bytes > available_memory:
            errors.append(
                f"Maximum memory usage ({report.total_estimate.max_bytes} bytes) "
                f"exceeds available memory ({available_memory} bytes)"
            )
            
        # Check alignment requirements
        for path in report.code_paths:
            for alloc_type, size in path.allocations:
                if size % memory_alignment != 0:
                    errors.append(
                        f"Allocation of {size} bytes in {path.path_id} "
                        f"not aligned to {memory_alignment} bytes"
                    )
                    
        return errors