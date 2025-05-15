"""Pattern matching implementations for file content analysis.

This module provides implementations of the pattern matching framework,
offering ready-to-use pattern matching functionality.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Pattern, Optional, Any, Union, Callable
from enum import Enum

from pydantic import BaseModel, Field

from .base import PatternMatcher
from ..utils.types import (
    FileMetadata, SensitivityLevel, ComplianceCategory, 
    BaseScanMatch, FileCategory
)
from ..utils.file_utils import read_file_sample


class FilePattern(BaseModel):
    """Generic pattern definition for file matching."""
    
    name: str
    description: str
    pattern: str
    regex: Optional[Pattern] = Field(None, exclude=True)
    category: str
    sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM
    context_rules: List[str] = Field(default_factory=list)
    false_positive_examples: List[str] = Field(default_factory=list)
    validation_func: Optional[str] = None
    binary_pattern: Optional[bytes] = None
    
    def __init__(self, **data):
        """Initialize pattern with data."""
        super().__init__(**data)
        if self.pattern:
            self.regex = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)
    
    def match(self, content: str) -> List[str]:
        """
        Find all matches of this pattern in the given text content.
        
        Args:
            content: Text content to search
            
        Returns:
            List of matched strings
        """
        if not self.regex:
            return []
        return self.regex.findall(content)
    
    def match_binary(self, content: bytes) -> List[bytes]:
        """
        Find all matches of this pattern in the given binary content.
        
        Args:
            content: Binary content to search
            
        Returns:
            List of matched byte sequences
        """
        if not self.binary_pattern:
            # Try to convert regex pattern to bytes and search
            try:
                pattern_bytes = self.pattern.encode('utf-8')
                return [m for m in re.findall(pattern_bytes, content)]
            except:
                return []
        else:
            # Search for literal binary pattern
            matches = []
            start = 0
            while True:
                start = content.find(self.binary_pattern, start)
                if start == -1:
                    break
                matches.append(self.binary_pattern)
                start += len(self.binary_pattern)
            return matches


class FilePatternMatch(BaseScanMatch):
    """Match result for a file pattern."""
    
    pattern_name: str
    pattern_description: str
    matched_content: str
    context: str = ""
    line_number: Optional[int] = None
    byte_offset: Optional[int] = None
    category: str
    sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM
    validation_status: bool = True


class PatternValidator:
    """Validation functions for pattern matches."""
    
    @staticmethod
    def validate_credit_card(cc: str) -> bool:
        """
        Validate a credit card number using the Luhn algorithm.
        
        Args:
            cc: Credit card number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove any non-digit characters
        cc = re.sub(r'\D', '', cc)
        
        if not cc.isdigit():
            return False
            
        # Check length (most cards are between 13-19 digits)
        if not (13 <= len(cc) <= 19):
            return False
            
        # Luhn algorithm
        digits = [int(d) for d in cc]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        return checksum % 10 == 0
    
    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """
        Validate a U.S. Social Security Number.
        
        Args:
            ssn: SSN to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove any hyphens or spaces
        ssn = re.sub(r'[\s-]', '', ssn)
        
        # Check if it's 9 digits
        if not re.match(r'^\d{9}$', ssn):
            return False
        
        # Check if it's not all zeros in each part
        if ssn[0:3] == '000' or ssn[3:5] == '00' or ssn[5:9] == '0000':
            return False
        
        # Check if first part is not 666 and not between 900-999
        if ssn[0:3] == '666' or int(ssn[0:3]) >= 900:
            return False
            
        return True
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """
        Validate an IPv4 address.
        
        Args:
            ip: IP address to validate
            
        Returns:
            True if valid, False otherwise
        """
        parts = ip.split('.')
        if len(parts) != 4:
            return False
            
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False
                
        return True


class RegexPatternMatcher(PatternMatcher[FilePattern, FilePatternMatch]):
    """Pattern matcher using regular expressions."""
    
    def __init__(
        self, 
        patterns: Optional[List[FilePattern]] = None,
        validators: Optional[Dict[str, Callable]] = None,
        context_lines: int = 3
    ):
        """
        Initialize with patterns and validators.
        
        Args:
            patterns: List of patterns to match
            validators: Dictionary of validation functions
            context_lines: Number of context lines to include in matches
        """
        super().__init__(patterns)
        self.context_lines = context_lines
        
        # Set up validators
        self.validators = validators or {
            'validate_ssn': PatternValidator.validate_ssn,
            'validate_credit_card': PatternValidator.validate_credit_card,
            'validate_ip': PatternValidator.validate_ip
        }
    
    def _get_context(self, lines: List[str], line_idx: int, match_text: str) -> str:
        """
        Get context lines around a match.
        
        Args:
            lines: All lines of content
            line_idx: Index of the line with the match
            match_text: The matched text
            
        Returns:
            String with context lines
        """
        start = max(0, line_idx - self.context_lines)
        end = min(len(lines), line_idx + self.context_lines + 1)
        
        context_lines = []
        for i in range(start, end):
            prefix = ">" if i == line_idx else " "
            # Truncate long lines
            line = lines[i][:1000] + "..." if len(lines[i]) > 1000 else lines[i]
            context_lines.append(f"{prefix} {line}")
        
        return "\n".join(context_lines)
    
    def match_content(
        self, 
        content: str, 
        file_metadata: Optional[FileMetadata] = None
    ) -> List[FilePatternMatch]:
        """
        Match patterns against text content.
        
        Args:
            content: Text content to match against
            file_metadata: Optional metadata about the file being matched
            
        Returns:
            List of pattern matches
        """
        matches = []
        lines = content.splitlines()
        
        # Process the content line by line to maintain context
        for line_idx, line in enumerate(lines):
            for pattern in self.patterns:
                for match in pattern.match(line):
                    # Validate the match if a validation function is specified
                    validation_status = True
                    if pattern.validation_func and pattern.validation_func in self.validators:
                        validation_status = self.validators[pattern.validation_func](match)
                    
                    # Only include validated matches
                    if validation_status:
                        context = self._get_context(lines, line_idx, match)
                        
                        matches.append(FilePatternMatch(
                            pattern_name=pattern.name,
                            pattern_description=pattern.description,
                            matched_content=match,
                            context=context,
                            line_number=line_idx + 1,  # 1-based line numbers
                            byte_offset=None,  # Could calculate, but not needed for text files
                            category=pattern.category,
                            sensitivity=pattern.sensitivity,
                            validation_status=validation_status
                        ))
        
        return matches
    
    def match_binary(
        self, 
        content: bytes, 
        file_metadata: Optional[FileMetadata] = None
    ) -> List[FilePatternMatch]:
        """
        Match patterns against binary content.
        
        Args:
            content: Binary content to match against
            file_metadata: Optional metadata about the file being matched
            
        Returns:
            List of pattern matches
        """
        matches = []
        
        # First try to decode as text if possible
        try:
            text_content = content.decode('utf-8', errors='replace')
            text_matches = self.match_content(text_content, file_metadata)
            matches.extend(text_matches)
        except UnicodeDecodeError:
            # If can't decode as text, continue with binary matching
            pass
        
        # Direct binary pattern matching
        for pattern in self.patterns:
            binary_matches = pattern.match_binary(content)
            for match_bytes in binary_matches:
                # Convert to string representation for consistent handling
                try:
                    match_str = match_bytes.decode('utf-8', errors='replace')
                except:
                    match_str = str(match_bytes)
                
                matches.append(FilePatternMatch(
                    pattern_name=pattern.name,
                    pattern_description=pattern.description,
                    matched_content=match_str,
                    context="[Binary data]",
                    line_number=None,
                    byte_offset=None,
                    category=pattern.category,
                    sensitivity=pattern.sensitivity,
                    validation_status=True
                ))
        
        return matches
    
    def match_file(
        self, 
        file_path: Union[str, Path], 
        max_size: Optional[int] = None
    ) -> List[FilePatternMatch]:
        """
        Match patterns against a file.
        
        Args:
            file_path: Path to the file to match against
            max_size: Maximum file size to read
            
        Returns:
            List of pattern matches
        """
        path = Path(file_path)
        
        # Get file type to determine how to process it
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(path))
        
        # Default to binary if we can't determine MIME type
        is_binary = True
        if mime_type and (mime_type.startswith('text/') or 
                        mime_type in ['application/json', 'application/xml', 
                                    'application/csv', 'application/javascript']):
            is_binary = False
        
        if not is_binary:
            # Text file handling
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                return self.match_content(content)
            except UnicodeDecodeError:
                # Fall back to binary if we can't decode as text
                is_binary = True
        
        if is_binary:
            # Binary file handling
            sample_size = max_size or (1024 * 1024)  # Default to 1MB if not specified
            content = read_file_sample(path, max_bytes=sample_size)
            return self.match_binary(content)


class FilePatternRegistry:
    """Registry for managing and accessing file patterns."""
    
    _patterns: Dict[str, List[FilePattern]] = {}
    
    @classmethod
    def register_pattern(cls, pattern: FilePattern, category: str = "default"):
        """
        Register a pattern in a category.
        
        Args:
            pattern: Pattern to register
            category: Category to register pattern in
        """
        if category not in cls._patterns:
            cls._patterns[category] = []
        cls._patterns[category].append(pattern)
    
    @classmethod
    def register_patterns(cls, patterns: List[FilePattern], category: str = "default"):
        """
        Register multiple patterns in a category.
        
        Args:
            patterns: List of patterns to register
            category: Category to register patterns in
        """
        for pattern in patterns:
            cls.register_pattern(pattern, category)
    
    @classmethod
    def get_patterns(cls, category: Optional[str] = None) -> List[FilePattern]:
        """
        Get patterns from a category.
        
        Args:
            category: Category to get patterns from, or None for all patterns
            
        Returns:
            List of patterns in the category
        """
        if category is None:
            # Return all patterns from all categories
            all_patterns = []
            for cat_patterns in cls._patterns.values():
                all_patterns.extend(cat_patterns)
            return all_patterns
        elif category in cls._patterns:
            return cls._patterns[category]
        else:
            return []
    
    @classmethod
    def get_patterns_by_sensitivity(
        cls, 
        sensitivity: SensitivityLevel, 
        category: Optional[str] = None
    ) -> List[FilePattern]:
        """
        Get patterns with a minimum sensitivity level.
        
        Args:
            sensitivity: Minimum sensitivity level
            category: Optional category to filter by
            
        Returns:
            List of patterns meeting the criteria
        """
        all_patterns = cls.get_patterns(category)
        
        # Map sensitivity levels to numeric values for comparison
        sensitivity_values = {
            SensitivityLevel.LOW: 1,
            SensitivityLevel.MEDIUM: 2,
            SensitivityLevel.HIGH: 3,
            SensitivityLevel.CRITICAL: 4
        }
        
        min_value = sensitivity_values[sensitivity]
        
        return [
            p for p in all_patterns 
            if sensitivity_values[p.sensitivity] >= min_value
        ]
    
    @classmethod
    def clear_patterns(cls, category: Optional[str] = None):
        """
        Clear patterns from a category or all categories.
        
        Args:
            category: Category to clear, or None for all categories
        """
        if category is None:
            cls._patterns.clear()
        elif category in cls._patterns:
            del cls._patterns[category]