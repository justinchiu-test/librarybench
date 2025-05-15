"""SQL pattern detection utilities for query language interpreters."""

import re
from typing import Any, Dict, List, Pattern as RegexPattern, Set, Tuple, Union, Optional

from common.pattern.detector import BasePatternDetector
from common.pattern.matcher import PatternMatch
from common.models.enums import PrivacyFunction


class SQLPrivacyPatternDetector(BasePatternDetector):
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