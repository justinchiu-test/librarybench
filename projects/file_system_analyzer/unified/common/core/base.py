"""Base classes for file system analysis.

This module defines the core abstractions and interfaces used by the
file system analyzer components.
"""

import os
import time
import abc
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Iterator, Generic, TypeVar

from pydantic import BaseModel

from ..utils.types import (
    FileMetadata, ScanOptions, ScanResult, ScanSummary, 
    ScanStatus, BaseScanMatch, FileCategory
)
from ..utils.file_utils import find_files, create_file_metadata


logger = logging.getLogger(__name__)


# Generic type for pattern definitions
P = TypeVar('P')
# Generic type for match results
M = TypeVar('M', bound=BaseScanMatch)
# Generic type for scan results
R = TypeVar('R', bound=ScanResult)


class PatternMatcher(abc.ABC, Generic[P, M]):
    """Base class for pattern matching against file content."""
    
    def __init__(self, patterns: Optional[List[P]] = None):
        """
        Initialize with patterns.
        
        Args:
            patterns: List of patterns to match
        """
        self.patterns = patterns or []
    
    @abc.abstractmethod
    def match_content(self, content: str, file_metadata: Optional[FileMetadata] = None) -> List[M]:
        """
        Match patterns against content.
        
        Args:
            content: String content to match against
            file_metadata: Optional metadata about the file being matched
            
        Returns:
            List of matches found
        """
        pass
    
    @abc.abstractmethod
    def match_binary(self, content: bytes, file_metadata: Optional[FileMetadata] = None) -> List[M]:
        """
        Match patterns against binary content.
        
        Args:
            content: Binary content to match against
            file_metadata: Optional metadata about the file being matched
            
        Returns:
            List of matches found
        """
        pass
    
    @abc.abstractmethod
    def match_file(self, file_path: Union[str, Path], max_size: Optional[int] = None) -> List[M]:
        """
        Match patterns against a file.
        
        Args:
            file_path: Path to the file to match against
            max_size: Maximum file size to read
            
        Returns:
            List of matches found
        """
        pass


class FileSystemScanner(abc.ABC, Generic[R]):
    """Base class for file system scanning."""
    
    def __init__(self, options: Optional[ScanOptions] = None):
        """
        Initialize scanner with options.
        
        Args:
            options: Scanner configuration options
        """
        self.options = options or ScanOptions()
    
    def should_ignore_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if a file should be ignored based on options.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        path_str = str(file_path)
        
        # Check file extension
        _, ext = os.path.splitext(path_str)
        if ext.lower() in self.options.ignore_extensions:
            return True
        
        # Check ignore patterns
        for pattern in self.options.ignore_patterns:
            import re
            try:
                if re.search(pattern, path_str):
                    return True
            except re.error:
                # If pattern is not a valid regex, try literal matching
                if pattern in path_str:
                    return True
        
        # Check file size if the file exists
        if os.path.isfile(file_path):
            try:
                if os.path.getsize(file_path) > self.options.max_file_size:
                    return True
            except (OSError, IOError):
                # If we can't check the size, assume we should ignore it
                return True
        
        # Check if file is hidden and we're not including hidden files
        if not self.options.include_hidden:
            filename = os.path.basename(path_str)
            if filename.startswith('.'):
                return True
        
        return False
    
    @abc.abstractmethod
    def scan_file(self, file_path: Union[str, Path]) -> R:
        """
        Scan a single file.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Scan result for the file
        """
        pass
    
    def scan_directory(self, directory_path: Union[str, Path]) -> Iterator[R]:
        """
        Scan a directory for files.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            Iterator of scan results for files in the directory
        """
        for root, dirs, files in os.walk(directory_path):
            # Filter directories based on options
            if not self.options.include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Skip directories matching ignore patterns
            dirs[:] = [d for d in dirs if not self.should_ignore_file(os.path.join(root, d))]
            
            # Process files in current directory
            for file in files:
                file_path = os.path.join(root, file)
                if not self.should_ignore_file(file_path):
                    yield self.scan_file(file_path)
            
            # Break if not recursive
            if not self.options.recursive:
                break
    
    def scan_files(self, file_paths: List[Union[str, Path]]) -> Iterator[R]:
        """
        Scan a list of files.
        
        Args:
            file_paths: List of file paths to scan
            
        Returns:
            Iterator of scan results for the files
        """
        for file_path in file_paths:
            if not self.should_ignore_file(file_path):
                yield self.scan_file(file_path)
    
    @abc.abstractmethod
    def summarize_scan(self, results: List[R]) -> ScanSummary:
        """
        Create a summary of scan results.
        
        Args:
            results: List of scan results to summarize
            
        Returns:
            Summary of scan results
        """
        pass


class ReportGenerator(abc.ABC):
    """Base class for report generation."""
    
    @abc.abstractmethod
    def generate_report(
        self, 
        scan_results: List[ScanResult],
        scan_summary: Optional[ScanSummary] = None
    ) -> Any:
        """
        Generate a report from scan results.
        
        Args:
            scan_results: List of scan results to include in the report
            scan_summary: Optional summary of scan results
            
        Returns:
            Generated report
        """
        pass
    
    @abc.abstractmethod
    def export_report(self, report: Any, output_path: Union[str, Path]) -> str:
        """
        Export a report to a file.
        
        Args:
            report: Report to export
            output_path: Path to export to
            
        Returns:
            Path to exported report
        """
        pass


class AnalysisEngine(abc.ABC):
    """Base class for analysis engines."""
    
    @abc.abstractmethod
    def analyze(self, scan_results: List[ScanResult]) -> Any:
        """
        Analyze scan results.
        
        Args:
            scan_results: Scan results to analyze
            
        Returns:
            Analysis results
        """
        pass


class ScanSession:
    """Manages a file system scanning session with multiple components."""
    
    def __init__(
        self,
        scanner: FileSystemScanner,
        output_dir: Optional[Union[str, Path]] = None,
        user_id: str = "system"
    ):
        """
        Initialize a scan session.
        
        Args:
            scanner: Scanner to use for file system scanning
            output_dir: Directory to store output files
            user_id: ID of the user performing the scan
        """
        self.scanner = scanner
        self.output_dir = output_dir
        self.user_id = user_id
        
        # Initialize state
        self.scan_results = []
        self.scan_summary = None
        self.start_time = None
        self.end_time = None
        self.duration = 0.0
        self.status = ScanStatus.PENDING
        self.error = None
    
    def scan_directory(self, directory_path: Union[str, Path]) -> ScanSummary:
        """
        Scan a directory and record results.
        
        Args:
            directory_path: Directory to scan
            
        Returns:
            Summary of scan results
        """
        self.start_time = datetime.now(timezone.utc)
        start_timestamp = time.time()
        self.status = ScanStatus.IN_PROGRESS
        
        try:
            # Perform the scan
            self.scan_results = list(self.scanner.scan_directory(directory_path))
            
            # Create scan summary
            self.scan_summary = self.scanner.summarize_scan(self.scan_results)
            
            # Update session state
            self.end_time = datetime.now(timezone.utc)
            self.duration = time.time() - start_timestamp
            self.status = ScanStatus.COMPLETED
            
            return self.scan_summary
            
        except Exception as e:
            # Record error
            self.end_time = datetime.now(timezone.utc)
            self.duration = time.time() - start_timestamp
            self.status = ScanStatus.FAILED
            self.error = str(e)
            
            # Re-raise the exception
            raise
    
    def scan_files(self, file_paths: List[Union[str, Path]]) -> ScanSummary:
        """
        Scan a list of files and record results.
        
        Args:
            file_paths: List of file paths to scan
            
        Returns:
            Summary of scan results
        """
        self.start_time = datetime.now(timezone.utc)
        start_timestamp = time.time()
        self.status = ScanStatus.IN_PROGRESS
        
        try:
            # Perform the scan
            self.scan_results = list(self.scanner.scan_files(file_paths))
            
            # Create scan summary
            self.scan_summary = self.scanner.summarize_scan(self.scan_results)
            
            # Update session state
            self.end_time = datetime.now(timezone.utc)
            self.duration = time.time() - start_timestamp
            self.status = ScanStatus.COMPLETED
            
            return self.scan_summary
            
        except Exception as e:
            # Record error
            self.end_time = datetime.now(timezone.utc)
            self.duration = time.time() - start_timestamp
            self.status = ScanStatus.FAILED
            self.error = str(e)
            
            # Re-raise the exception
            raise