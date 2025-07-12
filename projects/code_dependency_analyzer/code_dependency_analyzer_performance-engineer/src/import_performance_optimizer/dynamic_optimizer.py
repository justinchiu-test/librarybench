"""Dynamic import optimization suggestions based on usage patterns."""

import ast
import os
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import timedelta
from pathlib import Path
from collections import defaultdict

from .models import DynamicImportSuggestion


class DynamicImportOptimizer:
    """Analyzes usage patterns and suggests dynamic import optimizations."""

    def __init__(self) -> None:
        self._function_imports: Dict[str, Set[str]] = defaultdict(set)
        self._class_imports: Dict[str, Set[str]] = defaultdict(set)
        self._conditional_imports: Dict[str, List[str]] = defaultdict(list)
        self._import_usage_count: Dict[str, int] = defaultdict(int)
        self._module_import_times: Dict[str, float] = {}
        self._module_memory_usage: Dict[str, int] = {}

    def analyze_file(self, file_path: str) -> None:
        """Analyze a Python file for dynamic import opportunities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            self._analyze_ast(tree, file_path)
        except Exception:
            pass

    def analyze_directory(self, directory: str) -> None:
        """Analyze all Python files in a directory for optimization opportunities."""
        path = Path(directory)
        for py_file in path.rglob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                self.analyze_file(str(py_file))

    def _analyze_ast(self, tree: ast.AST, file_path: str) -> None:
        """Analyze AST for import usage patterns."""
        module_imports = self._extract_module_level_imports(tree)
        
        class UsageAnalyzer(ast.NodeVisitor):
            def __init__(self, optimizer, file_path):
                self.optimizer = optimizer
                self.file_path = file_path
                self.current_function = None
                self.current_class = None
                self.in_conditional = False
                
            def visit_FunctionDef(self, node):
                old_function = self.current_function
                # If we're already in a function, keep the outer function context
                if not self.current_function:
                    self.current_function = node.name
                
                self.generic_visit(node)  # Visit all child nodes
                
                self.current_function = old_function
            
            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)
            
            def visit_ClassDef(self, node):
                old_class = self.current_class
                old_function = self.current_function
                self.current_class = node.name
                self.current_function = None  # Reset function context in class
                
                self.generic_visit(node)  # Visit all child nodes
                
                self.current_class = old_class
                self.current_function = old_function
            
            def visit_If(self, node):
                old_conditional = self.in_conditional
                self.in_conditional = True
                
                for child in node.body + node.orelse:
                    self.visit(child)
                
                self.in_conditional = old_conditional
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load) and node.id in module_imports:
                    self._record_usage(node.id)
                self.generic_visit(node)
            
            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name) and node.value.id in module_imports:
                    self._record_usage(node.value.id)
                self.generic_visit(node)
            
            def _record_usage(self, module_name):
                self.optimizer._import_usage_count[module_name] += 1
                
                if self.current_function and self.current_class:
                    # Inside a method of a class
                    key = f"{self.file_path}::{self.current_class}"
                    self.optimizer._class_imports[key].add(module_name)
                elif self.current_function:
                    key = f"{self.file_path}::{self.current_function}"
                    self.optimizer._function_imports[key].add(module_name)
                elif self.current_class:
                    key = f"{self.file_path}::{self.current_class}"
                    self.optimizer._class_imports[key].add(module_name)
                
                if self.in_conditional:
                    self.optimizer._conditional_imports[module_name].append(
                        f"{self.file_path}:{self.current_function or self.current_class or 'module'}"
                    )
        
        analyzer = UsageAnalyzer(self, file_path)
        analyzer.visit(tree)

    def _extract_module_level_imports(self, tree: ast.AST) -> Set[str]:
        """Extract module-level imports."""
        imports = set()
        
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.asname if alias.asname else alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.add(alias.asname if alias.asname else alias.name)
        
        return imports

    def set_performance_data(self, import_times: Dict[str, float], 
                           memory_usage: Dict[str, int]) -> None:
        """Set performance data from profiler and memory analyzer."""
        self._module_import_times = import_times
        self._module_memory_usage = memory_usage

    def generate_suggestions(self, min_time_threshold_ms: float = 50.0,
                           min_memory_threshold_mb: float = 1.0) -> List[DynamicImportSuggestion]:
        """Generate dynamic import suggestions based on analysis."""
        suggestions = []
        
        min_time_seconds = min_time_threshold_ms / 1000
        min_memory_bytes = min_memory_threshold_mb * 1024 * 1024
        
        for module_name, import_time in self._module_import_times.items():
            memory_usage = self._module_memory_usage.get(module_name, 0)
            
            if import_time < min_time_seconds and memory_usage < min_memory_bytes:
                continue
            
            usage_count = self._import_usage_count.get(module_name, 0)
            if usage_count == 0:
                continue
            
            function_usage = self._get_function_specific_usage(module_name)
            conditional_usage = len(self._conditional_imports.get(module_name, []))
            
            if function_usage or conditional_usage > 0:
                suggestion = self._create_suggestion(
                    module_name, import_time, memory_usage,
                    function_usage, conditional_usage > 0
                )
                suggestions.append(suggestion)
        
        return sorted(suggestions, 
                     key=lambda s: s.estimated_time_improvement, 
                     reverse=True)

    def _get_function_specific_usage(self, module_name: str) -> List[str]:
        """Get functions that use a specific module."""
        functions = []
        
        for func_key, modules in self._function_imports.items():
            if module_name in modules:
                functions.append(func_key)
        
        return functions

    def _create_suggestion(self, module_name: str, import_time: float,
                         memory_usage: int, function_usage: List[str],
                         has_conditional_usage: bool) -> DynamicImportSuggestion:
        """Create a dynamic import suggestion."""
        current_import = f"import {module_name}"
        code_examples = []
        
        if function_usage:
            suggested_import = f"# Move import inside functions that use it"
            code_examples.append(self._generate_function_import_example(
                module_name, function_usage[0]
            ))
            improvement_factor = 0.8
        elif has_conditional_usage:
            suggested_import = f"# Import only when condition is met"
            code_examples.append(self._generate_conditional_import_example(module_name))
            improvement_factor = 0.6
        else:
            suggested_import = f"# Use importlib for dynamic import"
            code_examples.append(self._generate_importlib_example(module_name))
            improvement_factor = 0.5
        
        estimated_time_improvement = timedelta(seconds=import_time * improvement_factor)
        estimated_memory_savings = int(memory_usage * improvement_factor)
        
        usage_patterns = function_usage[:5] if function_usage else ["module-level usage"]
        
        return DynamicImportSuggestion(
            module_name=module_name,
            current_import_statement=current_import,
            suggested_import_statement=suggested_import,
            usage_patterns=usage_patterns,
            estimated_time_improvement=estimated_time_improvement,
            estimated_memory_savings=estimated_memory_savings,
            code_examples=code_examples
        )

    def _generate_function_import_example(self, module_name: str, 
                                        function_key: str) -> str:
        """Generate example code for function-level import."""
        func_name = function_key.split("::")[-1]
        
        return f"""# Before:
import {module_name}

def {func_name}():
    result = {module_name}.some_function()
    return result

# After:
def {func_name}():
    import {module_name}
    result = {module_name}.some_function()
    return result"""

    def _generate_conditional_import_example(self, module_name: str) -> str:
        """Generate example code for conditional import."""
        return f"""# Before:
import {module_name}

if some_condition:
    result = {module_name}.process()

# After:
if some_condition:
    import {module_name}
    result = {module_name}.process()"""

    def _generate_importlib_example(self, module_name: str) -> str:
        """Generate example code for importlib dynamic import."""
        return f"""# Before:
import {module_name}

# After:
import importlib

# Lazy load when needed
def get_{module_name.replace('.', '_')}():
    return importlib.import_module('{module_name}')

# Usage:
{module_name.replace('.', '_')} = get_{module_name.replace('.', '_')}()
result = {module_name.replace('.', '_')}.some_function()"""

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Generate optimization summary report."""
        suggestions = self.generate_suggestions()
        
        total_time_savings = sum(
            s.estimated_time_improvement.total_seconds() 
            for s in suggestions
        )
        
        total_memory_savings = sum(
            s.estimated_memory_savings 
            for s in suggestions
        )
        
        function_specific = sum(
            1 for s in suggestions 
            if "inside functions" in s.suggested_import_statement
        )
        
        conditional_imports = sum(
            1 for s in suggestions 
            if "condition" in s.suggested_import_statement
        )
        
        return {
            "total_suggestions": len(suggestions),
            "total_time_savings_seconds": total_time_savings,
            "total_memory_savings_mb": total_memory_savings / (1024 * 1024),
            "function_specific_count": function_specific,
            "conditional_import_count": conditional_imports,
            "top_opportunities": suggestions[:5],
            "summary": f"Found {len(suggestions)} dynamic import opportunities "
                      f"with {total_time_savings:.2f}s time savings and "
                      f"{total_memory_savings / (1024 * 1024):.2f}MB memory savings"
        }