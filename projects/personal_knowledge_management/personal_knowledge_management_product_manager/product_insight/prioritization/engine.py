"""
Feature prioritization engine for ProductInsight.

This module provides the main functionality for feature prioritization,
including scoring and ranking features using various frameworks.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseModel

from product_insight.models import Feature, PriorityScoreCard, StatusEnum
from product_insight.prioritization.models import (
    FeatureScorer,
    PrioritizationCriteria,
    PrioritizationMethod,
)
from product_insight.storage import FileStorage, StorageInterface


class PrioritizationResult(BaseModel):
    """Result of feature prioritization."""
    
    scored_features: List[Tuple[Feature, PriorityScoreCard]]
    method: PrioritizationMethod
    execution_time_ms: int
    criteria: Optional[PrioritizationCriteria] = None


class PrioritizationStats(BaseModel):
    """Statistics about prioritization data."""
    
    total_features: int
    prioritized_features: int
    avg_score: float
    top_score: float
    bottom_score: float
    method_distribution: Dict[str, int]
    status_distribution: Dict[str, int]


class FeaturePrioritizer:
    """Prioritizes features using various prioritization frameworks."""
    
    def __init__(
        self,
        storage_dir: str,
        feature_storage: Optional[StorageInterface[Feature]] = None,
        scorecard_storage: Optional[StorageInterface[PriorityScoreCard]] = None,
    ):
        """Initialize the feature prioritizer.
        
        Args:
            storage_dir: Base directory for storing feature data
            feature_storage: Optional custom storage for features
            scorecard_storage: Optional custom storage for scorecards
        """
        self.feature_storage = feature_storage or FileStorage(
            entity_type=Feature,
            storage_dir=f"{storage_dir}/features",
            format="json"
        )
        
        self.scorecard_storage = scorecard_storage or FileStorage(
            entity_type=PriorityScoreCard,
            storage_dir=f"{storage_dir}/scorecards",
            format="json"
        )
        
        self.scorer = FeatureScorer()
    
    def add_feature(self, feature: Feature) -> Feature:
        """Add a new feature.
        
        Args:
            feature: Feature to add
            
        Returns:
            Added feature
        """
        return self.feature_storage.save(feature)
    
    def update_feature(self, feature: Feature) -> Feature:
        """Update an existing feature.
        
        Args:
            feature: Feature to update
            
        Returns:
            Updated feature
        """
        return self.feature_storage.save(feature)
    
    def get_feature(self, feature_id: UUID) -> Feature:
        """Get a feature by ID.
        
        Args:
            feature_id: ID of the feature to get
            
        Returns:
            Feature
        """
        return self.feature_storage.get(feature_id)
    
    def delete_feature(self, feature_id: UUID) -> bool:
        """Delete a feature.
        
        Args:
            feature_id: ID of the feature to delete
            
        Returns:
            True if the feature was deleted, False otherwise
        """
        # Delete any associated scorecards
        try:
            scorecards = self.scorecard_storage.list({"feature_id": feature_id})
            for scorecard in scorecards:
                self.scorecard_storage.delete(scorecard.id)
        except Exception as e:
            print(f"Error deleting scorecards for feature {feature_id}: {e}")
        
        # Delete the feature
        return self.feature_storage.delete(feature_id)
    
    def get_all_features(self) -> List[Feature]:
        """Get all features.
        
        Returns:
            List of features
        """
        return self.feature_storage.list()
    
    def get_features_by_status(self, status: StatusEnum) -> List[Feature]:
        """Get features with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of features with the given status
        """
        all_features = self.feature_storage.list()
        return [feature for feature in all_features if feature.status == status]
    
    def get_scorecard(self, feature_id: UUID) -> Optional[PriorityScoreCard]:
        """Get the priority scorecard for a feature.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            PriorityScoreCard if found, None otherwise
        """
        try:
            scorecards = self.scorecard_storage.list({"feature_id": feature_id})
            if scorecards:
                return scorecards[0]
        except Exception:
            pass
        
        return None
    
    def prioritize_feature(
        self,
        feature_id: UUID,
        method: PrioritizationMethod,
        criteria: Optional[PrioritizationCriteria] = None,
        save_result: bool = True
    ) -> Tuple[Feature, PriorityScoreCard]:
        """Prioritize a single feature.
        
        Args:
            feature_id: ID of the feature to prioritize
            method: Prioritization method to use
            criteria: Optional prioritization criteria
            save_result: Whether to save the result
            
        Returns:
            Tuple of (feature, scorecard)
        """
        feature = self.feature_storage.get(feature_id)
        
        # Create default criteria if not provided
        if criteria is None:
            criteria = PrioritizationCriteria(method=method)
        
        # Score the feature
        scorecard = self.scorer.score_feature(feature, method, criteria)
        
        if save_result:
            # Save the scorecard
            self.scorecard_storage.save(scorecard)
            
            # Update the feature with the priority score and method
            feature.priority_score = scorecard.total_score
            feature.priority_method = method.value
            self.feature_storage.save(feature)
        
        return feature, scorecard
    
    def prioritize_features(
        self,
        feature_ids: Optional[List[UUID]] = None,
        method: PrioritizationMethod = PrioritizationMethod.WEIGHTED,
        criteria: Optional[PrioritizationCriteria] = None,
        save_results: bool = True
    ) -> PrioritizationResult:
        """Prioritize multiple features.
        
        Args:
            feature_ids: Optional list of feature IDs to prioritize (all if None)
            method: Prioritization method to use
            criteria: Optional prioritization criteria
            save_results: Whether to save the results
            
        Returns:
            PrioritizationResult with scored features
        """
        start_time = time.time()
        
        # Get features to prioritize
        if feature_ids:
            features = [self.feature_storage.get(fid) for fid in feature_ids]
        else:
            features = self.feature_storage.list()
        
        # Create default criteria if not provided
        if criteria is None:
            criteria = PrioritizationCriteria(method=method)
        
        # Score and rank features
        scored_features = []
        
        for feature in features:
            scorecard = self.scorer.score_feature(feature, method, criteria)
            
            if save_results:
                # Save the scorecard
                self.scorecard_storage.save(scorecard)
                
                # Update the feature with the priority score and method
                feature.priority_score = scorecard.total_score
                feature.priority_method = method.value
                self.feature_storage.save(feature)
            
            scored_features.append((feature, scorecard))
        
        # Sort by score
        scored_features.sort(key=lambda x: x[1].total_score if x[1].total_score else 0, reverse=True)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return PrioritizationResult(
            scored_features=scored_features,
            method=method,
            execution_time_ms=execution_time,
            criteria=criteria
        )
    
    def get_prioritization_stats(self) -> PrioritizationStats:
        """Get statistics about feature prioritization.
        
        Returns:
            PrioritizationStats with statistics
        """
        all_features = self.feature_storage.list()
        
        # Calculate metrics
        total_features = len(all_features)
        prioritized_features = sum(1 for f in all_features if f.priority_score is not None)
        
        # Score statistics
        scores = [f.priority_score for f in all_features if f.priority_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        top_score = max(scores) if scores else 0
        bottom_score = min(scores) if scores else 0
        
        # Method distribution
        method_distribution = {}
        for feature in all_features:
            if feature.priority_method:
                method = feature.priority_method
                method_distribution[method] = method_distribution.get(method, 0) + 1
        
        # Status distribution
        status_distribution = {}
        for feature in all_features:
            status = feature.status.value if feature.status else "unknown"
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return PrioritizationStats(
            total_features=total_features,
            prioritized_features=prioritized_features,
            avg_score=avg_score,
            top_score=top_score,
            bottom_score=bottom_score,
            method_distribution=method_distribution,
            status_distribution=status_distribution
        )
    
    def compare_prioritization_methods(
        self, feature_ids: List[UUID]
    ) -> Dict[str, List[Tuple[Feature, float]]]:
        """Compare different prioritization methods for a set of features.
        
        Args:
            feature_ids: List of feature IDs to compare
            
        Returns:
            Dictionary mapping method names to lists of (feature, score) tuples
        """
        features = [self.feature_storage.get(fid) for fid in feature_ids]
        
        results = {}
        
        # Score features with each method
        for method in PrioritizationMethod:
            scored_features = []
            
            for feature in features:
                scorecard = self.scorer.score_feature(feature, method)
                scored_features.append((feature, scorecard.total_score or 0))
            
            # Sort by score
            scored_features.sort(key=lambda x: x[1], reverse=True)
            
            results[method.value] = scored_features
        
        return results
    
    def get_top_features(
        self, 
        limit: int = 10, 
        method: Optional[PrioritizationMethod] = None
    ) -> List[Tuple[Feature, float]]:
        """Get the top prioritized features.
        
        Args:
            limit: Maximum number of features to return
            method: Optional prioritization method to filter by
            
        Returns:
            List of (feature, score) tuples
        """
        all_features = self.feature_storage.list()
        
        # Filter by method if specified
        if method:
            filtered_features = [
                f for f in all_features 
                if f.priority_method == method.value and f.priority_score is not None
            ]
        else:
            filtered_features = [
                f for f in all_features if f.priority_score is not None
            ]
        
        # Sort by score
        sorted_features = sorted(
            filtered_features,
            key=lambda f: f.priority_score if f.priority_score is not None else 0,
            reverse=True
        )
        
        # Return top features with scores
        return [(f, f.priority_score or 0) for f in sorted_features[:limit]]