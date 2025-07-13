"""Configuration for PyPatternGuard scanner."""

from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class ScannerConfig(BaseModel):
    """Configuration for the security scanner."""
    
    model_config = ConfigDict()
    
    # Scan settings
    max_file_size_mb: float = Field(default=10.0, description="Maximum file size to scan in MB")
    file_extensions: List[str] = Field(
        default=[".py", ".pyw"],
        description="File extensions to scan"
    )
    exclude_patterns: List[str] = Field(
        default=["__pycache__", ".git", ".venv", "venv", "env", "node_modules"],
        description="Patterns to exclude from scanning"
    )
    
    # Performance settings
    max_workers: int = Field(default=4, description="Maximum number of parallel workers")
    chunk_size: int = Field(default=1000, description="Lines per chunk for processing")
    memory_limit_mb: int = Field(default=2048, description="Memory limit in MB")
    timeout_seconds: int = Field(default=300, description="Scan timeout in seconds")
    
    # Detection settings
    min_confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for reporting vulnerabilities"
    )
    enable_heuristics: bool = Field(
        default=True,
        description="Enable heuristic-based detection"
    )
    check_dependencies: bool = Field(
        default=False,
        description="Check dependencies for vulnerabilities"
    )
    
    # Reporting settings
    report_format: str = Field(
        default="json",
        description="Output format (json, xml)",
        pattern="^(json|xml)$"
    )
    include_code_snippets: bool = Field(
        default=True,
        description="Include code snippets in reports"
    )
    snippet_lines_context: int = Field(
        default=3,
        description="Number of context lines for code snippets"
    )
    
    # Compliance settings
    compliance_frameworks: List[str] = Field(
        default=["PCI-DSS", "SOC2"],
        description="Compliance frameworks to check"
    )
    
    # Suppression settings
    suppression_file: Optional[Path] = Field(
        default=None,
        description="Path to suppression rules file"
    )
    enable_auto_suppression: bool = Field(
        default=False,
        description="Enable automatic suppression of common false positives"
    )
    
    # Custom rules
    custom_rules_path: Optional[Path] = Field(
        default=None,
        description="Path to custom detection rules"
    )
    
    # Advanced settings
    ast_timeout_seconds: int = Field(
        default=10,
        description="Timeout for AST parsing per file"
    )
    incremental_scan: bool = Field(
        default=True,
        description="Enable incremental scanning"
    )
    cache_results: bool = Field(
        default=True,
        description="Cache scan results"
    )
    
    @field_serializer('suppression_file', 'custom_rules_path')
    def serialize_path(self, path: Optional[Path]) -> Optional[str]:
        """Serialize Path objects to strings."""
        return str(path) if path else None
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")
        if self.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")
        return True