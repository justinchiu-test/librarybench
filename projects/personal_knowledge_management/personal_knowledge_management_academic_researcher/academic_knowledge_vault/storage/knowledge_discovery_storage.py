"""
Knowledge Discovery storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for knowledge discoveries, graphs and analyses.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.knowledge_discovery import (
    DiscoveryConfidence,
    DiscoveryType,
    KnowledgeDiscovery,
    KnowledgeGraph,
    TemporalAnalysis,
    TopicModel,
)
from academic_knowledge_vault.storage.base import JsonFileStorage


class KnowledgeDiscoveryStorage(JsonFileStorage[KnowledgeDiscovery]):
    """Storage for knowledge discoveries."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize knowledge discovery storage.
        
        Args:
            base_dir: Base directory for discovery storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, KnowledgeDiscovery, create_dir)
    
    def get_by_type(self, discovery_type: Union[str, DiscoveryType]) -> List[str]:
        """
        Get discoveries of a specific type.
        
        Args:
            discovery_type: Type to filter by
            
        Returns:
            List of discovery IDs of the specified type
        """
        if isinstance(discovery_type, str):
            discovery_type = DiscoveryType(discovery_type)
        
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                if discovery.discovery_type == discovery_type:
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids
    
    def get_by_confidence(self, confidence: Union[str, DiscoveryConfidence]) -> List[str]:
        """
        Get discoveries with a specific confidence level.
        
        Args:
            confidence: Confidence level to filter by
            
        Returns:
            List of discovery IDs with the specified confidence
        """
        if isinstance(confidence, str):
            confidence = DiscoveryConfidence(confidence)
        
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                if discovery.confidence == confidence:
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids
    
    def get_by_review_status(self, reviewed: bool) -> List[str]:
        """
        Get discoveries based on review status.
        
        Args:
            reviewed: True to get reviewed discoveries, False for unreviewed
            
        Returns:
            List of discovery IDs matching the review status
        """
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                if discovery.reviewed == reviewed:
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids
    
    def get_by_related_item(self, item_id: str) -> List[str]:
        """
        Get discoveries related to a specific item.
        
        Args:
            item_id: ID of the related item
            
        Returns:
            List of discovery IDs related to the item
        """
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                # Check in both related_items and central_items
                is_related = False
                
                for ref in discovery.related_items:
                    if ref.item_id == item_id:
                        is_related = True
                        break
                
                if not is_related:
                    for ref in discovery.central_items:
                        if ref.item_id == item_id:
                            is_related = True
                            break
                
                if is_related:
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> List[str]:
        """
        Get discoveries created within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of discovery IDs in the date range
        """
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                discovered_at = discovery.discovered_at
                
                include = True
                
                if start_date and discovered_at < start_date:
                    include = False
                
                if end_date and discovered_at > end_date:
                    include = False
                
                if include:
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids
    
    def search_by_description(self, text: str) -> List[str]:
        """
        Search for discoveries by description.
        
        Args:
            text: Text to search for in discovery descriptions
            
        Returns:
            List of discovery IDs with matching descriptions
        """
        text = text.lower()
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                if text in discovery.description.lower():
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids
    
    def search_by_method(self, method: str) -> List[str]:
        """
        Search for discoveries by discovery method.
        
        Args:
            method: Method to search for
            
        Returns:
            List of discovery IDs with matching methods
        """
        method = method.lower()
        result_ids = []
        
        for discovery_id in self.list_ids():
            try:
                discovery = self.get(discovery_id)
                
                if method in discovery.discovery_method.lower():
                    result_ids.append(discovery_id)
                    
            except Exception:
                # Skip problematic discoveries
                continue
        
        return result_ids


class KnowledgeGraphStorage(JsonFileStorage[KnowledgeGraph]):
    """Storage for knowledge graphs."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize knowledge graph storage.
        
        Args:
            base_dir: Base directory for graph storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, KnowledgeGraph, create_dir)
    
    def search_by_name(self, text: str) -> List[str]:
        """
        Search for graphs by name.
        
        Args:
            text: Text to search for in graph names
            
        Returns:
            List of graph IDs with matching names
        """
        text = text.lower()
        result_ids = []
        
        for graph_id in self.list_ids():
            try:
                graph = self.get(graph_id)
                
                if text in graph.name.lower():
                    result_ids.append(graph_id)
                    
            except Exception:
                # Skip problematic graphs
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for graphs with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, graphs must have all tags; if False, any tag is sufficient
            
        Returns:
            List of graph IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for graph_id in self.list_ids():
            try:
                graph = self.get(graph_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in graph.tags for tag in tags):
                        result_ids.append(graph_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in graph.tags for tag in tags):
                        result_ids.append(graph_id)
                    
            except Exception:
                # Skip problematic graphs
                continue
        
        return result_ids
    
    def get_by_node_count_range(self, min_count: int, max_count: int) -> List[str]:
        """
        Get graphs with a node count within a specific range.
        
        Args:
            min_count: Minimum node count
            max_count: Maximum node count
            
        Returns:
            List of graph IDs with node counts in the range
        """
        result_ids = []
        
        for graph_id in self.list_ids():
            try:
                graph = self.get(graph_id)
                
                if min_count <= graph.node_count <= max_count:
                    result_ids.append(graph_id)
                    
            except Exception:
                # Skip problematic graphs
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> List[str]:
        """
        Get graphs created within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of graph IDs in the date range
        """
        result_ids = []
        
        for graph_id in self.list_ids():
            try:
                graph = self.get(graph_id)
                
                created_at = graph.created_at
                
                include = True
                
                if start_date and created_at < start_date:
                    include = False
                
                if end_date and created_at > end_date:
                    include = False
                
                if include:
                    result_ids.append(graph_id)
                    
            except Exception:
                # Skip problematic graphs
                continue
        
        return result_ids
    
    def contains_node(self, node_id: str) -> List[str]:
        """
        Find graphs that contain a specific node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of graph IDs containing the node
        """
        result_ids = []
        
        for graph_id in self.list_ids():
            try:
                graph = self.get(graph_id)
                
                if node_id in graph.nodes:
                    result_ids.append(graph_id)
                    
            except Exception:
                # Skip problematic graphs
                continue
        
        return result_ids


class TopicModelStorage(JsonFileStorage[TopicModel]):
    """Storage for topic models."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize topic model storage.
        
        Args:
            base_dir: Base directory for model storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, TopicModel, create_dir)
    
    def search_by_name(self, text: str) -> List[str]:
        """
        Search for models by name.
        
        Args:
            text: Text to search for in model names
            
        Returns:
            List of model IDs with matching names
        """
        text = text.lower()
        result_ids = []
        
        for model_id in self.list_ids():
            try:
                model = self.get(model_id)
                
                if text in model.name.lower():
                    result_ids.append(model_id)
                    
            except Exception:
                # Skip problematic models
                continue
        
        return result_ids
    
    def get_by_algorithm(self, algorithm: str) -> List[str]:
        """
        Get models using a specific algorithm.
        
        Args:
            algorithm: Algorithm to filter by
            
        Returns:
            List of model IDs using the algorithm
        """
        algorithm = algorithm.lower()
        result_ids = []
        
        for model_id in self.list_ids():
            try:
                model = self.get(model_id)
                
                if algorithm in model.algorithm.lower():
                    result_ids.append(model_id)
                    
            except Exception:
                # Skip problematic models
                continue
        
        return result_ids
    
    def get_by_num_topics(self, min_topics: int, max_topics: int) -> List[str]:
        """
        Get models with a number of topics within a specific range.
        
        Args:
            min_topics: Minimum number of topics
            max_topics: Maximum number of topics
            
        Returns:
            List of model IDs with topic counts in the range
        """
        result_ids = []
        
        for model_id in self.list_ids():
            try:
                model = self.get(model_id)
                
                if min_topics <= model.num_topics <= max_topics:
                    result_ids.append(model_id)
                    
            except Exception:
                # Skip problematic models
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> List[str]:
        """
        Get models created within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of model IDs in the date range
        """
        result_ids = []
        
        for model_id in self.list_ids():
            try:
                model = self.get(model_id)
                
                created_at = model.created_at
                
                include = True
                
                if start_date and created_at < start_date:
                    include = False
                
                if end_date and created_at > end_date:
                    include = False
                
                if include:
                    result_ids.append(model_id)
                    
            except Exception:
                # Skip problematic models
                continue
        
        return result_ids
    
    def get_models_for_document(self, document_id: str) -> List[str]:
        """
        Get models that include a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of model IDs including the document
        """
        result_ids = []
        
        for model_id in self.list_ids():
            try:
                model = self.get(model_id)
                
                if document_id in model.document_topics:
                    result_ids.append(model_id)
                    
            except Exception:
                # Skip problematic models
                continue
        
        return result_ids


class TemporalAnalysisStorage(JsonFileStorage[TemporalAnalysis]):
    """Storage for temporal analyses."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize temporal analysis storage.
        
        Args:
            base_dir: Base directory for analysis storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, TemporalAnalysis, create_dir)
    
    def search_by_name(self, text: str) -> List[str]:
        """
        Search for analyses by name.
        
        Args:
            text: Text to search for in analysis names
            
        Returns:
            List of analysis IDs with matching names
        """
        text = text.lower()
        result_ids = []
        
        for analysis_id in self.list_ids():
            try:
                analysis = self.get(analysis_id)
                
                if text in analysis.name.lower():
                    result_ids.append(analysis_id)
                    
            except Exception:
                # Skip problematic analyses
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None,
                         use_analysis_dates: bool = False) -> List[str]:
        """
        Get analyses within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            use_analysis_dates: If True, filter by analysis dates; if False, filter by creation dates
            
        Returns:
            List of analysis IDs in the date range
        """
        result_ids = []
        
        for analysis_id in self.list_ids():
            try:
                analysis = self.get(analysis_id)
                
                if use_analysis_dates:
                    # Use the analysis start and end dates
                    include = True
                    
                    if start_date and analysis.start_date < start_date:
                        include = False
                    
                    if end_date and analysis.end_date > end_date:
                        include = False
                else:
                    # Use the creation date
                    created_at = analysis.created_at
                    
                    include = True
                    
                    if start_date and created_at < start_date:
                        include = False
                    
                    if end_date and created_at > end_date:
                        include = False
                
                if include:
                    result_ids.append(analysis_id)
                    
            except Exception:
                # Skip problematic analyses
                continue
        
        return result_ids
    
    def get_analyses_tracking_item(self, item_id: str) -> List[str]:
        """
        Get analyses that track a specific item.
        
        Args:
            item_id: ID of the tracked item
            
        Returns:
            List of analysis IDs tracking the item
        """
        result_ids = []
        
        for analysis_id in self.list_ids():
            try:
                analysis = self.get(analysis_id)
                
                for item in analysis.tracked_items:
                    if item.get("id") == item_id:
                        result_ids.append(analysis_id)
                        break
                    
            except Exception:
                # Skip problematic analyses
                continue
        
        return result_ids