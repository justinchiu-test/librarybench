"""Main security scanner implementation."""

import ast
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Set

from .config import ScannerConfig
from .models import (
    ScanResult,
    Vulnerability,
    ComplianceReport,
    ComplianceRequirement,
    ComplianceFramework,
    SuppressionRule,
)
from .patterns import (
    HardcodedSecretDetector,
    SQLInjectionDetector,
    CryptographicMisuseDetector,
    InputValidationDetector,
)
from .suppression import SuppressionManager
from .compliance import ComplianceMapper
from .reports import ReportGenerator


class SecurityScanner:
    """Main security scanner for detecting vulnerabilities."""
    
    def __init__(self, config: Optional[ScannerConfig] = None):
        self.config = config or ScannerConfig()
        self.config.validate_config()
        
        # Initialize detectors
        self.detectors = [
            HardcodedSecretDetector(),
            SQLInjectionDetector(),
            CryptographicMisuseDetector(),
            InputValidationDetector(),
        ]
        
        # Initialize components
        self.suppression_manager = SuppressionManager(self.config.suppression_file)
        self.compliance_mapper = ComplianceMapper()
        self.report_generator = ReportGenerator()
        
        # Scan state
        self._scanned_files: Set[Path] = set()
        self._scan_errors: List[Dict[str, Any]] = []
    
    def scan(self, target_path: str) -> ScanResult:
        """Scan target path for security vulnerabilities."""
        start_time = time.time()
        target = Path(target_path).resolve()
        
        if not target.exists():
            raise ValueError(f"Target path does not exist: {target}")
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Collect files to scan
        files_to_scan = self._collect_files(target)
        
        # Scan files
        all_vulnerabilities = []
        total_lines = 0
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_file = {
                executor.submit(self._scan_file, file_path): file_path
                for file_path in files_to_scan
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    vulnerabilities, lines_count = future.result()
                    all_vulnerabilities.extend(vulnerabilities)
                    total_lines += lines_count
                    self._scanned_files.add(file_path)
                except Exception as e:
                    self._scan_errors.append({
                        "file": str(file_path),
                        "error": str(e),
                        "type": type(e).__name__
                    })
        
        # Apply suppression rules
        all_vulnerabilities = self._apply_suppressions(all_vulnerabilities)
        
        # Create scan result
        scan_duration = time.time() - start_time
        scan_result = ScanResult(
            scan_id=scan_id,
            timestamp=datetime.now(),
            target_path=target,
            total_files_scanned=len(self._scanned_files),
            total_lines_scanned=total_lines,
            scan_duration_seconds=scan_duration,
            vulnerabilities=all_vulnerabilities,
            scan_errors=self._scan_errors,
            metadata={
                "scanner_version": "1.0.0",
                "config": self.config.model_dump(),
                "detectors": [d.__class__.__name__ for d in self.detectors]
            }
        )
        
        return scan_result
    
    def _collect_files(self, target: Path) -> List[Path]:
        """Collect files to scan based on configuration."""
        files = []
        
        if target.is_file():
            if self._should_scan_file(target):
                files.append(target)
        else:
            for extension in self.config.file_extensions:
                files.extend(target.rglob(f"*{extension}"))
        
        # Filter files
        filtered_files = []
        for file_path in files:
            if self._should_scan_file(file_path):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        # Check file size
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                return False
        except:
            return False
        
        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _scan_file(self, file_path: Path) -> tuple[List[Vulnerability], int]:
        """Scan individual file for vulnerabilities."""
        vulnerabilities = []
        lines_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines_count = len(content.splitlines())
            
            # Parse AST if possible
            tree = None
            try:
                tree = ast.parse(content, filename=str(file_path))
            except:
                # Continue with pattern-based detection only
                pass
            
            # Run all detectors
            for detector in self.detectors:
                try:
                    vulns = detector.detect(file_path, content, tree)
                    vulnerabilities.extend(vulns)
                except Exception as e:
                    self._scan_errors.append({
                        "file": str(file_path),
                        "detector": detector.__class__.__name__,
                        "error": str(e)
                    })
            
            # Filter by confidence threshold
            vulnerabilities = [
                v for v in vulnerabilities
                if v.confidence >= self.config.min_confidence_threshold
            ]
            
        except Exception as e:
            self._scan_errors.append({
                "file": str(file_path),
                "error": str(e),
                "type": "file_read_error"
            })
        
        return vulnerabilities, lines_count
    
    def _apply_suppressions(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Apply suppression rules to vulnerabilities."""
        for vuln in vulnerabilities:
            if self.suppression_manager.should_suppress(vuln):
                vuln.suppressed = True
                vuln.suppression_reason = self.suppression_manager.get_suppression_reason(vuln)
        return vulnerabilities
    
    def generate_compliance_report(self, scan_result: ScanResult) -> ComplianceReport:
        """Generate compliance report from scan results."""
        return self.compliance_mapper.generate_report(scan_result)
    
    def export_results(self, scan_result: ScanResult, output_path: str, 
                      format: Optional[str] = None) -> None:
        """Export scan results to file."""
        format = format or self.config.report_format
        self.report_generator.export(scan_result, output_path, format)