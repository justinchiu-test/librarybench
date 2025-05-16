"""Feedback Analysis Engine - Core module for processing user feedback.

This module provides capabilities for:
- Natural language processing for theme extraction
- Clustering algorithms for grouping related feedback
- Sentiment analysis for emotional content classification
- Frequency and impact assessment for feedback weighting
- Trend detection for emerging user concerns

The engine uses the common library's KnowledgeBase and Storage implementations
for core functionality, while providing domain-specific analysis capabilities.
"""
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from uuid import UUID
import os
import re

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import from ProductMind models
from productmind.models import (
    Feedback, 
    FeedbackCluster, 
    Sentiment, 
    SourceType, 
    Theme
)

# Import directly from common library
from common.core.storage import BaseStorage, StorageError
from common.core.knowledge import KnowledgeGraph, StandardKnowledgeBase, KnowledgeBase
from common.core.models import KnowledgeNode, NodeType, Relation, RelationType

# Import ProductMind specific storage - for better test compatibility
from productmind.storage import LocalStorage


class FeedbackAnalysisEngine:
    """
    Engine for analyzing customer feedback through NLP, clustering, and sentiment analysis.
    
    This class provides methods to:
    - Process and analyze batches of feedback
    - Extract themes and topics from feedback
    - Cluster similar feedback items
    - Analyze sentiment of feedback
    - Detect trends in feedback over time
    """
    
    def __init__(
        self,
        storage_dir: str = "./data",
        storage: Optional[BaseStorage] = None,
        vectorizer_max_features: int = 10000,
        min_cluster_size: int = 5,
        n_clusters: int = None,
        max_themes: int = 20
    ):
        """
        Initialize the feedback analysis engine.
        
        Args:
            storage_dir: Directory to store feedback data (used if storage is not provided)
            storage: Optional BaseStorage implementation to use
            vectorizer_max_features: Maximum features for TF-IDF vectorizer
            min_cluster_size: Minimum samples per cluster for DBSCAN
            n_clusters: Number of clusters for KMeans (if None, auto-determined)
            max_themes: Maximum number of themes to extract
        """
        if storage is not None:
            self.storage = storage
        else:
            # Create storage directory if it doesn't exist
            os.makedirs(os.path.join(storage_dir, "feedback"), exist_ok=True)
            os.makedirs(os.path.join(storage_dir, "clusters"), exist_ok=True)
            os.makedirs(os.path.join(storage_dir, "themes"), exist_ok=True)
            
            # Use ProductMind's LocalStorage wrapper for backward compatibility
            self.storage = LocalStorage(Path(storage_dir))
            
        # Initialize the knowledge base and graph using the common library
        self.knowledge_base = StandardKnowledgeBase(self.storage)
        self.knowledge_graph = KnowledgeGraph()
            
        self.storage_dir = storage_dir
        self.vectorizer = TfidfVectorizer(
            max_features=vectorizer_max_features,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2
        )
        self.min_cluster_size = min_cluster_size
        self.n_clusters = n_clusters
        self.max_themes = max_themes
        self._feedback_cache = {}
        self._clusters = {}
        self._themes = {}
        
    
    def add_feedback(self, feedback: Union[Feedback, List[Feedback]]) -> List[str]:
        """
        Add new feedback to the system.
        
        Args:
            feedback: Single feedback item or list of feedback items
            
        Returns:
            List of feedback IDs that were added
        """
        if isinstance(feedback, Feedback):
            feedback = [feedback]
        
        feedback_ids = []
        for item in feedback:
            # Make sure node_type is set - use the standard OTHER type 
            # which is the default in the Feedback model
            if not hasattr(item, 'node_type') or not item.node_type:
                setattr(item, 'node_type', NodeType.OTHER)
                
            # Add to knowledge base (which will save to storage)
            self.knowledge_base.add_node(item)
            
            # Add to knowledge graph
            self.knowledge_graph.add_node(
                str(item.id), 
                type="feedback", 
                title=item.title or "Untitled Feedback"
            )
            
            # If the feedback has a parent or source, create relationships
            if hasattr(item, 'parent_id') and item.parent_id:
                try:
                    self.knowledge_base.link_nodes(
                        item.id,
                        item.parent_id,
                        RelationType.CHILD_OF
                    )
                except Exception as e:
                    print(f"Error linking feedback to parent: {e}")
                    
            # If feedback has themes, create relationships
            if hasattr(item, 'themes') and item.themes:
                for theme_name in item.themes:
                    # Find existing theme or create a new one
                    theme = None
                    
                    # Try to find an existing theme with this name
                    all_themes = self.get_all_themes()
                    for existing_theme in all_themes:
                        if existing_theme.name == theme_name:
                            theme = existing_theme
                            break
                    
                    if not theme:
                        # Create new theme if it doesn't exist
                        theme = Theme(
                            name=theme_name,
                            description=f"Theme for {theme_name}",
                            keywords=[theme_name.lower()],
                            frequency=1,
                            impact_score=1.0,
                            sentiment_distribution={},
                            feedback_ids=[item.id],
                            node_type=NodeType.TAG
                        )
                        self.knowledge_base.add_node(theme)
                        self._themes[str(theme.id)] = theme
                        
                    # Link feedback to theme
                    try:
                        # Use an existing RelationType that makes sense for tagging themes
                        self.knowledge_base.link_nodes(
                            item.id,
                            theme.id,
                            RelationType.RELATES_TO,
                            metadata={"relationship": "tagged_with"}
                        )
                    except Exception as e:
                        print(f"Error linking feedback to theme: {e}")
            
            # Keep in cache for quick access
            self._feedback_cache[str(item.id)] = item
            feedback_ids.append(str(item.id))
        
        return feedback_ids
    
    def get_feedback(self, feedback_id: Union[str, UUID]) -> Optional[Feedback]:
        """
        Retrieve feedback by ID.
        
        Args:
            feedback_id: ID of feedback to retrieve (string or UUID)
            
        Returns:
            Feedback item if found, None otherwise
        """
        # Convert to string for cache lookup
        feedback_id_str = str(feedback_id)
        
        # Try to get from cache first
        if feedback_id_str in self._feedback_cache:
            return self._feedback_cache[feedback_id_str]
        
        # Try to get from knowledge base
        try:
            # Convert to UUID if it's a string
            if isinstance(feedback_id, str):
                uuid_obj = UUID(feedback_id)
            else:
                uuid_obj = feedback_id
                
            feedback = self.knowledge_base.get_node(uuid_obj, Feedback)
            if feedback:
                self._feedback_cache[feedback_id_str] = feedback
                return feedback
        except (ValueError, AttributeError) as e:
            # Handle invalid UUID format or other errors
            pass
        
        return None
    
    def get_all_feedback(self) -> List[Feedback]:
        """
        Retrieve all feedback.
        
        Returns:
            List of all feedback items
        """
        # Use knowledge base to get all feedback
        feedback_list = self.knowledge_base.get_nodes_by_type(Feedback)
        
        # Update cache with retrieved feedback
        for feedback in feedback_list:
            self._feedback_cache[str(feedback.id)] = feedback
        
        return feedback_list
    
    def analyze_sentiment(self, feedback: Union[Feedback, List[Feedback]]) -> Dict[str, Sentiment]:
        """
        Analyze sentiment of feedback.
        
        This is a simple rule-based sentiment analyzer. In a real implementation,
        this would use a more sophisticated NLP model.
        
        Args:
            feedback: Single feedback item or list of feedback items
            
        Returns:
            Dictionary mapping feedback ID to sentiment
        """
        if isinstance(feedback, Feedback):
            feedback = [feedback]
        
        results = {}
        
        positive_words = {
            "good", "great", "excellent", "amazing", "love", "like", "helpful",
            "awesome", "fantastic", "best", "perfect", "easy", "pleased", "happy"
        }

        negative_words = {
            "bad", "poor", "terrible", "awful", "hate", "dislike", "difficult",
            "confusing", "frustrating", "worst", "buggy", "slow", "issue", "problem",
            "broken", "can't", "cannot"
        }
        
        for item in feedback:
            text = item.content.lower()
            words = set(re.findall(r'\b\w+\b', text))
            
            positive_count = len(words.intersection(positive_words))
            negative_count = len(words.intersection(negative_words))
            
            if positive_count > negative_count * 2:
                sentiment = Sentiment.POSITIVE
            elif negative_count > positive_count * 2:
                sentiment = Sentiment.NEGATIVE
            elif positive_count > 0 and negative_count > 0:
                sentiment = Sentiment.MIXED
            else:
                sentiment = Sentiment.NEUTRAL
            
            # Update the feedback item with the sentiment
            item.sentiment = sentiment
            self.knowledge_base.update_node(item)
            self._feedback_cache[str(item.id)] = item
            
            results[str(item.id)] = sentiment
        
        return results
    
    def cluster_feedback(
        self, 
        feedback_ids: Optional[List[str]] = None,
        algorithm: str = "kmeans",
        force_recompute: bool = False
    ) -> List[FeedbackCluster]:
        """
        Cluster feedback into groups of similar items.
        
        Args:
            feedback_ids: List of feedback IDs to cluster (if None, use all feedback)
            algorithm: Clustering algorithm to use ("kmeans" or "dbscan")
            force_recompute: Whether to force recomputation of existing clusters
            
        Returns:
            List of feedback clusters
        """
        # Get all feedback if feedback_ids not provided
        if feedback_ids is None:
            all_feedback = self.get_all_feedback()
            feedback_ids = [str(item.id) for item in all_feedback]
        
        # Get feedback items from IDs
        feedback_items = []
        for fid in feedback_ids:
            item = self.get_feedback(fid)
            if item:
                feedback_items.append(item)
        
        if not feedback_items:
            return []
        
        # Extract content for vectorization
        texts = [item.content for item in feedback_items]
        
        # Vectorize text
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Perform clustering
        if algorithm == "kmeans":
            # Determine number of clusters if not provided
            if self.n_clusters is None:
                n_clusters = min(max(3, len(feedback_items) // 10), 20)
            else:
                n_clusters = self.n_clusters
                
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            centroids = kmeans.cluster_centers_
            
        elif algorithm == "dbscan":
            # Compute similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)
            dbscan = DBSCAN(
                eps=0.3,
                min_samples=self.min_cluster_size,
                metric="precomputed"
            )
            # DBSCAN expects distances, not similarities
            # Ensure values are non-negative by using absolute values and clipping
            distances = np.clip(1 - similarity_matrix, 0, 2)
            cluster_labels = dbscan.fit_predict(distances)
            
            # Compute centroids for each cluster
            centroids = []
            for label in set(cluster_labels):
                if label == -1:  # Noise points in DBSCAN
                    centroids.append(np.zeros(tfidf_matrix.shape[1]))
                else:
                    mask = cluster_labels == label
                    centroid = tfidf_matrix[mask].toarray().mean(axis=0)
                    centroids.append(centroid)
            centroids = np.array(centroids)
        else:
            raise ValueError(f"Unsupported clustering algorithm: {algorithm}")
        
        # Create cluster objects
        clusters = []
        cluster_map = defaultdict(list)
        
        # Group feedback by cluster
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Skip noise points from DBSCAN
                cluster_map[int(label)].append(feedback_items[i])
        
        # Create cluster objects
        for label, items in cluster_map.items():
            if len(items) < 1:
                continue
                
            # Get top terms for this cluster
            if label < len(centroids):
                centroid = centroids[label]
                feature_names = self.vectorizer.get_feature_names_out()
                
                # Get top terms from centroid
                if isinstance(centroid, np.ndarray):
                    top_indices = centroid.argsort()[-10:][::-1]
                    top_terms = [feature_names[i] for i in top_indices]
                else:
                    dense_centroid = centroid.toarray()[0]
                    top_indices = dense_centroid.argsort()[-10:][::-1]
                    top_terms = [feature_names[i] for i in top_indices]
            else:
                top_terms = []
            
            # Get sentiment distribution
            sentiment_counts = Counter(item.sentiment for item in items if item.sentiment)
            sentiment_dist = {
                sentiment: sentiment_counts.get(sentiment, 0) for sentiment in Sentiment
            }
            
            # Create cluster name from common terms
            cluster_name = " ".join(top_terms[:3])
            if not cluster_name:
                cluster_name = f"Cluster {label}"
            
            # Create cluster object with cluster_id as ID for compatibility with tests
            cluster = FeedbackCluster(
                id=label,  # Use label as ID for test compatibility
                cluster_numeric_id=label,  # Keep as integer
                name=cluster_name,
                description=f"Cluster containing {len(items)} feedback items",
                centroid=centroid.tolist() if isinstance(centroid, np.ndarray) else centroid.toarray()[0].tolist(),
                feedback_ids=[item.id for item in items],
                themes=top_terms[:5],
                sentiment_distribution=sentiment_dist,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                node_type=NodeType.OTHER
            )
            
            # Store cluster
            self.knowledge_base.add_node(cluster)
            
            # Update both caches by numeric ID and ID (which is still label)
            self._clusters[cluster.cluster_numeric_id] = cluster
            self._clusters[cluster.id] = cluster
            
            clusters.append(cluster)
            
            # Update feedback items with cluster.id to match test expectations
            for item in items:
                item.cluster_id = cluster.id  # Use the same ID as the cluster
                self.knowledge_base.update_node(item)
                self._feedback_cache[str(item.id)] = item
        
        return clusters
    
    def extract_themes(
        self, 
        feedback_ids: Optional[List[str]] = None,
        min_frequency: int = 3,
        force_recompute: bool = False
    ) -> List[Theme]:
        """
        Extract common themes from feedback.
        
        Args:
            feedback_ids: List of feedback IDs to analyze (if None, use all feedback)
            min_frequency: Minimum frequency for a theme to be considered
            force_recompute: Whether to force recomputation of existing themes
            
        Returns:
            List of extracted themes
        """
        # Clear themes cache if recomputing
        if force_recompute:
            self._themes.clear()
            
        # Clear knowledge base themes if recomputing
        if force_recompute:
            # Get all existing themes
            existing_themes = self.knowledge_base.get_nodes_by_type(Theme)
            # Delete them from the knowledge base
            for theme in existing_themes:
                self.knowledge_base.delete_node(theme.id)
                
        # Get all feedback if feedback_ids not provided
        if feedback_ids is None:
            all_feedback = self.get_all_feedback()
            feedback_ids = [str(item.id) for item in all_feedback]
        
        # Get feedback items from IDs
        feedback_items = []
        for fid in feedback_ids:
            item = self.get_feedback(fid)
            if item:
                feedback_items.append(item)
        
        if not feedback_items:
            return []
        
        # Extract content for vectorization
        texts = [item.content for item in feedback_items]
        
        # Vectorize text
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Extract top terms across all documents
        tfidf_sums = tfidf_matrix.sum(axis=0).A1
        top_indices = tfidf_sums.argsort()[-50:][::-1]
        
        # Create theme objects
        themes = []
        theme_counter = 0
        
        # Track theme names to avoid duplicates
        theme_names = set()
        
        for idx in top_indices:
            if theme_counter >= self.max_themes:
                break
                
            term = feature_names[idx]
            
            # Skip single character terms and very common words
            if len(term) <= 1:
                continue
            
            # Skip if this theme name already exists
            term_title = term.title()
            if term_title in theme_names:
                continue
                
            theme_names.add(term_title)
                
            # Find related terms
            term_vector = np.zeros(len(feature_names))
            term_vector[idx] = 1
            
            # Get documents containing this term
            doc_indices = []
            for i, text in enumerate(texts):
                if term in text.lower():
                    doc_indices.append(i)
            
            if len(doc_indices) < min_frequency:
                continue
                
            # Calculate co-occurring terms
            co_terms = []
            if doc_indices:
                doc_vectors = tfidf_matrix[doc_indices].toarray()
                term_sums = doc_vectors.sum(axis=0)
                co_term_indices = term_sums.argsort()[-10:][::-1]
                co_terms = [feature_names[i] for i in co_term_indices]
            
            # Get sentiment distribution for this theme
            related_feedback = [feedback_items[i] for i in doc_indices]
            sentiment_counts = Counter(
                item.sentiment for item in related_feedback if item.sentiment
            )
            sentiment_dist = {
                sentiment: sentiment_counts.get(sentiment, 0) for sentiment in Sentiment
            }
            
            # Calculate impact score (based on frequency and sentiment)
            impact_score = (
                len(doc_indices) / len(feedback_items) * 10 +
                sentiment_counts.get(Sentiment.POSITIVE, 0) * 0.1 +
                sentiment_counts.get(Sentiment.NEGATIVE, 0) * 0.2
            )
            
            # Create theme object
            theme = Theme(
                name=term_title,
                description=f"Theme related to {term} with {len(doc_indices)} mentions",
                keywords=co_terms,
                frequency=len(doc_indices),
                impact_score=impact_score,
                sentiment_distribution=sentiment_dist,
                feedback_ids=[feedback_items[i].id for i in doc_indices],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                node_type=NodeType.TAG
            )
            
            # Store theme
            self.knowledge_base.add_node(theme)
            
            # Store in cache with both string and UUID keys for compatibility
            theme_id_str = str(theme.id)
            self._themes[theme_id_str] = theme
            
            themes.append(theme)
            
            # Update feedback items with theme
            for i in doc_indices:
                feedback = feedback_items[i]
                if term_title not in feedback.themes:
                    feedback.themes.append(term_title)
                    self.knowledge_base.update_node(feedback)
                    self._feedback_cache[str(feedback.id)] = feedback
            
            theme_counter += 1
        
        return themes
    
    def detect_trends(
        self,
        timeframe: str = "week",
        min_growth_rate: float = 1.5,
        limit: int = 10
    ) -> List[Dict]:
        """
        Detect emerging trends in feedback over time.
        
        Args:
            timeframe: Time period for trend analysis ("day", "week", "month")
            min_growth_rate: Minimum growth rate to consider a trend
            limit: Maximum number of trends to return
            
        Returns:
            List of trending themes with growth metrics
        """
        all_feedback = self.get_all_feedback()
        
        if not all_feedback:
            return []
            
        # Determine time periods based on timeframe
        now = datetime.now()
        
        if timeframe == "day":
            days_ago = lambda d: (now - d.created_at).total_seconds() / (24 * 3600)
            current_period = [f for f in all_feedback if days_ago(f) <= 1]
            previous_period = [f for f in all_feedback if 1 < days_ago(f) <= 2]
        elif timeframe == "week":
            weeks_ago = lambda d: (now - d.created_at).total_seconds() / (7 * 24 * 3600)
            current_period = [f for f in all_feedback if weeks_ago(f) <= 1]
            previous_period = [f for f in all_feedback if 1 < weeks_ago(f) <= 2]
        elif timeframe == "month":
            months_ago = lambda d: (now - d.created_at).days / 30
            current_period = [f for f in all_feedback if months_ago(f) <= 1]
            previous_period = [f for f in all_feedback if 1 < months_ago(f) <= 2]
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        
        # Count theme occurrences in each period
        current_themes = Counter()
        for feedback in current_period:
            for theme in feedback.themes:
                current_themes[theme] += 1
        
        previous_themes = Counter()
        for feedback in previous_period:
            for theme in feedback.themes:
                previous_themes[theme] += 1
        
        # Calculate growth rates
        trends = []
        
        for theme, current_count in current_themes.items():
            previous_count = previous_themes.get(theme, 0)
            
            # Avoid division by zero
            if previous_count == 0:
                if current_count >= 3:  # New theme with at least 3 mentions
                    growth_rate = float('inf')
                else:
                    continue
            else:
                growth_rate = current_count / previous_count
            
            if growth_rate >= min_growth_rate:
                trends.append({
                    "theme": theme,
                    "current_count": current_count,
                    "previous_count": previous_count,
                    "growth_rate": growth_rate if growth_rate != float('inf') else 999.99,
                    "is_new": previous_count == 0
                })
        
        # Sort trends by growth rate
        trends.sort(key=lambda x: x["growth_rate"], reverse=True)
        
        return trends[:limit]
    
    def get_cluster(self, cluster_id: int) -> Optional[FeedbackCluster]:
        """
        Get a cluster by ID.
        
        Args:
            cluster_id: ID of the cluster
            
        Returns:
            Cluster if found, None otherwise
        """
        # Try to get from cache first
        if cluster_id in self._clusters:
            return self._clusters[cluster_id]
        
        try:
            # Get all clusters and find the one with matching numeric ID
            all_clusters = self.get_all_clusters()
            for cluster in all_clusters:
                if cluster.cluster_numeric_id == cluster_id:
                    self._clusters[cluster_id] = cluster
                    return cluster
                
        except Exception as e:
            # Handle any errors in retrieval
            print(f"Error retrieving cluster {cluster_id}: {e}")
            pass
        
        return None
    
    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """
        Get a theme by ID.
        
        Args:
            theme_id: ID of the theme
            
        Returns:
            Theme if found, None otherwise
        """
        # Try to get from cache first
        if theme_id in self._themes:
            return self._themes[theme_id]
        
        # Try to get from knowledge base
        try:
            # First try using the knowledge base's direct node retrieval
            theme = self.knowledge_base.get_node(UUID(theme_id), Theme)
            if theme:
                self._themes[theme_id] = theme
                return theme
                
            # If not found but the theme has a NodeType, try using get_node_by_type
            # This is a fallback mechanism for compatibility
            themes = self.knowledge_base.get_nodes_by_type(Theme)
            for theme in themes:
                if str(theme.id) == theme_id:
                    self._themes[theme_id] = theme
                    return theme
        except ValueError:
            # Handle invalid UUID format
            pass
        except Exception as e:
            # Handle other errors
            print(f"Error retrieving theme {theme_id}: {e}")
            pass
        
        return None
    
    def get_all_clusters(self) -> List[FeedbackCluster]:
        """
        Get all clusters.
        
        Returns:
            List of all clusters
        """
        # Use knowledge base to get all clusters
        clusters = self.knowledge_base.get_nodes_by_type(FeedbackCluster)
        
        # If no clusters found, fall back to storage for backward compatibility
        if not clusters:
            clusters = self.storage.list_all(FeedbackCluster)
        
        # Update cache with numeric cluster IDs
        for cluster in clusters:
            self._clusters[cluster.cluster_numeric_id] = cluster
        
        return clusters
    
    def get_all_themes(self) -> List[Theme]:
        """
        Get all themes.
        
        Returns:
            List of all themes
        """
        # Get themes directly from the knowledge base - most reliable source
        themes = self.knowledge_base.get_nodes_by_type(Theme)
        
        # If no themes found, fall back to storage for backward compatibility
        if not themes:
            themes = self.storage.list_all(Theme)
        
        # Reset cache and update with unique themes by name
        self._themes.clear()
        
        # Use a dict to deduplicate by name, keeping only the first instance of each theme name
        themes_by_name = {}
        for theme in themes:
            if theme.name not in themes_by_name:
                themes_by_name[theme.name] = theme
        
        # Build the final unique themes list and update cache
        unique_themes = list(themes_by_name.values())
        
        # Update cache with theme IDs
        for theme in unique_themes:
            self._themes[str(theme.id)] = theme
        
        return unique_themes
    
    def search_feedback(self, query: str, limit: int = 100) -> List[Feedback]:
        """
        Search for feedback items matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching feedback items
        """
        # Use the knowledge base search functionality from common library
        try:
            search_results = self.knowledge_base.search(query, [Feedback])
            
            # If results are returned and not empty
            if search_results and 'Feedback' in search_results and search_results['Feedback']:
                return search_results['Feedback'][:limit]
        except Exception as e:
            print(f"Knowledge base search error: {e}")
        
        # Fallback to direct storage search for backward compatibility
        try:
            results = self.storage.search_text(Feedback, query, ["content", "title"])
            if results:
                # Add to knowledge base for future searches
                for feedback in results:
                    if not self.knowledge_base.get_node(feedback.id, Feedback):
                        self.knowledge_base.add_node(feedback)
                return results[:limit]
        except Exception as e:
            print(f"Storage search error: {e}")
            
        # Try a different approach if all else fails - search in local cache
        matched_feedback = []
        all_feedback = self.get_all_feedback()
        query_lower = query.lower()
        
        for feedback in all_feedback:
            if (query_lower in feedback.content.lower() or 
                (feedback.title and query_lower in feedback.title.lower())):
                matched_feedback.append(feedback)
                if len(matched_feedback) >= limit:
                    break
                    
        return matched_feedback[:limit]
    
    def get_feedback_by_theme(self, theme_name: str) -> List[Feedback]:
        """
        Get all feedback items associated with a theme.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            List of feedback items with the theme
        """
        results = []
        
        # First try to find the theme by name
        theme = None
        all_themes = self.get_all_themes()
        
        for existing_theme in all_themes:
            if existing_theme.name == theme_name:
                theme = existing_theme
                break
        
        if theme:
            try:
                # Try to use the knowledge graph relationships to find feedback associated with the theme
                related_nodes = self.knowledge_base.get_related_nodes(
                    theme.id, 
                    [RelationType.RELATES_TO], 
                    direction="in"
                )
                
                # Extract feedback from related nodes
                if related_nodes and RelationType.RELATES_TO.value in related_nodes:
                    for node in related_nodes[RelationType.RELATES_TO.value]:
                        if isinstance(node, Feedback):
                            results.append(node)
                            
                # If we found results this way, return them
                if results:
                    return results
            except Exception as e:
                print(f"Error retrieving related nodes for theme {theme_name}: {e}")
        
        # Fallback to traditional method if relationship query didn't work or theme not found
        all_feedback = self.get_all_feedback()
        
        for feedback in all_feedback:
            if theme_name in feedback.themes:
                # Only add if not already in results
                if not any(f.id == feedback.id for f in results):
                    results.append(feedback)
                    
                    # Create the relationship for future queries if we're using fallback and theme was found
                    if theme:
                        try:
                            self.knowledge_base.link_nodes(
                                feedback.id,
                                theme.id,
                                RelationType.RELATES_TO,
                                metadata={"relationship": "tagged_with"}
                            )
                        except Exception as e:
                            print(f"Error linking feedback to theme: {e}")
        
        return results
    
    def get_feedback_by_cluster(self, cluster_id: int) -> List[Feedback]:
        """
        Get all feedback items in a cluster.
        
        Args:
            cluster_id: ID of the cluster
            
        Returns:
            List of feedback items in the cluster
        """
        results = []
        
        # Get the cluster first
        cluster = self.get_cluster(cluster_id)
        if not cluster:
            return []
            
        # Try to use direct lookup of feedback_ids first - most reliable
        if hasattr(cluster, 'feedback_ids') and cluster.feedback_ids:
            # Get feedback items by IDs using the knowledge base
            for feedback_id in cluster.feedback_ids:
                feedback = self.get_feedback(feedback_id)
                if feedback:
                    results.append(feedback)
                    
            # If we found results this way, return them
            if results:
                return results
            
        # Fallback: search all feedback for matching cluster_id
        all_feedback = self.get_all_feedback()
        
        for feedback in all_feedback:
            if hasattr(feedback, 'cluster_id') and feedback.cluster_id == cluster_id:
                # Only add if not already in results
                if not any(f.id == feedback.id for f in results):
                    results.append(feedback)
        
        return results