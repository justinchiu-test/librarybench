"""Database Pattern Analyzer for detecting N+1 queries and inefficient database patterns."""

import ast
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DatabaseIssueType(Enum):
    """Types of database performance issues."""
    
    N_PLUS_1_QUERY = "N+1 Query Problem"
    MISSING_BULK_OPERATION = "Missing Bulk Operation"
    INEFFICIENT_PAGINATION = "Inefficient Pagination"
    MISSING_INDEX_HINT = "Missing Index Usage"
    EXCESSIVE_JOINS = "Excessive Joins"
    MISSING_CONNECTION_POOLING = "Missing Connection Pooling"
    UNBOUNDED_RESULT_SET = "Unbounded Result Set"


@dataclass
class DatabaseIssue:
    """Represents a detected database performance issue."""
    
    issue_type: DatabaseIssueType
    location: str
    line_number: int
    severity: str  # "high", "medium", "low"
    description: str
    recommendation: str
    orm_type: Optional[str] = None  # "django", "sqlalchemy", "peewee", etc.
    query_count_estimate: Optional[int] = None


class DatabasePatternAnalyzer:
    """Analyzes code for database performance anti-patterns."""
    
    def __init__(self):
        self._orm_patterns = {
            'django': DjangoORMAnalyzer(),
            'sqlalchemy': SQLAlchemyAnalyzer(),
            'peewee': PeeweeAnalyzer(),
            'generic': GenericORMAnalyzer(),
        }
    
    def analyze_file(self, file_path: str) -> List[DatabaseIssue]:
        """Analyze a Python file for database patterns.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            List of DatabaseIssue objects
        """
        with open(file_path, 'r') as f:
            source = f.read()
        
        return self.analyze_source(source)
    
    def analyze_source(self, source: str) -> List[DatabaseIssue]:
        """Analyze Python source code for database patterns.
        
        Args:
            source: Python source code as string
            
        Returns:
            List of DatabaseIssue objects
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        issues = []
        
        # Detect which ORM is being used
        orm_detector = ORMDetector()
        orm_detector.visit(tree)
        detected_orms = orm_detector.detected_orms
        
        # Run appropriate analyzers
        if not detected_orms:
            # Run generic analyzer if no specific ORM detected
            analyzer = self._orm_patterns['generic']
            analyzer.visit(tree)
            issues.extend(analyzer.get_issues())
        else:
            for orm in detected_orms:
                if orm in self._orm_patterns:
                    analyzer = self._orm_patterns[orm]
                    analyzer.visit(tree)
                    issues.extend(analyzer.get_issues())
        
        # Run general database pattern analysis
        general_analyzer = GeneralDatabaseAnalyzer()
        general_analyzer.visit(tree)
        issues.extend(general_analyzer.get_issues())
        
        return issues


class ORMDetector(ast.NodeVisitor):
    """Detects which ORM frameworks are being used."""
    
    def __init__(self):
        self.detected_orms: Set[str] = set()
        self._orm_imports = {
            'django.db': 'django',
            'sqlalchemy': 'sqlalchemy',
            'peewee': 'peewee',
            'tortoise': 'tortoise',
        }
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            for pattern, orm in self._orm_imports.items():
                if pattern in alias.name:
                    self.detected_orms.add(orm)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            for pattern, orm in self._orm_imports.items():
                if pattern in node.module:
                    self.detected_orms.add(orm)
        self.generic_visit(node)


class BaseORMAnalyzer(ast.NodeVisitor):
    """Base class for ORM-specific analyzers."""
    
    def __init__(self):
        self.issues: List[DatabaseIssue] = []
        self.current_function: Optional[str] = None
        self.loop_depth: int = 0
        self.queries_in_loop: List[Tuple[str, int]] = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_For(self, node: ast.For):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_While(self, node: ast.While):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def get_issues(self) -> List[DatabaseIssue]:
        return self.issues


class DjangoORMAnalyzer(BaseORMAnalyzer):
    """Analyzer specific to Django ORM patterns."""
    
    def visit_Attribute(self, node: ast.Attribute):
        # Detect Django ORM query methods
        if node.attr in ['all', 'filter', 'get', 'exclude', 'first', 'last']:
            if self.loop_depth > 0:
                # Query inside a loop - potential N+1
                self._check_for_n_plus_1(node)
        
        # Check for missing select_related/prefetch_related
        if node.attr in ['all', 'filter'] and self.loop_depth == 0:
            self._check_for_missing_prefetch(node)
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        # Check for bulk operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'create' and self.loop_depth > 0:
                self.issues.append(DatabaseIssue(
                    issue_type=DatabaseIssueType.MISSING_BULK_OPERATION,
                    location=self.current_function or "module level",
                    line_number=node.lineno,
                    severity="high",
                    description="Creating objects in a loop instead of using bulk_create",
                    recommendation="Use Model.objects.bulk_create() for multiple insertions",
                    orm_type="django"
                ))
            
            # Check for inefficient pagination
            if node.func.attr in ['all', 'filter']:
                self._check_pagination_pattern(node)
        
        self.generic_visit(node)
    
    def _check_for_n_plus_1(self, node: ast.Attribute):
        """Check for N+1 query patterns in Django."""
        # This is a simplified check - in practice would need more context
        self.issues.append(DatabaseIssue(
            issue_type=DatabaseIssueType.N_PLUS_1_QUERY,
            location=self.current_function or "module level",
            line_number=node.lineno,
            severity="high",
            description="Database query inside a loop - potential N+1 problem",
            recommendation="Use select_related() or prefetch_related() to optimize queries",
            orm_type="django"
        ))
    
    def _check_for_missing_prefetch(self, node: ast.Attribute):
        """Check if prefetch_related or select_related is missing."""
        # Look for patterns where related objects might be accessed
        # This is a heuristic - would need more sophisticated analysis
        pass
    
    def _check_pagination_pattern(self, node: ast.Call):
        """Check for inefficient pagination patterns."""
        # Look for offset-based pagination on large datasets
        for arg in node.args:
            if isinstance(arg, ast.Subscript):
                # Detected slicing - potential inefficient pagination
                if isinstance(arg.slice, ast.Slice):
                    if arg.slice.lower and isinstance(arg.slice.lower, ast.Constant):
                        if arg.slice.lower.value > 1000:
                            self.issues.append(DatabaseIssue(
                                issue_type=DatabaseIssueType.INEFFICIENT_PAGINATION,
                                location=self.current_function or "module level",
                                line_number=node.lineno,
                                severity="medium",
                                description="Large offset in pagination can be inefficient",
                                recommendation="Consider cursor-based pagination for large datasets",
                                orm_type="django"
                            ))


class SQLAlchemyAnalyzer(BaseORMAnalyzer):
    """Analyzer specific to SQLAlchemy patterns."""
    
    def visit_Attribute(self, node: ast.Attribute):
        # Detect SQLAlchemy query methods
        if node.attr in ['query', 'filter', 'all', 'first', 'one', 'items', 'orders']:
            if self.loop_depth > 0:
                self._check_for_n_plus_1(node)
        
        # Check for missing eager loading
        if node.attr == 'query':
            self._check_for_missing_eager_loading(node)
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        # Check for bulk operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['add', 'merge'] and self.loop_depth > 0:
                self.issues.append(DatabaseIssue(
                    issue_type=DatabaseIssueType.MISSING_BULK_OPERATION,
                    location=self.current_function or "module level",
                    line_number=node.lineno,
                    severity="high",
                    description="Adding/merging objects in a loop",
                    recommendation="Use bulk_insert_mappings() or bulk_save_objects()",
                    orm_type="sqlalchemy"
                ))
            
            # Check for missing limit on queries
            if node.func.attr in ['all', 'filter']:
                self._check_unbounded_queries(node)
        
        self.generic_visit(node)
    
    def _check_for_n_plus_1(self, node: ast.Attribute):
        """Check for N+1 query patterns in SQLAlchemy."""
        self.issues.append(DatabaseIssue(
            issue_type=DatabaseIssueType.N_PLUS_1_QUERY,
            location=self.current_function or "module level",
            line_number=node.lineno,
            severity="high",
            description="Query executed inside a loop - potential N+1 problem",
            recommendation="Use joinedload(), subqueryload(), or selectinload()",
            orm_type="sqlalchemy"
        ))
    
    def _check_for_missing_eager_loading(self, node: ast.Attribute):
        """Check if eager loading options are missing."""
        # This would need more context to determine if relationships are accessed
        pass
    
    def _check_unbounded_queries(self, node: ast.Call):
        """Check for queries without limits."""
        has_limit = any(
            isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'limit'
            for arg in ast.walk(node)
        )
        
        if not has_limit:
            self.issues.append(DatabaseIssue(
                issue_type=DatabaseIssueType.UNBOUNDED_RESULT_SET,
                location=self.current_function or "module level",
                line_number=node.lineno,
                severity="medium",
                description="Query without limit clause may return large result set",
                recommendation="Add .limit() to queries or implement pagination",
                orm_type="sqlalchemy"
            ))


class PeeweeAnalyzer(BaseORMAnalyzer):
    """Analyzer specific to Peewee ORM patterns."""
    
    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in ['select', 'get', 'where']:
            if self.loop_depth > 0:
                self._check_for_n_plus_1(node)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'create' and self.loop_depth > 0:
                self.issues.append(DatabaseIssue(
                    issue_type=DatabaseIssueType.MISSING_BULK_OPERATION,
                    location=self.current_function or "module level",
                    line_number=node.lineno,
                    severity="high",
                    description="Creating objects in a loop",
                    recommendation="Use insert_many() for bulk insertions",
                    orm_type="peewee"
                ))
        self.generic_visit(node)
    
    def _check_for_n_plus_1(self, node: ast.Attribute):
        self.issues.append(DatabaseIssue(
            issue_type=DatabaseIssueType.N_PLUS_1_QUERY,
            location=self.current_function or "module level",
            line_number=node.lineno,
            severity="high",
            description="Query in loop - potential N+1 issue",
            recommendation="Use prefetch() to eager load related objects",
            orm_type="peewee"
        ))


class GenericORMAnalyzer(BaseORMAnalyzer):
    """Generic analyzer for database patterns when ORM is unknown."""
    
    def visit_Call(self, node: ast.Call):
        # Look for common database operation patterns
        if isinstance(node.func, ast.Attribute):
            # Check for SQL execute patterns
            if node.func.attr in ['execute', 'executemany', 'fetchall', 'fetchone']:
                if self.loop_depth > 0:
                    self.issues.append(DatabaseIssue(
                        issue_type=DatabaseIssueType.N_PLUS_1_QUERY,
                        location=self.current_function or "module level",
                        line_number=node.lineno,
                        severity="high",
                        description="Database operation inside loop",
                        recommendation="Consider batching queries or using JOIN operations",
                        orm_type="generic"
                    ))
        
        self.generic_visit(node)


class GeneralDatabaseAnalyzer(ast.NodeVisitor):
    """Analyzes general database patterns regardless of ORM."""
    
    def __init__(self):
        self.issues: List[DatabaseIssue] = []
        self.connection_creations: List[int] = []
        self.connection_pool_usage: bool = False
    
    def visit_Call(self, node: ast.Call):
        # Check for connection creation patterns
        if isinstance(node.func, ast.Name):
            if node.func.id in ['connect', 'create_connection']:
                self.connection_creations.append(node.lineno)
            elif 'pool' in node.func.id.lower():
                self.connection_pool_usage = True
        
        # Check for raw SQL with potential issues
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['execute', 'executescript']:
                self._check_sql_patterns(node)
        
        self.generic_visit(node)
    
    def _check_sql_patterns(self, node: ast.Call):
        """Check for problematic SQL patterns."""
        if node.args:
            sql_arg = node.args[0]
            if isinstance(sql_arg, ast.Constant) and isinstance(sql_arg.value, str):
                sql = sql_arg.value.lower()
                
                # Check for SELECT * patterns
                if 'select *' in sql:
                    self.issues.append(DatabaseIssue(
                        issue_type=DatabaseIssueType.UNBOUNDED_RESULT_SET,
                        location="SQL query",
                        line_number=node.lineno,
                        severity="low",
                        description="SELECT * can retrieve unnecessary columns",
                        recommendation="Specify only required columns in SELECT statement"
                    ))
                
                # Check for missing WHERE clause
                if 'select' in sql and 'from' in sql and 'where' not in sql and 'limit' not in sql:
                    self.issues.append(DatabaseIssue(
                        issue_type=DatabaseIssueType.UNBOUNDED_RESULT_SET,
                        location="SQL query",
                        line_number=node.lineno,
                        severity="medium",
                        description="Query without WHERE or LIMIT clause",
                        recommendation="Add WHERE conditions or LIMIT to prevent large result sets"
                    ))
    
    def get_issues(self) -> List[DatabaseIssue]:
        # Check for missing connection pooling
        if len(self.connection_creations) > 1 and not self.connection_pool_usage:
            self.issues.append(DatabaseIssue(
                issue_type=DatabaseIssueType.MISSING_CONNECTION_POOLING,
                location="Multiple connection creations",
                line_number=self.connection_creations[0],
                severity="medium",
                description="Multiple database connections created without pooling",
                recommendation="Use connection pooling to reuse database connections"
            ))
        
        return self.issues