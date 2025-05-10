"""
Feedback management module for ProductInsight.

This module provides the main functionality for managing customer feedback,
including importing, processing, clustering, and analyzing feedback.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseModel

from product_insight.feedback.analyzer import FeedbackAnalyzer
from product_insight.feedback.clustering import (
    ClusteringParams,
    ClusteringResult,
    FeedbackClusterer,
)
from product_insight.models import FeedbackCluster, FeedbackItem, SentimentEnum, Tag
from product_insight.storage import FileStorage


class FeedbackStats(BaseModel):
    """Statistics about feedback data."""
    
    total_items: int
    processed_items: int
    clustered_items: int
    unclustered_items: int
    num_clusters: int
    avg_cluster_size: float
    sentiment_counts: Dict[str, int]
    source_counts: Dict[str, int]
    tags_counts: Dict[str, int]
    recently_added_count: int
    recently_updated_count: int


class FeedbackManager:
    """Manages customer feedback processing and analysis."""
    
    def __init__(
        self,
        storage_dir: str,
        feedback_storage: Optional[FileStorage[FeedbackItem]] = None,
        cluster_storage: Optional[FileStorage[FeedbackCluster]] = None,
        use_advanced_embeddings: bool = False,
    ):
        """Initialize the feedback manager.
        
        Args:
            storage_dir: Base directory for storing feedback data
            feedback_storage: Optional custom storage for feedback items
            cluster_storage: Optional custom storage for feedback clusters
            use_advanced_embeddings: Whether to use advanced embeddings for clustering
        """
        self.analyzer = FeedbackAnalyzer()
        self.clusterer = FeedbackClusterer(use_advanced_embeddings=use_advanced_embeddings)

        # Initialize storage
        self.feedback_storage = feedback_storage or FileStorage(
            entity_type=FeedbackItem,
            storage_dir=f"{storage_dir}/feedback",
            format="json"
        )
        
        self.cluster_storage = cluster_storage or FileStorage(
            entity_type=FeedbackCluster,
            storage_dir=f"{storage_dir}/feedback_clusters",
            format="json"
        )
    
    def add_feedback(self, feedback: FeedbackItem, process: bool = True) -> FeedbackItem:
        """Add a new feedback item.
        
        Args:
            feedback: Feedback item to add
            process: Whether to process the feedback immediately
            
        Returns:
            Added feedback item
        """
        if process:
            feedback = self.analyzer.analyze_feedback_item(feedback)
        
        return self.feedback_storage.save(feedback)
    
    def batch_add_feedback(
        self, feedback_items: List[FeedbackItem], process: bool = True
    ) -> List[FeedbackItem]:
        """Add multiple feedback items.
        
        Args:
            feedback_items: List of feedback items to add
            process: Whether to process the feedback immediately
            
        Returns:
            List of added feedback items
        """
        if process:
            feedback_items = self.analyzer.batch_analyze_feedback(feedback_items)
        
        return [self.feedback_storage.save(item) for item in feedback_items]
    
    def process_feedback(self, feedback_id: UUID) -> FeedbackItem:
        """Process a feedback item for sentiment, features, and impact.
        
        Args:
            feedback_id: ID of the feedback item to process
            
        Returns:
            Processed feedback item
        """
        feedback = self.feedback_storage.get(feedback_id)
        
        feedback = self.analyzer.analyze_feedback_item(feedback)
        
        return self.feedback_storage.save(feedback)
    
    def batch_process_feedback(self, feedback_ids: List[UUID]) -> List[FeedbackItem]:
        """Process multiple feedback items.
        
        Args:
            feedback_ids: List of feedback item IDs to process
            
        Returns:
            List of processed feedback items
        """
        feedback_items = [self.feedback_storage.get(fid) for fid in feedback_ids]
        
        processed_items = self.analyzer.batch_analyze_feedback(feedback_items)
        
        return [self.feedback_storage.save(item) for item in processed_items]
    
    def get_unprocessed_feedback(self) -> List[FeedbackItem]:
        """Get all unprocessed feedback items.
        
        Returns:
            List of unprocessed feedback items
        """
        all_feedback = self.feedback_storage.list()
        return [item for item in all_feedback if not item.processed]
    
    def get_unclustered_feedback(self) -> List[FeedbackItem]:
        """Get all processed but unclustered feedback items.
        
        Returns:
            List of unclustered feedback items
        """
        all_feedback = self.feedback_storage.list()
        return [item for item in all_feedback if item.processed and not item.cluster_id]
    
    def cluster_feedback(
        self, params: Optional[ClusteringParams] = None, recalculate: bool = False
    ) -> ClusteringResult:
        """Cluster all processed feedback items.
        
        Args:
            params: Optional clustering parameters
            recalculate: Whether to recalculate all clusters
            
        Returns:
            ClusteringResult with clusters and metrics
        """
        start_time = time.time()
        
        # Get existing clusters
        existing_clusters = self.cluster_storage.list() if not recalculate else []
        
        # Get feedback to cluster
        if recalculate:
            # Cluster all processed feedback
            feedback_to_cluster = [
                item for item in self.feedback_storage.list() if item.processed
            ]
        else:
            # Only cluster unclustered feedback
            feedback_to_cluster = self.get_unclustered_feedback()
        
        if not feedback_to_cluster and not recalculate:
            # No new feedback to cluster
            return ClusteringResult(
                clusters=existing_clusters,
                unclustered_items=[],
                num_clusters=len(existing_clusters),
                execution_time_ms=0,
                avg_cluster_size=sum(len(c.feedback_ids) for c in existing_clusters) / len(existing_clusters) if existing_clusters else 0
            )
        
        if not existing_clusters or recalculate:
            # No existing clusters or recalculating, do full clustering
            result = self.clusterer.cluster_feedback(feedback_to_cluster, params)
            
            # Save new clusters
            for cluster in result.clusters:
                self.cluster_storage.save(cluster)
                
                # Update feedback items with cluster ID
                for feedback_id in cluster.feedback_ids:
                    try:
                        feedback = self.feedback_storage.get(feedback_id)
                        feedback.cluster_id = cluster.id
                        self.feedback_storage.save(feedback)
                    except Exception as e:
                        print(f"Error updating feedback item {feedback_id}: {e}")
        else:
            # Try to add new feedback to existing clusters
            all_feedback_dict = {
                item.id: item for item in self.feedback_storage.list()
            }
            
            updated_clusters, unclustered = self.clusterer.add_to_existing_clusters(
                feedback_to_cluster,
                existing_clusters,
                all_feedback_dict
            )
            
            # Save updated clusters
            for cluster in updated_clusters:
                self.cluster_storage.save(cluster)
                
                # Update feedback items with cluster ID
                for feedback_id in cluster.feedback_ids:
                    try:
                        feedback = all_feedback_dict.get(feedback_id)
                        if feedback and not feedback.cluster_id:
                            feedback.cluster_id = cluster.id
                            self.feedback_storage.save(feedback)
                    except Exception as e:
                        print(f"Error updating feedback item {feedback_id}: {e}")
            
            # If there are still unclustered items and enough to form new clusters
            if unclustered and len(unclustered) >= (params.min_cluster_size if params else 3):
                # Cluster the remaining items
                sub_result = self.clusterer.cluster_feedback(unclustered, params)
                
                # Save new clusters
                for cluster in sub_result.clusters:
                    self.cluster_storage.save(cluster)
                    
                    # Update feedback items with cluster ID
                    for feedback_id in cluster.feedback_ids:
                        try:
                            feedback = self.feedback_storage.get(feedback_id)
                            feedback.cluster_id = cluster.id
                            self.feedback_storage.save(feedback)
                        except Exception as e:
                            print(f"Error updating feedback item {feedback_id}: {e}")
                
                # Combine results
                result = ClusteringResult(
                    clusters=updated_clusters + sub_result.clusters,
                    unclustered_items=sub_result.unclustered_items,
                    num_clusters=len(updated_clusters) + sub_result.num_clusters,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    avg_cluster_size=(
                        sum(len(c.feedback_ids) for c in updated_clusters + sub_result.clusters) / 
                        (len(updated_clusters) + sub_result.num_clusters)
                    ) if updated_clusters or sub_result.clusters else 0,
                    avg_similarity=sub_result.avg_similarity,
                    silhouette_score=sub_result.silhouette_score
                )
            else:
                # Return results with unclustered items
                result = ClusteringResult(
                    clusters=updated_clusters,
                    unclustered_items=unclustered,
                    num_clusters=len(updated_clusters),
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    avg_cluster_size=(
                        sum(len(c.feedback_ids) for c in updated_clusters) / 
                        len(updated_clusters)
                    ) if updated_clusters else 0
                )
        
        return result
    
    def get_feedback_stats(self, days_for_recent: int = 30) -> FeedbackStats:
        """Get statistics about the feedback data.
        
        Args:
            days_for_recent: Number of days to consider as recent
            
        Returns:
            FeedbackStats object with statistics
        """
        all_feedback = self.feedback_storage.list()
        all_clusters = self.cluster_storage.list()
        
        # Calculate metrics
        total_items = len(all_feedback)
        processed_items = sum(1 for item in all_feedback if item.processed)
        clustered_items = sum(1 for item in all_feedback if item.cluster_id)
        unclustered_items = processed_items - clustered_items
        num_clusters = len(all_clusters)
        avg_cluster_size = (
            sum(len(c.feedback_ids) for c in all_clusters) / num_clusters
        ) if num_clusters else 0
        
        # Count sentiments
        sentiment_counts = {}
        for sentiment in SentimentEnum:
            sentiment_counts[sentiment.value] = sum(
                1 for item in all_feedback if item.sentiment == sentiment
            )
        
        # Count sources
        source_counts = {}
        for item in all_feedback:
            source = item.source.value if item.source else "unknown"
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Count tags
        tags_counts = {}
        for item in all_feedback:
            for tag in item.tags:
                tags_counts[tag.name] = tags_counts.get(tag.name, 0) + 1
        
        # Recent items
        recent_cutoff = datetime.now().timestamp() - (days_for_recent * 24 * 60 * 60)
        recently_added_count = sum(
            1 for item in all_feedback 
            if item.created_at.timestamp() >= recent_cutoff
        )
        recently_updated_count = sum(
            1 for item in all_feedback 
            if item.updated_at.timestamp() >= recent_cutoff
        )
        
        return FeedbackStats(
            total_items=total_items,
            processed_items=processed_items,
            clustered_items=clustered_items,
            unclustered_items=unclustered_items,
            num_clusters=num_clusters,
            avg_cluster_size=avg_cluster_size,
            sentiment_counts=sentiment_counts,
            source_counts=source_counts,
            tags_counts=tags_counts,
            recently_added_count=recently_added_count,
            recently_updated_count=recently_updated_count
        )
    
    def find_similar_feedback(
        self, feedback_id: UUID, min_similarity: float = 0.7
    ) -> List[Tuple[FeedbackItem, float]]:
        """Find feedback items similar to a given item.
        
        Args:
            feedback_id: ID of the feedback item
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of tuples with similar feedback items and their similarity scores
        """
        target_feedback = self.feedback_storage.get(feedback_id)
        all_feedback = self.feedback_storage.list()
        candidates = [item for item in all_feedback if item.id != feedback_id]
        
        return self.clusterer.get_similar_feedback(target_feedback, candidates, min_similarity)
    
    def get_highest_impact_clusters(self, limit: int = 10) -> List[FeedbackCluster]:
        """Get the highest impact feedback clusters.
        
        Args:
            limit: Maximum number of clusters to return
            
        Returns:
            List of highest impact clusters
        """
        all_clusters = self.cluster_storage.list()
        
        # Sort by impact score
        sorted_clusters = sorted(
            all_clusters,
            key=lambda c: c.impact_score if c.impact_score is not None else 0,
            reverse=True
        )
        
        return sorted_clusters[:limit]
    
    def get_sentiment_trends(
        self, days: int = 90, interval_days: int = 7
    ) -> Dict[str, List[Tuple[datetime, int]]]:
        """Get sentiment trends over time.
        
        Args:
            days: Number of days to include
            interval_days: Interval size in days
            
        Returns:
            Dictionary mapping sentiment to list of (date, count) pairs
        """
        all_feedback = self.feedback_storage.list()
        
        # Filter by date range
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_feedback = [
            item for item in all_feedback 
            if item.created_at.timestamp() >= cutoff
        ]
        
        # Group by interval
        intervals = {}
        interval_seconds = interval_days * 24 * 60 * 60
        
        for item in recent_feedback:
            if not item.sentiment:
                continue
                
            # Calculate which interval this falls into
            elapsed_seconds = item.created_at.timestamp() - cutoff
            interval_idx = int(elapsed_seconds / interval_seconds)
            interval_date = datetime.fromtimestamp(cutoff + (interval_idx * interval_seconds))
            
            if interval_date not in intervals:
                intervals[interval_date] = {s.value: 0 for s in SentimentEnum}
            
            intervals[interval_date][item.sentiment.value] += 1
        
        # Convert to the expected format
        result = {s.value: [] for s in SentimentEnum}
        
        for date in sorted(intervals.keys()):
            for sentiment, count in intervals[date].items():
                result[sentiment].append((date, count))
        
        return result