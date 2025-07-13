"""Concurrency Analyzer for detecting race conditions and thread safety issues."""

import ast
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ConcurrencyIssueType(Enum):
    """Types of concurrency issues that can be detected."""
    
    RACE_CONDITION = "Race Condition"
    DEADLOCK_RISK = "Potential Deadlock"
    MISSING_SYNCHRONIZATION = "Missing Synchronization"
    BLOCKING_IN_ASYNC = "Blocking Operation in Async Context"
    THREAD_UNSAFE_OPERATION = "Thread-Unsafe Operation"
    IMPROPER_LOCK_USAGE = "Improper Lock Usage"
    SHARED_STATE_MUTATION = "Unprotected Shared State Mutation"


@dataclass
class ConcurrencyIssue:
    """Represents a detected concurrency issue."""
    
    issue_type: ConcurrencyIssueType
    location: str
    line_number: int
    severity: str  # "high", "medium", "low"
    description: str
    recommendation: str
    affected_resources: List[str]
    context: Optional[str] = None  # "threading", "asyncio", "multiprocessing"


class ConcurrencyAnalyzer:
    """Analyzes code for concurrency anti-patterns and race conditions."""
    
    def __init__(self):
        self._thread_safe_types = {
            'queue.Queue', 'threading.Lock', 'threading.RLock',
            'threading.Semaphore', 'threading.Event', 'threading.Condition'
        }
        self._unsafe_operations = {
            'append', 'extend', 'remove', 'pop', 'clear',
            'update', 'setdefault', 'popitem'
        }
    
    def analyze_file(self, file_path: str) -> List[ConcurrencyIssue]:
        """Analyze a Python file for concurrency patterns.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            List of ConcurrencyIssue objects
        """
        with open(file_path, 'r') as f:
            source = f.read()
        
        return self.analyze_source(source)
    
    def analyze_source(self, source: str) -> List[ConcurrencyIssue]:
        """Analyze Python source code for concurrency patterns.
        
        Args:
            source: Python source code as string
            
        Returns:
            List of ConcurrencyIssue objects
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        issues = []
        
        # Run different analyzers
        shared_state_analyzer = SharedStateAnalyzer()
        shared_state_analyzer.visit(tree)
        issues.extend(shared_state_analyzer.get_issues())
        
        lock_analyzer = LockUsageAnalyzer()
        lock_analyzer.visit(tree)
        issues.extend(lock_analyzer.get_issues())
        
        async_analyzer = AsyncPatternAnalyzer()
        async_analyzer.visit(tree)
        issues.extend(async_analyzer.get_issues())
        
        thread_safety_analyzer = ThreadSafetyAnalyzer()
        thread_safety_analyzer.visit(tree)
        issues.extend(thread_safety_analyzer.get_issues())
        
        deadlock_analyzer = DeadlockAnalyzer()
        deadlock_analyzer.visit(tree)
        issues.extend(deadlock_analyzer.get_issues())
        
        return issues


class SharedStateAnalyzer(ast.NodeVisitor):
    """Analyzes shared state access patterns."""
    
    def __init__(self):
        self.issues: List[ConcurrencyIssue] = []
        self.global_vars: Set[str] = set()
        self.class_vars: Dict[str, Set[str]] = {}
        self.current_class: Optional[str] = None
        self.in_thread_context: bool = False
        self.protected_blocks: List[Tuple[int, int]] = []
        self.has_threading_import: bool = False
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if 'threading' in alias.name or 'concurrent' in alias.name:
                self.has_threading_import = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module and ('threading' in node.module or 'concurrent' in node.module):
            self.has_threading_import = True
        self.generic_visit(node)
    
    def visit_Global(self, node: ast.Global):
        self.global_vars.update(node.names)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        old_class = self.current_class
        self.current_class = node.name
        self.class_vars[node.name] = set()
        
        # Check for class-level variables
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        self.class_vars[node.name].add(target.id)
        
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Check if this is a thread-related function
        if any(decorator for decorator in node.decorator_list
               if self._is_thread_decorator(decorator)):
            self.in_thread_context = True
        
        # Check for thread creation in function
        old_context = self.in_thread_context
        if self._creates_thread(node):
            self.in_thread_context = True
        
        # Also check if function name suggests threading
        if any(word in node.name.lower() for word in ['thread', 'worker', 'concurrent', 'increment']):
            self.in_thread_context = True
        
        self.generic_visit(node)
        self.in_thread_context = old_context
    
    def visit_With(self, node: ast.With):
        # Track protected blocks (with lock:)
        for item in node.items:
            if self._is_lock_context(item.context_expr):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                self.protected_blocks.append((start_line, end_line))
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        # Consider in thread context if threading is imported and we're in a function that might use threads
        effective_thread_context = self.in_thread_context or self.has_threading_import
        
        if effective_thread_context:
            # Check for unprotected shared state mutation
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in self.global_vars:
                    if not self._is_protected(node.lineno):
                        self.issues.append(ConcurrencyIssue(
                            issue_type=ConcurrencyIssueType.SHARED_STATE_MUTATION,
                            location=f"Global variable '{target.id}'",
                            line_number=node.lineno,
                            severity="high",
                            description="Modifying global variable without synchronization",
                            recommendation="Use threading.Lock or other synchronization primitive",
                            affected_resources=[target.id],
                            context="threading"
                        ))
                
                elif isinstance(target, ast.Attribute) and self.current_class:
                    # Check for class variable mutation
                    if isinstance(target.value, ast.Name) and target.value.id == 'self':
                        if not self._is_protected(node.lineno) and effective_thread_context:
                            self.issues.append(ConcurrencyIssue(
                                issue_type=ConcurrencyIssueType.SHARED_STATE_MUTATION,
                                location=f"Instance variable 'self.{target.attr}'",
                                line_number=node.lineno,
                                severity="high",
                                description="Modifying instance variable without synchronization",
                                recommendation="Protect with lock or use thread-safe data structure",
                                affected_resources=[f"self.{target.attr}"],
                                context="threading"
                            ))
        
        self.generic_visit(node)
    
    def _is_thread_decorator(self, decorator: ast.AST) -> bool:
        """Check if decorator indicates thread execution."""
        if isinstance(decorator, ast.Name):
            return decorator.id in ['thread', 'threaded', 'async_thread']
        return False
    
    def _creates_thread(self, node: ast.FunctionDef) -> bool:
        """Check if function creates threads."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                if isinstance(stmt.func, ast.Attribute):
                    if stmt.func.attr in ['Thread', 'start', 'submit']:
                        return True
                elif isinstance(stmt.func, ast.Name):
                    if stmt.func.id in ['Thread', 'ThreadPoolExecutor']:
                        return True
            # Also check for threading.Thread pattern
            elif isinstance(stmt, ast.Name):
                if 'thread' in stmt.id.lower() or 'Thread' in stmt.id:
                    return True
        return False
    
    def _is_lock_context(self, node: ast.AST) -> bool:
        """Check if node represents a lock context."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return 'lock' in node.func.id.lower()
            elif isinstance(node.func, ast.Attribute):
                return 'lock' in node.func.attr.lower()
        elif isinstance(node, ast.Name):
            return 'lock' in node.id.lower()
        return False
    
    def _is_protected(self, line_number: int) -> bool:
        """Check if line is within a protected block."""
        return any(start <= line_number <= end for start, end in self.protected_blocks)
    
    def get_issues(self) -> List[ConcurrencyIssue]:
        return self.issues


class LockUsageAnalyzer(ast.NodeVisitor):
    """Analyzes lock usage patterns for deadlock risks."""
    
    def __init__(self):
        self.issues: List[ConcurrencyIssue] = []
        self.lock_acquisitions: Dict[str, List[Tuple[str, int]]] = {}
        self.current_function: Optional[str] = None
        self.lock_order: Dict[str, List[str]] = {}
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_function = self.current_function
        self.current_function = node.name
        self.lock_order[node.name] = []
        self.generic_visit(node)
        
        # Check for potential deadlocks
        if len(self.lock_order[node.name]) > 1:
            self._check_lock_ordering(node.name)
        
        self.current_function = old_function
    
    def visit_With(self, node: ast.With):
        if self.current_function:
            for item in node.items:
                lock_name = self._extract_lock_name(item.context_expr)
                if lock_name:
                    self.lock_order[self.current_function].append(lock_name)
                    
                    # Check for nested locks
                    if len(self.lock_order[self.current_function]) > 1:
                        self._check_nested_locks(node)
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        # Check for acquire/release patterns
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'acquire':
                lock_name = self._extract_lock_name(node.func.value)
                if lock_name and self.current_function:
                    # Look for corresponding release
                    if not self._has_matching_release(node, lock_name):
                        self.issues.append(ConcurrencyIssue(
                            issue_type=ConcurrencyIssueType.IMPROPER_LOCK_USAGE,
                            location=self.current_function,
                            line_number=node.lineno,
                            severity="high",
                            description=f"Lock '{lock_name}' acquired but not released",
                            recommendation="Ensure lock.release() is called or use 'with' statement",
                            affected_resources=[lock_name],
                            context="threading"
                        ))
        
        self.generic_visit(node)
    
    def _extract_lock_name(self, node: ast.AST) -> Optional[str]:
        """Extract lock variable name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._extract_lock_name(node.func)
        return None
    
    def _check_lock_ordering(self, function_name: str):
        """Check for inconsistent lock ordering that could cause deadlocks."""
        locks = self.lock_order[function_name]
        # Compare with other functions
        for other_func, other_locks in self.lock_order.items():
            if other_func != function_name and len(other_locks) > 1:
                # Check if locks are acquired in different order
                common_locks = set(locks) & set(other_locks)
                if len(common_locks) > 1:
                    # Check ordering
                    for i, lock1 in enumerate(locks):
                        for j, lock2 in enumerate(locks[i+1:], i+1):
                            if lock1 in other_locks and lock2 in other_locks:
                                other_idx1 = other_locks.index(lock1)
                                other_idx2 = other_locks.index(lock2)
                                if other_idx1 > other_idx2:
                                    self.issues.append(ConcurrencyIssue(
                                        issue_type=ConcurrencyIssueType.DEADLOCK_RISK,
                                        location=f"{function_name} and {other_func}",
                                        line_number=0,  # Would need to track actual line
                                        severity="high",
                                        description=f"Inconsistent lock ordering: {lock1}, {lock2}",
                                        recommendation="Acquire locks in consistent order across all code paths",
                                        affected_resources=[lock1, lock2],
                                        context="threading"
                                    ))
    
    def _check_nested_locks(self, node: ast.With):
        """Check for risky nested lock patterns."""
        if len(node.items) > 1:
            self.issues.append(ConcurrencyIssue(
                issue_type=ConcurrencyIssueType.DEADLOCK_RISK,
                location=self.current_function or "unknown",
                line_number=node.lineno,
                severity="medium",
                description="Multiple locks acquired simultaneously",
                recommendation="Consider acquiring locks separately or using threading.RLock",
                affected_resources=[],
                context="threading"
            ))
    
    def _has_matching_release(self, acquire_node: ast.Call, lock_name: str) -> bool:
        """Check if there's a matching release for an acquire."""
        # This is a simplified check - would need control flow analysis
        return False  # Conservative approach
    
    def get_issues(self) -> List[ConcurrencyIssue]:
        return self.issues


class AsyncPatternAnalyzer(ast.NodeVisitor):
    """Analyzes async/await patterns for concurrency issues."""
    
    def __init__(self):
        self.issues: List[ConcurrencyIssue] = []
        self.in_async_context: bool = False
        self.current_function: Optional[str] = None
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        old_context = self.in_async_context
        old_function = self.current_function
        self.in_async_context = True
        self.current_function = node.name
        
        self.generic_visit(node)
        
        self.in_async_context = old_context
        self.current_function = old_function
    
    def visit_Call(self, node: ast.Call):
        if self.in_async_context:
            # Check for blocking operations in async context
            if self._is_blocking_operation(node):
                self.issues.append(ConcurrencyIssue(
                    issue_type=ConcurrencyIssueType.BLOCKING_IN_ASYNC,
                    location=self.current_function or "async function",
                    line_number=node.lineno,
                    severity="high",
                    description="Blocking I/O operation in async function",
                    recommendation="Use async equivalent (e.g., aiofiles, httpx)",
                    affected_resources=[],
                    context="asyncio"
                ))
            
            # Check for thread operations in async
            if self._is_thread_operation(node):
                self.issues.append(ConcurrencyIssue(
                    issue_type=ConcurrencyIssueType.THREAD_UNSAFE_OPERATION,
                    location=self.current_function or "async function",
                    line_number=node.lineno,
                    severity="medium",
                    description="Thread operation in async context",
                    recommendation="Use asyncio.to_thread() or loop.run_in_executor()",
                    affected_resources=[],
                    context="asyncio"
                ))
        
        self.generic_visit(node)
    
    def _is_blocking_operation(self, node: ast.Call) -> bool:
        """Check if call is a blocking operation."""
        blocking_funcs = {'open', 'read', 'write', 'sleep', 'requests.get', 'requests.post'}
        
        if isinstance(node.func, ast.Name):
            return node.func.id in blocking_funcs
        elif isinstance(node.func, ast.Attribute):
            func_name = f"{node.func.value.id if isinstance(node.func.value, ast.Name) else ''}.{node.func.attr}"
            return any(blocking in func_name for blocking in blocking_funcs)
        
        return False
    
    def _is_thread_operation(self, node: ast.Call) -> bool:
        """Check if call involves threading."""
        thread_indicators = ['Thread', 'ThreadPoolExecutor', 'threading.']
        
        if isinstance(node.func, ast.Name):
            return any(ind in node.func.id for ind in thread_indicators)
        elif isinstance(node.func, ast.Attribute):
            return any(ind in node.func.attr for ind in thread_indicators)
        
        return False
    
    def get_issues(self) -> List[ConcurrencyIssue]:
        return self.issues


class ThreadSafetyAnalyzer(ast.NodeVisitor):
    """Analyzes thread safety of operations."""
    
    def __init__(self):
        self.issues: List[ConcurrencyIssue] = []
        self.shared_collections: Dict[str, str] = {}  # name -> type
        self.in_thread_context: bool = False
    
    def visit_Assign(self, node: ast.Assign):
        # Track collection assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.List):
                    self.shared_collections[target.id] = 'list'
                elif isinstance(node.value, ast.Dict):
                    self.shared_collections[target.id] = 'dict'
                elif isinstance(node.value, ast.Set):
                    self.shared_collections[target.id] = 'set'
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        # Check for unsafe operations on shared collections
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                var_name = node.func.value.id
                if var_name in self.shared_collections:
                    if node.func.attr in ['append', 'extend', 'remove', 'pop', 'clear', 'update']:
                        self.issues.append(ConcurrencyIssue(
                            issue_type=ConcurrencyIssueType.THREAD_UNSAFE_OPERATION,
                            location=f"Operation on {var_name}",
                            line_number=node.lineno,
                            severity="high",
                            description=f"Thread-unsafe operation '{node.func.attr}' on shared {self.shared_collections[var_name]}",
                            recommendation="Use thread-safe collection (e.g., queue.Queue) or protect with lock",
                            affected_resources=[var_name],
                            context="threading"
                        ))
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[ConcurrencyIssue]:
        return self.issues


class DeadlockAnalyzer(ast.NodeVisitor):
    """Analyzes code for potential deadlock scenarios."""
    
    def __init__(self):
        self.issues: List[ConcurrencyIssue] = []
        self.wait_conditions: List[Tuple[str, int]] = []
        self.signal_conditions: List[Tuple[str, int]] = []
    
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            # Check for wait without timeout
            if node.func.attr in ['wait', 'join']:
                has_timeout = any(
                    keyword.arg == 'timeout' for keyword in node.keywords
                ) or len(node.args) > 0
                
                if not has_timeout:
                    self.issues.append(ConcurrencyIssue(
                        issue_type=ConcurrencyIssueType.DEADLOCK_RISK,
                        location="Wait operation",
                        line_number=node.lineno,
                        severity="medium",
                        description=f"{node.func.attr}() called without timeout",
                        recommendation="Always use timeout to prevent indefinite blocking",
                        affected_resources=[],
                        context="threading"
                    ))
            
            # Track condition variable usage
            if node.func.attr == 'wait':
                obj_name = ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'unknown'
                self.wait_conditions.append((obj_name, node.lineno))
            elif node.func.attr in ['notify', 'notify_all']:
                obj_name = ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'unknown'
                self.signal_conditions.append((obj_name, node.lineno))
        
        self.generic_visit(node)
    
    def get_issues(self) -> List[ConcurrencyIssue]:
        # Check for waits without corresponding signals
        wait_objects = {obj for obj, _ in self.wait_conditions}
        signal_objects = {obj for obj, _ in self.signal_conditions}
        
        missing_signals = wait_objects - signal_objects
        for obj in missing_signals:
            line = next((line for o, line in self.wait_conditions if o == obj), 0)
            self.issues.append(ConcurrencyIssue(
                issue_type=ConcurrencyIssueType.DEADLOCK_RISK,
                location=f"Condition variable '{obj}'",
                line_number=line,
                severity="high",
                description="wait() called but no corresponding notify()",
                recommendation="Ensure all wait() calls have matching notify() calls",
                affected_resources=[obj],
                context="threading"
            ))
        
        return self.issues