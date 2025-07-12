"""Lazy loading opportunity detection for heavy modules."""

import ast
import os
import sys
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import timedelta
from pathlib import Path

from .models import LazyLoadingOpportunity


class LazyLoadingDetector:
    """Detects opportunities for lazy loading to optimize startup time."""

    def __init__(self) -> None:
        self._module_usage: Dict[str, List[Tuple[str, int]]] = {}
        self._import_locations: Dict[str, Tuple[str, int]] = {}
        self._module_import_times: Dict[str, float] = {}

    def analyze_file(self, file_path: str) -> None:
        """Analyze a Python file for import and usage patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            self._analyze_ast(tree, file_path)
        except Exception:
            pass

    def analyze_directory(self, directory: str) -> None:
        """Analyze all Python files in a directory recursively."""
        path = Path(directory)
        for py_file in path.rglob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                self.analyze_file(str(py_file))

    def _analyze_ast(self, tree: ast.AST, file_path: str) -> None:
        """Analyze AST for imports and their usage."""
        imports = self._extract_imports(tree, file_path)
        usages = self._extract_usages(tree, file_path)
        
        for module_name, import_line in imports.items():
            self._import_locations[module_name] = (file_path, import_line)
            
            module_usages = usages.get(module_name, [])
            if module_usages:
                self._module_usage[module_name] = module_usages

    def _extract_imports(self, tree: ast.AST, file_path: str) -> Dict[str, int]:
        """Extract import statements and their locations."""
        imports = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    imports[module_name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports[node.module] = node.lineno
        
        return imports

    def _extract_usages(self, tree: ast.AST, file_path: str) -> Dict[str, List[Tuple[str, int]]]:
        """Extract module usage locations."""
        usages = {}
        imported_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imported_names.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imported_names.add(name)
        
        class UsageVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_line = 0
                self.usages = {}
            
            def visit_Name(self, node):
                if node.id in imported_names:
                    if node.id not in self.usages:
                        self.usages[node.id] = []
                    self.usages[node.id].append((file_path, node.lineno))
                self.generic_visit(node)
            
            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name) and node.value.id in imported_names:
                    module_name = node.value.id
                    if module_name not in self.usages:
                        self.usages[module_name] = []
                    self.usages[module_name].append((file_path, node.lineno))
                self.generic_visit(node)
        
        visitor = UsageVisitor()
        visitor.visit(tree)
        
        return visitor.usages

    def set_module_import_times(self, import_times: Dict[str, float]) -> None:
        """Set import timing data from profiler."""
        self._module_import_times = import_times

    def detect_opportunities(self, min_import_time_ms: float = 10.0,
                           min_usage_delay_lines: int = 50) -> List[LazyLoadingOpportunity]:
        """Detect lazy loading opportunities based on analysis."""
        opportunities = []
        
        for module_name, (import_file, import_line) in self._import_locations.items():
            import_time = self._module_import_times.get(module_name, 0.0)
            
            if import_time < min_import_time_ms / 1000:
                continue
            
            usages = self._module_usage.get(module_name, [])
            
            if not usages:
                confidence = 0.9
                first_usage = None
                time_to_use = None
                transformation = self._generate_transformation(
                    module_name, import_file, import_line, None
                )
            else:
                first_usage_file, first_usage_line = min(usages, key=lambda x: x[1])
                
                if first_usage_file == import_file:
                    line_delay = first_usage_line - import_line
                    if line_delay < min_usage_delay_lines:
                        continue
                    
                    confidence = min(0.8, line_delay / 100.0)
                    first_usage = f"{first_usage_file}:{first_usage_line}"
                    time_to_use = timedelta(seconds=line_delay * 0.001)
                else:
                    confidence = 0.7
                    first_usage = f"{first_usage_file}:{first_usage_line}"
                    time_to_use = timedelta(seconds=1.0)
                
                transformation = self._generate_transformation(
                    module_name, import_file, import_line, first_usage_line
                )
            
            opportunities.append(LazyLoadingOpportunity(
                module_name=module_name,
                import_location=f"{import_file}:{import_line}",
                first_usage_location=first_usage,
                time_to_first_use=time_to_use,
                estimated_time_savings=timedelta(seconds=import_time * confidence),
                confidence_score=confidence,
                transformation_suggestion=transformation
            ))
        
        return sorted(opportunities, 
                     key=lambda x: x.estimated_time_savings, 
                     reverse=True)

    def _generate_transformation(self, module_name: str, file_path: str, 
                               import_line: int, usage_line: Optional[int]) -> str:
        """Generate transformation suggestion for lazy loading."""
        if usage_line is None:
            return f"Consider removing unused import: {module_name}"
        
        parts = module_name.split('.')
        if len(parts) > 1:
            suggestion = f"""Replace:
    import {module_name}

With lazy loading pattern:
    def _get_{parts[-1]}():
        global _{parts[-1]}
        if '_{parts[-1]}' not in globals():
            import {module_name}
            _{parts[-1]} = {module_name}
        return _{parts[-1]}

And update usage from:
    {module_name}.function()
To:
    _get_{parts[-1]}().function()"""
        else:
            suggestion = f"""Replace:
    import {module_name}

With lazy loading at first use:
    # At module level
    {module_name} = None
    
    # At first usage
    if {module_name} is None:
        import {module_name}"""
        
        return suggestion

    def get_summary_report(self) -> Dict[str, Any]:
        """Generate summary report of lazy loading opportunities."""
        opportunities = self.detect_opportunities()
        
        total_time_savings = sum(
            opp.estimated_time_savings.total_seconds() 
            for opp in opportunities
        )
        
        unused_imports = [
            opp for opp in opportunities 
            if opp.first_usage_location is None
        ]
        
        high_confidence = [
            opp for opp in opportunities 
            if opp.confidence_score >= 0.7
        ]
        
        return {
            "total_opportunities": len(opportunities),
            "total_time_savings_seconds": total_time_savings,
            "unused_imports_count": len(unused_imports),
            "high_confidence_count": len(high_confidence),
            "top_opportunities": opportunities[:10],
            "summary": f"Found {len(opportunities)} lazy loading opportunities "
                      f"with estimated {total_time_savings:.2f}s savings"
        }