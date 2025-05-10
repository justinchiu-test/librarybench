"""
Feedback clustering module for ProductInsight.

This module provides functionality for clustering similar feedback items to identify
patterns in user needs and pain points.
"""

import time
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from product_insight.models import FeedbackCluster, FeedbackItem, SentimentEnum, Tag


class ClusteringParams(BaseModel):
    """Parameters for feedback clustering."""

    min_cluster_size: int = 3
    max_distance: float = 0.7
    min_similarity: float = 0.3
    algorithm: str = "dbscan"


class ClusteringResult(BaseModel):
    """Result of feedback clustering operation."""

    clusters: List[FeedbackCluster]
    unclustered_items: List[FeedbackItem]
    num_clusters: int
    execution_time_ms: int
    avg_cluster_size: float
    avg_similarity: Optional[float] = None
    silhouette_score: Optional[float] = None


class FeedbackClusterer:
    """Clusters similar feedback items."""

    def __init__(self, params: Optional[ClusteringParams] = None, use_advanced_embeddings: bool = False):
        """Initialize the clusterer with parameters.

        Args:
            params: Optional clustering parameters
            use_advanced_embeddings: Whether to use advanced semantic embeddings
        """
        self.params = params or ClusteringParams()
        self.use_advanced_embeddings = use_advanced_embeddings
        # Initialize TF-IDF vectorizer for content similarity
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2)  # Use both unigrams and bigrams
        )
    
    def cluster_feedback(self, feedback_items: List[FeedbackItem], params: Optional[ClusteringParams] = None) -> ClusteringResult:
        """Cluster feedback items based on content similarity.

        Args:
            feedback_items: List of feedback items to cluster
            params: Optional clustering parameters to override default ones

        Returns:
            ClusteringResult with clusters and metrics
        """
        start_time = time.time()
        if not feedback_items:
            return ClusteringResult(
                clusters=[],
                unclustered_items=[],
                num_clusters=0,
                execution_time_ms=0,
                avg_cluster_size=0.0
            )

        # Use provided params if given, otherwise use default
        params = params or self.params

        # Extract content from feedback items
        contents = [item.content for item in feedback_items]

        # Transform content to TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform(contents)
        except Exception as e:
            print(f"Error in vectorization: {e}")
            return ClusteringResult(
                clusters=self._fallback_clustering(feedback_items, params),
                unclustered_items=[],
                num_clusters=1,
                execution_time_ms=int((time.time() - start_time) * 1000),
                avg_cluster_size=len(feedback_items)
            )

        # Compute similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Apply clustering algorithm
        clusters = []

        if params.algorithm == "dbscan":
            clusters = self._apply_dbscan(similarity_matrix, feedback_items, params)
        else:
            # Fallback to simple threshold-based clustering
            clusters = self._apply_threshold_clustering(similarity_matrix, feedback_items, params)

        # Filter clusters that are too small
        min_size = params.min_cluster_size
        clusters = [c for c in clusters if len(c.feedback_ids) >= min_size]

        # Calculate attributes for each cluster
        for cluster in clusters:
            cluster_items = [item for item in feedback_items if item.id in cluster.feedback_ids]
            self._enrich_cluster(cluster, cluster_items)

        # Find unclustered items
        clustered_ids = set()
        for cluster in clusters:
            clustered_ids.update(cluster.feedback_ids)

        unclustered_items = [item for item in feedback_items if item.id not in clustered_ids]

        # Calculate clustering metrics
        avg_cluster_size = sum(len(c.feedback_ids) for c in clusters) / len(clusters) if clusters else 0.0

        # Calculate average similarity within clusters
        avg_similarity = None
        if len(clusters) > 0:
            try:
                total_sim = 0.0
                count = 0
                for cluster in clusters:
                    cluster_items = [item for item in feedback_items if item.id in cluster.feedback_ids]
                    if len(cluster_items) > 1:
                        cluster_contents = [item.content for item in cluster_items]
                        cluster_vectors = self.vectorizer.transform(cluster_contents)
                        sim_matrix = cosine_similarity(cluster_vectors)

                        # Sum similarities (excluding self-similarity)
                        for i in range(len(cluster_items)):
                            for j in range(i + 1, len(cluster_items)):
                                total_sim += sim_matrix[i, j]
                                count += 1

                if count > 0:
                    avg_similarity = total_sim / count
            except Exception as e:
                print(f"Error calculating average similarity: {e}")

        # Calculate silhouette score if possible
        silhouette = None
        if len(clusters) > 1 and len(feedback_items) > len(clusters):
            try:
                # Create cluster labels for each item
                labels = np.zeros(len(feedback_items), dtype=int) - 1  # -1 is for unclustered
                for i, item in enumerate(feedback_items):
                    for ci, cluster in enumerate(clusters):
                        if item.id in cluster.feedback_ids:
                            labels[i] = ci
                            break

                # Only calculate for clustered items
                clustered_indices = np.where(labels >= 0)[0]
                if len(clustered_indices) > len(clusters):
                    # Extract features for clustered items
                    vectors = tfidf_matrix.toarray()[clustered_indices]
                    cluster_labels = labels[clustered_indices]
                    silhouette = silhouette_score(vectors, cluster_labels)
            except Exception as e:
                print(f"Error calculating silhouette score: {e}")

        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        return ClusteringResult(
            clusters=clusters,
            unclustered_items=unclustered_items,
            num_clusters=len(clusters),
            execution_time_ms=execution_time_ms,
            avg_cluster_size=avg_cluster_size,
            avg_similarity=avg_similarity,
            silhouette_score=silhouette
        )
    
    def _apply_dbscan(
        self, similarity_matrix: np.ndarray, feedback_items: List[FeedbackItem],
        params: ClusteringParams
    ) -> List[FeedbackCluster]:
        """Apply DBSCAN clustering.

        Args:
            similarity_matrix: Matrix of similarities between feedback items
            feedback_items: List of feedback items
            params: Clustering parameters

        Returns:
            List of feedback clusters
        """
        # Convert similarity matrix to distance matrix (1 - similarity)
        distance_matrix = 1 - similarity_matrix

        # Apply DBSCAN
        dbscan = DBSCAN(
            eps=params.max_distance,
            min_samples=params.min_cluster_size,
            metric="precomputed"
        )

        try:
            cluster_labels = dbscan.fit_predict(distance_matrix)
        except Exception as e:
            print(f"Error in DBSCAN: {e}")
            return self._fallback_clustering(feedback_items, params)

        # Create clusters from labels
        label_to_cluster = {}
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Noise points
                continue

            if label not in label_to_cluster:
                label_to_cluster[label] = FeedbackCluster(
                    id=uuid4(),
                    name=f"Cluster {label + 1}",
                    feedback_ids=[],
                    central_theme="",
                    sentiment_summary=None,
                    volume=0
                )

            label_to_cluster[label].feedback_ids.append(feedback_items[i].id)

        return list(label_to_cluster.values())
    
    def _apply_threshold_clustering(
        self, similarity_matrix: np.ndarray, feedback_items: List[FeedbackItem],
        params: ClusteringParams
    ) -> List[FeedbackCluster]:
        """Apply simple threshold-based clustering.

        Args:
            similarity_matrix: Matrix of similarities between feedback items
            feedback_items: List of feedback items
            params: Clustering parameters

        Returns:
            List of feedback clusters
        """
        n_items = len(feedback_items)
        clustered = [False] * n_items
        clusters = []

        for i in range(n_items):
            if clustered[i]:
                continue

            # Find items similar to this one
            similar_indices = []
            for j in range(n_items):
                if i != j and similarity_matrix[i, j] >= params.min_similarity:
                    similar_indices.append(j)

            # Create cluster if enough similar items
            if len(similar_indices) + 1 >= params.min_cluster_size:
                cluster = FeedbackCluster(
                    id=uuid4(),
                    name=f"Cluster {len(clusters) + 1}",
                    feedback_ids=[feedback_items[i].id],
                    central_theme="",
                    sentiment_summary=None,
                    volume=0
                )

                clustered[i] = True

                for j in similar_indices:
                    cluster.feedback_ids.append(feedback_items[j].id)
                    clustered[j] = True

                clusters.append(cluster)

        return clusters
    
    def _fallback_clustering(self, feedback_items: List[FeedbackItem], params: ClusteringParams) -> List[FeedbackCluster]:
        """Fallback clustering method if other methods fail.

        Args:
            feedback_items: List of feedback items
            params: Clustering parameters

        Returns:
            List of feedback clusters (one cluster containing all items)
        """
        # Create a single cluster with all items
        cluster = FeedbackCluster(
            id=uuid4(),
            name="All Feedback",
            feedback_ids=[item.id for item in feedback_items],
            central_theme="Diverse Feedback",
            sentiment_summary=None,
            volume=len(feedback_items)
        )

        self._enrich_cluster(cluster, feedback_items)

        return [cluster]
    
    def _enrich_cluster(self, cluster: FeedbackCluster, feedback_items: List[FeedbackItem]) -> None:
        """Enrich a cluster with additional information.
        
        Args:
            cluster: Feedback cluster to enrich
            feedback_items: Feedback items in the cluster
        """
        if not feedback_items:
            return
        
        # Extract common terms from the TF-IDF vectorizer
        try:
            if hasattr(self.vectorizer, 'vocabulary_'):
                # Get most common terms based on TF-IDF scores
                contents = [item.content for item in feedback_items]
                tfidf = self.vectorizer.transform(contents)
                feature_names = self.vectorizer.get_feature_names_out()
                
                # Sum TF-IDF scores across all documents in cluster
                cluster_tfidf = np.sum(tfidf, axis=0)
                indices = np.argsort(cluster_tfidf.toarray()[0])[::-1]
                
                # Take top 5 terms
                top_indices = indices[:5]
                cluster.common_terms = [feature_names[i] for i in top_indices]
        except Exception:
            # Fallback to simple word frequency
            word_freq = {}
            for item in feedback_items:
                words = item.content.lower().split()
                for word in set(words):
                    if len(word) > 3:  # Skip short words
                        word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get most frequent words
            common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            cluster.common_terms = [word for word, _ in common_words]
        
        # Calculate summary sentiment
        cluster.sentiment_summary = self._summarize_sentiment(feedback_items)

        # Calculate impact score
        cluster.impact_score = self._calculate_cluster_impact(feedback_items)

        # Generate cluster name based on common terms
        if cluster.common_terms:
            cluster.name = f"Feedback about {', '.join(cluster.common_terms[:2])}"

        # Create simple summary
        terms_str = ', '.join(cluster.common_terms)
        sentiment_text = cluster.sentiment_summary.value if cluster.sentiment_summary else "unknown"
        cluster.summary = (
            f"Cluster of {len(feedback_items)} feedback items about {terms_str} "
            f"with {sentiment_text} sentiment"
        )
        
        # Set confidence based on cluster coherence
        try:
            # Calculate average similarity between items in cluster
            contents = [item.content for item in feedback_items]
            vectors = self.vectorizer.transform(contents)
            sim_matrix = cosine_similarity(vectors)
            
            # Average similarity (excluding self-similarity)
            n = len(feedback_items)
            total_sim = 0
            count = 0
            
            for i in range(n):
                for j in range(i + 1, n):
                    total_sim += sim_matrix[i, j]
                    count += 1
            
            if count > 0:
                avg_sim = total_sim / count
                cluster.confidence = float(avg_sim)
            else:
                cluster.confidence = 0.5
        except Exception:
            cluster.confidence = 0.5
    
    def _summarize_sentiment(self, feedback_items: List[FeedbackItem]) -> SentimentEnum:
        """Summarize the sentiment of a cluster of feedback items.
        
        Args:
            feedback_items: List of feedback items
            
        Returns:
            Summary sentiment
        """
        sentiment_counts = {
            SentimentEnum.VERY_NEGATIVE: 0,
            SentimentEnum.NEGATIVE: 0,
            SentimentEnum.NEUTRAL: 0,
            SentimentEnum.POSITIVE: 0,
            SentimentEnum.VERY_POSITIVE: 0,
        }
        
        for item in feedback_items:
            if item.sentiment:
                sentiment_counts[item.sentiment] += 1
        
        if not any(sentiment_counts.values()):
            return SentimentEnum.NEUTRAL
        
        # Return the most common sentiment
        return max(sentiment_counts, key=sentiment_counts.get)
    
    def _calculate_cluster_impact(self, feedback_items: List[FeedbackItem]) -> float:
        """Calculate the impact score for a cluster of feedback items.

        Args:
            feedback_items: List of feedback items

        Returns:
            Impact score between 0 and 1
        """
        # Average the individual impact scores, with a multiplier for cluster size
        if not feedback_items:
            return 0.0

        avg_impact = sum(item.impact_score or 0.0 for item in feedback_items) / len(feedback_items)

        # Size factor increases with cluster size, but plateaus
        size_factor = min(1 + (len(feedback_items) / 10), 2.0)

        # Negative sentiment increases impact
        sentiment_summary = self._summarize_sentiment(feedback_items)
        sentiment_factor = 1.0
        if sentiment_summary == SentimentEnum.VERY_NEGATIVE:
            sentiment_factor = 1.5
        elif sentiment_summary == SentimentEnum.NEGATIVE:
            sentiment_factor = 1.3

        # Calculate final impact score
        impact = avg_impact * size_factor * sentiment_factor

        # Normalize to 0-1 range
        return min(max(impact, 0.0), 1.0)

    def get_similar_feedback(
        self, target_feedback: FeedbackItem, candidates: List[FeedbackItem],
        min_similarity: float = 0.7
    ) -> List[Tuple[FeedbackItem, float]]:
        """Find feedback items similar to a target item.

        Args:
            target_feedback: The target feedback item
            candidates: List of candidate feedback items
            min_similarity: Minimum similarity threshold

        Returns:
            List of tuples with similar feedback items and their similarity scores,
            sorted by similarity (highest first)
        """
        if not candidates:
            return []

        try:
            # Vectorize all content
            contents = [target_feedback.content] + [item.content for item in candidates]
            vectors = self.vectorizer.fit_transform(contents)

            # Calculate similarity between target and each candidate
            target_vector = vectors[0:1]  # First row is the target
            candidate_vectors = vectors[1:]  # Remaining rows are candidates

            similarities = cosine_similarity(target_vector, candidate_vectors)[0]

            # Create result list with items above threshold
            result = []
            for i, sim in enumerate(similarities):
                if sim >= min_similarity:
                    result.append((candidates[i], float(sim)))

            # Sort by similarity (highest first)
            return sorted(result, key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"Error calculating similarities: {e}")
            return []
    
    def assign_to_clusters(
        self, item: FeedbackItem, existing_clusters: List[FeedbackCluster],
        all_items: Dict[UUID, FeedbackItem], similarity_threshold: float = None
    ) -> List[UUID]:
        """Assign a feedback item to existing clusters if it's similar enough.

        Args:
            item: Feedback item to assign
            existing_clusters: Existing clusters to consider
            all_items: Dictionary of all feedback items by ID
            similarity_threshold: Optional override for minimum similarity threshold

        Returns:
            List of cluster IDs that the item was assigned to
        """
        assigned_clusters = []

        # Use provided threshold or fall back to default
        threshold = similarity_threshold if similarity_threshold is not None else self.params.min_similarity

        try:
            # Calculate similarity to each cluster
            for cluster in existing_clusters:
                # Get items in the cluster
                cluster_items = [all_items[item_id] for item_id in cluster.feedback_ids
                               if item_id in all_items]

                if not cluster_items:
                    continue

                # Calculate average similarity to items in cluster
                contents = [item.content] + [ci.content for ci in cluster_items]
                vectors = self.vectorizer.transform(contents)

                # Check similarity of new item to each cluster item
                similarities = []
                for i in range(1, len(contents)):
                    sim = cosine_similarity(vectors[0:1], vectors[i:i+1])[0][0]
                    similarities.append(sim)

                # Calculate average similarity
                if similarities:
                    avg_sim = sum(similarities) / len(similarities)

                    # If similarity is above threshold, assign to cluster
                    if avg_sim >= threshold:
                        assigned_clusters.append(cluster.id)
        except Exception as e:
            print(f"Error assigning to clusters: {e}")

        return assigned_clusters

    def add_to_existing_clusters(
        self, new_items: List[FeedbackItem], existing_clusters: List[FeedbackCluster],
        all_items: Dict[UUID, FeedbackItem], similarity_threshold: float = 0.3
    ) -> Tuple[List[FeedbackCluster], List[FeedbackItem]]:
        """Add new feedback items to existing clusters if they're similar enough.

        Args:
            new_items: New feedback items to cluster
            existing_clusters: Existing clusters to consider
            all_items: Dictionary of all feedback items by ID
            similarity_threshold: Minimum similarity threshold for assignment

        Returns:
            Tuple with updated clusters and unclustered items
        """
        updated_clusters = existing_clusters.copy()
        unclustered_items = []

        for item in new_items:
            assigned = False

            # Try to assign to existing clusters
            assigned_clusters = self.assign_to_clusters(item, existing_clusters, all_items, similarity_threshold)

            if assigned_clusters:
                # Add to assigned clusters
                for cluster_id in assigned_clusters:
                    for cluster in updated_clusters:
                        if cluster.id == cluster_id and item.id not in cluster.feedback_ids:
                            cluster.feedback_ids.append(item.id)
                assigned = True

            if not assigned:
                unclustered_items.append(item)

        # Re-enrich clusters with new items
        for cluster in updated_clusters:
            cluster_items = [all_items[item_id] for item_id in cluster.feedback_ids
                          if item_id in all_items]
            self._enrich_cluster(cluster, cluster_items)

        return updated_clusters, unclustered_items