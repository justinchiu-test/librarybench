"""Concrete scanner implementations for file system analysis.

This module provides implementations of the base scanner classes,
offering ready-to-use file system scanning functionality.
"""

import os
import re
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

from pydantic import BaseModel, Field

from .base import FileSystemScanner, PatternMatcher, P, M
from ..utils.types import (
    FileMetadata, ScanOptions, ScanResult, ScanSummary, 
    ScanStatus, BaseScanMatch, FileCategory
)
from ..utils.file_utils import (
    find_files, create_file_metadata, detect_file_type, 
    calculate_file_hash, read_file_sample
)


logger = logging.getLogger(__name__)


class GenericScanMatch(BaseScanMatch):
    """Generic implementation of a scan match."""
    
    def __init__(self, **data):
        """Initialize with data."""
        super().__init__(**data)


class GenericScanResult(ScanResult):
    """Generic implementation of a scan result."""
    
    def __init__(self, **data):
        """Initialize with data."""
        super().__init__(**data)
    
    @property
    def has_matches(self) -> bool:
        """Check if the result has any matches."""
        return len(self.matches) > 0


class DirectoryScanner(FileSystemScanner[GenericScanResult]):
    """
    Generic directory scanner implementation.
    
    This scanner can work with any pattern matcher to find patterns in files.
    """
    
    def __init__(
        self, 
        pattern_matcher: Optional[PatternMatcher] = None,
        options: Optional[ScanOptions] = None
    ):
        """
        Initialize scanner with options and pattern matcher.
        
        Args:
            pattern_matcher: Pattern matcher to use for content matching
            options: Scanner configuration options
        """
        super().__init__(options)
        self.pattern_matcher = pattern_matcher
    
    def get_file_metadata(self, file_path: Union[str, Path]) -> FileMetadata:
        """
        Get metadata for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File metadata
        """
        path = Path(file_path)
        calculate_hash = True  # Can make this configurable if needed
        
        file_metadata = create_file_metadata(
            file_path=path,
            calculate_hash=calculate_hash
        )
        
        # Get MIME type if not already determined
        if file_metadata.file_type == "unknown" or file_metadata.mime_type == "application/octet-stream":
            mime_type, file_type = detect_file_type(path)
            file_metadata.mime_type = mime_type
            file_metadata.file_type = file_type
        
        return file_metadata
    
    def scan_file(self, file_path: Union[str, Path]) -> GenericScanResult:
        """
        Scan a single file.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Scan result for the file
        """
        if self.should_ignore_file(file_path):
            # Create minimal metadata without scanning
            metadata = create_file_metadata(file_path, calculate_hash=False)
            return GenericScanResult(
                file_metadata=metadata,
                matches=[],
                scan_time=datetime.now(),
                scan_duration=0.0
            )
        
        start_time = datetime.now()
        try:
            metadata = self.get_file_metadata(file_path)
            
            matches = []
            if self.pattern_matcher is not None:
                # Only scan text files or files we know how to handle
                is_text = (metadata.mime_type.startswith('text/') or 
                         metadata.mime_type in ['application/json', 'application/xml', 
                                              'application/csv'])
                
                if is_text:
                    try:
                        # Apply pattern matcher to file
                        matches = self.pattern_matcher.match_file(file_path)
                    except UnicodeDecodeError:
                        # If we can't decode as text, try binary matching
                        sample = read_file_sample(file_path)
                        matches = self.pattern_matcher.match_binary(sample, metadata)
                else:
                    # Binary file - only check the first portion for binary patterns
                    sample = read_file_sample(file_path)
                    matches = self.pattern_matcher.match_binary(sample, metadata)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return GenericScanResult(
                file_metadata=metadata,
                matches=matches,
                scan_time=start_time,
                scan_duration=duration
            )
        
        except Exception as e:
            # Catch any errors and include them in the result
            logger.error(f"Error scanning file {file_path}: {e}")
            
            try:
                metadata = create_file_metadata(file_path, calculate_hash=False)
            except Exception:
                # If we can't get metadata, create minimal metadata
                metadata = FileMetadata(
                    file_path=str(file_path),
                    file_size=0,
                    file_type="unknown",
                    mime_type="unknown",
                    modification_time=datetime.now()
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return GenericScanResult(
                file_metadata=metadata,
                matches=[],
                scan_time=start_time,
                scan_duration=duration,
                error=str(e)
            )
    
    def parallel_scan_directory(
        self, 
        directory_path: Union[str, Path],
        max_workers: Optional[int] = None
    ) -> List[GenericScanResult]:
        """
        Scan a directory using parallel processing.
        
        Args:
            directory_path: Directory to scan
            max_workers: Maximum number of worker threads
            
        Returns:
            List of scan results
        """
        if max_workers is None:
            max_workers = self.options.num_threads
        
        # First find all files
        file_paths = list(find_files(
            root_path=directory_path,
            recursive=self.options.recursive,
            max_size=self.options.max_file_size,
            skip_hidden=not self.options.include_hidden,
            follow_symlinks=self.options.follow_symlinks,
            max_depth=self.options.max_depth,
        ))
        
        # Filter files based on scanner options
        file_paths = [fp for fp in file_paths if not self.should_ignore_file(fp)]
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {executor.submit(self.scan_file, path): path for path in file_paths}
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {path}: {e}")
                    # Create an error result
                    metadata = FileMetadata(
                        file_path=str(path),
                        file_size=0,
                        modification_time=datetime.now()
                    )
                    results.append(GenericScanResult(
                        file_metadata=metadata,
                        matches=[],
                        scan_time=datetime.now(),
                        scan_duration=0.0,
                        error=str(e)
                    ))
        
        return results
    
    def summarize_scan(self, results: List[GenericScanResult]) -> ScanSummary:
        """
        Create a summary of scan results.
        
        Args:
            results: Scan results to summarize
            
        Returns:
            Summary of scan results
        """
        if not results:
            return ScanSummary(
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                total_files=0,
                files_matched=0,
                total_matches=0,
                files_with_errors=0,
                categorized_matches={}
            )
        
        start_time = min(r.scan_time for r in results)
        end_time = max(r.scan_time for r in results)
        duration = sum(r.scan_duration for r in results)
        
        files_matched = sum(1 for r in results if r.has_matches)
        total_matches = sum(len(r.matches) for r in results)
        files_with_errors = sum(1 for r in results if r.error is not None)
        
        # Categorize matches
        categorized_matches = Counter()
        
        for result in results:
            for match in result.matches:
                # Count by category
                categorized_matches[match.category] += 1
        
        return ScanSummary(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_files=len(results),
            files_matched=files_matched,
            total_matches=total_matches,
            files_with_errors=files_with_errors,
            categorized_matches=dict(categorized_matches)
        )


class ParallelDirectoryScanner(DirectoryScanner):
    """
    Scanner that scans directories in parallel.
    
    This scanner overrides the scan_directory method to use parallel processing.
    """
    
    def scan_directory(self, directory_path: Union[str, Path]) -> Iterator[GenericScanResult]:
        """
        Scan a directory using parallel processing.
        
        Args:
            directory_path: Directory to scan
            
        Returns:
            Iterator of scan results
        """
        results = self.parallel_scan_directory(
            directory_path=directory_path,
            max_workers=self.options.num_threads
        )
        for result in results:
            yield result