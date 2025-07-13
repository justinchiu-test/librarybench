"""Complexity Analyzer module for Big O notation detection."""

import ast
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ComplexityClass(Enum):
    """Enumeration of complexity classes."""
    
    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N_SQUARED = "O(n^2)"
    O_N_CUBED = "O(n^3)"
    O_2_N = "O(2^n)"
    O_N_FACTORIAL = "O(n!)"


@dataclass
class ComplexityResult:
    """Result of complexity analysis for a function."""
    
    function_name: str
    time_complexity: ComplexityClass
    space_complexity: ComplexityClass
    loop_depth: int
    recursive: bool
    details: Dict[str, Any]
    line_number: int


class ComplexityAnalyzer:
    """Analyzes code to determine Big O complexity."""
    
    def __init__(self):
        self._loop_keywords = {'for', 'while'}
        self._recursive_calls: Dict[str, List[str]] = {}
        
    def analyze_file(self, file_path: str) -> List[ComplexityResult]:
        """Analyze a Python file for complexity patterns.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            List of ComplexityResult objects
        """
        with open(file_path, 'r') as f:
            source = f.read()
        
        return self.analyze_source(source)
    
    def analyze_source(self, source: str) -> List[ComplexityResult]:
        """Analyze Python source code for complexity patterns.
        
        Args:
            source: Python source code as string
            
        Returns:
            List of ComplexityResult objects
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        results = []
        self._recursive_calls.clear()
        
        # First pass: collect all function definitions
        function_collector = FunctionCollector()
        function_collector.visit(tree)
        
        # Second pass: analyze each function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result = self._analyze_function(node, function_collector.functions)
                if result:
                    results.append(result)
        
        return results
    
    def _analyze_function(
        self, 
        node: ast.FunctionDef, 
        all_functions: Dict[str, ast.FunctionDef]
    ) -> Optional[ComplexityResult]:
        """Analyze a single function for complexity.
        
        Args:
            node: AST node representing the function
            all_functions: Dictionary of all functions in the module
            
        Returns:
            ComplexityResult or None if analysis fails
        """
        analyzer = FunctionComplexityAnalyzer(node.name, all_functions)
        analyzer.visit(node)
        
        time_complexity = self._determine_time_complexity(analyzer)
        space_complexity = self._determine_space_complexity(analyzer)
        
        return ComplexityResult(
            function_name=node.name,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            loop_depth=analyzer.max_loop_depth,
            recursive=analyzer.is_recursive,
            details={
                'has_nested_loops': analyzer.has_nested_loops,
                'has_exponential_recursion': analyzer.has_exponential_recursion,
                'data_structure_operations': analyzer.data_structure_ops,
                'recursive_calls': analyzer.recursive_calls,
            },
            line_number=node.lineno
        )
    
    def _determine_time_complexity(
        self, 
        analyzer: 'FunctionComplexityAnalyzer'
    ) -> ComplexityClass:
        """Determine time complexity based on analysis results."""
        if analyzer.has_exponential_recursion:
            return ComplexityClass.O_2_N
        
        if analyzer.is_recursive and analyzer.has_nested_loops:
            # Recursive with nested loops often leads to factorial
            return ComplexityClass.O_N_FACTORIAL
        
        if analyzer.max_loop_depth >= 3:
            return ComplexityClass.O_N_CUBED
        elif analyzer.max_loop_depth == 2:
            return ComplexityClass.O_N_SQUARED
        elif analyzer.max_loop_depth == 1:
            # Check for divide and conquer patterns
            if analyzer.has_divide_and_conquer:
                return ComplexityClass.O_N_LOG_N
            return ComplexityClass.O_N
        elif analyzer.has_logarithmic_pattern:
            return ComplexityClass.O_LOG_N
        
        return ComplexityClass.O_1
    
    def _determine_space_complexity(
        self, 
        analyzer: 'FunctionComplexityAnalyzer'
    ) -> ComplexityClass:
        """Determine space complexity based on analysis results."""
        if analyzer.creates_2d_structures:
            return ComplexityClass.O_N_SQUARED
        elif analyzer.creates_lists or analyzer.is_recursive:
            return ComplexityClass.O_N
        elif analyzer.has_logarithmic_pattern and analyzer.is_recursive:
            return ComplexityClass.O_LOG_N
        
        return ComplexityClass.O_1


class FunctionCollector(ast.NodeVisitor):
    """Collects all function definitions in a module."""
    
    def __init__(self):
        self.functions: Dict[str, ast.FunctionDef] = {}
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions[node.name] = node
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.functions[node.name] = node
        self.generic_visit(node)


class FunctionComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes complexity patterns within a function."""
    
    def __init__(self, function_name: str, all_functions: Dict[str, ast.FunctionDef]):
        self.function_name = function_name
        self.all_functions = all_functions
        self.current_loop_depth = 0
        self.max_loop_depth = 0
        self.has_nested_loops = False
        self.is_recursive = False
        self.has_exponential_recursion = False
        self.recursive_calls = 0
        self.data_structure_ops = []
        self.creates_lists = False
        self.creates_2d_structures = False
        self.has_logarithmic_pattern = False
        self.has_divide_and_conquer = False
    
    def visit_For(self, node: ast.For):
        self._enter_loop()
        self.generic_visit(node)
        self._exit_loop()
    
    def visit_While(self, node: ast.While):
        self._enter_loop()
        # Check for logarithmic patterns (e.g., i = i * 2, i = i // 2)
        if self._is_logarithmic_while(node):
            self.has_logarithmic_pattern = True
        self.generic_visit(node)
        self._exit_loop()
    
    def visit_Call(self, node: ast.Call):
        # Check for recursive calls
        if isinstance(node.func, ast.Name):
            if node.func.id == self.function_name:
                self.is_recursive = True
                self.recursive_calls += 1
                # Check if multiple recursive calls (exponential pattern)
                if self.recursive_calls > 1:
                    self.has_exponential_recursion = True
        
        # Check for data structure operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['append', 'extend', 'insert']:
                self.creates_lists = True
            elif node.func.attr in ['sort', 'sorted']:
                self.data_structure_ops.append('sort')
        
        self.generic_visit(node)
    
    def visit_ListComp(self, node: ast.ListComp):
        self.creates_lists = True
        # Check for nested comprehensions
        if any(isinstance(gen.iter, ast.ListComp) for gen in node.generators):
            self.creates_2d_structures = True
        # Check for [[...] for _ in range(n)] pattern (2D structure)
        if isinstance(node.elt, ast.ListComp) or isinstance(node.elt, ast.List):
            self.creates_2d_structures = True
        self.generic_visit(node)
    
    def visit_DictComp(self, node: ast.DictComp):
        self.creates_lists = True
        self.generic_visit(node)
    
    def visit_List(self, node: ast.List):
        # Check for 2D list creation
        if any(isinstance(elt, ast.List) for elt in node.elts):
            self.creates_2d_structures = True
        self.generic_visit(node)
    
    def _enter_loop(self):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        if self.current_loop_depth > 1:
            self.has_nested_loops = True
    
    def _exit_loop(self):
        self.current_loop_depth -= 1
    
    def _is_logarithmic_while(self, node: ast.While) -> bool:
        """Check if while loop has logarithmic pattern."""
        # Look for patterns like: while n > 0: n = n // 2
        # or binary search pattern: while left <= right: mid = (left + right) // 2
        
        # Check for binary search pattern
        has_mid_calculation = False
        has_range_adjustment = False
        
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                # Check for mid = (left + right) // 2 pattern
                if any(target.id == 'mid' for target in stmt.targets if isinstance(target, ast.Name)):
                    if isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, ast.FloorDiv):
                        has_mid_calculation = True
                
                # Check for left = mid + 1 or right = mid - 1 patterns
                if any(target.id in ['left', 'right'] for target in stmt.targets if isinstance(target, ast.Name)):
                    if isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, (ast.Add, ast.Sub)):
                        has_range_adjustment = True
                
                # Check for n = n // 2 or n = n * 2 patterns
                if isinstance(stmt.value, ast.BinOp):
                    if isinstance(stmt.value.op, (ast.Div, ast.FloorDiv)):
                        # Check if dividing by 2 or similar
                        if isinstance(stmt.value.right, ast.Constant):
                            if stmt.value.right.value in [2, 2.0]:
                                return True
                    elif isinstance(stmt.value.op, ast.Mult):
                        # Check if multiplying by 2
                        if isinstance(stmt.value.right, ast.Constant):
                            if stmt.value.right.value in [2, 2.0]:
                                return True
        
        # Binary search pattern detected
        if has_mid_calculation and has_range_adjustment:
            return True
        
        return False