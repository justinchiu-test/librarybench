"""Database file detection and categorization."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Iterator, Union
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from collections import Counter

from ..utils.types import DatabaseEngine, FileCategory, DatabaseFile, ScanStatus, AnalysisResult
from ..utils.file_utils import find_files, get_file_stats
from .file_patterns import COMPILED_DB_PATTERNS, COMPILED_DIR_PATTERNS

# Import from common library
from common.core.base import FileSystemScanner, PatternMatcher, ScanSession
from common.core.patterns import FilePattern, FilePatternMatch, RegexPatternMatcher, FilePatternRegistry
from common.utils.types import FileMetadata, ScanOptions, ScanResult


logger = logging.getLogger(__name__)


class DatabaseFileAnalysisResult(AnalysisResult):
    """Results from database file analysis."""

    total_files_scanned: int
    total_size_bytes: int
    files_by_engine: Dict[DatabaseEngine, int]
    size_by_engine: Dict[DatabaseEngine, int]
    files_by_category: Dict[FileCategory, int]
    size_by_category: Dict[FileCategory, int]
    detected_files: List[DatabaseFile]


class DatabaseFileDetector(FileSystemScanner[DatabaseFileAnalysisResult]):
    """
    Detects and categorizes database files across multiple database engines.
    
    This class identifies files associated with various database engines
    (MySQL, PostgreSQL, MongoDB, Oracle, SQL Server) and categorizes them
    by their function (data, index, log, etc.).
    """

    def __init__(
        self,
        options: Optional[ScanOptions] = None,
        content_sampling_size: int = 8192,
        max_workers: int = 10,
    ):
        """
        Initialize the database file detector.

        Args:
            options: Scanner configuration options
            content_sampling_size: Number of bytes to read for content-based detection
            max_workers: Maximum number of worker threads for parallel processing
        """
        # Define default options if none provided
        if options is None:
            options = ScanOptions(
                ignore_extensions={
                    '.exe', '.dll', '.so', '.pyc', '.pyo', '.class', '.jar',
                    '.zip', '.tar', '.gz', '.7z', '.rar', '.bz2',
                    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
                    '.mp3', '.mp4', '.avi', '.mov', '.pdf', '.doc', '.docx',
                    '.xls', '.xlsx', '.ppt', '.pptx',
                }
            )
            
        super().__init__(options)
        self.content_sampling_size = content_sampling_size
        self.max_workers = max_workers
        
        # Initialize pattern matcher for database files
        self.pattern_matcher = RegexPatternMatcher()
        
        # For backward compatibility with tests
        self.ignore_extensions = self.options.ignore_extensions
        # Patterns are already registered with the registry in file_patterns.py

    def detect_engine_from_path(self, file_path: Path) -> Optional[DatabaseEngine]:
        """
        Detect database engine based on file path pattern.

        Args:
            file_path: Path to the file

        Returns:
            Detected database engine, or None if not detected
        """
        path_str = str(file_path)
        parent_path_str = str(file_path.parent)
        
        # Check directory patterns for engine hints
        for engine, patterns in COMPILED_DIR_PATTERNS.items():
            for pattern in patterns:
                if pattern.search(parent_path_str):
                    return engine
        
        # Check file extension patterns
        for engine, categories in COMPILED_DB_PATTERNS.items():
            for category, patterns in categories.items():
                for pattern in patterns:
                    if pattern.search(path_str):
                        return engine
                        
        return None
        
    def detect_engine_from_matches(self, matches: List[FilePatternMatch]) -> Optional[DatabaseEngine]:
        """
        Detect database engine based on pattern matches.

        Args:
            matches: List of pattern matches

        Returns:
            Detected database engine, or None if not detected
        """
        if not matches:
            return None
            
        # Count matches by engine
        engine_counts = Counter()
        
        for match in matches:
            # Extract engine from pattern name (e.g., "mysql_data_0")
            for engine in DatabaseEngine:
                if engine.value in match.pattern_name:
                    engine_counts[engine] += 1
                    break
        
        # Return the engine with the most matches, if any
        if engine_counts:
            return engine_counts.most_common(1)[0][0]
            
        return None

    def detect_category_from_path(
        self, file_path: Path, engine: Optional[DatabaseEngine] = None
    ) -> FileCategory:
        """
        Detect file category based on file path pattern.

        Args:
            file_path: Path to the file
            engine: Database engine to limit the search (optional)

        Returns:
            Detected file category, or FileCategory.UNKNOWN if not detected
        """
        path_str = str(file_path)

        # Special case for PostgreSQL WAL files for test compatibility
        if "pg_wal" in path_str or "pg_xlog" in path_str:
            return FileCategory.LOG

        # Special case for MongoDB index files
        if "index-" in path_str and engine == DatabaseEngine.MONGODB:
            return FileCategory.INDEX

        # If engine is specified, only check patterns for that engine
        engines_to_check = [engine] if engine and engine != DatabaseEngine.UNKNOWN else list(COMPILED_DB_PATTERNS.keys())

        for check_engine in engines_to_check:
            for category, patterns in COMPILED_DB_PATTERNS[check_engine].items():
                for pattern in patterns:
                    if pattern.search(path_str):
                        return category

        return FileCategory.UNKNOWN

    def sample_file_content(self, file_path: Path) -> Optional[bytes]:
        """
        Read a sample of file content for content-based detection.

        Args:
            file_path: Path to the file

        Returns:
            Sample of file content, or None if file can't be read
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read(self.content_sampling_size)
        except (PermissionError, OSError, IOError) as e:
            logger.debug(f"Cannot read content from {file_path}: {e}")
            return None

    def detect_engine_from_content(self, content: bytes) -> Optional[DatabaseEngine]:
        """
        Detect database engine based on file content.

        Args:
            content: File content sample

        Returns:
            Detected database engine, or None if not detected
        """
        # MySQL signature detection
        if b"MySQL" in content or b"InnoDB" in content:
            return DatabaseEngine.MYSQL
            
        # PostgreSQL signature detection
        if b"PostgreSQL" in content or b"PGDMP" in content:
            return DatabaseEngine.POSTGRESQL
            
        # MongoDB signature detection
        if b"MongoDB" in content or b"WiredTiger" in content:
            return DatabaseEngine.MONGODB
            
        # Oracle signature detection
        if b"Oracle" in content or b"ORACLE" in content:
            return DatabaseEngine.ORACLE
            
        # SQL Server signature detection
        if b"Microsoft SQL Server" in content or b"MSSQL" in content:
            return DatabaseEngine.MSSQL
            
        return None

    def analyze_file(self, file_path: Path) -> Optional[DatabaseFile]:
        """
        Analyze a single file to determine if it's a database file.

        Args:
            file_path: Path to the file

        Returns:
            DatabaseFile object if it's a database file, None otherwise
        """
        try:
            # Skip files with ignored extensions
            if file_path.suffix.lower() in self.options.ignore_extensions:
                return None
                
            # Get file stats
            stats = get_file_stats(file_path)
            
            # Skip directories and non-existent files
            if not stats.get("is_file", False) or not stats.get("exists", False):
                return None
                
            # Try to detect database engine from path
            engine = self.detect_engine_from_path(file_path)
            
            # If we couldn't detect from path and file is not too large, sample content
            if (not engine or engine == DatabaseEngine.UNKNOWN) and stats.get("size_bytes", 0) < 10_000_000:
                # Use pattern matcher to look for database-specific patterns
                matches = self.pattern_matcher.match_file(file_path, max_size=self.content_sampling_size)
                if matches:
                    engine_from_matches = self.detect_engine_from_matches(matches)
                    if engine_from_matches:
                        engine = engine_from_matches
                else:
                    # Fall back to content-based detection if no patterns matched
                    content = self.sample_file_content(file_path)
                    if content:
                        content_engine = self.detect_engine_from_content(content)
                        if content_engine:
                            engine = content_engine
            
            # If still no engine detected, skip this file
            if not engine:
                return None
                
            # Detect file category
            category = self.detect_category_from_path(file_path, engine)
            
            # Create database file object
            return DatabaseFile(
                path=str(file_path),
                engine=engine,
                category=category,
                size_bytes=stats.get("size_bytes", 0),
                last_modified=stats.get("last_modified", datetime.now()),
                creation_time=stats.get("creation_time"),
                last_accessed=stats.get("last_accessed"),
                is_compressed=file_path.suffix.lower() in {'.gz', '.zip', '.bz2', '.xz', '.7z', '.rar'},
            )
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return None

    def scan_file(self, file_path: Union[str, Path]) -> DatabaseFileAnalysisResult:
        """
        Scan a single file for database characteristics.

        Args:
            file_path: Path to the file to scan

        Returns:
            Analysis result for the file
        """
        try:
            # Analyze the file using the analyze_file method
            db_file = self.analyze_file(Path(file_path))
            
            if db_file:
                # Create a result with a single file
                return DatabaseFileAnalysisResult(
                    analysis_duration_seconds=0.0,  # Set when summarized
                    scan_status=ScanStatus.COMPLETED,
                    total_files_scanned=1,
                    total_size_bytes=db_file.size_bytes,
                    files_by_engine={db_file.engine: 1},
                    size_by_engine={db_file.engine: db_file.size_bytes},
                    files_by_category={db_file.category: 1},
                    size_by_category={db_file.category: db_file.size_bytes},
                    detected_files=[db_file],
                )
            else:
                # File not a database file
                return DatabaseFileAnalysisResult(
                    analysis_duration_seconds=0.0,
                    scan_status=ScanStatus.COMPLETED,
                    total_files_scanned=1,
                    total_size_bytes=0,
                    files_by_engine={},
                    size_by_engine={},
                    files_by_category={},
                    size_by_category={},
                    detected_files=[],
                )
                
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return DatabaseFileAnalysisResult(
                analysis_duration_seconds=0.0,
                scan_status=ScanStatus.FAILED,
                error_message=str(e),
                total_files_scanned=1,
                total_size_bytes=0,
                files_by_engine={},
                size_by_engine={},
                files_by_category={},
                size_by_category={},
                detected_files=[],
            )
    
    def summarize_scan(self, results: List[DatabaseFileAnalysisResult]) -> DatabaseFileAnalysisResult:
        """
        Create a summary of scan results.

        Args:
            results: List of scan results to summarize

        Returns:
            Summary of scan results
        """
        start_time = datetime.now()
        
        # Combine all detected files
        all_detected_files = []
        for result in results:
            all_detected_files.extend(result.detected_files)
        
        # Compute statistics
        total_files_scanned = sum(r.total_files_scanned for r in results)
        total_size_bytes = sum(f.size_bytes for f in all_detected_files)
        
        files_by_engine = Counter()
        size_by_engine = Counter()
        files_by_category = Counter()
        size_by_category = Counter()
        
        for file in all_detected_files:
            files_by_engine[file.engine] += 1
            size_by_engine[file.engine] += file.size_bytes
            files_by_category[file.category] += 1
            size_by_category[file.category] += file.size_bytes
        
        # Determine overall status
        status = ScanStatus.COMPLETED
        error_message = None
        for result in results:
            if result.scan_status == ScanStatus.FAILED:
                status = ScanStatus.FAILED
                error_message = result.error_message
                break
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return DatabaseFileAnalysisResult(
            analysis_duration_seconds=duration,
            scan_status=status,
            error_message=error_message,
            total_files_scanned=total_files_scanned,
            total_size_bytes=total_size_bytes,
            files_by_engine=dict(files_by_engine),
            size_by_engine=dict(size_by_engine),
            files_by_category=dict(files_by_category),
            size_by_category=dict(size_by_category),
            detected_files=all_detected_files,
        )
        
    def scan_directory_with_session(
        self,
        root_path: Union[str, Path],
        recursive: bool = True,
        follow_symlinks: bool = False,
        max_depth: Optional[int] = None,
        max_files: Optional[int] = None,
    ) -> DatabaseFileAnalysisResult:
        """
        Scan a directory for database files using a scan session.
        Maintains compatibility with the original API.

        Args:
            root_path: Starting directory for search
            recursive: Whether to search recursively
            follow_symlinks: Whether to follow symbolic links
            max_depth: Maximum directory depth to search
            max_files: Maximum number of files to process

        Returns:
            Analysis result containing detected database files and statistics
        """
        # Update options
        self.options.recursive = recursive
        self.options.follow_symlinks = follow_symlinks
        self.options.max_depth = max_depth
        self.options.max_files = max_files
        
        # Create and use scan session
        session = ScanSession(scanner=self)
        try:
            return session.scan_directory(root_path)
        except Exception as e:
            logger.error(f"Error in scan session: {e}")
            return DatabaseFileAnalysisResult(
                analysis_duration_seconds=0.0,
                scan_status=ScanStatus.FAILED,
                error_message=str(e),
                total_files_scanned=0,
                total_size_bytes=0,
                files_by_engine={},
                size_by_engine={},
                files_by_category={},
                size_by_category={},
                detected_files=[],
            )
            
    # Original method reimplemented for backward compatibility with tests
    def scan_directory(
        self,
        root_path: Union[str, Path],
        recursive: bool = True,
        follow_symlinks: bool = False,
        max_depth: Optional[int] = None,
        max_files: Optional[int] = None,
    ) -> DatabaseFileAnalysisResult:
        """
        Scan a directory for database files.
        
        Original method reimplemented for backward compatibility with tests.

        Args:
            root_path: Starting directory for search
            recursive: Whether to search recursively
            follow_symlinks: Whether to follow symbolic links
            max_depth: Maximum directory depth to search
            max_files: Maximum number of files to process

        Returns:
            Analysis result containing detected database files and statistics
        """
        start_time = datetime.now()
        root = Path(root_path)
        
        if not root.exists() or not root.is_dir():
            return DatabaseFileAnalysisResult(
                analysis_duration_seconds=0.0,
                scan_status=ScanStatus.FAILED,
                error_message=f"Root path {root_path} does not exist or is not a directory",
                total_files_scanned=0,
                total_size_bytes=0,
                files_by_engine={},
                size_by_engine={},
                files_by_category={},
                size_by_category={},
                detected_files=[],
            )
            
        try:
            # Find all files matching criteria
            all_files = list(find_files(
                root_path=root,
                extensions=None,  # We'll filter by extension in analyze_file
                max_depth=max_depth,
                follow_symlinks=follow_symlinks,
                recursive=recursive,
                max_files=max_files,
            ))
                
            total_files = len(all_files)
            logger.info(f"Found {total_files} files to analyze in {root_path}")
            
            # Process files in parallel
            detected_files = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {executor.submit(self.analyze_file, f): f for f in all_files}
                for future in as_completed(future_to_file):
                    result = future.result()
                    if result:
                        detected_files.append(result)
            
            # Compute statistics
            total_size = sum(f.size_bytes for f in detected_files)
            
            files_by_engine = Counter()
            size_by_engine = Counter()
            files_by_category = Counter()
            size_by_category = Counter()
            
            for file in detected_files:
                files_by_engine[file.engine] += 1
                size_by_engine[file.engine] += file.size_bytes
                files_by_category[file.category] += 1
                size_by_category[file.category] += file.size_bytes
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return DatabaseFileAnalysisResult(
                analysis_duration_seconds=duration,
                scan_status=ScanStatus.COMPLETED,
                total_files_scanned=total_files,
                total_size_bytes=total_size,
                files_by_engine=dict(files_by_engine),
                size_by_engine=dict(size_by_engine),
                files_by_category=dict(files_by_category),
                size_by_category=dict(size_by_category),
                detected_files=detected_files,
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"Error scanning directory {root_path}: {e}")
            return DatabaseFileAnalysisResult(
                analysis_duration_seconds=duration,
                scan_status=ScanStatus.FAILED,
                error_message=str(e),
                total_files_scanned=0,
                total_size_bytes=0,
                files_by_engine={},
                size_by_engine={},
                files_by_category={},
                size_by_category={},
                detected_files=[],
            )