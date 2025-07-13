"""Memory Leak Detector module for identifying circular references and memory issues."""

import ast
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class MemoryLeakType(Enum):
    """Types of memory leaks that can be detected."""
    
    CIRCULAR_REFERENCE = "Circular Reference"
    MISSING_CLEANUP = "Missing Cleanup"
    GLOBAL_CACHE_GROWTH = "Unbounded Global Cache"
    LARGE_OBJECT_RETENTION = "Large Object Retention"
    GENERATOR_EXHAUSTION = "Generator Not Properly Closed"
    EVENT_LISTENER_LEAK = "Event Listener Not Removed"


@dataclass
class MemoryLeakIssue:
    """Represents a detected memory leak issue."""
    
    leak_type: MemoryLeakType
    location: str
    line_number: int
    severity: str  # "high", "medium", "low"
    description: str
    recommendation: str
    code_snippet: Optional[str] = None


class MemoryLeakDetector:
    """Detects memory leak patterns in Python code."""
    
    def __init__(self):
        self._class_references: Dict[str, Set[str]] = {}
        self._global_caches: Set[str] = set()
        self._event_handlers: Dict[str, List[str]] = {}
        
    def analyze_file(self, file_path: str) -> List[MemoryLeakIssue]:
        """Analyze a Python file for memory leak patterns.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            List of MemoryLeakIssue objects
        """
        with open(file_path, 'r') as f:
            source = f.read()
        
        return self.analyze_source(source)
    
    def analyze_source(self, source: str) -> List[MemoryLeakIssue]:
        """Analyze Python source code for memory leak patterns.
        
        Args:
            source: Python source code as string
            
        Returns:
            List of MemoryLeakIssue objects
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        issues = []
        
        # Analyze for different types of memory leaks
        circular_ref_analyzer = CircularReferenceAnalyzer()
        circular_ref_analyzer.visit(tree)
        issues.extend(circular_ref_analyzer.get_issues())
        
        cleanup_analyzer = CleanupAnalyzer()
        cleanup_analyzer.visit(tree)
        issues.extend(cleanup_analyzer.get_issues())
        
        cache_analyzer = GlobalCacheAnalyzer()
        cache_analyzer.visit(tree)
        issues.extend(cache_analyzer.get_issues())
        
        generator_analyzer = GeneratorAnalyzer()
        generator_analyzer.visit(tree)
        issues.extend(generator_analyzer.get_issues())
        
        event_listener_analyzer = EventListenerAnalyzer()
        event_listener_analyzer.visit(tree)
        issues.extend(event_listener_analyzer.get_issues())
        
        return issues


class CircularReferenceAnalyzer(ast.NodeVisitor):
    """Analyzes code for circular reference patterns."""
    
    def __init__(self):
        self.issues: List[MemoryLeakIssue] = []
        self.current_class: Optional[str] = None
        self.class_attributes: Dict[str, Set[str]] = {}
        self.instance_references: Dict[str, Set[str]] = {}
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        self.class_attributes[node.name] = set()
        self.generic_visit(node)
        self.current_class = None
    
    def visit_Assign(self, node: ast.Assign):
        # Look for self-referencing assignments
        if self.current_class and self._is_self_reference(node):
            # Check for parent-child circular references
            for target in node.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    if target.value.id == 'self':
                        attr_name = target.attr
                        
                        # Check if this creates a circular reference
                        if isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name):
                                if node.value.func.id == self.current_class:
                                    # Parent creating child of same type
                                    for arg in node.value.args:
                                        if isinstance(arg, ast.Name) and arg.id == 'self':
                                            self.issues.append(MemoryLeakIssue(
                                                leak_type=MemoryLeakType.CIRCULAR_REFERENCE,
                                                location=f"{self.current_class}.{attr_name}",
                                                line_number=node.lineno,
                                                severity="high",
                                                description="Potential circular reference: parent-child cycle",
                                                recommendation="Use weakref for parent references",
                                                code_snippet=ast.unparse(node) if hasattr(ast, 'unparse') else None
                                            ))
        
        # Check for circular references in data structures
        if isinstance(node.value, ast.Dict):
            self._check_dict_circular_refs(node)
        
        self.generic_visit(node)
    
    def _is_self_reference(self, node: ast.Assign) -> bool:
        """Check if assignment creates a self-reference."""
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                    # Check if value references self
                    if self._contains_self_reference(node.value):
                        return True
        return False
    
    def _contains_self_reference(self, node: ast.AST) -> bool:
        """Recursively check if node contains reference to self."""
        if isinstance(node, ast.Name) and node.id == 'self':
            return True
        
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name) and child.value.id == 'self':
                    return True
        
        return False
    
    def _check_dict_circular_refs(self, node: ast.Assign):
        """Check for circular references in dictionary assignments."""
        dict_node = node.value
        if isinstance(dict_node, ast.Dict):
            for key, value in zip(dict_node.keys, dict_node.values):
                # Check if key is 'self' string and value references self
                if (isinstance(key, ast.Constant) and key.value == 'self' and 
                    self._contains_self_reference(value)):
                    self.issues.append(MemoryLeakIssue(
                        leak_type=MemoryLeakType.CIRCULAR_REFERENCE,
                        location=f"Dictionary at line {node.lineno}",
                        line_number=node.lineno,
                        severity="high",
                        description="Dictionary contains circular reference to self",
                        recommendation="Consider using weakref for self-references in dictionaries"
                    ))
                elif self._contains_self_reference(value):
                    self.issues.append(MemoryLeakIssue(
                        leak_type=MemoryLeakType.CIRCULAR_REFERENCE,
                        location=f"Dictionary at line {node.lineno}",
                        line_number=node.lineno,
                        severity="medium",
                        description="Dictionary contains reference to self",
                        recommendation="Consider using weakref for self-references in dictionaries"
                    ))
    
    def get_issues(self) -> List[MemoryLeakIssue]:
        return self.issues


class CleanupAnalyzer(ast.NodeVisitor):
    """Analyzes code for missing cleanup patterns."""
    
    def __init__(self):
        self.issues: List[MemoryLeakIssue] = []
        self.current_class: Optional[str] = None
        self.has_init: Dict[str, bool] = {}
        self.has_del: Dict[str, bool] = {}
        self.resources_acquired: Dict[str, Set[str]] = {}
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        self.has_init[node.name] = False
        self.has_del[node.name] = False
        self.resources_acquired[node.name] = set()
        
        self.generic_visit(node)
        
        # Check if class acquires resources but lacks __del__
        if self.has_init[node.name] and self.resources_acquired[node.name] and not self.has_del[node.name]:
            self.issues.append(MemoryLeakIssue(
                leak_type=MemoryLeakType.MISSING_CLEANUP,
                location=f"Class {node.name}",
                line_number=node.lineno,
                severity="high",
                description="Class acquires resources but lacks __del__ method",
                recommendation="Implement __del__ method or use context manager pattern"
            ))
        
        self.current_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.current_class:
            if node.name == '__init__':
                self.has_init[self.current_class] = True
                self._analyze_init_resources(node)
            elif node.name == '__del__':
                self.has_del[self.current_class] = True
        
        self.generic_visit(node)
    
    def _analyze_init_resources(self, node: ast.FunctionDef):
        """Analyze __init__ method for resource acquisition."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                # Check for file opens, socket connections, etc.
                if isinstance(stmt.func, ast.Name):
                    if stmt.func.id in ['open', 'socket', 'connect']:
                        self.resources_acquired[self.current_class].add(stmt.func.id)
                elif isinstance(stmt.func, ast.Attribute):
                    if stmt.func.attr in ['open', 'connect', 'acquire']:
                        self.resources_acquired[self.current_class].add(stmt.func.attr)
    
    def get_issues(self) -> List[MemoryLeakIssue]:
        return self.issues


class GlobalCacheAnalyzer(ast.NodeVisitor):
    """Analyzes code for unbounded global cache growth."""
    
    def __init__(self):
        self.issues: List[MemoryLeakIssue] = []
        self.global_dicts: Set[str] = set()
        self.cache_additions: Dict[str, List[int]] = {}
        self.cache_removals: Dict[str, List[int]] = {}
    
    def visit_Assign(self, node: ast.Assign):
        # Check for global dictionary/cache assignments
        for target in node.targets:
            if isinstance(target, ast.Name) and isinstance(node.value, (ast.Dict, ast.Call)):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    if node.value.func.id in ['dict', 'defaultdict', 'OrderedDict']:
                        self.global_dicts.add(target.id)
                elif isinstance(node.value, ast.Dict):
                    self.global_dicts.add(target.id)
        
        self.generic_visit(node)
    
    def visit_Subscript(self, node: ast.Subscript):
        # Check for cache additions (dict[key] = value)
        if isinstance(node.ctx, ast.Store):
            if isinstance(node.value, ast.Name) and node.value.id in self.global_dicts:
                if node.value.id not in self.cache_additions:
                    self.cache_additions[node.value.id] = []
                self.cache_additions[node.value.id].append(node.lineno)
        
        self.generic_visit(node)
    
    def visit_Delete(self, node: ast.Delete):
        # Check for cache removals
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name) and target.value.id in self.global_dicts:
                    if target.value.id not in self.cache_removals:
                        self.cache_removals[target.value.id] = []
                    self.cache_removals[target.value.id].append(node.lineno)
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[MemoryLeakIssue]:
        # Check for caches that have additions but no removals
        for cache_name in self.cache_additions:
            if cache_name not in self.cache_removals or len(self.cache_removals[cache_name]) == 0:
                if len(self.cache_additions[cache_name]) > 0:
                    self.issues.append(MemoryLeakIssue(
                        leak_type=MemoryLeakType.GLOBAL_CACHE_GROWTH,
                        location=f"Global cache '{cache_name}'",
                        line_number=self.cache_additions[cache_name][0],
                        severity="high",
                        description="Cache only adds items, never removes them",
                        recommendation="Implement cache eviction policy (LRU, TTL, size limit)"
                    ))
        
        return self.issues


class GeneratorAnalyzer(ast.NodeVisitor):
    """Analyzes generator usage for potential memory issues."""
    
    def __init__(self):
        self.issues: List[MemoryLeakIssue] = []
        self.generator_vars: Set[str] = set()
    
    def visit_Assign(self, node: ast.Assign):
        # Check for generator assignments
        if isinstance(node.value, (ast.GeneratorExp, ast.Call)):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                if 'generator' in node.value.func.id.lower() or node.value.func.id in ['iter', 'itertools']:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.generator_vars.add(target.id)
        
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For):
        # Check if generator is used in for loop without proper cleanup
        if isinstance(node.iter, ast.Name) and node.iter.id in self.generator_vars:
            # Check if there's a break without cleanup
            has_break = any(isinstance(stmt, ast.Break) for stmt in ast.walk(node))
            if has_break:
                self.issues.append(MemoryLeakIssue(
                    leak_type=MemoryLeakType.GENERATOR_EXHAUSTION,
                    location=f"Generator '{node.iter.id}' in for loop",
                    line_number=node.lineno,
                    severity="medium",
                    description="Generator may not be properly closed on early exit",
                    recommendation="Use try/finally or contextlib.closing for generator cleanup"
                ))
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[MemoryLeakIssue]:
        return self.issues


class EventListenerAnalyzer(ast.NodeVisitor):
    """Analyzes event listener registration/removal patterns."""
    
    def __init__(self):
        self.issues: List[MemoryLeakIssue] = []
        self.listener_registrations: Dict[str, List[int]] = {}
        self.listener_removals: Dict[str, List[int]] = {}
    
    def visit_Call(self, node: ast.Call):
        # Check for event listener registration patterns
        if isinstance(node.func, ast.Attribute):
            if any(pattern in node.func.attr.lower() for pattern in ['add_listener', 'on', 'bind', 'subscribe', 'register']):
                obj_name = ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'unknown'
                if obj_name not in self.listener_registrations:
                    self.listener_registrations[obj_name] = []
                self.listener_registrations[obj_name].append(node.lineno)
            
            elif any(pattern in node.func.attr.lower() for pattern in ['remove_listener', 'off', 'unbind', 'unsubscribe', 'unregister']):
                obj_name = ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'unknown'
                if obj_name not in self.listener_removals:
                    self.listener_removals[obj_name] = []
                self.listener_removals[obj_name].append(node.lineno)
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[MemoryLeakIssue]:
        # Check for listeners that are registered but never removed
        for obj_name, registrations in self.listener_registrations.items():
            if obj_name not in self.listener_removals or len(self.listener_removals[obj_name]) < len(registrations):
                self.issues.append(MemoryLeakIssue(
                    leak_type=MemoryLeakType.EVENT_LISTENER_LEAK,
                    location=f"Event listeners on '{obj_name}'",
                    line_number=registrations[0],
                    severity="medium",
                    description="Event listeners registered but not all removed",
                    recommendation="Ensure all event listeners are removed when no longer needed"
                ))
        
        return self.issues