"""
Differential analysis for detecting changes in sensitive data.

This module provides functionality to compare scan results over time
to identify newly added, modified, or removed sensitive content.
"""

import os
import json
import pickle
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, Tuple

from pydantic import BaseModel, Field

# Import from common library
from common.core.base import Serializable
from common.core.analysis import DifferentialAnalyzer as CommonDifferentialAnalyzer, AnalysisResult
from common.utils.crypto import CryptoProvider
from common.utils.types import ScanResult as CommonScanResult
from common.utils.types import ScanSummary as CommonScanSummary
from common.utils.types import FileMetadata as CommonFileMetadata

# Import from local package
from file_system_analyzer.detection.scanner import ScanResult, SensitiveDataMatch, FileMetadata
from file_system_analyzer.detection.patterns import ComplianceCategory, SensitivityLevel


class ChangeType(str, Enum):
    """Types of changes detected in differential analysis."""
    NEW_FILE = "new_file"
    MODIFIED_FILE = "modified_file"
    REMOVED_FILE = "removed_file"
    NEW_MATCH = "new_match"
    REMOVED_MATCH = "removed_match"
    FILE_UNCHANGED = "file_unchanged"


class BaselineEntry(BaseModel, Serializable):
    """Entry in a baseline for a single file."""
    file_path: str
    file_hash: str
    last_modified: datetime
    matches: List[SensitiveDataMatch] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Implement Serializable interface
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for serialization."""
        data = self.model_dump()
        data["last_modified"] = data["last_modified"].isoformat()
        
        # Convert matches
        matches_list = []
        for match in self.matches:
            if hasattr(match, "to_dict") and callable(match.to_dict):
                matches_list.append(match.to_dict())
            else:
                match_dict = match.model_dump()
                matches_list.append(match_dict)
                
        data["matches"] = matches_list
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BaselineEntry':
        """Create a BaselineEntry from a dictionary."""
        # Convert datetime strings
        if "last_modified" in data and isinstance(data["last_modified"], str):
            data["last_modified"] = datetime.fromisoformat(data["last_modified"])
            
        # Convert matches
        if "matches" in data:
            matches = []
            for match_data in data["matches"]:
                matches.append(SensitiveDataMatch(**match_data))
            data["matches"] = matches
            
        return cls(**data)


class ScanBaseline(BaseModel, Serializable):
    """Baseline of a previous scan for differential analysis."""
    baseline_id: str
    creation_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    name: str
    description: Optional[str] = None
    files: Dict[str, BaselineEntry] = Field(default_factory=dict)
    verification_info: Optional[Dict[str, Any]] = None
    
    def sign(self, crypto_provider: CryptoProvider) -> None:
        """Sign the baseline with cryptographic verification."""
        # Create a canonical representation of the baseline
        baseline_data = self.model_dump(exclude={"verification_info"})
        baseline_json = json.dumps(baseline_data, sort_keys=True, default=str).encode()
        
        # Create a hash of the baseline
        baseline_hash = crypto_provider.secure_hash(baseline_json)
        
        # Create a timestamped signature
        signature = crypto_provider.timestamp_signature(baseline_json)
        
        self.verification_info = {
            "baseline_hash": baseline_hash,
            "signature": signature,
            "verification_method": "crypto_provider",
            "key_id": crypto_provider.key_id
        }
    
    def verify(self, crypto_provider: CryptoProvider) -> bool:
        """Verify the cryptographic signature of the baseline."""
        if not self.verification_info:
            return False
            
        # Recreate the baseline data without verification_info
        baseline_data = self.model_dump(exclude={"verification_info"})
        baseline_json = json.dumps(baseline_data, sort_keys=True, default=str).encode()
        
        # Verify the hash
        calculated_hash = crypto_provider.secure_hash(baseline_json)
        stored_hash = self.verification_info.get("baseline_hash")
        if calculated_hash != stored_hash:
            return False
            
        # Verify the signature
        signature = self.verification_info.get("signature", {})
        return crypto_provider.verify_timestamped_signature(baseline_json, signature)
        
    # Implement Serializable interface
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for serialization."""
        data = self.model_dump()
        data["creation_time"] = data["creation_time"].isoformat()
        
        # Convert files
        files_dict = {}
        for file_path, entry in self.files.items():
            files_dict[file_path] = entry.to_dict()
        data["files"] = files_dict
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScanBaseline':
        """Create a ScanBaseline from a dictionary."""
        # Convert datetime strings
        if "creation_time" in data and isinstance(data["creation_time"], str):
            data["creation_time"] = datetime.fromisoformat(data["creation_time"])
            
        # Convert files
        if "files" in data:
            files = {}
            for file_path, entry_data in data["files"].items():
                files[file_path] = BaselineEntry.from_dict(entry_data)
            data["files"] = files
            
        return cls(**data)


class FileChange(BaseModel, Serializable):
    """Changes detected in a file between baseline and current scan."""
    file_path: str
    change_type: ChangeType
    baseline_hash: Optional[str] = None
    current_hash: Optional[str] = None
    baseline_modified: Optional[datetime] = None
    current_modified: Optional[datetime] = None
    new_matches: List[SensitiveDataMatch] = Field(default_factory=list)
    removed_matches: List[SensitiveDataMatch] = Field(default_factory=list)
    
    @property
    def has_sensitive_changes(self) -> bool:
        """Check if there are sensitive data changes in this file."""
        return len(self.new_matches) > 0 or len(self.removed_matches) > 0
    
    # Implement Serializable interface
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for serialization."""
        data = self.model_dump()
        
        # Convert datetimes
        if self.baseline_modified:
            data["baseline_modified"] = self.baseline_modified.isoformat()
        if self.current_modified:
            data["current_modified"] = self.current_modified.isoformat()
        
        # Convert matches
        new_matches_list = []
        for match in self.new_matches:
            if hasattr(match, "to_dict") and callable(match.to_dict):
                new_matches_list.append(match.to_dict())
            else:
                match_dict = match.model_dump()
                new_matches_list.append(match_dict)
        data["new_matches"] = new_matches_list
        
        removed_matches_list = []
        for match in self.removed_matches:
            if hasattr(match, "to_dict") and callable(match.to_dict):
                removed_matches_list.append(match.to_dict())
            else:
                match_dict = match.model_dump()
                removed_matches_list.append(match_dict)
        data["removed_matches"] = removed_matches_list
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileChange':
        """Create a FileChange from a dictionary."""
        # Convert datetime strings
        if "baseline_modified" in data and isinstance(data["baseline_modified"], str):
            data["baseline_modified"] = datetime.fromisoformat(data["baseline_modified"])
        if "current_modified" in data and isinstance(data["current_modified"], str):
            data["current_modified"] = datetime.fromisoformat(data["current_modified"])
            
        # Convert matches
        if "new_matches" in data:
            new_matches = []
            for match_data in data["new_matches"]:
                new_matches.append(SensitiveDataMatch(**match_data))
            data["new_matches"] = new_matches
            
        if "removed_matches" in data:
            removed_matches = []
            for match_data in data["removed_matches"]:
                removed_matches.append(SensitiveDataMatch(**match_data))
            data["removed_matches"] = removed_matches
            
        return cls(**data)


class DifferentialScanResult(BaseModel, Serializable):
    """Results of a differential scan comparing current results to a baseline."""
    baseline_id: str
    scan_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changes: List[FileChange] = Field(default_factory=list)
    
    @property
    def new_files(self) -> List[FileChange]:
        """Get all new files."""
        return [c for c in self.changes if c.change_type == ChangeType.NEW_FILE]
    
    @property
    def modified_files(self) -> List[FileChange]:
        """Get all modified files."""
        return [c for c in self.changes if c.change_type == ChangeType.MODIFIED_FILE]
    
    @property
    def removed_files(self) -> List[FileChange]:
        """Get all removed files."""
        return [c for c in self.changes if c.change_type == ChangeType.REMOVED_FILE]
    
    @property
    def unchanged_files(self) -> List[FileChange]:
        """Get all unchanged files."""
        return [c for c in self.changes if c.change_type == ChangeType.FILE_UNCHANGED]
    
    @property
    def files_with_new_matches(self) -> List[FileChange]:
        """Get all files with new sensitive data matches."""
        return [c for c in self.changes if len(c.new_matches) > 0]
    
    @property
    def files_with_removed_matches(self) -> List[FileChange]:
        """Get all files with removed sensitive data matches."""
        return [c for c in self.changes if len(c.removed_matches) > 0]
    
    @property
    def has_sensitive_changes(self) -> bool:
        """Check if there are any sensitive data changes."""
        return any(c.has_sensitive_changes for c in self.changes)
    
    @property
    def total_new_matches(self) -> int:
        """Get the total number of new sensitive data matches."""
        return sum(len(c.new_matches) for c in self.changes)
    
    @property
    def total_removed_matches(self) -> int:
        """Get the total number of removed sensitive data matches."""
        return sum(len(c.removed_matches) for c in self.changes)
    
    # Implement Serializable interface
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for serialization."""
        data = self.model_dump()
        data["scan_time"] = self.scan_time.isoformat()
        
        # Convert changes
        changes_list = []
        for change in self.changes:
            changes_list.append(change.to_dict())
        data["changes"] = changes_list
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DifferentialScanResult':
        """Create a DifferentialScanResult from a dictionary."""
        # Convert datetime strings
        if "scan_time" in data and isinstance(data["scan_time"], str):
            data["scan_time"] = datetime.fromisoformat(data["scan_time"])
            
        # Convert changes
        if "changes" in data:
            changes = []
            for change_data in data["changes"]:
                changes.append(FileChange.from_dict(change_data))
            data["changes"] = changes
            
        return cls(**data)


class DifferentialAnalyzer(CommonDifferentialAnalyzer):
    """Analyzer for comparing scan results to a baseline."""
    
    def __init__(self, crypto_provider: Optional[CryptoProvider] = None):
        """Initialize the analyzer."""
        super().__init__()
        self.crypto_provider = crypto_provider
    
    def create_baseline(
        self, 
        scan_results: List[ScanResult], 
        name: str, 
        description: Optional[str] = None,
        baseline_id: Optional[str] = None,
        crypto_provider: Optional[CryptoProvider] = None
    ) -> ScanBaseline:
        """Create a baseline from scan results."""
        baseline = ScanBaseline(
            baseline_id=baseline_id or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
            name=name,
            description=description,
            files={}
        )
        
        # Add each file to the baseline
        for result in scan_results:
            file_path = result.file_metadata.file_path
            
            baseline.files[file_path] = BaselineEntry(
                file_path=file_path,
                file_hash=result.file_metadata.hash_sha256,
                last_modified=result.file_metadata.modification_time,
                matches=result.matches,
                metadata={
                    "file_size": result.file_metadata.file_size,
                    "file_type": result.file_metadata.file_type,
                    "mime_type": result.file_metadata.mime_type,
                    "scan_time": result.scan_time.isoformat()
                }
            )
        
        # Sign the baseline if a crypto provider is available
        if crypto_provider:
            baseline.sign(crypto_provider)
            
        return baseline
    
    def save_baseline(self, baseline: ScanBaseline, file_path: str) -> None:
        """Save a baseline to a file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save as JSON using Serializable interface
        with open(file_path, 'w') as f:
            f.write(json.dumps(baseline.to_dict(), default=str))
    
    def load_baseline(self, file_path: str) -> ScanBaseline:
        """Load a baseline from a file."""
        with open(file_path, 'r') as f:
            data = json.loads(f.read())
        
        # Use Serializable interface to create the baseline
        return ScanBaseline.from_dict(data)
    
    def compare_to_baseline(
        self, 
        baseline: ScanBaseline, 
        current_results: List[ScanResult]
    ) -> DifferentialScanResult:
        """Compare current scan results to a baseline."""
        diff_result = DifferentialScanResult(
            baseline_id=baseline.baseline_id,
            changes=[]
        )
        
        # Create a mapping of file paths to current results for efficient lookup
        current_files = {r.file_metadata.file_path: r for r in current_results}
        
        # Create sets of file paths for faster comparison
        baseline_paths = set(baseline.files.keys())
        current_paths = set(current_files.keys())
        
        # Find new files
        for file_path in current_paths - baseline_paths:
            result = current_files[file_path]
            
            change = FileChange(
                file_path=file_path,
                change_type=ChangeType.NEW_FILE,
                current_hash=result.file_metadata.hash_sha256,
                current_modified=result.file_metadata.modification_time,
                new_matches=result.matches
            )
            
            diff_result.changes.append(change)
        
        # Find removed files
        for file_path in baseline_paths - current_paths:
            baseline_entry = baseline.files[file_path]
            
            change = FileChange(
                file_path=file_path,
                change_type=ChangeType.REMOVED_FILE,
                baseline_hash=baseline_entry.file_hash,
                baseline_modified=baseline_entry.last_modified,
                removed_matches=baseline_entry.matches
            )
            
            diff_result.changes.append(change)
        
        # Compare common files
        for file_path in baseline_paths & current_paths:
            baseline_entry = baseline.files[file_path]
            current_result = current_files[file_path]
            
            # Determine if the file content has changed
            if baseline_entry.file_hash != current_result.file_metadata.hash_sha256:
                change_type = ChangeType.MODIFIED_FILE
                
                # Compare matches to find new and removed
                baseline_matches = {
                    (m.pattern_name, m.matched_content): m 
                    for m in baseline_entry.matches
                }
                current_matches = {
                    (m.pattern_name, m.matched_content): m 
                    for m in current_result.matches
                }
                
                baseline_keys = set(baseline_matches.keys())
                current_keys = set(current_matches.keys())
                
                new_matches = [current_matches[k] for k in current_keys - baseline_keys]
                removed_matches = [baseline_matches[k] for k in baseline_keys - current_keys]
                
                change = FileChange(
                    file_path=file_path,
                    change_type=change_type,
                    baseline_hash=baseline_entry.file_hash,
                    current_hash=current_result.file_metadata.hash_sha256,
                    baseline_modified=baseline_entry.last_modified,
                    current_modified=current_result.file_metadata.modification_time,
                    new_matches=new_matches,
                    removed_matches=removed_matches
                )
                
                diff_result.changes.append(change)
            else:
                # File hasn't changed, but we still record it
                change = FileChange(
                    file_path=file_path,
                    change_type=ChangeType.FILE_UNCHANGED,
                    baseline_hash=baseline_entry.file_hash,
                    current_hash=current_result.file_metadata.hash_sha256,
                    baseline_modified=baseline_entry.last_modified,
                    current_modified=current_result.file_metadata.modification_time
                )
                
                diff_result.changes.append(change)
        
        return diff_result
    
    # Implement CommonDifferentialAnalyzer interface methods
    def analyze(self, data: Any, options: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Analyze data with specified options (CommonDifferentialAnalyzer interface)."""
        if not options:
            options = {}
            
        # Check if required data is present
        if not isinstance(data, dict) or "current" not in data or "baseline" not in data:
            raise ValueError("Data must contain 'current' and 'baseline' keys")
            
        current_results = data["current"]
        baseline = data["baseline"]
        
        # Perform differential analysis
        diff_result = self.compare_to_baseline(baseline, current_results)
        
        # Convert to AnalysisResult
        result = AnalysisResult(
            timestamp=datetime.now(timezone.utc),
            analysis_duration_seconds=0.0,  # Would be set by timing the actual analysis
            scan_status="completed"
        )
        
        # Add differential-specific data
        result.metadata = {
            "baseline_id": diff_result.baseline_id,
            "new_files_count": len(diff_result.new_files),
            "modified_files_count": len(diff_result.modified_files),
            "removed_files_count": len(diff_result.removed_files),
            "unchanged_files_count": len(diff_result.unchanged_files),
            "new_matches_count": diff_result.total_new_matches,
            "removed_matches_count": diff_result.total_removed_matches,
            "has_sensitive_changes": diff_result.has_sensitive_changes
        }
        
        # Add the differential result for access by callers
        result.raw_data = diff_result
        
        return result
    
    def can_analyze(self, data: Any) -> bool:
        """Check if the analyzer can analyze the given data."""
        return (isinstance(data, dict) and 
                "current" in data and 
                "baseline" in data and
                isinstance(data["current"], list) and
                isinstance(data["baseline"], ScanBaseline))
    
    def to_common_baseline(self, baseline: ScanBaseline) -> dict:
        """Convert a ScanBaseline to a format compatible with common library."""
        return baseline.to_dict()
    
    def from_common_baseline(self, data: dict) -> ScanBaseline:
        """Create a ScanBaseline from a common format dictionary."""
        return ScanBaseline.from_dict(data)