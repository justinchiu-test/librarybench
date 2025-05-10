"""
Knowledge Discovery models for the Academic Knowledge Vault system.

This module defines the data models for automated knowledge discovery and insights.
"""

import datetime
import enum
from typing import Dict, List, Optional, Set, Union, Any

from pydantic import BaseModel, Field, validator

from academic_knowledge_vault.models.base import (
    BaseKnowledgeItem,
    KnowledgeItemType,
    LinkedItem,
    Reference,
)


class DiscoveryType(str, enum.Enum):
    """Types of knowledge discoveries."""

    RELATED_CONCEPTS = "related_concepts"
    KNOWLEDGE_GAP = "knowledge_gap"
    CONTRADICTING_EVIDENCE = "contradicting_evidence"
    EMERGING_PATTERN = "emerging_pattern"
    CITATION_TREND = "citation_trend"
    POTENTIAL_COLLABORATION = "potential_collaboration"
    RESEARCH_OPPORTUNITY = "research_opportunity"


class DiscoveryConfidence(str, enum.Enum):
    """Confidence levels for knowledge discoveries."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPECULATIVE = "speculative"


class KnowledgeDiscovery(BaseKnowledgeItem):
    """An automated discovery or insight within the knowledge base."""

    # Discovery information
    discovery_type: DiscoveryType
    description: str
    confidence: DiscoveryConfidence = DiscoveryConfidence.MEDIUM
    
    # Discovery context
    context_explanation: Optional[str] = None
    discovered_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    discovery_method: str  # Algorithm or method used
    
    # Related knowledge items
    related_items: List[Reference] = Field(default_factory=list)
    central_items: List[Reference] = Field(default_factory=list)  # Most important items
    
    # User interaction
    reviewed: bool = False
    reviewed_at: Optional[datetime.datetime] = None
    user_feedback: Optional[str] = None
    user_rating: Optional[int] = None  # 1-5 scale
    
    # Actions
    suggested_actions: List[str] = Field(default_factory=list)
    completed_actions: List[str] = Field(default_factory=list)
    
    def mark_as_reviewed(self, feedback: Optional[str] = None, rating: Optional[int] = None) -> None:
        """Mark the discovery as reviewed by the user."""
        self.reviewed = True
        self.reviewed_at = datetime.datetime.now()
        if feedback:
            self.user_feedback = feedback
        if rating and 1 <= rating <= 5:
            self.user_rating = rating
        self.update_timestamp()
    
    def add_related_item(self, reference: Reference) -> None:
        """Add a related item to the discovery."""
        for existing_ref in self.related_items:
            if existing_ref.item_id == reference.item_id:
                return  # Reference already exists
        self.related_items.append(reference)
        self.update_timestamp()
    
    def add_suggested_action(self, action: str) -> None:
        """Add a suggested action for this discovery."""
        if action not in self.suggested_actions:
            self.suggested_actions.append(action)
            self.update_timestamp()
    
    def complete_action(self, action: str) -> None:
        """Mark a suggested action as completed."""
        if action in self.suggested_actions and action not in self.completed_actions:
            self.completed_actions.append(action)
            self.update_timestamp()


class KnowledgeGraph(BaseModel):
    """A graph representation of knowledge items and their relationships."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Graph data
    nodes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Graph properties
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0
    
    # Graph metadata
    tags: Set[str] = Field(default_factory=set)
    visualization_settings: Optional[Dict[str, Any]] = None
    
    def add_node(self, node_id: str, node_type: KnowledgeItemType, properties: Dict[str, Any]) -> None:
        """Add a node to the graph."""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            **properties
        }
        self.node_count = len(self.nodes)
        self._update_graph_metrics()
        self.updated_at = datetime.datetime.now()
    
    def add_edge(self, source_id: str, target_id: str, relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Add an edge to the graph."""
        edge = {
            "source": source_id,
            "target": target_id,
            "type": relationship_type
        }
        
        if properties:
            edge.update(properties)
        
        self.edges.append(edge)
        self.edge_count = len(self.edges)
        self._update_graph_metrics()
        self.updated_at = datetime.datetime.now()
    
    def _update_graph_metrics(self) -> None:
        """Update graph metrics such as density."""
        if self.node_count <= 1:
            self.density = 0.0
        else:
            # Density is the ratio of actual edges to possible edges
            possible_edges = self.node_count * (self.node_count - 1)
            self.density = self.edge_count / possible_edges


class TopicModel(BaseModel):
    """A topic model generated from the knowledge base content."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Model information
    algorithm: str
    num_topics: int
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Topics
    topics: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Document-topic assignments
    document_topics: Dict[str, List[Dict[str, float]]] = Field(default_factory=dict)
    
    # Model evaluation metrics
    coherence_score: Optional[float] = None
    perplexity: Optional[float] = None
    
    def add_topic(self, topic_id: int, terms: List[Dict[str, float]]) -> None:
        """Add a topic to the model."""
        self.topics.append({
            "id": topic_id,
            "terms": terms
        })
    
    def assign_document_topics(self, document_id: str, topic_weights: List[Dict[str, float]]) -> None:
        """Assign topic weights to a document."""
        self.document_topics[document_id] = topic_weights
    
    def get_documents_for_topic(self, topic_id: int, threshold: float = 0.1) -> List[str]:
        """Get all documents where the given topic has a weight above the threshold."""
        result = []
        for doc_id, topics in self.document_topics.items():
            for topic in topics:
                if topic["id"] == topic_id and topic["weight"] >= threshold:
                    result.append(doc_id)
                    break
        return result
    
    def get_topics_for_document(self, document_id: str, threshold: float = 0.1) -> List[int]:
        """Get all topics for a document with weights above the threshold."""
        if document_id not in self.document_topics:
            return []
        
        return [
            topic["id"] for topic in self.document_topics[document_id]
            if topic["weight"] >= threshold
        ]


class TemporalAnalysis(BaseModel):
    """An analysis of knowledge changes over time."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Analysis parameters
    start_date: datetime.datetime
    end_date: datetime.datetime
    time_intervals: List[Dict[str, datetime.datetime]] = Field(default_factory=list)
    
    # Tracked entities
    tracked_items: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Time series data
    time_series: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    
    # Analysis results
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    significant_changes: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_time_interval(self, start: datetime.datetime, end: datetime.datetime, label: Optional[str] = None) -> None:
        """Add a time interval to the analysis."""
        interval = {
            "start": start,
            "end": end
        }
        if label:
            interval["label"] = label
        
        self.time_intervals.append(interval)
    
    def add_tracked_item(self, item_id: str, item_type: KnowledgeItemType, properties: Dict[str, Any]) -> None:
        """Add an item to track in the temporal analysis."""
        self.tracked_items.append({
            "id": item_id,
            "type": item_type,
            **properties
        })
    
    def add_time_series_data(self, series_name: str, data_points: List[Dict[str, Any]]) -> None:
        """Add time series data to the analysis."""
        self.time_series[series_name] = data_points
    
    def add_trend(self, trend_type: str, description: str, significance: float, affected_items: List[str]) -> None:
        """Add an identified trend to the analysis."""
        self.trends.append({
            "type": trend_type,
            "description": description,
            "significance": significance,
            "affected_items": affected_items
        })
    
    def add_significant_change(self, change_type: str, description: str, time_point: datetime.datetime, 
                             affected_items: List[str], magnitude: float) -> None:
        """Add a significant change point to the analysis."""
        self.significant_changes.append({
            "type": change_type,
            "description": description,
            "time_point": time_point,
            "affected_items": affected_items,
            "magnitude": magnitude
        })


import uuid