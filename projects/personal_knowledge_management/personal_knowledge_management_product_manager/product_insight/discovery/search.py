"""
Knowledge search module for ProductInsight.

This module provides functionality for searching across different knowledge domains
and ranking results by relevance.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field

from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    SearchQuery,
    SearchResult,
    SearchResults,
    Stakeholder,
    StakeholderPerspective,
    StrategicObjective,
)
from product_insight.storage import FileStorage, StorageInterface


class SearchIndex(BaseModel):
    """In-memory search index for fast lookups."""
    
    feedback_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    feature_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    objective_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    decision_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    competitor_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    stakeholder_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    perspective_index: Dict[UUID, Dict[str, float]] = Field(default_factory=dict)
    
    # Entity data caches
    feedback_data: Dict[UUID, FeedbackItem] = Field(default_factory=dict)
    feature_data: Dict[UUID, Feature] = Field(default_factory=dict)
    objective_data: Dict[UUID, StrategicObjective] = Field(default_factory=dict)
    decision_data: Dict[UUID, Decision] = Field(default_factory=dict)
    competitor_data: Dict[UUID, Competitor] = Field(default_factory=dict)
    stakeholder_data: Dict[UUID, Stakeholder] = Field(default_factory=dict)
    perspective_data: Dict[UUID, StakeholderPerspective] = Field(default_factory=dict)
    
    # Term frequency cache
    term_frequencies: Dict[str, int] = Field(default_factory=dict)
    total_terms: int = 0


class SearchEngine:
    """Engine for searching across different knowledge domains."""
    
    def __init__(
        self,
        storage_dir: str,
        feedback_storage: Optional[StorageInterface[FeedbackItem]] = None,
        feedback_cluster_storage: Optional[StorageInterface[FeedbackCluster]] = None,
        feature_storage: Optional[StorageInterface[Feature]] = None,
        objective_storage: Optional[StorageInterface[StrategicObjective]] = None,
        decision_storage: Optional[StorageInterface[Decision]] = None,
        competitor_storage: Optional[StorageInterface[Competitor]] = None,
        stakeholder_storage: Optional[StorageInterface[Stakeholder]] = None,
        perspective_storage: Optional[StorageInterface[StakeholderPerspective]] = None,
    ):
        """Initialize the search engine.
        
        Args:
            storage_dir: Base directory for storing data
            feedback_storage: Optional custom storage for feedback
            feedback_cluster_storage: Optional custom storage for feedback clusters
            feature_storage: Optional custom storage for features
            objective_storage: Optional custom storage for objectives
            decision_storage: Optional custom storage for decisions
            competitor_storage: Optional custom storage for competitors
            stakeholder_storage: Optional custom storage for stakeholders
            perspective_storage: Optional custom storage for stakeholder perspectives
        """
        self.feedback_storage = feedback_storage or FileStorage(
            entity_type=FeedbackItem,
            storage_dir=f"{storage_dir}/feedback",
            format="json"
        )
        
        self.feedback_cluster_storage = feedback_cluster_storage or FileStorage(
            entity_type=FeedbackCluster,
            storage_dir=f"{storage_dir}/feedback_clusters",
            format="json"
        )
        
        self.feature_storage = feature_storage or FileStorage(
            entity_type=Feature,
            storage_dir=f"{storage_dir}/features",
            format="json"
        )
        
        self.objective_storage = objective_storage or FileStorage(
            entity_type=StrategicObjective,
            storage_dir=f"{storage_dir}/objectives",
            format="json"
        )
        
        self.decision_storage = decision_storage or FileStorage(
            entity_type=Decision,
            storage_dir=f"{storage_dir}/decisions",
            format="json"
        )
        
        self.competitor_storage = competitor_storage or FileStorage(
            entity_type=Competitor,
            storage_dir=f"{storage_dir}/competitors",
            format="json"
        )
        
        self.stakeholder_storage = stakeholder_storage or FileStorage(
            entity_type=Stakeholder,
            storage_dir=f"{storage_dir}/stakeholders",
            format="json"
        )
        
        self.perspective_storage = perspective_storage or FileStorage(
            entity_type=StakeholderPerspective,
            storage_dir=f"{storage_dir}/stakeholder_perspectives",
            format="json"
        )
        
        self.index = SearchIndex()
        self.index_built = False
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into a list of terms.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokenized terms
        """
        if not text:
            return []
        
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into tokens and remove stopwords
        tokens = text.split()
        stopwords = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
            'such', 'when', 'who', 'how', 'where', 'why', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'but',
            'at', 'by', 'with', 'from', 'here', 'there', 'when', 'where', 'how',
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'can', 'will', 'should', 'now', 'would', 'could', 'i', 'you',
            'your', 'we', 'our', 'they', 'their', 'he', 'she', 'his', 'her'
        }
        
        # Filter out stopwords and short terms
        filtered_tokens = [
            token for token in tokens
            if token not in stopwords and len(token) > 2
        ]
        
        return filtered_tokens
    
    def _extract_terms(self, entity: Any) -> Dict[str, float]:
        """Extract search terms from an entity with weights.
        
        Args:
            entity: Entity to extract terms from
            
        Returns:
            Dictionary mapping terms to weights
        """
        terms = {}
        
        if hasattr(entity, 'id'):
            entity_id = str(entity.id)
            terms[entity_id] = 2.0  # ID is a strong match
        
        # Handle different entity types
        if isinstance(entity, FeedbackItem):
            # Extract from feedback
            if entity.content:
                for token in self._tokenize(entity.content):
                    terms[token] = terms.get(token, 0) + 1.0
            
            # Source and customer segment
            if entity.source:
                terms[entity.source.value] = 1.5
            if entity.customer_segment:
                for token in self._tokenize(entity.customer_segment):
                    terms[token] = terms.get(token, 0) + 1.2
            
            # Tags
            for tag in entity.tags:
                for token in self._tokenize(tag.name):
                    terms[token] = terms.get(token, 0) + 2.0
        
        elif isinstance(entity, Feature):
            # Extract from feature
            if entity.name:
                for token in self._tokenize(entity.name):
                    terms[token] = terms.get(token, 0) + 2.0
            
            if entity.description:
                for token in self._tokenize(entity.description):
                    terms[token] = terms.get(token, 0) + 1.0
            
            # Tags
            for tag in entity.tags:
                for token in self._tokenize(tag.name):
                    terms[token] = terms.get(token, 0) + 1.5
            
            # Status
            if entity.status:
                terms[entity.status.value] = 1.2
        
        elif isinstance(entity, StrategicObjective):
            # Extract from objective
            if entity.name:
                for token in self._tokenize(entity.name):
                    terms[token] = terms.get(token, 0) + 2.0
            
            if entity.description:
                for token in self._tokenize(entity.description):
                    terms[token] = terms.get(token, 0) + 1.0
            
            # Tags
            for tag in entity.tags:
                for token in self._tokenize(tag.name):
                    terms[token] = terms.get(token, 0) + 1.5
            
            # Status and priority
            if entity.status:
                terms[entity.status.value] = 1.2
            if entity.priority:
                terms[entity.priority.value] = 1.2
            
            # Metric type
            if entity.metric_type:
                terms[entity.metric_type.value] = 1.5
        
        elif isinstance(entity, Decision):
            # Extract from decision
            if entity.title:
                for token in self._tokenize(entity.title):
                    terms[token] = terms.get(token, 0) + 2.0
            
            if entity.description:
                for token in self._tokenize(entity.description):
                    terms[token] = terms.get(token, 0) + 1.5
            
            if entity.context:
                for token in self._tokenize(entity.context):
                    terms[token] = terms.get(token, 0) + 1.0
            
            if entity.rationale:
                for token in self._tokenize(entity.rationale):
                    terms[token] = terms.get(token, 0) + 1.2
            
            # Alternatives
            for alt in entity.alternatives:
                for token in self._tokenize(alt):
                    terms[token] = terms.get(token, 0) + 0.8
            
            # Supporting data
            for data in entity.supporting_data:
                for token in self._tokenize(data):
                    terms[token] = terms.get(token, 0) + 0.7
            
            # Outcome and retrospective
            if entity.outcome_notes:
                for token in self._tokenize(entity.outcome_notes):
                    terms[token] = terms.get(token, 0) + 1.0
            
            if entity.retrospective:
                for token in self._tokenize(entity.retrospective):
                    terms[token] = terms.get(token, 0) + 1.0
            
            # Tags
            for tag in entity.tags:
                for token in self._tokenize(tag.name):
                    terms[token] = terms.get(token, 0) + 1.5
        
        elif isinstance(entity, Competitor):
            # Extract from competitor
            if entity.name:
                for token in self._tokenize(entity.name):
                    terms[token] = terms.get(token, 0) + 2.0
            
            if entity.description:
                for token in self._tokenize(entity.description):
                    terms[token] = terms.get(token, 0) + 1.5
            
            # Website
            if entity.website:
                domain = entity.website.split('//')[-1].split('/')[0]
                for token in self._tokenize(domain):
                    terms[token] = terms.get(token, 0) + 1.2
            
            # Pricing
            if entity.pricing_model:
                for token in self._tokenize(entity.pricing_model):
                    terms[token] = terms.get(token, 0) + 1.0
            
            if entity.pricing_details:
                for token in self._tokenize(entity.pricing_details):
                    terms[token] = terms.get(token, 0) + 0.8
            
            # Target segments
            for segment in entity.target_segments:
                for token in self._tokenize(segment):
                    terms[token] = terms.get(token, 0) + 1.3
            
            # Strengths and weaknesses
            for strength in entity.strengths:
                for token in self._tokenize(strength):
                    terms[token] = terms.get(token, 0) + 1.2
            
            for weakness in entity.weaknesses:
                for token in self._tokenize(weakness):
                    terms[token] = terms.get(token, 0) + 1.2
            
            # Feature comparison
            for feature, has_feature in entity.feature_comparison.items():
                for token in self._tokenize(feature):
                    terms[token] = terms.get(token, 0) + 0.7
            
            # Detailed comparisons
            for feature, details in entity.detailed_comparisons.items():
                for token in self._tokenize(f"{feature} {details}"):
                    terms[token] = terms.get(token, 0) + 0.5
            
            # Notes
            if entity.notes:
                for token in self._tokenize(entity.notes):
                    terms[token] = terms.get(token, 0) + 0.7
            
            # Tags
            for tag in entity.tags:
                for token in self._tokenize(tag.name):
                    terms[token] = terms.get(token, 0) + 1.5
        
        elif isinstance(entity, Stakeholder):
            # Extract from stakeholder
            if entity.name:
                for token in self._tokenize(entity.name):
                    terms[token] = terms.get(token, 0) + 2.0
            
            if entity.organization:
                for token in self._tokenize(entity.organization):
                    terms[token] = terms.get(token, 0) + 1.5
            
            # Role and influence
            if entity.role:
                terms[entity.role.value] = 1.5
            if entity.influence:
                terms[entity.influence.value] = 1.2
            
            # Key concerns
            for concern in entity.key_concerns:
                for token in self._tokenize(concern):
                    terms[token] = terms.get(token, 0) + 1.3
            
            # Communication preferences
            if entity.communication_preferences:
                for token in self._tokenize(entity.communication_preferences):
                    terms[token] = terms.get(token, 0) + 0.8
            
            # Engagement history
            for entry in entity.engagement_history:
                for token in self._tokenize(entry):
                    terms[token] = terms.get(token, 0) + 0.7
            
            # Notes
            if entity.notes:
                for token in self._tokenize(entity.notes):
                    terms[token] = terms.get(token, 0) + 1.0
        
        elif isinstance(entity, StakeholderPerspective):
            # Extract from stakeholder perspective
            if entity.topic:
                for token in self._tokenize(entity.topic):
                    terms[token] = terms.get(token, 0) + 2.0
            
            if entity.perspective:
                for token in self._tokenize(entity.perspective):
                    terms[token] = terms.get(token, 0) + 1.5
            
            # Sentiment
            if entity.sentiment:
                terms[entity.sentiment.value] = 1.2
            
            # Context
            if entity.context:
                for token in self._tokenize(entity.context):
                    terms[token] = terms.get(token, 0) + 1.0
        
        return terms
    
    def build_index(self) -> None:
        """Build the search index from all entities."""
        # Clear existing index
        self.index = SearchIndex()
        start_time = datetime.now()
        
        # Index feedback
        print("Indexing feedback...")
        feedback_items = self.feedback_storage.list()
        for item in feedback_items:
            terms = self._extract_terms(item)
            self.index.feedback_index[item.id] = terms
            self.index.feedback_data[item.id] = item
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Index features
        print("Indexing features...")
        features = self.feature_storage.list()
        for feature in features:
            terms = self._extract_terms(feature)
            self.index.feature_index[feature.id] = terms
            self.index.feature_data[feature.id] = feature
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Index objectives
        print("Indexing objectives...")
        objectives = self.objective_storage.list()
        for objective in objectives:
            terms = self._extract_terms(objective)
            self.index.objective_index[objective.id] = terms
            self.index.objective_data[objective.id] = objective
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Index decisions
        print("Indexing decisions...")
        decisions = self.decision_storage.list()
        for decision in decisions:
            terms = self._extract_terms(decision)
            self.index.decision_index[decision.id] = terms
            self.index.decision_data[decision.id] = decision
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Index competitors
        print("Indexing competitors...")
        competitors = self.competitor_storage.list()
        for competitor in competitors:
            terms = self._extract_terms(competitor)
            self.index.competitor_index[competitor.id] = terms
            self.index.competitor_data[competitor.id] = competitor
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Index stakeholders
        print("Indexing stakeholders...")
        stakeholders = self.stakeholder_storage.list()
        for stakeholder in stakeholders:
            terms = self._extract_terms(stakeholder)
            self.index.stakeholder_index[stakeholder.id] = terms
            self.index.stakeholder_data[stakeholder.id] = stakeholder
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Index stakeholder perspectives
        print("Indexing stakeholder perspectives...")
        perspectives = self.perspective_storage.list()
        for perspective in perspectives:
            terms = self._extract_terms(perspective)
            self.index.perspective_index[perspective.id] = terms
            self.index.perspective_data[perspective.id] = perspective
            
            # Update term frequencies
            for term in terms:
                self.index.term_frequencies[term] = self.index.term_frequencies.get(term, 0) + 1
                self.index.total_terms += 1
        
        # Mark index as built
        self.index_built = True
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Index built in {duration:.2f} seconds.")
        print(f"Indexed {len(self.index.feedback_index)} feedback items")
        print(f"Indexed {len(self.index.feature_index)} features")
        print(f"Indexed {len(self.index.objective_index)} objectives")
        print(f"Indexed {len(self.index.decision_index)} decisions")
        print(f"Indexed {len(self.index.competitor_index)} competitors")
        print(f"Indexed {len(self.index.stakeholder_index)} stakeholders")
        print(f"Indexed {len(self.index.perspective_index)} perspectives")
    
    def _calculate_relevance(
        self, query_terms: List[str], entity_terms: Dict[str, float]
    ) -> float:
        """Calculate relevance score between query and entity.
        
        Args:
            query_terms: List of query terms
            entity_terms: Dictionary mapping entity terms to weights
            
        Returns:
            Relevance score
        """
        score = 0.0
        
        for term in query_terms:
            if term in entity_terms:
                term_weight = entity_terms[term]
                
                # Apply inverse document frequency weighting
                if term in self.index.term_frequencies and self.index.term_frequencies[term] > 0:
                    idf = 1.0 / self.index.term_frequencies[term]
                    score += term_weight * idf * 100.0  # Scale up for better scores
                else:
                    score += term_weight * 10.0  # Default weight for unique terms
        
        return score
    
    def search(self, query: SearchQuery) -> SearchResults:
        """Search for entities matching the query.
        
        Args:
            query: Search query parameters
            
        Returns:
            SearchResults with matching entities
        """
        start_time = datetime.now()
        
        # Build index if needed
        if not self.index_built:
            self.build_index()
        
        # Tokenize query
        query_terms = self._tokenize(query.query)
        
        # Search in each domain
        results = []
        
        # Search in feedback
        if query.include_feedback:
            for feedback_id, terms in self.index.feedback_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    feedback = self.index.feedback_data[feedback_id]
                    
                    # Apply tag filtering
                    if query.tags and not any(tag.name in query.tags for tag in feedback.tags):
                        continue
                    
                    # Apply date filtering
                    if query.date_from and feedback.created_at < query.date_from:
                        continue
                    if query.date_to and feedback.created_at > query.date_to:
                        continue
                    
                    # Create search result
                    result = SearchResult(
                        entity_id=feedback_id,
                        entity_type="feedback",
                        title=f"Feedback: {feedback.content[:50]}...",
                        snippet=feedback.content[:200],
                        relevance_score=relevance,
                        date=feedback.created_at,
                        tags=feedback.tags
                    )
                    
                    results.append(result)
        
        # Search in features
        if query.include_features:
            for feature_id, terms in self.index.feature_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    feature = self.index.feature_data[feature_id]
                    
                    # Apply tag filtering
                    if query.tags and not any(tag.name in query.tags for tag in feature.tags):
                        continue
                    
                    # Apply date filtering
                    if query.date_from and feature.created_at < query.date_from:
                        continue
                    if query.date_to and feature.created_at > query.date_to:
                        continue
                    
                    # Create search result
                    result = SearchResult(
                        entity_id=feature_id,
                        entity_type="feature",
                        title=f"Feature: {feature.name}",
                        snippet=feature.description[:200],
                        relevance_score=relevance,
                        date=feature.created_at,
                        tags=feature.tags
                    )
                    
                    results.append(result)
        
        # Search in objectives
        if query.include_objectives:
            for objective_id, terms in self.index.objective_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    objective = self.index.objective_data[objective_id]
                    
                    # Apply tag filtering
                    if query.tags and not any(tag.name in query.tags for tag in objective.tags):
                        continue
                    
                    # Apply date filtering
                    if query.date_from and objective.created_at < query.date_from:
                        continue
                    if query.date_to and objective.created_at > query.date_to:
                        continue
                    
                    # Create search result
                    result = SearchResult(
                        entity_id=objective_id,
                        entity_type="objective",
                        title=f"Objective: {objective.name}",
                        snippet=objective.description[:200],
                        relevance_score=relevance,
                        date=objective.created_at,
                        tags=objective.tags
                    )
                    
                    results.append(result)
        
        # Search in decisions
        if query.include_decisions:
            for decision_id, terms in self.index.decision_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    decision = self.index.decision_data[decision_id]
                    
                    # Apply tag filtering
                    if query.tags and not any(tag.name in query.tags for tag in decision.tags):
                        continue
                    
                    # Apply date filtering
                    if query.date_from and decision.decision_date < query.date_from:
                        continue
                    if query.date_to and decision.decision_date > query.date_to:
                        continue
                    
                    # Create search result
                    result = SearchResult(
                        entity_id=decision_id,
                        entity_type="decision",
                        title=f"Decision: {decision.title}",
                        snippet=decision.description[:200],
                        relevance_score=relevance,
                        date=decision.decision_date,
                        tags=decision.tags
                    )
                    
                    results.append(result)
        
        # Search in competitors
        if query.include_competitors:
            for competitor_id, terms in self.index.competitor_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    competitor = self.index.competitor_data[competitor_id]
                    
                    # Apply tag filtering
                    if query.tags and not any(tag.name in query.tags for tag in competitor.tags):
                        continue
                    
                    # Apply date filtering
                    if query.date_from and competitor.created_at < query.date_from:
                        continue
                    if query.date_to and competitor.created_at > query.date_to:
                        continue
                    
                    # Create search result
                    description = competitor.description or ""
                    result = SearchResult(
                        entity_id=competitor_id,
                        entity_type="competitor",
                        title=f"Competitor: {competitor.name}",
                        snippet=description[:200],
                        relevance_score=relevance,
                        date=competitor.created_at,
                        tags=competitor.tags
                    )
                    
                    results.append(result)
        
        # Search in stakeholders
        if query.include_stakeholders:
            for stakeholder_id, terms in self.index.stakeholder_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    stakeholder = self.index.stakeholder_data[stakeholder_id]
                    
                    # Apply date filtering
                    if query.date_from and stakeholder.created_at < query.date_from:
                        continue
                    if query.date_to and stakeholder.created_at > query.date_to:
                        continue
                    
                    # Create search result
                    organization = f" ({stakeholder.organization})" if stakeholder.organization else ""
                    notes = stakeholder.notes or ""
                    
                    result = SearchResult(
                        entity_id=stakeholder_id,
                        entity_type="stakeholder",
                        title=f"Stakeholder: {stakeholder.name}{organization}",
                        snippet=notes[:200],
                        relevance_score=relevance,
                        date=stakeholder.created_at,
                        tags=[]
                    )
                    
                    results.append(result)
            
            # Search in stakeholder perspectives
            for perspective_id, terms in self.index.perspective_index.items():
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0:
                    perspective = self.index.perspective_data[perspective_id]
                    
                    # Get stakeholder name
                    stakeholder_name = "Unknown"
                    if perspective.stakeholder_id in self.index.stakeholder_data:
                        stakeholder_name = self.index.stakeholder_data[perspective.stakeholder_id].name
                    
                    # Apply date filtering
                    if query.date_from and perspective.date_recorded < query.date_from:
                        continue
                    if query.date_to and perspective.date_recorded > query.date_to:
                        continue
                    
                    # Create search result
                    result = SearchResult(
                        entity_id=perspective_id,
                        entity_type="perspective",
                        title=f"Perspective: {stakeholder_name} on {perspective.topic}",
                        snippet=perspective.perspective[:200],
                        relevance_score=relevance,
                        date=perspective.date_recorded,
                        tags=[]
                    )
                    
                    results.append(result)
        
        # Sort by relevance score
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        # Apply limit
        results = results[:query.limit]
        
        # Prepare facets (counts by entity type)
        facets = {
            "entity_type": {}
        }
        
        for result in results:
            entity_type = result.entity_type
            facets["entity_type"][entity_type] = facets["entity_type"].get(entity_type, 0) + 1
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Create search results
        search_results = SearchResults(
            query=query.query,
            results=results,
            total_count=len(results),
            execution_time_ms=execution_time_ms,
            facets=facets
        )
        
        return search_results
    
    def find_related_entities(
        self, entity_id: UUID, entity_type: str, max_results: int = 10
    ) -> Dict[str, List[SearchResult]]:
        """Find entities related to a specific entity.
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            max_results: Maximum number of results per category
            
        Returns:
            Dictionary mapping entity types to lists of related entities
        """
        # Build index if needed
        if not self.index_built:
            self.build_index()
        
        related_entities = {
            "feedback": [],
            "feature": [],
            "objective": [],
            "decision": [],
            "competitor": [],
            "stakeholder": [],
            "perspective": []
        }
        
        # Get the source entity terms
        source_terms = {}
        
        if entity_type == "feedback" and entity_id in self.index.feedback_index:
            source_terms = self.index.feedback_index[entity_id]
            
            # Add special handling for feedback clusters
            feedback = self.index.feedback_data[entity_id]
            if feedback.cluster_id:
                try:
                    cluster = self.feedback_cluster_storage.get(feedback.cluster_id)
                    
                    # Add other feedback in the same cluster
                    for other_id in cluster.feedback_ids:
                        if other_id != entity_id and other_id in self.index.feedback_data:
                            other = self.index.feedback_data[other_id]
                            
                            result = SearchResult(
                                entity_id=other_id,
                                entity_type="feedback",
                                title=f"Feedback: {other.content[:50]}...",
                                snippet=other.content[:200],
                                relevance_score=0.9,  # High relevance for same cluster
                                date=other.created_at,
                                tags=other.tags
                            )
                            
                            related_entities["feedback"].append(result)
                except Exception:
                    pass
        
        elif entity_type == "feature" and entity_id in self.index.feature_index:
            source_terms = self.index.feature_index[entity_id]
            
            # Add special handling for feature relationships
            feature = self.index.feature_data[entity_id]
            
            # Add feedback associated with this feature
            for feedback_id, feedback in self.index.feedback_data.items():
                if entity_id in feedback.feedback_cluster_ids or entity_id in feedback.feedback_ids:
                    result = SearchResult(
                        entity_id=feedback_id,
                        entity_type="feedback",
                        title=f"Feedback: {feedback.content[:50]}...",
                        snippet=feedback.content[:200],
                        relevance_score=0.9,  # High relevance for direct association
                        date=feedback.created_at,
                        tags=feedback.tags
                    )
                    
                    related_entities["feedback"].append(result)
            
            # Add dependent features
            for other_id, other in self.index.feature_data.items():
                if entity_id in other.dependencies:
                    result = SearchResult(
                        entity_id=other_id,
                        entity_type="feature",
                        title=f"Feature: {other.name}",
                        snippet=other.description[:200],
                        relevance_score=0.9,  # High relevance for dependencies
                        date=other.created_at,
                        tags=other.tags
                    )
                    
                    related_entities["feature"].append(result)
        
        elif entity_type == "objective" and entity_id in self.index.objective_index:
            source_terms = self.index.objective_index[entity_id]
            
            # Add special handling for objective relationships
            objective = self.index.objective_data[entity_id]
            
            # Add parent objective
            if objective.parent_id and objective.parent_id in self.index.objective_data:
                parent = self.index.objective_data[objective.parent_id]
                
                result = SearchResult(
                    entity_id=parent.id,
                    entity_type="objective",
                    title=f"Parent Objective: {parent.name}",
                    snippet=parent.description[:200],
                    relevance_score=0.95,  # Very high relevance for parent
                    date=parent.created_at,
                    tags=parent.tags
                )
                
                related_entities["objective"].append(result)
            
            # Add child objectives
            for child_id in objective.child_ids:
                if child_id in self.index.objective_data:
                    child = self.index.objective_data[child_id]
                    
                    result = SearchResult(
                        entity_id=child.id,
                        entity_type="objective",
                        title=f"Child Objective: {child.name}",
                        snippet=child.description[:200],
                        relevance_score=0.9,  # High relevance for children
                        date=child.created_at,
                        tags=child.tags
                    )
                    
                    related_entities["objective"].append(result)
        
        elif entity_type == "decision" and entity_id in self.index.decision_index:
            source_terms = self.index.decision_index[entity_id]
            
            # Add special handling for decision relationships
            decision = self.index.decision_data[entity_id]
            
            # Add related features
            for feature_id in decision.feature_ids:
                if feature_id in self.index.feature_data:
                    feature = self.index.feature_data[feature_id]
                    
                    result = SearchResult(
                        entity_id=feature_id,
                        entity_type="feature",
                        title=f"Feature: {feature.name}",
                        snippet=feature.description[:200],
                        relevance_score=0.9,  # High relevance for direct association
                        date=feature.created_at,
                        tags=feature.tags
                    )
                    
                    related_entities["feature"].append(result)
            
            # Add related objectives
            for objective_id in decision.objective_ids:
                if objective_id in self.index.objective_data:
                    objective = self.index.objective_data[objective_id]
                    
                    result = SearchResult(
                        entity_id=objective_id,
                        entity_type="objective",
                        title=f"Objective: {objective.name}",
                        snippet=objective.description[:200],
                        relevance_score=0.9,  # High relevance for direct association
                        date=objective.created_at,
                        tags=objective.tags
                    )
                    
                    related_entities["objective"].append(result)
        
        elif entity_type == "competitor" and entity_id in self.index.competitor_index:
            source_terms = self.index.competitor_index[entity_id]
        
        elif entity_type == "stakeholder" and entity_id in self.index.stakeholder_index:
            source_terms = self.index.stakeholder_index[entity_id]
            
            # Add special handling for stakeholder relationships
            stakeholder = self.index.stakeholder_data[entity_id]
            
            # Add perspectives from this stakeholder
            for perspective_id, perspective in self.index.perspective_data.items():
                if perspective.stakeholder_id == entity_id:
                    result = SearchResult(
                        entity_id=perspective_id,
                        entity_type="perspective",
                        title=f"Perspective: {perspective.topic}",
                        snippet=perspective.perspective[:200],
                        relevance_score=0.95,  # Very high relevance for own perspectives
                        date=perspective.date_recorded,
                        tags=[]
                    )
                    
                    related_entities["perspective"].append(result)
            
            # Add features this stakeholder is interested in
            for feature_id in stakeholder.feature_preferences:
                if feature_id in self.index.feature_data:
                    feature = self.index.feature_data[feature_id]
                    preference = stakeholder.feature_preferences[feature_id]
                    
                    result = SearchResult(
                        entity_id=feature_id,
                        entity_type="feature",
                        title=f"Feature: {feature.name} (Preference: {preference:.2f})",
                        snippet=feature.description[:200],
                        relevance_score=preference * 0.9,  # Scale by preference
                        date=feature.created_at,
                        tags=feature.tags
                    )
                    
                    related_entities["feature"].append(result)
            
            # Add objectives this stakeholder is aligned with
            for objective_id in stakeholder.objective_alignment:
                if objective_id in self.index.objective_data:
                    objective = self.index.objective_data[objective_id]
                    alignment = stakeholder.objective_alignment[objective_id]
                    
                    result = SearchResult(
                        entity_id=objective_id,
                        entity_type="objective",
                        title=f"Objective: {objective.name} (Alignment: {alignment:.2f})",
                        snippet=objective.description[:200],
                        relevance_score=alignment * 0.9,  # Scale by alignment
                        date=objective.created_at,
                        tags=objective.tags
                    )
                    
                    related_entities["objective"].append(result)
        
        elif entity_type == "perspective" and entity_id in self.index.perspective_index:
            source_terms = self.index.perspective_index[entity_id]
            
            # Add special handling for perspective relationships
            perspective = self.index.perspective_data[entity_id]
            
            # Add stakeholder
            if perspective.stakeholder_id in self.index.stakeholder_data:
                stakeholder = self.index.stakeholder_data[perspective.stakeholder_id]
                
                result = SearchResult(
                    entity_id=stakeholder.id,
                    entity_type="stakeholder",
                    title=f"Stakeholder: {stakeholder.name}",
                    snippet=stakeholder.notes[:200] if stakeholder.notes else "",
                    relevance_score=0.95,  # Very high relevance for own stakeholder
                    date=stakeholder.created_at,
                    tags=[]
                )
                
                related_entities["stakeholder"].append(result)
            
            # Add related features
            for feature_id in perspective.related_feature_ids:
                if feature_id in self.index.feature_data:
                    feature = self.index.feature_data[feature_id]
                    
                    result = SearchResult(
                        entity_id=feature_id,
                        entity_type="feature",
                        title=f"Feature: {feature.name}",
                        snippet=feature.description[:200],
                        relevance_score=0.9,  # High relevance for direct association
                        date=feature.created_at,
                        tags=feature.tags
                    )
                    
                    related_entities["feature"].append(result)
            
            # Add related objectives
            for objective_id in perspective.related_objective_ids:
                if objective_id in self.index.objective_data:
                    objective = self.index.objective_data[objective_id]
                    
                    result = SearchResult(
                        entity_id=objective_id,
                        entity_type="objective",
                        title=f"Objective: {objective.name}",
                        snippet=objective.description[:200],
                        relevance_score=0.9,  # High relevance for direct association
                        date=objective.created_at,
                        tags=objective.tags
                    )
                    
                    related_entities["objective"].append(result)
        
        # If we have source terms, find semantically similar entities
        if source_terms:
            # Get the most important terms
            important_terms = sorted(
                source_terms.items(), key=lambda x: x[1], reverse=True
            )[:20]
            
            query_terms = [term for term, _ in important_terms]
            
            # Search in each domain (excluding the source entity)
            
            # Search in feedback
            for feedback_id, terms in self.index.feedback_index.items():
                if entity_type == "feedback" and feedback_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:  # Threshold to filter out less relevant results
                    feedback = self.index.feedback_data[feedback_id]
                    
                    result = SearchResult(
                        entity_id=feedback_id,
                        entity_type="feedback",
                        title=f"Feedback: {feedback.content[:50]}...",
                        snippet=feedback.content[:200],
                        relevance_score=relevance,
                        date=feedback.created_at,
                        tags=feedback.tags
                    )
                    
                    related_entities["feedback"].append(result)
            
            # Search in features
            for feature_id, terms in self.index.feature_index.items():
                if entity_type == "feature" and feature_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:
                    feature = self.index.feature_data[feature_id]
                    
                    result = SearchResult(
                        entity_id=feature_id,
                        entity_type="feature",
                        title=f"Feature: {feature.name}",
                        snippet=feature.description[:200],
                        relevance_score=relevance,
                        date=feature.created_at,
                        tags=feature.tags
                    )
                    
                    related_entities["feature"].append(result)
            
            # Search in objectives
            for objective_id, terms in self.index.objective_index.items():
                if entity_type == "objective" and objective_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:
                    objective = self.index.objective_data[objective_id]
                    
                    result = SearchResult(
                        entity_id=objective_id,
                        entity_type="objective",
                        title=f"Objective: {objective.name}",
                        snippet=objective.description[:200],
                        relevance_score=relevance,
                        date=objective.created_at,
                        tags=objective.tags
                    )
                    
                    related_entities["objective"].append(result)
            
            # Search in decisions
            for decision_id, terms in self.index.decision_index.items():
                if entity_type == "decision" and decision_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:
                    decision = self.index.decision_data[decision_id]
                    
                    result = SearchResult(
                        entity_id=decision_id,
                        entity_type="decision",
                        title=f"Decision: {decision.title}",
                        snippet=decision.description[:200],
                        relevance_score=relevance,
                        date=decision.decision_date,
                        tags=decision.tags
                    )
                    
                    related_entities["decision"].append(result)
            
            # Search in competitors
            for competitor_id, terms in self.index.competitor_index.items():
                if entity_type == "competitor" and competitor_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:
                    competitor = self.index.competitor_data[competitor_id]
                    
                    description = competitor.description or ""
                    result = SearchResult(
                        entity_id=competitor_id,
                        entity_type="competitor",
                        title=f"Competitor: {competitor.name}",
                        snippet=description[:200],
                        relevance_score=relevance,
                        date=competitor.created_at,
                        tags=competitor.tags
                    )
                    
                    related_entities["competitor"].append(result)
            
            # Search in stakeholders
            for stakeholder_id, terms in self.index.stakeholder_index.items():
                if entity_type == "stakeholder" and stakeholder_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:
                    stakeholder = self.index.stakeholder_data[stakeholder_id]
                    
                    organization = f" ({stakeholder.organization})" if stakeholder.organization else ""
                    notes = stakeholder.notes or ""
                    
                    result = SearchResult(
                        entity_id=stakeholder_id,
                        entity_type="stakeholder",
                        title=f"Stakeholder: {stakeholder.name}{organization}",
                        snippet=notes[:200],
                        relevance_score=relevance,
                        date=stakeholder.created_at,
                        tags=[]
                    )
                    
                    related_entities["stakeholder"].append(result)
            
            # Search in perspectives
            for perspective_id, terms in self.index.perspective_index.items():
                if entity_type == "perspective" and perspective_id == entity_id:
                    continue
                
                relevance = self._calculate_relevance(query_terms, terms)
                
                if relevance > 0.5:
                    perspective = self.index.perspective_data[perspective_id]
                    
                    # Get stakeholder name
                    stakeholder_name = "Unknown"
                    if perspective.stakeholder_id in self.index.stakeholder_data:
                        stakeholder_name = self.index.stakeholder_data[perspective.stakeholder_id].name
                    
                    result = SearchResult(
                        entity_id=perspective_id,
                        entity_type="perspective",
                        title=f"Perspective: {stakeholder_name} on {perspective.topic}",
                        snippet=perspective.perspective[:200],
                        relevance_score=relevance,
                        date=perspective.date_recorded,
                        tags=[]
                    )
                    
                    related_entities["perspective"].append(result)
        
        # Sort each category by relevance and apply limits
        for entity_type, results in related_entities.items():
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            related_entities[entity_type] = results[:max_results]
        
        return related_entities