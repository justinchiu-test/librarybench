"""Base analysis framework shared across implementations."""

import time
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Type variable for analyzable items
T = TypeVar('T')
# Type variable for analysis results
R = TypeVar('R')


class AnalysisResult(BaseModel, Generic[T]):
    """
    Result of an analysis operation.
    
    Provides information about the analysis process and outcome.
    """
    
    id: Union[str, UUID] = Field(default_factory=uuid4)
    subject_id: Optional[Union[str, UUID]] = None
    subject_type: str
    analysis_type: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[float] = None
    result_summary: Dict[str, Any] = Field(default_factory=dict)
    detailed_results: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class AnalysisParameters(BaseModel):
    """
    Parameters for an analysis operation.
    
    Used to configure analysis options and settings.
    """
    
    period_start: Optional[Union[date, datetime]] = None
    period_end: Optional[Union[date, datetime]] = None
    include_details: bool = True
    calculation_mode: str = "standard"  # "standard", "detailed", "fast"
    grouping: Optional[str] = None
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class BaseAnalyzer(Generic[T, R], ABC):
    """
    Abstract base class for analysis engines.
    
    Defines the core interface and functionality for all analyzers
    across different persona implementations.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self._analysis_cache: Dict[str, R] = {}
    
    @abstractmethod
    def analyze(
        self, subject: T, parameters: Optional[AnalysisParameters] = None
    ) -> R:
        """
        Analyze a single subject.
        
        Args:
            subject: The subject to analyze
            parameters: Optional parameters to configure the analysis
            
        Returns:
            Analysis result
        """
        pass
    
    def analyze_batch(
        self, subjects: List[T], parameters: Optional[AnalysisParameters] = None
    ) -> List[R]:
        """
        Analyze multiple subjects.
        
        Args:
            subjects: List of subjects to analyze
            parameters: Optional parameters to configure the analysis
            
        Returns:
            List of analysis results
        """
        # Start performance timer
        start_time = time.time()
        
        # Analyze each subject
        results = []
        for subject in subjects:
            result = self.analyze(subject, parameters)
            results.append(result)
        
        # Performance metrics
        elapsed_time = time.time() - start_time
        
        return results
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._analysis_cache = {}
    
    def _generate_cache_key(
        self, subject_id: Union[str, UUID], parameters: Optional[AnalysisParameters] = None
    ) -> str:
        """
        Generate a cache key for a subject and parameters.
        
        Args:
            subject_id: ID of the subject being analyzed
            parameters: Optional parameters to configure the analysis
            
        Returns:
            Cache key string
        """
        # Start with the subject ID
        key = f"subject_{subject_id}"
        
        # Add parameter details if provided
        if parameters:
            param_dict = parameters.dict(exclude_none=True)
            for k, v in sorted(param_dict.items()):
                if k != "custom_settings":
                    key += f"_{k}_{v}"
                    
            # Handle custom settings separately (they could be complex)
            if parameters.custom_settings:
                for k, v in sorted(parameters.custom_settings.items()):
                    key += f"_{k}_{v}"
        
        return key
    
    def _get_from_cache(
        self, subject_id: Union[str, UUID], parameters: Optional[AnalysisParameters] = None
    ) -> Optional[R]:
        """
        Get a cached analysis result if available.
        
        Args:
            subject_id: ID of the subject being analyzed
            parameters: Optional parameters to configure the analysis
            
        Returns:
            Cached result or None if not found
        """
        cache_key = self._generate_cache_key(subject_id, parameters)
        return self._analysis_cache.get(cache_key)
    
    def _save_to_cache(
        self, subject_id: Union[str, UUID], result: R, parameters: Optional[AnalysisParameters] = None
    ) -> None:
        """
        Save an analysis result to the cache.
        
        Args:
            subject_id: ID of the subject being analyzed
            result: The analysis result to cache
            parameters: Optional parameters to configure the analysis
        """
        cache_key = self._generate_cache_key(subject_id, parameters)
        self._analysis_cache[cache_key] = result