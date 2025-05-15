"""
Compliance Data Discovery Scanner.

This module provides the main scanner functionality that integrates all the components
of the Compliance Data Discovery Analyzer.
"""

import os
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Iterator

from pydantic import BaseModel, Field

# Import from common library
from common.core.base import ScanSession
from common.core.api import BaseAnalyzerAPI, APIResult, NotificationConfig, CacheConfig
from common.core.analysis import DifferentialAnalyzer, GenericAnalyzer
from common.core.reporting import GenericReportGenerator, Report
from common.utils.crypto import CryptoProvider
from common.utils.export import export_to_json, export_to_html, export_results
from common.utils.cache import cache_result

# Import from persona-specific modules
from file_system_analyzer.detection.scanner import (
    SensitiveDataScanner, 
    ScanOptions, 
    ScanResult,
    ScanSummary
)
from file_system_analyzer.detection.patterns import (
    PatternDefinitions,
    ComplianceCategory,
    SensitivityLevel
)
from file_system_analyzer.audit.logger import (
    AuditLogger,
    AuditEventType
)
from file_system_analyzer.reporting.reports import (
    ReportGenerator,
    ComplianceReport
)
from file_system_analyzer.reporting.frameworks import FrameworkRegistry
from file_system_analyzer.differential.analyzer import (
    DifferentialAnalyzer as SecurityDifferentialAnalyzer,
    ScanBaseline,
    DifferentialScanResult
)
from file_system_analyzer.custody.evidence import (
    EvidencePackager,
    EvidencePackage,
    EvidenceType
)


class ComplianceScanOptions(BaseModel):
    """Options for a compliance scan."""
    scan_options: ScanOptions = Field(default_factory=ScanOptions)
    output_dir: Optional[str] = None
    user_id: str = "system"
    baseline_id: Optional[str] = None
    create_baseline: bool = False
    baseline_name: Optional[str] = None
    generate_reports: bool = True
    report_frameworks: List[str] = Field(default_factory=list)
    create_evidence_package: bool = False
    evidence_package_name: Optional[str] = None
    audit_log_file: Optional[str] = None


class ComplianceScanner:
    """Main scanner for compliance data discovery."""
    
    def __init__(
        self, 
        options: Optional[ComplianceScanOptions] = None,
        crypto_provider: Optional[CryptoProvider] = None
    ):
        """Initialize scanner with options."""
        self.options = options or ComplianceScanOptions()
        self.crypto_provider = crypto_provider or CryptoProvider.generate()
        
        # Create components
        self.scanner = SensitiveDataScanner(self.options.scan_options)
        self.audit_logger = AuditLogger(
            log_file=self.options.audit_log_file,
            crypto_provider=self.crypto_provider,
            user_id=self.options.user_id
        )
        self.diff_analyzer = SecurityDifferentialAnalyzer()
        self.evidence_packager = EvidencePackager(crypto_provider=self.crypto_provider)
        
        # Initialize state
        self.scan_results = []
        self.scan_summary = None
        self.baseline = None
        self.diff_result = None
        self.reports = {}
        self.evidence_package = None
    
    def scan_directory(self, directory_path: str) -> ScanSummary:
        """Scan a directory for sensitive data."""
        start_time = datetime.now(timezone.utc)
        start_timestamp = time.time()
        
        # Log scan start
        self.audit_logger.log_event(
            event_type=AuditEventType.SCAN_START,
            details={
                "directory": directory_path,
                "recursive": self.options.scan_options.recursive,
                "max_file_size": self.options.scan_options.max_file_size,
                "categories": [c.value for c in self.options.scan_options.categories],
                "min_sensitivity": self.options.scan_options.min_sensitivity
            },
            user_id=self.options.user_id
        )
        
        try:
            # Perform the scan
            self.scan_results = list(self.scanner.scan_directory(directory_path))
            
            # Create scan summary
            self.scan_summary = self.scanner.summarize_scan(self.scan_results)
            
            # Create baseline if requested
            if self.options.create_baseline:
                baseline_name = self.options.baseline_name or f"Baseline_{start_time.strftime('%Y%m%d_%H%M%S')}"
                self.baseline = self.diff_analyzer.create_baseline(
                    scan_results=self.scan_results,
                    name=baseline_name,
                    baseline_id=self.options.baseline_id,
                    crypto_provider=self.crypto_provider
                )
                
                # Save baseline if output directory is specified
                if self.options.output_dir:
                    os.makedirs(self.options.output_dir, exist_ok=True)
                    baseline_path = os.path.join(self.options.output_dir, f"{baseline_name}.json")
                    self.diff_analyzer.save_baseline(self.baseline, baseline_path)
                    
                    # Log baseline creation
                    self.audit_logger.log_event(
                        event_type=AuditEventType.BASELINE_CREATION,
                        details={
                            "baseline_id": self.baseline.baseline_id,
                            "baseline_name": baseline_name,
                            "file_path": baseline_path,
                            "file_count": len(self.baseline.files)
                        },
                        user_id=self.options.user_id
                    )
            
            # Compare to baseline if specified
            elif self.options.baseline_id:
                # Load baseline
                baseline_path = os.path.join(
                    self.options.output_dir or ".", 
                    f"{self.options.baseline_id}.json"
                )
                
                if not os.path.exists(baseline_path):
                    raise FileNotFoundError(f"Baseline not found: {baseline_path}")
                    
                baseline = self.diff_analyzer.load_baseline(baseline_path)
                
                # Verify baseline integrity
                if baseline.verification_info and not baseline.verify(self.crypto_provider):
                    raise ValueError("Baseline integrity verification failed")
                    
                # Compare current scan to baseline
                self.diff_result = self.diff_analyzer.compare_to_baseline(
                    baseline=baseline,
                    current_results=self.scan_results
                )
                
                # Log baseline comparison
                self.audit_logger.log_event(
                    event_type=AuditEventType.BASELINE_COMPARISON,
                    details={
                        "baseline_id": baseline.baseline_id,
                        "new_files": len(self.diff_result.new_files),
                        "modified_files": len(self.diff_result.modified_files),
                        "removed_files": len(self.diff_result.removed_files),
                        "new_matches": self.diff_result.total_new_matches,
                        "removed_matches": self.diff_result.total_removed_matches
                    },
                    user_id=self.options.user_id
                )
            
            # Generate compliance reports if requested
            if self.options.generate_reports:
                frameworks = self.options.report_frameworks
                if not frameworks:
                    # Use all frameworks if none specified
                    frameworks = list(FrameworkRegistry.get_all_frameworks().keys())
                
                for framework_id in frameworks:
                    try:
                        report_generator = ReportGenerator(framework_id)
                        report = report_generator.generate_report(
                            scan_results=self.scan_results,
                            scan_summary=self.scan_summary
                        )
                        
                        # Sign the report
                        report.sign(self.crypto_provider)
                        
                        self.reports[framework_id] = report
                        
                        # Save report if output directory is specified
                        if self.options.output_dir:
                            os.makedirs(self.options.output_dir, exist_ok=True)
                            report_path = os.path.join(
                                self.options.output_dir, 
                                f"compliance_report_{framework_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
                            )
                            report.save(report_path, verify=True, crypto_provider=self.crypto_provider)
                            
                            # Log report generation
                            self.audit_logger.log_event(
                                event_type=AuditEventType.REPORT_GENERATION,
                                details={
                                    "framework_id": framework_id,
                                    "framework_name": report.framework_name,
                                    "file_path": report_path,
                                    "finding_count": report.total_findings
                                },
                                user_id=self.options.user_id
                            )
                    except Exception as e:
                        # Log error but continue with other frameworks
                        self.audit_logger.log_event(
                            event_type=AuditEventType.SYSTEM_ERROR,
                            details={
                                "error": f"Failed to generate report for framework {framework_id}: {str(e)}",
                                "framework_id": framework_id
                            },
                            user_id=self.options.user_id
                        )
            
            # Create evidence package if requested
            if self.options.create_evidence_package and self.options.output_dir:
                package_name = self.options.evidence_package_name or f"Evidence_{start_time.strftime('%Y%m%d_%H%M%S')}"
                self.evidence_package = self.evidence_packager.create_package(
                    name=package_name,
                    description=f"Evidence package for scan of {directory_path}",
                    metadata={
                        "scan_directory": directory_path,
                        "scan_time": start_time.isoformat(),
                        "user_id": self.options.user_id
                    }
                )
                
                # Create temporary directory for evidence files
                evidence_dir = os.path.join(self.options.output_dir, "evidence_files")
                os.makedirs(evidence_dir, exist_ok=True)
                
                # Add reports to evidence package
                for framework_id, report in self.reports.items():
                    report_path = os.path.join(
                        evidence_dir, 
                        f"compliance_report_{framework_id}.json"
                    )
                    with open(report_path, 'w') as f:
                        f.write(report.to_json())
                    
                    self.evidence_packager.add_file_to_package(
                        package=self.evidence_package,
                        file_path=report_path,
                        evidence_type=EvidenceType.COMPLIANCE_REPORT,
                        description=f"Compliance report for {report.framework_name}",
                        metadata={
                            "framework_id": framework_id,
                            "framework_name": report.framework_name,
                            "finding_count": report.total_findings
                        }
                    )
                
                # Add baseline to evidence package if created
                if self.baseline:
                    baseline_path = os.path.join(evidence_dir, "baseline.json")
                    self.diff_analyzer.save_baseline(self.baseline, baseline_path)
                    
                    self.evidence_packager.add_file_to_package(
                        package=self.evidence_package,
                        file_path=baseline_path,
                        evidence_type=EvidenceType.SCAN_BASELINE,
                        description="Scan baseline",
                        metadata={
                            "baseline_id": self.baseline.baseline_id,
                            "baseline_name": self.baseline.name,
                            "file_count": len(self.baseline.files)
                        }
                    )
                
                # Add audit log to evidence package
                if self.options.audit_log_file and os.path.exists(self.options.audit_log_file):
                    self.evidence_packager.add_file_to_package(
                        package=self.evidence_package,
                        file_path=self.options.audit_log_file,
                        evidence_type=EvidenceType.AUDIT_LOG,
                        description="Audit log",
                        metadata={
                            "entry_count": len(self.audit_logger.audit_log.entries)
                        }
                    )
                
                # Add scan summary to evidence package
                summary_path = os.path.join(evidence_dir, "scan_summary.json")
                with open(summary_path, 'w') as f:
                    f.write(json.dumps(self.scan_summary.dict(), default=str))
                    
                self.evidence_packager.add_file_to_package(
                    package=self.evidence_package,
                    file_path=summary_path,
                    evidence_type=EvidenceType.METADATA,
                    description="Scan summary",
                    metadata={
                        "total_files": self.scan_summary.total_files,
                        "files_with_sensitive_data": self.scan_summary.files_with_sensitive_data,
                        "total_matches": self.scan_summary.total_matches
                    }
                )
                
                # Export the evidence package
                package_path = self.evidence_packager.export_package(
                    package=self.evidence_package,
                    output_dir=self.options.output_dir,
                    files_dir=evidence_dir,
                    user_id=self.options.user_id
                )
                
                # Log evidence package creation
                self.audit_logger.log_event(
                    event_type=AuditEventType.REPORT_EXPORT,
                    details={
                        "package_id": self.evidence_package.package_id,
                        "package_name": package_name,
                        "file_path": package_path,
                        "item_count": len(self.evidence_package.items)
                    },
                    user_id=self.options.user_id
                )
            
            # Log scan completion
            end_time = datetime.now(timezone.utc)
            duration = time.time() - start_timestamp
            
            self.audit_logger.log_event(
                event_type=AuditEventType.SCAN_COMPLETE,
                details={
                    "directory": directory_path,
                    "duration": duration,
                    "total_files": self.scan_summary.total_files,
                    "files_with_sensitive_data": self.scan_summary.files_with_sensitive_data,
                    "total_matches": self.scan_summary.total_matches
                },
                user_id=self.options.user_id
            )
            
            return self.scan_summary
            
        except Exception as e:
            # Log scan error
            self.audit_logger.log_event(
                event_type=AuditEventType.SCAN_ERROR,
                details={
                    "directory": directory_path,
                    "error": str(e)
                },
                user_id=self.options.user_id
            )
            
            # Re-raise the exception
            raise


class ComplianceScannerAPI(BaseAnalyzerAPI[ScanResult, Any]):
    """API for compliance scanning operations."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        user_id: str = "system",
        crypto_provider: Optional[CryptoProvider] = None,
        cache_config: Optional[CacheConfig] = None,
        notification_config: Optional[NotificationConfig] = None
    ):
        """
        Initialize the compliance scanner API.
        
        Args:
            output_dir: Directory for output files
            user_id: ID of the user performing operations
            crypto_provider: Provider for cryptographic operations
            cache_config: Configuration for result caching
            notification_config: Configuration for notifications
        """
        # Create scanner components
        scan_options = ScanOptions()
        scanner = SensitiveDataScanner(scan_options)
        analyzer = GenericAnalyzer("Compliance Analyzer")
        
        # Set up compliance report generator
        report_generator = ReportGenerator("default")
        
        super().__init__(
            scanner=scanner,
            analyzer=analyzer,
            report_generator=report_generator,
            cache_config=cache_config,
            notification_config=notification_config
        )
        
        # Security-specific components
        self.output_dir = output_dir
        self.user_id = user_id
        self.crypto_provider = crypto_provider or CryptoProvider.generate()
        self.audit_logger = AuditLogger(
            log_file=os.path.join(output_dir, "audit.log") if output_dir else None,
            crypto_provider=self.crypto_provider,
            user_id=user_id
        )
        self.diff_analyzer = SecurityDifferentialAnalyzer()
        self.evidence_packager = EvidencePackager(crypto_provider=self.crypto_provider)
    
    def analyze_results(self, scan_results: List[ScanResult]) -> Any:
        """
        Analyze scan results.
        
        Args:
            scan_results: Scan results to analyze
            
        Returns:
            Analysis results
        """
        # Use the security-specific analyzer
        return self.analyzer.analyze(scan_results)
    
    def create_baseline(
        self,
        scan_results: List[ScanResult],
        baseline_name: Optional[str] = None,
        baseline_id: Optional[str] = None
    ) -> ScanBaseline:
        """
        Create a baseline from scan results.
        
        Args:
            scan_results: Scan results to create baseline from
            baseline_name: Name for the baseline
            baseline_id: Optional ID for the baseline
            
        Returns:
            Created baseline
        """
        if not baseline_name:
            baseline_name = f"Baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        baseline = self.diff_analyzer.create_baseline(
            scan_results=scan_results,
            name=baseline_name,
            baseline_id=baseline_id,
            crypto_provider=self.crypto_provider
        )
        
        # Log baseline creation
        self.audit_logger.log_event(
            event_type=AuditEventType.BASELINE_CREATION,
            details={
                "baseline_id": baseline.baseline_id,
                "baseline_name": baseline_name,
                "file_count": len(baseline.files)
            },
            user_id=self.user_id
        )
        
        return baseline
    
    def compare_to_baseline(
        self,
        baseline_path: str,
        scan_results: List[ScanResult]
    ) -> DifferentialScanResult:
        """
        Compare scan results to a baseline.
        
        Args:
            baseline_path: Path to the baseline file
            scan_results: Current scan results
            
        Returns:
            Differential scan result
        """
        # Load baseline
        baseline = self.diff_analyzer.load_baseline(baseline_path)
        
        # Verify baseline integrity
        if baseline.verification_info and not baseline.verify(self.crypto_provider):
            raise ValueError("Baseline integrity verification failed")
            
        # Compare current scan to baseline
        diff_result = self.diff_analyzer.compare_to_baseline(
            baseline=baseline,
            current_results=scan_results
        )
        
        # Log baseline comparison
        self.audit_logger.log_event(
            event_type=AuditEventType.BASELINE_COMPARISON,
            details={
                "baseline_id": baseline.baseline_id,
                "new_files": len(diff_result.new_files),
                "modified_files": len(diff_result.modified_files),
                "removed_files": len(diff_result.removed_files),
                "new_matches": diff_result.total_new_matches,
                "removed_matches": diff_result.total_removed_matches
            },
            user_id=self.user_id
        )
        
        return diff_result
    
    def create_evidence_package(
        self,
        scan_results: List[ScanResult],
        scan_summary: ScanSummary,
        package_name: Optional[str] = None,
        directory_path: Optional[str] = None
    ) -> str:
        """
        Create an evidence package for scan results.
        
        Args:
            scan_results: Scan results to include in the package
            scan_summary: Summary of scan results
            package_name: Name for the evidence package
            directory_path: Path that was scanned
            
        Returns:
            Path to the exported evidence package
        """
        if not self.output_dir:
            raise ValueError("Output directory is required for evidence packaging")
            
        if not package_name:
            package_name = f"Evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        # Create evidence package
        package = self.evidence_packager.create_package(
            name=package_name,
            description=f"Evidence package for compliance scan",
            metadata={
                "scan_directory": directory_path or "unknown",
                "scan_time": datetime.now().isoformat(),
                "user_id": self.user_id
            }
        )
        
        # Create temporary directory for evidence files
        evidence_dir = os.path.join(self.output_dir, "evidence_files")
        os.makedirs(evidence_dir, exist_ok=True)
        
        # Add scan summary to evidence package
        summary_path = os.path.join(evidence_dir, "scan_summary.json")
        with open(summary_path, 'w') as f:
            f.write(json.dumps(scan_summary.dict(), default=str))
            
        self.evidence_packager.add_file_to_package(
            package=package,
            file_path=summary_path,
            evidence_type=EvidenceType.METADATA,
            description="Scan summary",
            metadata={
                "total_files": scan_summary.total_files,
                "files_with_sensitive_data": scan_summary.files_with_sensitive_data,
                "total_matches": scan_summary.total_matches
            }
        )
        
        # Add audit log to evidence package
        audit_log_path = self.audit_logger.log_file
        if audit_log_path and os.path.exists(audit_log_path):
            self.evidence_packager.add_file_to_package(
                package=package,
                file_path=audit_log_path,
                evidence_type=EvidenceType.AUDIT_LOG,
                description="Audit log",
                metadata={
                    "entry_count": len(self.audit_logger.audit_log.entries)
                }
            )
        
        # Export the evidence package
        package_path = self.evidence_packager.export_package(
            package=package,
            output_dir=self.output_dir,
            files_dir=evidence_dir,
            user_id=self.user_id
        )
        
        # Log evidence package creation
        self.audit_logger.log_event(
            event_type=AuditEventType.REPORT_EXPORT,
            details={
                "package_id": package.package_id,
                "package_name": package_name,
                "file_path": package_path,
                "item_count": len(package.items)
            },
            user_id=self.user_id
        )
        
        return package_path
    
    def generate_compliance_report(
        self,
        scan_results: List[ScanResult],
        scan_summary: ScanSummary,
        framework_id: str
    ) -> ComplianceReport:
        """
        Generate a compliance report for a specific framework.
        
        Args:
            scan_results: Scan results to include in the report
            scan_summary: Summary of scan results
            framework_id: ID of the compliance framework
            
        Returns:
            Generated compliance report
        """
        # Create framework-specific report generator
        report_generator = ReportGenerator(framework_id)
        
        # Generate report
        report = report_generator.generate_report(
            scan_results=scan_results,
            scan_summary=scan_summary
        )
        
        # Sign the report
        report.sign(self.crypto_provider)
        
        # Log report generation
        self.audit_logger.log_event(
            event_type=AuditEventType.REPORT_GENERATION,
            details={
                "framework_id": framework_id,
                "framework_name": report.framework_name,
                "finding_count": report.total_findings
            },
            user_id=self.user_id
        )
        
        return report
    
    def comprehensive_analysis(
        self,
        target_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> APIResult:
        """
        Perform a comprehensive compliance analysis of a target path.
        
        Args:
            target_path: Path to analyze
            output_dir: Optional directory for output files
            options: Optional analysis options
            use_cache: Whether to use cached results if available
            
        Returns:
            API result with comprehensive analysis information
        """
        # Combine options with target_path for cache key
        options_key = json.dumps(options, sort_keys=True) if options else ""
        cache_key = f"compliance_analysis:{target_path}:{options_key}"
        
        # Try to get from cache
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return APIResult(
                    success=True,
                    message=f"Retrieved cached compliance analysis for {target_path}",
                    result_data=cached_result
                )
        
        try:
            start_time = datetime.now()
            
            # Set up scan options from provided options
            scan_options = self.scanner.options
            if options:
                # Update scanner options if provided
                if "recursive" in options:
                    scan_options.recursive = options["recursive"]
                if "max_file_size" in options:
                    scan_options.max_file_size = options["max_file_size"]
                if "categories" in options:
                    scan_options.categories = options["categories"]
                if "min_sensitivity" in options:
                    scan_options.min_sensitivity = options["min_sensitivity"]
            
            # Create scan session
            session = ScanSession(scanner=self.scanner)
            
            # Log scan start
            self.audit_logger.log_event(
                event_type=AuditEventType.SCAN_START,
                details={
                    "directory": str(target_path),
                    "recursive": scan_options.recursive,
                    "max_file_size": scan_options.max_file_size,
                    "min_sensitivity": scan_options.min_sensitivity
                },
                user_id=self.user_id
            )
            
            # Perform the scan
            scan_summary = session.scan_directory(target_path)
            scan_results = session.scan_results
            
            # Analyze the results
            analysis_result = self.analyze_results(scan_results)
            
            # Create compliance reports for all frameworks
            frameworks = options.get("frameworks", []) if options else []
            if not frameworks:
                # Use all frameworks if none specified
                frameworks = list(FrameworkRegistry.get_all_frameworks().keys())
            
            # Generate reports
            reports = {}
            for framework_id in frameworks:
                try:
                    reports[framework_id] = self.generate_compliance_report(
                        scan_results=scan_results,
                        scan_summary=scan_summary,
                        framework_id=framework_id
                    )
                except Exception as e:
                    self.audit_logger.log_event(
                        event_type=AuditEventType.SYSTEM_ERROR,
                        details={
                            "error": f"Failed to generate report for framework {framework_id}: {str(e)}",
                            "framework_id": framework_id
                        },
                        user_id=self.user_id
                    )
            
            # Create differential analysis if requested
            diff_result = None
            if options and options.get("baseline_path"):
                try:
                    diff_result = self.compare_to_baseline(
                        baseline_path=options["baseline_path"],
                        scan_results=scan_results
                    )
                except Exception as e:
                    self.audit_logger.log_event(
                        event_type=AuditEventType.SYSTEM_ERROR,
                        details={
                            "error": f"Failed to perform differential analysis: {str(e)}",
                            "baseline_path": options["baseline_path"]
                        },
                        user_id=self.user_id
                    )
            
            # Create evidence package if requested
            evidence_package_path = None
            if options and options.get("create_evidence") and output_dir:
                try:
                    evidence_package_path = self.create_evidence_package(
                        scan_results=scan_results,
                        scan_summary=scan_summary,
                        package_name=options.get("evidence_name"),
                        directory_path=str(target_path)
                    )
                except Exception as e:
                    self.audit_logger.log_event(
                        event_type=AuditEventType.SYSTEM_ERROR,
                        details={
                            "error": f"Failed to create evidence package: {str(e)}"
                        },
                        user_id=self.user_id
                    )
            
            # Export reports if requested
            exported_reports = {}
            if output_dir:
                output_path = Path(output_dir)
                os.makedirs(output_path, exist_ok=True)
                
                for framework_id, report in reports.items():
                    try:
                        export_path = output_path / f"compliance_report_{framework_id}.json"
                        report.save(export_path, verify=True, crypto_provider=self.crypto_provider)
                        exported_reports[framework_id] = str(export_path)
                    except Exception as e:
                        self.audit_logger.log_event(
                            event_type=AuditEventType.SYSTEM_ERROR,
                            details={
                                "error": f"Failed to export report for framework {framework_id}: {str(e)}",
                                "framework_id": framework_id
                            },
                            user_id=self.user_id
                        )
            
            # Create result dictionary
            result = {
                "scan_summary": scan_summary.dict(),
                "analysis": analysis_result.dict() if hasattr(analysis_result, "dict") else analysis_result,
                "frameworks": {
                    framework_id: {
                        "name": report.framework_name,
                        "findings": report.total_findings,
                        "compliant": report.is_compliant
                    }
                    for framework_id, report in reports.items()
                },
                "exported_reports": exported_reports,
                "evidence_package": evidence_package_path,
                "differential_analysis": diff_result.dict() if diff_result and hasattr(diff_result, "dict") else None
            }
            
            # Cache the result
            if use_cache:
                self.cache.set(cache_key, result)
            
            # Log scan completion
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.audit_logger.log_event(
                event_type=AuditEventType.SCAN_COMPLETE,
                details={
                    "directory": str(target_path),
                    "duration": duration,
                    "total_files": scan_summary.total_files,
                    "files_with_sensitive_data": scan_summary.files_with_sensitive_data,
                    "total_matches": scan_summary.total_matches
                },
                user_id=self.user_id
            )
            
            return APIResult(
                success=True,
                message=f"Completed comprehensive compliance analysis of {target_path}",
                timestamp=end_time,
                duration_seconds=duration,
                result_data=result
            )
            
        except Exception as e:
            # Log scan error
            self.audit_logger.log_event(
                event_type=AuditEventType.SCAN_ERROR,
                details={
                    "directory": str(target_path),
                    "error": str(e)
                },
                user_id=self.user_id
            )
            
            return APIResult(
                success=False,
                message=f"Error during compliance analysis of {target_path}",
                errors=[str(e)]
            )