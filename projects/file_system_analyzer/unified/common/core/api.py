"""Common API framework for file system analysis.

This module provides a standardized API framework for file system analysis
that can be extended by persona-specific implementations.
"""

import os
import time
import json
import logging
import threading
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Type, Generic, TypeVar
from datetime import datetime, timedelta
from pathlib import Path
from abc import ABC, abstractmethod
from functools import lru_cache

from pydantic import BaseModel, Field

from .base import FileSystemScanner, AnalysisEngine, ReportGenerator, ScanSession
from .scanner import DirectoryScanner
from ..utils.types import (
    ScanOptions, ScanResult, ScanSummary, AnalysisResult, 
    PriorityLevel, ScanStatus
)


logger = logging.getLogger(__name__)


# Type variables for generic API components
R = TypeVar('R', bound=ScanResult)  # For scan results
A = TypeVar('A', bound=AnalysisResult)  # For analysis results


class APIResult(BaseModel):
    """Base class for API operation results."""
    
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    result_data: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)


class NotificationConfig(BaseModel):
    """Configuration for result notifications."""
    
    enabled: bool = False
    min_priority: PriorityLevel = PriorityLevel.HIGH
    notification_methods: List[str] = Field(default_factory=lambda: ["console"])
    recipient: Optional[str] = None
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class CacheConfig(BaseModel):
    """Configuration for result caching."""
    
    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour default TTL
    max_items: int = 100
    invalidate_on_file_change: bool = True


class AnalysisNotifier:
    """Notifies about important analysis results."""
    
    def __init__(self, config: NotificationConfig):
        """
        Initialize notifier with configuration.
        
        Args:
            config: Notification configuration
        """
        self.config = config
    
    def should_notify(self, priority: PriorityLevel) -> bool:
        """
        Check if notification should be sent for a priority level.
        
        Args:
            priority: Priority level to check
            
        Returns:
            True if notification should be sent, False otherwise
        """
        if not self.config.enabled:
            return False
            
        # Map priority levels to numeric values
        priority_values = {
            PriorityLevel.INFORMATIONAL: 1,
            PriorityLevel.LOW: 2,
            PriorityLevel.MEDIUM: 3,
            PriorityLevel.HIGH: 4,
            PriorityLevel.CRITICAL: 5
        }
        
        # Check if priority is at or above the minimum configured priority
        min_value = priority_values[self.config.min_priority]
        current_value = priority_values[priority]
        
        return current_value >= min_value
    
    def notify(self, message: str, priority: PriorityLevel, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a notification.
        
        Args:
            message: Notification message
            priority: Priority level
            details: Optional additional details
            
        Returns:
            True if notification was sent, False otherwise
        """
        if not self.should_notify(priority):
            return False
        
        # Send to each configured notification method
        for method in self.config.notification_methods:
            try:
                if method == "console":
                    self._console_notify(message, priority, details)
                elif method == "email" and self.config.recipient:
                    self._email_notify(message, priority, details)
                # Add other notification methods as needed
            except Exception as e:
                logger.error(f"Error sending notification via {method}: {e}")
        
        return True
    
    def _console_notify(self, message: str, priority: PriorityLevel, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Send a console notification.
        
        Args:
            message: Notification message
            priority: Priority level
            details: Optional additional details
        """
        priority_prefix = {
            PriorityLevel.INFORMATIONAL: "[INFO]",
            PriorityLevel.LOW: "[LOW]",
            PriorityLevel.MEDIUM: "[MEDIUM]",
            PriorityLevel.HIGH: "[HIGH]",
            PriorityLevel.CRITICAL: "[CRITICAL]"
        }
        
        prefix = priority_prefix.get(priority, "[NOTIFICATION]")
        logger.info(f"{prefix} {message}")
        
        if details:
            logger.info(f"Details: {json.dumps(details, indent=2, default=str)}")
    
    def _email_notify(self, message: str, priority: PriorityLevel, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Send an email notification.
        
        Args:
            message: Notification message
            priority: Priority level
            details: Optional additional details
        """
        # This is a placeholder for email notification
        # In a real implementation, this would use an email library
        recipient = self.config.recipient
        logger.info(f"Would send email to {recipient}: {priority} - {message}")


class ResultCache:
    """Cache for analysis results."""
    
    def __init__(self, config: CacheConfig):
        """
        Initialize cache with configuration.
        
        Args:
            config: Cache configuration
        """
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or None if not found or expired
        """
        if not self.config.enabled:
            return None
        
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check if entry has expired
            timestamp = self.timestamps.get(key)
            if timestamp:
                age = datetime.now() - timestamp
                if age.total_seconds() > self.config.ttl_seconds:
                    # Remove expired entry
                    del self.cache[key]
                    del self.timestamps[key]
                    return None
            
            return self.cache[key]
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.config.enabled:
            return
        
        with self.lock:
            # Ensure we don't exceed max items
            if len(self.cache) >= self.config.max_items and key not in self.cache:
                # Remove oldest entry
                oldest_key = min(self.timestamps.items(), key=lambda x: x[1])[0]
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            # Set new value
            self.cache[key] = value
            self.timestamps[key] = datetime.now()
    
    def invalidate(self, key: str) -> None:
        """
        Invalidate a cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()


class BaseAnalyzerAPI(Generic[R, A], ABC):
    """
    Base API for file system analysis.
    
    This provides a standardized interface for file system analysis operations
    that can be extended by persona-specific implementations.
    """
    
    def __init__(
        self,
        scanner: Optional[FileSystemScanner[R]] = None,
        analyzer: Optional[AnalysisEngine] = None,
        report_generator: Optional[ReportGenerator] = None,
        cache_config: Optional[CacheConfig] = None,
        notification_config: Optional[NotificationConfig] = None
    ):
        """
        Initialize API with components.
        
        Args:
            scanner: Scanner to use for file system scanning
            analyzer: Analyzer to use for processing scan results
            report_generator: Report generator for creating reports
            cache_config: Configuration for result caching
            notification_config: Configuration for notifications
        """
        self.scanner = scanner or self._create_default_scanner()
        self.analyzer = analyzer or self._create_default_analyzer()
        self.report_generator = report_generator or self._create_default_report_generator()
        
        self.cache = ResultCache(cache_config or CacheConfig())
        self.notifier = AnalysisNotifier(notification_config or NotificationConfig())
        
        self.last_scan_time = None
        self.last_scan_directory = None
    
    def _create_default_scanner(self) -> FileSystemScanner[R]:
        """
        Create a default scanner.
        
        Returns:
            Default file system scanner
        """
        return DirectoryScanner()
    
    def _create_default_analyzer(self) -> AnalysisEngine:
        """
        Create a default analyzer.
        
        Returns:
            Default analysis engine
        """
        from .analysis import GenericAnalyzer
        return GenericAnalyzer()
    
    def _create_default_report_generator(self) -> ReportGenerator:
        """
        Create a default report generator.
        
        Returns:
            Default report generator
        """
        from .reporting import GenericReportGenerator
        return GenericReportGenerator()
    
    def _generate_cache_key(self, operation: str, path: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key for an operation.
        
        Args:
            operation: Operation name
            path: File or directory path
            options: Optional operation options
            
        Returns:
            Cache key string
        """
        key_parts = [operation, path]
        
        if options:
            # Sort options for consistent keys
            sorted_options = json.dumps(options, sort_keys=True)
            key_parts.append(sorted_options)
        
        return ":".join(key_parts)
    
    def scan_directory(
        self,
        directory_path: Union[str, Path],
        scan_options: Optional[ScanOptions] = None,
        use_cache: bool = True
    ) -> APIResult:
        """
        Scan a directory.
        
        Args:
            directory_path: Directory to scan
            scan_options: Options for scanning
            use_cache: Whether to use cached results if available
            
        Returns:
            API result with scan summary
        """
        path = str(Path(directory_path).absolute())
        start_time = datetime.now()
        
        try:
            # Check cache if enabled
            if use_cache:
                cache_key = self._generate_cache_key("scan_directory", path, 
                                                   scan_options.dict() if scan_options else None)
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"Using cached results for {path}")
                    return APIResult(
                        success=True,
                        message="Using cached scan results",
                        timestamp=datetime.now(),
                        duration_seconds=0.0,
                        result_data=cached_result
                    )
            
            # Update scanner options if provided
            if scan_options:
                self.scanner.options = scan_options
            
            # Create scan session and perform scan
            session = ScanSession(scanner=self.scanner)
            scan_summary = session.scan_directory(directory_path)
            
            # Store scan results for later use
            self.last_scan_time = datetime.now()
            self.last_scan_directory = path
            
            # Create result
            result_data = {
                "summary": scan_summary.dict(),
                "status": session.status,
                "scan_time": self.last_scan_time.isoformat(),
                "file_count": scan_summary.total_files,
                "matches_count": scan_summary.total_matches
            }
            
            # Cache result if caching is enabled
            if use_cache:
                cache_key = self._generate_cache_key("scan_directory", path, 
                                                   scan_options.dict() if scan_options else None)
                self.cache.set(cache_key, result_data)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return APIResult(
                success=True,
                message=f"Successfully scanned directory: {path}",
                timestamp=datetime.now(),
                duration_seconds=duration,
                result_data=result_data
            )
            
        except Exception as e:
            logger.error(f"Error scanning directory {path}: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            
            return APIResult(
                success=False,
                message=f"Error scanning directory: {path}",
                timestamp=datetime.now(),
                duration_seconds=duration,
                errors=[str(e)]
            )
    
    @abstractmethod
    def analyze_results(self, scan_results: List[R]) -> A:
        """
        Analyze scan results.
        
        Args:
            scan_results: Scan results to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    def generate_report(
        self,
        analysis_result: A,
        output_format: str = "json",
        output_file: Optional[Union[str, Path]] = None
    ) -> APIResult:
        """
        Generate a report from analysis results.
        
        Args:
            analysis_result: Analysis results to include in the report
            output_format: Format for the report (json, csv, html)
            output_file: Optional file to write the report to
            
        Returns:
            API result with report information
        """
        start_time = datetime.now()
        
        try:
            # Convert analysis result to scan results list
            # This may need customization in implementations
            scan_results = getattr(analysis_result, "scan_results", [])
            
            # Generate the report
            report = self.report_generator.generate_report(scan_results)
            
            # Export the report if output file specified
            report_path = None
            if output_file:
                report_path = self.report_generator.export_report(
                    report, 
                    output_file,
                    format=output_format
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return APIResult(
                success=True,
                message=f"Successfully generated {output_format} report",
                timestamp=datetime.now(),
                duration_seconds=duration,
                result_data={
                    "format": output_format,
                    "report_path": str(report_path) if report_path else None,
                    "report_id": getattr(report.metadata, "report_id", None)
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            
            return APIResult(
                success=False,
                message="Error generating report",
                timestamp=datetime.now(),
                duration_seconds=duration,
                errors=[str(e)]
            )
    
    @abstractmethod
    def comprehensive_analysis(
        self,
        target_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> APIResult:
        """
        Perform a comprehensive analysis of a target path.
        
        This is a high-level method that combines scanning, analysis, and reporting
        in a single operation.
        
        Args:
            target_path: Path to analyze
            output_dir: Optional directory for output files
            options: Optional analysis options
            use_cache: Whether to use cached results if available
            
        Returns:
            API result with comprehensive analysis information
        """
        pass