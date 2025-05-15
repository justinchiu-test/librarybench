"""Analysis functionality for file system scanning results.

This module provides analysis capabilities for processing and deriving 
insights from file system scan results.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union, Tuple
from collections import Counter

from pydantic import BaseModel, Field

from .base import AnalysisEngine
from ..utils.types import (
    ScanResult, ScanSummary, FileCategory, ComplianceCategory,
    PriorityLevel, SensitivityLevel, FileMetadata, AnalysisResult, 
    FindingBase, ScanStatus
)
from ..utils.crypto import CryptoProvider


logger = logging.getLogger(__name__)


class Finding(FindingBase):
    """A finding from analysis of scan results."""
    
    details: Dict[str, Any] = Field(default_factory=dict)
    remediation_steps: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    
    @classmethod
    def from_scan_result(cls, result: ScanResult, scan_idx: int) -> "Finding":
        """
        Create a finding from a scan result.
        
        Args:
            result: Scan result to create finding from
            scan_idx: Index of the scan result
            
        Returns:
            Finding created from scan result
        """
        # Skip results without matches
        if not result.matches:
            return None
        
        # Determine highest sensitivity match
        highest_sensitivity = max(
            [match.sensitivity for match in result.matches],
            key=lambda s: {
                SensitivityLevel.LOW: 1, 
                SensitivityLevel.MEDIUM: 2, 
                SensitivityLevel.HIGH: 3, 
                SensitivityLevel.CRITICAL: 4
            }[s]
        )
        
        # Map sensitivity to priority
        priority_map = {
            SensitivityLevel.LOW: PriorityLevel.LOW,
            SensitivityLevel.MEDIUM: PriorityLevel.MEDIUM,
            SensitivityLevel.HIGH: PriorityLevel.HIGH,
            SensitivityLevel.CRITICAL: PriorityLevel.CRITICAL
        }
        
        # Group matches by category
        categories = Counter([match.category for match in result.matches])
        most_common_category = categories.most_common(1)[0][0]
        
        return cls(
            id=f"FIND-{scan_idx}",
            title=f"Sensitive data found in {result.file_metadata.file_path}",
            description=f"Found {len(result.matches)} matches in file",
            priority=priority_map[highest_sensitivity],
            affected_files=[result.file_metadata.file_path],
            details={
                "file_type": result.file_metadata.file_type,
                "file_size": result.file_metadata.file_size,
                "primary_category": most_common_category,
                "match_count": len(result.matches),
                "categories": dict(categories)
            }
        )


class GenericAnalyzer(AnalysisEngine):
    """
    Generic analyzer for scan results.
    
    This analyzer processes scan results to generate findings and insights.
    """
    
    def __init__(self, name: str = "Generic Analyzer"):
        """
        Initialize analyzer.
        
        Args:
            name: Name of the analyzer
        """
        self.name = name
    
    def analyze(self, scan_results: List[ScanResult]) -> AnalysisResult:
        """
        Analyze scan results.
        
        Args:
            scan_results: List of scan results to analyze
            
        Returns:
            Analysis results
        """
        start_time = datetime.now()
        
        try:
            # Generate findings from scan results
            findings = []
            for i, result in enumerate(scan_results):
                if result.matches:
                    finding = Finding.from_scan_result(result, i)
                    if finding:
                        findings.append(finding)
            
            # Generate summary statistics
            total_matches = sum(len(r.matches) for r in scan_results)
            files_with_matches = sum(1 for r in scan_results if len(r.matches) > 0)
            
            # Categorize findings by priority
            findings_by_priority = Counter([f.priority for f in findings])
            
            # Generate recommendations
            recommendations = []
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return AnalysisResult(
                timestamp=end_time,
                analysis_duration_seconds=duration,
                scan_status=ScanStatus.COMPLETED,
                error_message=None,
                recommendations=recommendations,
                findings=findings,
                summary={
                    "total_files": len(scan_results),
                    "files_with_matches": files_with_matches,
                    "total_matches": total_matches,
                    "findings_by_priority": dict(findings_by_priority)
                }
            )
            
        except Exception as e:
            logger.error(f"Error analyzing scan results: {e}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return AnalysisResult(
                timestamp=end_time,
                analysis_duration_seconds=duration,
                scan_status=ScanStatus.FAILED,
                error_message=str(e),
                recommendations=[],
                findings=[]
            )


class DifferentialAnalyzer(AnalysisEngine):
    """
    Analyzer for comparing scan results over time.
    
    This analyzer identifies changes and trends in scan results.
    """
    
    class ScanBaseline(BaseModel):
        """Baseline for differential analysis."""
        
        baseline_id: str
        name: str
        created_at: datetime
        files: Dict[str, Dict[str, Any]]
        metadata: Dict[str, Any] = Field(default_factory=dict)
        verification_info: Optional[Dict[str, Any]] = None
        
        def verify(self, crypto_provider: CryptoProvider) -> bool:
            """
            Verify baseline integrity.
            
            Args:
                crypto_provider: Provider for crypto operations
                
            Returns:
                True if verification succeeds, False otherwise
            """
            from ..utils.crypto import verify_signed_data
            
            if not self.verification_info:
                return False
            
            # Create a copy of the baseline data without the verification info
            baseline_data = self.dict(exclude={"verification_info"})
            
            # Verify the signature
            return verify_signed_data(
                data=baseline_data,
                signature_info=self.verification_info,
                crypto_provider=crypto_provider
            )
    
    class DifferentialResult(BaseModel):
        """Result of a differential analysis."""
        
        baseline_id: str
        timestamp: datetime
        new_files: List[str]
        modified_files: List[str]
        removed_files: List[str]
        new_matches: Dict[str, List[Dict[str, Any]]]
        removed_matches: Dict[str, List[Dict[str, Any]]]
        
        @property
        def total_new_matches(self) -> int:
            """Get total number of new matches."""
            return sum(len(matches) for matches in self.new_matches.values())
        
        @property
        def total_removed_matches(self) -> int:
            """Get total number of removed matches."""
            return sum(len(matches) for matches in self.removed_matches.values())
    
    def __init__(self, name: str = "Differential Analyzer"):
        """
        Initialize analyzer.
        
        Args:
            name: Name of the analyzer
        """
        self.name = name
    
    def create_baseline(
        self,
        scan_results: List[ScanResult],
        name: str,
        baseline_id: Optional[str] = None,
        crypto_provider: Optional[CryptoProvider] = None
    ) -> ScanBaseline:
        """
        Create a baseline from scan results.
        
        Args:
            scan_results: List of scan results to create baseline from
            name: Name for the baseline
            baseline_id: Optional ID for the baseline
            crypto_provider: Optional crypto provider for signing
            
        Returns:
            Created baseline
        """
        import uuid
        baseline_id = baseline_id or str(uuid.uuid4())
        
        # Create file entries for the baseline
        files = {}
        for result in scan_results:
            file_path = result.file_metadata.file_path
            
            # Create a serializable version of matches
            matches = []
            for match in result.matches:
                matches.append(match.dict())
            
            files[file_path] = {
                "metadata": result.file_metadata.dict(),
                "matches": matches,
                "scan_time": result.scan_time.isoformat(),
                "hash": result.file_metadata.hash_sha256
            }
        
        # Create the baseline
        baseline = self.ScanBaseline(
            baseline_id=baseline_id,
            name=name,
            created_at=datetime.now(),
            files=files,
            metadata={
                "creator": self.name,
                "results_count": len(scan_results),
                "total_matches": sum(len(result.matches) for result in scan_results)
            }
        )
        
        # Sign the baseline if crypto provider is available
        if crypto_provider:
            from ..utils.crypto import sign_data
            
            # Create a copy of the baseline data
            baseline_data = baseline.dict(exclude={"verification_info"})
            
            # Sign the baseline data
            verification_info = sign_data(baseline_data, crypto_provider)
            
            # Update the baseline with verification info
            baseline.verification_info = verification_info
        
        return baseline
    
    def save_baseline(
        self,
        baseline: ScanBaseline,
        file_path: Union[str, Path]
    ) -> str:
        """
        Save baseline to a file.
        
        Args:
            baseline: Baseline to save
            file_path: Path to save to
            
        Returns:
            Path to saved file
        """
        path = Path(file_path)
        
        # Create parent directory if it doesn't exist
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(path, 'w') as f:
            f.write(json.dumps(baseline.dict(), indent=2, default=str))
        
        return str(path)
    
    def load_baseline(self, file_path: Union[str, Path]) -> ScanBaseline:
        """
        Load baseline from a file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            Loaded baseline
        """
        path = Path(file_path)
        
        # Load from file
        with open(path, 'r') as f:
            data = json.loads(f.read())
        
        return self.ScanBaseline(**data)
    
    def compare_to_baseline(
        self,
        baseline: ScanBaseline,
        current_results: List[ScanResult]
    ) -> DifferentialResult:
        """
        Compare current results to a baseline.
        
        Args:
            baseline: Baseline to compare to
            current_results: Current scan results
            
        Returns:
            Differential analysis result
        """
        # Create maps for faster lookup
        baseline_files = set(baseline.files.keys())
        current_files = set(result.file_metadata.file_path for result in current_results)
        current_results_map = {
            result.file_metadata.file_path: result 
            for result in current_results
        }
        
        # Identify file changes
        new_files = current_files - baseline_files
        removed_files = baseline_files - current_files
        common_files = baseline_files.intersection(current_files)
        
        # Identify modified files
        modified_files = []
        for file_path in common_files:
            baseline_hash = baseline.files[file_path].get("hash")
            current_hash = current_results_map[file_path].file_metadata.hash_sha256
            
            if baseline_hash != current_hash:
                modified_files.append(file_path)
        
        # Identify match changes
        new_matches = {}
        removed_matches = {}
        
        # Process new and modified files for new matches
        for file_path in new_files.union(modified_files):
            if file_path in current_results_map and current_results_map[file_path].matches:
                new_matches[file_path] = [
                    match.dict() for match in current_results_map[file_path].matches
                ]
        
        # Process removed and modified files for removed matches
        for file_path in removed_files.union(modified_files):
            if file_path in baseline.files and baseline.files[file_path]["matches"]:
                if file_path in modified_files:
                    # For modified files, identify which matches were removed
                    baseline_match_ids = {
                        self._match_signature(match): match 
                        for match in baseline.files[file_path]["matches"]
                    }
                    current_match_ids = {
                        self._match_signature(match.dict())
                        for match in current_results_map[file_path].matches
                    }
                    
                    removed_match_ids = set(baseline_match_ids.keys()) - current_match_ids
                    if removed_match_ids:
                        removed_matches[file_path] = [
                            baseline_match_ids[match_id] 
                            for match_id in removed_match_ids
                        ]
                else:
                    # For removed files, all matches were removed
                    removed_matches[file_path] = baseline.files[file_path]["matches"]
        
        return self.DifferentialResult(
            baseline_id=baseline.baseline_id,
            timestamp=datetime.now(),
            new_files=list(new_files),
            modified_files=modified_files,
            removed_files=list(removed_files),
            new_matches=new_matches,
            removed_matches=removed_matches
        )
    
    def _match_signature(self, match: Dict[str, Any]) -> str:
        """
        Create a signature for a match to identify it uniquely.
        
        Args:
            match: Match data
            
        Returns:
            Signature string
        """
        sig_parts = [
            match.get("pattern_name", ""),
            match.get("matched_content", ""),
            str(match.get("line_number", ""))
        ]
        return "|".join(sig_parts)
    
    def analyze(self, scan_results: List[ScanResult]) -> AnalysisResult:
        """
        Analyze scan results.
        
        For differential analyzer, this performs a basic analysis without
        comparison to a baseline.
        
        Args:
            scan_results: List of scan results to analyze
            
        Returns:
            Analysis results
        """
        # Use the generic analyzer for basic analysis
        generic_analyzer = GenericAnalyzer(name=f"{self.name} - Generic")
        return generic_analyzer.analyze(scan_results)