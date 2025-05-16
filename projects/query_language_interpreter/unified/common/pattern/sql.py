"""SQL pattern detection utilities for query language interpreters."""

import re
from typing import Any, Dict, List, Pattern as RegexPattern, Set, Tuple, Union, Optional

from common.pattern.detector import BasePatternDetector
from common.pattern.matcher import PatternMatch
from common.models.enums import PrivacyFunction


class SQLPatternMatch(PatternMatch):
    """Represents an SQL pattern match result."""
    
    def __init__(
        self,
        pattern_id: str,
        matched_text: str,
        start: int,
        end: int,
        sql_component: str,
        groups: Dict[str, str] = None,
        confidence: float = 0.0,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize an SQL pattern match.

        Args:
            pattern_id: Identifier of the pattern that matched
            matched_text: Text that matched the pattern
            start: Start position of the match
            end: End position of the match
            sql_component: SQL component type (SELECT, FROM, JOIN, etc.)
            groups: Named capturing groups
            confidence: Confidence score for the match
            metadata: Additional metadata
        """
        super().__init__(
            pattern_id=pattern_id,
            matched_text=matched_text,
            start=start,
            end=end,
            groups=groups,
            confidence=confidence,
            category=sql_component,
            metadata=metadata,
        )
        self.sql_component = sql_component
    
    def __str__(self) -> str:
        """String representation of the match.

        Returns:
            str: String representation
        """
        return f"SQLPatternMatch(pattern={self.pattern_id}, component={self.sql_component}, confidence={self.confidence:.2f})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "pattern_id": self.pattern_id,
            "matched_text": self.matched_text,
            "start": self.start,
            "end": self.end,
            "sql_component": self.sql_component,
            "confidence": self.confidence,
            "groups": self.groups,
            "metadata": self.metadata,
        }


class SQLPatternDetector(BasePatternDetector):
    """SQL pattern detector for query analysis."""
    
    # Common SQL patterns
    DEFAULT_PATTERNS = {
        "select_clause": {
            "regex": r"SELECT\s+(?P<projection>.+?)(?:\s+FROM|$)",
            "category": "SELECT",
            "threshold": 0.9,
        },
        "from_clause": {
            "regex": r"FROM\s+(?P<tables>.+?)(?:\s+(?:WHERE|GROUP BY|ORDER BY|LIMIT|JOIN)|$)",
            "category": "FROM",
            "threshold": 0.9,
        },
        "where_clause": {
            "regex": r"WHERE\s+(?P<conditions>.+?)(?:\s+(?:GROUP BY|ORDER BY|LIMIT)|$)",
            "category": "WHERE",
            "threshold": 0.9,
        },
        "join_clause": {
            "regex": r"(?P<join_type>(?:INNER|LEFT|RIGHT|FULL|OUTER|CROSS)?\s*JOIN)\s+(?P<table>.+?)\s+ON\s+(?P<condition>.+?)(?:\s+(?:WHERE|JOIN|GROUP BY|ORDER BY|LIMIT)|$)",
            "category": "JOIN",
            "threshold": 0.9,
        },
        "group_by_clause": {
            "regex": r"GROUP BY\s+(?P<columns>.+?)(?:\s+(?:HAVING|ORDER BY|LIMIT)|$)",
            "category": "GROUP_BY",
            "threshold": 0.9,
        },
        "order_by_clause": {
            "regex": r"ORDER BY\s+(?P<columns>.+?)(?:\s+(?:LIMIT)|$)",
            "category": "ORDER_BY",
            "threshold": 0.9,
        },
        "limit_clause": {
            "regex": r"LIMIT\s+(?P<limit>\d+)(?:\s+OFFSET\s+(?P<offset>\d+))?",
            "category": "LIMIT",
            "threshold": 0.9,
        },
        "insert_clause": {
            "regex": r"INSERT\s+INTO\s+(?P<table>.+?)\s*(?:\((?P<columns>.+?)\))?\s+VALUES\s*(?P<values>\(.+?\))",
            "category": "INSERT",
            "threshold": 0.9,
        },
        "update_clause": {
            "regex": r"UPDATE\s+(?P<table>.+?)\s+SET\s+(?P<set>.+?)(?:\s+WHERE\s+(?P<conditions>.+?))?(?:\s+(?:ORDER BY|LIMIT)|$)",
            "category": "UPDATE",
            "threshold": 0.9,
        },
        "delete_clause": {
            "regex": r"DELETE\s+FROM\s+(?P<table>.+?)(?:\s+WHERE\s+(?P<conditions>.+?))?(?:\s+(?:ORDER BY|LIMIT)|$)",
            "category": "DELETE",
            "threshold": 0.9,
        },
    }
    
    def __init__(self, patterns: Dict[str, Any] = None):
        """Initialize an SQL pattern detector.

        Args:
            patterns: Dictionary of pattern definitions
        """
        # Start with default patterns, then update with any custom patterns
        all_patterns = self.DEFAULT_PATTERNS.copy()
        if patterns:
            all_patterns.update(patterns)
        
        super().__init__(all_patterns)
    
    def detect(self, sql_query: str) -> List[SQLPatternMatch]:
        """Detect SQL patterns in a query.

        Args:
            sql_query: SQL query to analyze

        Returns:
            List[SQLPatternMatch]: List of SQL pattern matches
        """
        # Normalize query (remove extra whitespace and make uppercase)
        normalized_query = re.sub(r'\s+', ' ', sql_query).strip()
        
        # Get basic matches using parent method
        base_matches = super().detect(normalized_query)
        
        # Convert to SQL matches
        sql_matches = []
        for match in base_matches:
            # Create SQL match
            sql_match = SQLPatternMatch(
                pattern_id=match.pattern_id,
                matched_text=match.matched_text,
                start=match.start,
                end=match.end,
                sql_component=match.category,
                groups=match.groups,
                confidence=match.confidence,
                metadata=match.metadata,
            )
            
            sql_matches.append(sql_match)
        
        return sql_matches
    
    def extract_tables(self, sql_query: str) -> List[str]:
        """Extract table names from an SQL query.

        Args:
            sql_query: SQL query to analyze

        Returns:
            List[str]: List of table names
        """
        tables = []
        
        # Get FROM clause matches
        from_matches = self.detect_by_category(sql_query, "FROM")
        for match in from_matches:
            if "tables" in match.groups:
                tables_str = match.groups["tables"]
                # Split by commas and clean up
                table_parts = [t.strip() for t in tables_str.split(",")]
                tables.extend(table_parts)
        
        # Get JOIN clause matches
        join_matches = self.detect_by_category(sql_query, "JOIN")
        for match in join_matches:
            if "table" in match.groups:
                tables.append(match.groups["table"].strip())
        
        return tables
    
    def extract_columns(self, sql_query: str) -> List[str]:
        """Extract column names from an SQL query.

        Args:
            sql_query: SQL query to analyze

        Returns:
            List[str]: List of column names
        """
        columns = []
        
        # Get SELECT clause matches
        select_matches = self.detect_by_category(sql_query, "SELECT")
        for match in select_matches:
            if "projection" in match.groups:
                projection = match.groups["projection"]
                # Handle special case of SELECT *
                if projection.strip() == "*":
                    columns.append("*")
                else:
                    # Split by commas and clean up
                    col_parts = [c.strip() for c in projection.split(",")]
                    # Extract column names from complex expressions
                    for col in col_parts:
                        # Handle aliases with AS
                        if " AS " in col.upper():
                            col = col.split(" AS ")[0].strip()
                        # Handle function calls
                        if "(" in col:
                            # Extract column from function if possible
                            inside_parens = re.search(r'\((.+?)\)', col)
                            if inside_parens:
                                col_content = inside_parens.group(1).strip()
                                if col_content != "*":
                                    columns.append(col_content)
                        else:
                            columns.append(col)
        
        return columns
    
    def analyze_query(self, sql_query: str) -> Dict[str, Any]:
        """Analyze an SQL query and extract its components.

        Args:
            sql_query: SQL query to analyze

        Returns:
            Dict[str, Any]: Analysis results
        """
        matches = self.detect(sql_query)
        
        # Extract query type
        query_type = None
        if any(m.sql_component == "SELECT" for m in matches):
            query_type = "SELECT"
        elif any(m.sql_component == "INSERT" for m in matches):
            query_type = "INSERT"
        elif any(m.sql_component == "UPDATE" for m in matches):
            query_type = "UPDATE"
        elif any(m.sql_component == "DELETE" for m in matches):
            query_type = "DELETE"
        
        # Extract components
        components = {}
        for match in matches:
            components[match.sql_component] = {
                "text": match.matched_text,
                "groups": match.groups,
            }
        
        # Extract tables and columns
        tables = self.extract_tables(sql_query)
        columns = self.extract_columns(sql_query)
        
        return {
            "query_type": query_type,
            "components": components,
            "tables": tables,
            "columns": columns,
            "matches": [m.to_dict() for m in matches],
        }
    
    def extract_table_relationships(self, sql_text: str) -> List[Tuple[str, str]]:
        """Extract table relationships from JOIN conditions.
        
        Args:
            sql_text: SQL query text
            
        Returns:
            List of (table1, table2) relationship tuples
        """
        # This is a simplified implementation
        relationships = []
        
        # Extract JOIN ... ON conditions
        join_pattern = r'JOIN\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?\s+ON\s+([^WHERE]+)'
        join_matches = re.finditer(join_pattern, sql_text, re.IGNORECASE)
        
        for match in join_matches:
            join_table = match.group(1)
            join_alias = match.group(2) or join_table
            condition = match.group(3)
            
            # Extract tables from the condition
            condition_pattern = r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
            condition_matches = re.finditer(condition_pattern, condition)
            
            for cmatch in condition_matches:
                left_table, left_field, right_table, right_field = cmatch.groups()
                relationships.append((left_table, right_table))
        
        return relationships


class SQLPrivacyPatternDetector(SQLPatternDetector):
    """Pattern detector for SQL privacy functions."""
    
    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize the SQL privacy pattern detector.
        
        Args:
            confidence_threshold: Confidence threshold for matches
        """
        super().__init__()
        self.confidence_threshold = confidence_threshold
        self._initialize_patterns()
    
    def _initialize_patterns(self) -> None:
        """Initialize standard privacy function patterns."""
        # Create regex patterns for privacy functions
        function_pattern = r'(%s)\s*\(\s*([^,\)]+)(?:\s*,\s*([^\)]+))?\s*\)'
        
        # Add patterns for all privacy functions
        for func in PrivacyFunction:
            pattern = function_pattern % func.value
            self.add_pattern(
                pattern_id=func.value,
                regex=pattern,
                threshold=self.confidence_threshold,
                category="privacy_function",
                metadata={
                    "function_name": func.value,
                    "description": f"{func.value} privacy function"
                }
            )
    
    def detect_privacy_functions(self, sql_text: str) -> List[Dict[str, Any]]:
        """Extract privacy functions from SQL query.
        
        Args:
            sql_text: SQL query text
            
        Returns:
            List of extracted privacy functions with their parameters
        """
        # Find all privacy function patterns in the SQL
        matches = self.detect_by_category(sql_text, "privacy_function")
        
        # Parse the matches into a structured format
        extracted_functions = []
        for match in matches:
            # Get the function name (pattern_id)
            function_name = match.pattern_id
            
            # Extract field and arguments from the match
            groups = match.groups or {}
            # If no groups were captured, try to extract from the matched text
            if not groups and match.matched_text:
                # Extract field name from the function call
                field_match = re.search(r'\(\s*([^,\)]+)', match.matched_text)
                if field_match:
                    field_name = field_match.group(1).strip()
                    # Extract arguments if any
                    args_match = re.search(r',\s*([^\)]+)', match.matched_text)
                    args_text = args_match.group(1).strip() if args_match else ""
                    
                    # Parse arguments
                    args = self._parse_function_args(args_text)
                    
                    extracted_functions.append({
                        "function": function_name,
                        "field": field_name,
                        "args": args
                    })
            else:
                # If groups were captured, use them
                if len(groups) > 0:
                    field_name = groups.get('1', "").strip() if '1' in groups else ""
                    args_text = groups.get('2', "").strip() if '2' in groups else ""
                    
                    # Parse arguments
                    args = self._parse_function_args(args_text)
                    
                    extracted_functions.append({
                        "function": function_name,
                        "field": field_name,
                        "args": args
                    })
        
        return extracted_functions
    
    def has_privacy_functions(self, sql_text: str) -> bool:
        """Check if SQL contains privacy functions.
        
        Args:
            sql_text: SQL query text
            
        Returns:
            True if privacy functions are found, False otherwise
        """
        matches = self.detect_by_category(sql_text, "privacy_function")
        return len(matches) > 0
    
    def _parse_function_args(self, args_text: str) -> Dict[str, str]:
        """Parse function arguments from text.
        
        Args:
            args_text: Arguments text
            
        Returns:
            Dictionary of argument name-value pairs
        """
        if not args_text:
            return {}
            
        args = {}
        
        # Handle key=value arguments
        for arg_pair in args_text.split(','):
            if '=' in arg_pair:
                key, value = arg_pair.split('=', 1)
                args[key.strip()] = value.strip().strip("'\"")
            else:
                # Positional arguments
                args[f"arg{len(args) + 1}"] = arg_pair.strip().strip("'\"")
                
        return args