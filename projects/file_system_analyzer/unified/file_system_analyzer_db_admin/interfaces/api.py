"""API interfaces for the Database Storage Optimization Analyzer."""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from datetime import datetime
import json
import uuid
import os
from pathlib import Path

# Import from common library
from common.core.api import BaseAnalyzerAPI, APIResult, NotificationConfig, CacheConfig
from common.utils.export import export_results
from common.utils.types import ScanStatus

# Import from persona-specific modules
from ..utils.types import (
    DatabaseEngine, 
    FileCategory, 
    AnalysisResult,
    OptimizationRecommendation,
    DatabaseFile
)
from ..db_file_recognition.detector import DatabaseFileDetector
from ..transaction_log_analysis.log_analyzer import TransactionLogAnalyzer
from ..index_efficiency.index_analyzer import IndexEfficiencyAnalyzer
from ..tablespace_fragmentation.fragmentation_analyzer import TablespaceFragmentationAnalyzer
from ..backup_compression.compression_analyzer import BackupCompressionAnalyzer
from .export import ExportInterface, NotificationInterface
from .filesystem import FileSystemInterface


logger = logging.getLogger(__name__)


class StorageOptimizerAPI(BaseAnalyzerAPI):
    """
    Main API for the Database Storage Optimization Analyzer.
    
    This class provides a unified API for all analysis capabilities, along
    with result caching, export options, and notification features.
    """

    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        cache_results: bool = True,
        cache_ttl_seconds: int = 3600,
        read_only: bool = True,
        notification_config: Optional[NotificationConfig] = None,
        cache_config: Optional[CacheConfig] = None
    ):
        """
        Initialize the Storage Optimizer API.

        Args:
            output_dir: Directory for output files
            cache_results: Whether to cache analysis results
            cache_ttl_seconds: Time-to-live for cached results
            read_only: Enforce read-only operations
            notification_config: Configuration for notifications
            cache_config: Configuration for caching
        """
        # Set up cache config
        if cache_config is None:
            cache_config = CacheConfig(
                enabled=cache_results,
                ttl_seconds=cache_ttl_seconds,
                max_items=100
            )
        
        # Set up notification config
        if notification_config is None:
            notification_config = NotificationConfig(
                enabled=False
            )
            
        # Create file detector for database files
        self.file_detector = DatabaseFileDetector()
        
        # Initialize base analyzer API with file detector as scanner
        super().__init__(
            scanner=self.file_detector,
            analyzer=None,  # We'll use specific analyzers for each analysis type
            report_generator=None,  # We'll use export_interface for reports
            cache_config=cache_config,
            notification_config=notification_config
        )
        
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.read_only = read_only
        
        # Initialize interfaces
        self.fs_interface = FileSystemInterface(read_only=read_only)
        self.export_interface = ExportInterface(output_dir=output_dir)
        self.notification_interface = NotificationInterface()
        
        # Initialize analyzers
        self.log_analyzer = TransactionLogAnalyzer()
        self.index_analyzer = IndexEfficiencyAnalyzer()
        self.fragmentation_analyzer = TablespaceFragmentationAnalyzer()
        self.backup_analyzer = BackupCompressionAnalyzer()
        
        # For backward compatibility
        self.cache_results = cache_config.enabled
        self.cache_ttl_seconds = cache_config.ttl_seconds
        self.results_cache = {}
        self.cache_timestamps = {}
    
    def analyze_results(self, scan_results: List[Any]) -> Any:
        """
        Analyze scan results.
        
        Args:
            scan_results: Scan results to analyze
            
        Returns:
            Analysis results
        """
        # This is a placeholder that would typically call a specific analyzer
        # Actual implementation done in specific analysis methods
        return {}
    
    def analyze_database_files(
        self,
        root_path: Union[str, Path],
        recursive: bool = True,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False,
        max_files: Optional[int] = None,
        export_format: Optional[str] = None,
        export_filename: Optional[str] = None,
        notify_on_critical: bool = False,
        notification_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze database files in a directory.

        Args:
            root_path: Starting directory
            recursive: Whether to search recursively
            max_depth: Maximum directory depth to search
            follow_symlinks: Whether to follow symbolic links
            max_files: Maximum number of files to analyze
            export_format: Export format (json, csv, html)
            export_filename: Export filename
            notify_on_critical: Whether to send notifications for critical findings
            notification_email: Email address for notifications

        Returns:
            Analysis result dictionary
        """
        # Generate cache key
        cache_key = f"db_files_{root_path}_{recursive}_{max_depth}_{follow_symlinks}_{max_files}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        # Perform analysis
        analysis_result = self.file_detector.scan_directory(
            root_path=root_path,
            recursive=recursive,
            follow_symlinks=follow_symlinks,
            max_depth=max_depth,
            max_files=max_files,
        )
        
        # Export if requested
        if export_format and export_filename:
            self._export_result(analysis_result, export_format, export_filename)
            
        # Send notifications if requested
        if notify_on_critical and notification_email and analysis_result.recommendations:
            self.notification_interface.send_email_notification(
                recommendations=analysis_result.recommendations,
                recipient=notification_email,
                subject="Database File Analysis - Critical Findings",
            )
            
        # Cache result
        result_dict = json.loads(analysis_result.json())
        self._store_in_cache(cache_key, result_dict)
        
        return result_dict
    
    def analyze_transaction_logs(
        self,
        log_files: List[Dict[str, Any]],
        historical_sizes: Optional[Dict[str, List[Tuple[datetime, int]]]] = None,
        operation_frequencies: Optional[Dict[str, Dict[str, List[int]]]] = None,
        export_format: Optional[str] = None,
        export_filename: Optional[str] = None,
        notify_on_critical: bool = False,
        notification_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze transaction log files.

        Args:
            log_files: List of log file information dictionaries
            historical_sizes: Dictionary mapping file paths to historical size data
            operation_frequencies: Dictionary mapping engines to operation frequencies
            export_format: Export format (json, csv, html)
            export_filename: Export filename
            notify_on_critical: Whether to send notifications for critical findings
            notification_email: Email address for notifications

        Returns:
            Analysis result dictionary
        """
        # Convert log files to DatabaseFile objects
        db_log_files = []
        for log_file in log_files:
            try:
                db_log_files.append(DatabaseFile(**log_file))
            except Exception as e:
                logger.error(f"Error converting log file data: {e}")
                
        # Generate cache key based on input data
        cache_key = f"tx_logs_{hash(str(log_files))}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        # Perform analysis
        analysis_result = self.log_analyzer.analyze_logs(
            log_files=db_log_files,
            historical_sizes=historical_sizes,
            operation_frequencies=operation_frequencies,
        )
        
        # Export if requested
        if export_format and export_filename:
            self._export_result(analysis_result, export_format, export_filename)
            
        # Send notifications if requested
        if notify_on_critical and notification_email and analysis_result.recommendations:
            self.notification_interface.send_email_notification(
                recommendations=analysis_result.recommendations,
                recipient=notification_email,
                subject="Transaction Log Analysis - Critical Findings",
            )
            
        # Cache result
        result_dict = json.loads(analysis_result.json())
        self._store_in_cache(cache_key, result_dict)
        
        return result_dict
    
    def analyze_index_efficiency(
        self,
        indexes: List[Dict[str, Any]],
        tables_sizes: Optional[Dict[str, int]] = None,
        export_format: Optional[str] = None,
        export_filename: Optional[str] = None,
        notify_on_critical: bool = False,
        notification_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze index efficiency.

        Args:
            indexes: List of index information dictionaries
            tables_sizes: Dictionary mapping table names to sizes in bytes
            export_format: Export format (json, csv, html)
            export_filename: Export filename
            notify_on_critical: Whether to send notifications for critical findings
            notification_email: Email address for notifications

        Returns:
            Analysis result dictionary
        """
        from ..index_efficiency.index_analyzer import IndexInfo
        
        # Convert indexes to IndexInfo objects
        index_objects = []
        for index_data in indexes:
            try:
                index_objects.append(IndexInfo(**index_data))
            except Exception as e:
                logger.error(f"Error converting index data: {e}")
                
        # Generate cache key based on input data
        cache_key = f"indexes_{hash(str(indexes))}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        # Perform analysis
        analysis_result = self.index_analyzer.analyze_indexes(
            indexes=index_objects,
            tables_sizes=tables_sizes,
        )
        
        # Export if requested
        if export_format and export_filename:
            self._export_result(analysis_result, export_format, export_filename)
            
        # Send notifications if requested
        if notify_on_critical and notification_email and analysis_result.recommendations:
            self.notification_interface.send_email_notification(
                recommendations=analysis_result.recommendations,
                recipient=notification_email,
                subject="Index Efficiency Analysis - Critical Findings",
            )
            
        # Cache result
        result_dict = json.loads(analysis_result.json())
        self._store_in_cache(cache_key, result_dict)
        
        return result_dict
    
    def analyze_tablespace_fragmentation(
        self,
        tablespaces: List[Dict[str, Any]],
        fragmentation_data: Optional[Dict[str, Dict[str, Any]]] = None,
        export_format: Optional[str] = None,
        export_filename: Optional[str] = None,
        notify_on_critical: bool = False,
        notification_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze tablespace fragmentation.

        Args:
            tablespaces: List of tablespace information dictionaries
            fragmentation_data: Dictionary with raw fragmentation data by tablespace name
            export_format: Export format (json, csv, html)
            export_filename: Export filename
            notify_on_critical: Whether to send notifications for critical findings
            notification_email: Email address for notifications

        Returns:
            Analysis result dictionary
        """
        from ..tablespace_fragmentation.fragmentation_analyzer import TablespaceInfo
        
        # Convert tablespaces to TablespaceInfo objects
        tablespace_objects = []
        for ts_data in tablespaces:
            try:
                tablespace_objects.append(TablespaceInfo(**ts_data))
            except Exception as e:
                logger.error(f"Error converting tablespace data: {e}")
                
        # Generate cache key based on input data
        cache_key = f"tablespaces_{hash(str(tablespaces))}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        # Perform analysis
        analysis_result = self.fragmentation_analyzer.analyze_tablespace_fragmentation(
            tablespaces=tablespace_objects,
            fragmentation_data=fragmentation_data,
        )
        
        # Export if requested
        if export_format and export_filename:
            self._export_result(analysis_result, export_format, export_filename)
            
        # Send notifications if requested
        if notify_on_critical and notification_email and analysis_result.recommendations:
            self.notification_interface.send_email_notification(
                recommendations=analysis_result.recommendations,
                recipient=notification_email,
                subject="Tablespace Fragmentation Analysis - Critical Findings",
            )
            
        # Cache result
        result_dict = json.loads(analysis_result.json())
        self._store_in_cache(cache_key, result_dict)
        
        return result_dict
    
    def analyze_backup_compression(
        self,
        backups: List[Dict[str, Any]],
        export_format: Optional[str] = None,
        export_filename: Optional[str] = None,
        notify_on_critical: bool = False,
        notification_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze backup compression efficiency.

        Args:
            backups: List of backup information dictionaries
            export_format: Export format (json, csv, html)
            export_filename: Export filename
            notify_on_critical: Whether to send notifications for critical findings
            notification_email: Email address for notifications

        Returns:
            Analysis result dictionary
        """
        from ..backup_compression.compression_analyzer import BackupInfo
        
        # Convert backups to BackupInfo objects
        backup_objects = []
        for backup_data in backups:
            try:
                backup_objects.append(BackupInfo(**backup_data))
            except Exception as e:
                logger.error(f"Error converting backup data: {e}")
                
        # Generate cache key based on input data
        cache_key = f"backups_{hash(str(backups))}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        # Perform analysis
        analysis_result = self.backup_analyzer.analyze_backup_compression(
            backups=backup_objects,
        )
        
        # Export if requested
        if export_format and export_filename:
            self._export_result(analysis_result, export_format, export_filename)
            
        # Send notifications if requested
        if notify_on_critical and notification_email and analysis_result.recommendations:
            self.notification_interface.send_email_notification(
                recommendations=analysis_result.recommendations,
                recipient=notification_email,
                subject="Backup Compression Analysis - Critical Findings",
            )
            
        # Cache result
        result_dict = json.loads(analysis_result.json())
        self._store_in_cache(cache_key, result_dict)
        
        return result_dict
    
    def comprehensive_analysis(
        self,
        root_path: Union[str, Path],
        recursive: bool = True,
        export_format: Optional[str] = None,
        export_filename: Optional[str] = None,
        notify_on_critical: bool = False,
        notification_email: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a target path.
        
        This is a high-level method that combines scanning, analysis, and reporting
        in a single operation.
        
        Args:
            root_path: Path to analyze
            recursive: Whether to search recursively 
            export_format: Export format (json, csv, html)
            export_filename: Export filename
            notify_on_critical: Whether to send notifications for critical findings
            notification_email: Email address for notifications
            options: Optional analysis options
            use_cache: Whether to use cached results if available
            
        Returns:
            API result with comprehensive analysis information
        """
        # Generate cache key
        options_str = json.dumps(options or {}, sort_keys=True)
        cache_key = f"comprehensive_{root_path}_{recursive}_{options_str}"
        
        # Try to get from cache
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
            
        # Start with database file analysis
        logger.info(f"Starting comprehensive analysis of {root_path}")
        
        file_analysis = self.analyze_database_files(
            root_path=root_path,
            recursive=recursive,
        )
        
        # Extract database files by category
        db_files = file_analysis.get("detected_files", [])
        
        # Group files by category
        log_files = [f for f in db_files if f.get("category") == "log"]
        backup_files = [f for f in db_files if f.get("category") == "backup"]
        
        # Perform log analysis if we found log files
        log_analysis = {}
        if log_files:
            logger.info(f"Analyzing {len(log_files)} log files")
            log_analysis = self.analyze_transaction_logs(log_files=log_files)
        
        # Perform backup analysis if we found backup files
        backup_analysis = {}
        if backup_files:
            logger.info(f"Analyzing {len(backup_files)} backup files")
            backup_analysis = self.analyze_backup_compression(backups=backup_files)
        
        # Combine all analysis results
        comprehensive_result = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(root_path),
            "file_analysis": file_analysis,
            "log_analysis": log_analysis,
            "backup_analysis": backup_analysis,
            
            # Combine recommendations from all analyses
            "all_recommendations": (
                file_analysis.get("recommendations", []) +
                log_analysis.get("recommendations", []) +
                backup_analysis.get("recommendations", [])
            ),
        }
        
        # Export if requested
        if export_format and export_filename:
            if export_format == "json":
                self.export_interface.export_json(
                    data=comprehensive_result,
                    filename=export_filename,
                )
            elif export_format == "html":
                self.export_interface.export_html_report(
                    data=comprehensive_result,
                    filename=export_filename,
                    title="Comprehensive Database Storage Analysis",
                )
        
        # Send notifications if requested
        if notify_on_critical and notification_email:
            self.notification_interface.send_email_notification(
                recommendations=comprehensive_result["all_recommendations"],
                recipient=notification_email,
                subject="Comprehensive Storage Analysis - Critical Findings",
            )
            
        # Cache result
        if use_cache:
            self._store_in_cache(cache_key, comprehensive_result)
        
        return comprehensive_result
    
    # Legacy methods for backward compatibility
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get result from cache if available and not expired."""
        return self.cache.get(cache_key)
    
    def _store_in_cache(self, cache_key: str, result: Any) -> None:
        """Store result in cache."""
        self.cache.set(cache_key, result)
    
    def _export_result(
        self, 
        result: Any, 
        export_format: str, 
        export_filename: str
    ) -> Optional[str]:
        """
        Export analysis result in the specified format.

        Args:
            result: Analysis result
            export_format: Export format (json, csv, html)
            export_filename: Export filename

        Returns:
            Path to exported file, or None on error
        """
        try:
            output_path = self.output_dir / export_filename
            return export_results(
                data=result.dict() if hasattr(result, "dict") else result,
                file_path=output_path,
                format=export_format
            )
                
        except Exception as e:
            logger.error(f"Error exporting result: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear the results cache."""
        self.cache.clear()
        # For backward compatibility
        self.results_cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cleared results cache")
    
    def get_cached_analysis_keys(self) -> List[str]:
        """Get list of cached analysis keys."""
        return self.cache.get_all_keys()