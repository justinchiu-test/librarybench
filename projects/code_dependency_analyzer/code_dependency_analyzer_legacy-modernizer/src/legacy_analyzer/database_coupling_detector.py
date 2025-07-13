"""Database coupling detection module."""

import ast
import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set

from .models import DatabaseCoupling


class DatabaseCouplingDetector:
    """Detects database coupling through shared imports and SQL analysis."""

    # Common ORM patterns
    ORM_PATTERNS = {
        "sqlalchemy": ["Base", "declarative_base", "Table", "Column", "create_engine"],
        "django": ["models.Model", "models.CharField", "models.ForeignKey"],
        "peewee": ["Model", "CharField", "ForeignKeyField"],
        "tortoise": ["Model", "fields.CharField", "fields.ForeignKeyField"],
    }

    # SQL keywords for raw query detection
    SQL_KEYWORDS = [
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "FROM",
        "WHERE",
        "JOIN",
        "TABLE",
        "INTO",
        "VALUES",
    ]

    def __init__(self) -> None:
        self.module_db_access: Dict[str, Set[str]] = defaultdict(set)
        self.module_tables: Dict[str, Set[str]] = defaultdict(set)
        self.module_orm_models: Dict[str, Set[str]] = defaultdict(set)
        self.module_raw_queries: Dict[str, List[str]] = defaultdict(list)

    def analyze_database_coupling(self, root_path: str) -> List[DatabaseCoupling]:
        """Analyze codebase for database coupling patterns."""
        self.module_db_access.clear()
        self.module_tables.clear()
        self.module_orm_models.clear()
        self.module_raw_queries.clear()

        # Analyze all Python files
        for file_path in self._find_python_files(root_path):
            self._analyze_file(file_path, root_path)

        # Find coupled modules
        return self._find_coupled_modules()

    def _find_python_files(self, root_path: str) -> List[str]:
        """Find all Python files in the given directory."""
        python_files = []
        for root, _, files in os.walk(root_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files

    def _analyze_file(self, file_path: str, root_path: str) -> None:
        """Analyze a single file for database access patterns."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            relative_path = os.path.relpath(file_path, root_path)

            # Detect ORM usage
            self._detect_orm_usage(tree, relative_path)

            # Detect table references
            self._detect_table_references(tree, content, relative_path)

            # Detect raw SQL queries
            self._detect_raw_sql(content, relative_path)

        except Exception:
            # Skip files that can't be parsed
            pass

    def _detect_orm_usage(self, tree: ast.AST, module_path: str) -> None:
        """Detect ORM model usage in the AST."""
        for node in ast.walk(tree):
            # Check for class definitions that inherit from ORM base classes
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_str = (
                        ast.unparse(base)
                        if hasattr(ast, "unparse")
                        else self._ast_to_str(base)
                    )

                    # Check if it's an ORM model
                    for orm, patterns in self.ORM_PATTERNS.items():
                        if any(pattern in base_str for pattern in patterns):
                            self.module_orm_models[module_path].add(node.name)
                            self.module_db_access[module_path].add(orm)

                            # Try to extract table name
                            table_name = self._extract_table_name(node, orm)
                            if table_name:
                                self.module_tables[module_path].add(table_name)

            # Check for ORM imports
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    for orm in self.ORM_PATTERNS:
                        if orm in node.module:
                            self.module_db_access[module_path].add(orm)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    for orm in self.ORM_PATTERNS:
                        if orm in alias.name:
                            self.module_db_access[module_path].add(orm)

    def _ast_to_str(self, node: ast.AST) -> str:
        """Convert AST node to string (fallback for older Python versions)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._ast_to_str(node.value)}.{node.attr}"
        return ""

    def _extract_table_name(
        self, class_node: ast.ClassDef, orm_type: str
    ) -> Optional[str]:
        """Extract table name from ORM model definition."""
        # Look for __tablename__ attribute (SQLAlchemy)
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__tablename__":
                        if isinstance(node.value, ast.Constant):
                            return node.value.value

        # Look for Meta class with db_table (Django)
        for node in class_node.body:
            if isinstance(node, ast.ClassDef) and node.name == "Meta":
                for meta_node in node.body:
                    if isinstance(meta_node, ast.Assign):
                        for target in meta_node.targets:
                            if isinstance(target, ast.Name) and target.id == "db_table":
                                if isinstance(meta_node.value, ast.Constant):
                                    return meta_node.value.value

        # Default to class name as table name
        return class_node.name.lower()

    def _detect_table_references(
        self, tree: ast.AST, content: str, module_path: str
    ) -> None:
        """Detect direct table references in code."""
        # Look for string literals that might be table names
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value.strip()

                # Check if it looks like a table name or SQL fragment
                if (value.isidentifier() or "_" in value) and " " not in value:
                    # Simple heuristic: lowercase identifiers with underscores
                    if value.islower() and "_" in value:
                        self.module_tables[module_path].add(value)

    def _detect_raw_sql(self, content: str, module_path: str) -> None:
        """Detect raw SQL queries in the code."""
        # Look for SQL keywords in strings
        string_pattern = r'["\']([^"\']+)["\']'
        strings = re.findall(string_pattern, content)

        for string_content in strings:
            upper_content = string_content.upper()

            # Check if string contains SQL keywords
            sql_keyword_count = sum(
                1 for keyword in self.SQL_KEYWORDS if keyword in upper_content
            )

            if sql_keyword_count >= 2:  # At least 2 SQL keywords
                self.module_raw_queries[module_path].append(string_content)

                # Try to extract table names from SQL
                table_pattern = (
                    r"(?:FROM|JOIN|INTO|UPDATE|TABLE)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
                )
                tables = re.findall(table_pattern, upper_content)
                for table in tables:
                    self.module_tables[module_path].add(table.lower())

    def _find_coupled_modules(self) -> List[DatabaseCoupling]:
        """Find modules that share database access."""
        couplings = []

        # Group modules by shared tables
        table_to_modules: Dict[str, Set[str]] = defaultdict(set)
        for module, tables in self.module_tables.items():
            for table in tables:
                table_to_modules[table].add(module)

        # Group modules by shared ORM models
        model_to_modules: Dict[str, Set[str]] = defaultdict(set)
        for module, models in self.module_orm_models.items():
            for model in models:
                model_to_modules[model].add(module)

        # Create coupling entries for shared tables
        for table, modules in table_to_modules.items():
            if len(modules) > 1:
                module_list = list(modules)

                # Calculate coupling strength
                total_tables = sum(len(self.module_tables[m]) for m in module_list)
                avg_tables = total_tables / len(module_list) if module_list else 0
                coupling_strength = min(
                    1.0, len(module_list) / 10.0 * (1 + 1 / (avg_tables + 1))
                )

                # Estimate decoupling effort
                raw_query_count = sum(
                    len(self.module_raw_queries[m]) for m in module_list
                )
                effort_hours = (
                    len(module_list) * 8  # Base effort per module
                    + raw_query_count * 2  # Extra effort for raw queries
                    + len(module_list)
                    * len(module_list)
                    * 0.5  # Integration complexity
                )

                coupling = DatabaseCoupling(
                    coupled_modules=module_list,
                    shared_tables=[table],
                    orm_models=[],
                    raw_sql_queries=[],
                    coupling_strength=coupling_strength,
                    decoupling_effort_hours=effort_hours,
                )

                # Add raw SQL queries if any
                for module in module_list:
                    coupling.raw_sql_queries.extend(
                        self.module_raw_queries.get(module, [])
                    )

                couplings.append(coupling)

        # Create coupling entries for shared ORM models
        for model, modules in model_to_modules.items():
            if len(modules) > 1:
                module_list = list(modules)

                # Check if we already have a coupling for these modules
                existing_coupling = None
                for coupling in couplings:
                    if set(coupling.coupled_modules) == set(module_list):
                        existing_coupling = coupling
                        break

                if existing_coupling:
                    existing_coupling.orm_models.append(model)
                else:
                    coupling_strength = min(1.0, len(module_list) / 5.0)
                    effort_hours = len(module_list) * 12

                    coupling = DatabaseCoupling(
                        coupled_modules=module_list,
                        shared_tables=[],
                        orm_models=[model],
                        raw_sql_queries=[],
                        coupling_strength=coupling_strength,
                        decoupling_effort_hours=effort_hours,
                    )
                    couplings.append(coupling)

        return couplings
