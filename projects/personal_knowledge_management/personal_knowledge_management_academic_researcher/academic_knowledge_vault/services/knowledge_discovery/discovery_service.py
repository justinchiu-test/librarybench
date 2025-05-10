"""
Knowledge Discovery service for the Academic Knowledge Vault system.

This module provides functionality for automated knowledge discovery and insights.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType, Reference
from academic_knowledge_vault.models.knowledge_discovery import (
    DiscoveryConfidence,
    DiscoveryType,
    KnowledgeDiscovery,
    KnowledgeGraph,
    TemporalAnalysis,
    TopicModel,
)
from academic_knowledge_vault.storage.knowledge_discovery_storage import (
    KnowledgeDiscoveryStorage,
    KnowledgeGraphStorage,
    TemporalAnalysisStorage,
    TopicModelStorage,
)


class KnowledgeDiscoveryService:
    """Service for discovering insights and connections in the knowledge base."""
    
    def __init__(self,
                discovery_storage: KnowledgeDiscoveryStorage,
                graph_storage: KnowledgeGraphStorage,
                topic_model_storage: TopicModelStorage,
                temporal_analysis_storage: TemporalAnalysisStorage):
        """
        Initialize the knowledge discovery service.
        
        Args:
            discovery_storage: Storage for discoveries
            graph_storage: Storage for knowledge graphs
            topic_model_storage: Storage for topic models
            temporal_analysis_storage: Storage for temporal analyses
        """
        self.discovery_storage = discovery_storage
        self.graph_storage = graph_storage
        self.topic_model_storage = topic_model_storage
        self.temporal_analysis_storage = temporal_analysis_storage
    
    def create_discovery(self,
                        discovery_type: Union[str, DiscoveryType],
                        description: str,
                        confidence: Union[str, DiscoveryConfidence],
                        discovery_method: str,
                        context_explanation: Optional[str] = None,
                        related_items: Optional[List[Dict[str, Any]]] = None,
                        central_items: Optional[List[Dict[str, Any]]] = None,
                        suggested_actions: Optional[List[str]] = None,
                        tags: Optional[List[str]] = None) -> str:
        """
        Create a new knowledge discovery.
        
        Args:
            discovery_type: Type of discovery
            description: Description of the discovery
            confidence: Confidence level
            discovery_method: Method used to make the discovery
            context_explanation: Explanation of the discovery context
            related_items: List of related item dictionaries
            central_items: List of central item dictionaries
            suggested_actions: List of suggested actions
            tags: Tags for the discovery
            
        Returns:
            ID of the created discovery
        """
        # Handle string types
        if isinstance(discovery_type, str):
            discovery_type = DiscoveryType(discovery_type)
        
        if isinstance(confidence, str):
            confidence = DiscoveryConfidence(confidence)
        
        # Create reference objects for related items
        related_refs = []
        if related_items:
            for item_dict in related_items:
                item_type = item_dict.get("item_type")
                if isinstance(item_type, str):
                    item_type = KnowledgeItemType(item_type)
                
                reference = Reference(
                    item_id=item_dict["item_id"],
                    item_type=item_type,
                    context=item_dict.get("context")
                )
                related_refs.append(reference)
        
        # Create reference objects for central items
        central_refs = []
        if central_items:
            for item_dict in central_items:
                item_type = item_dict.get("item_type")
                if isinstance(item_type, str):
                    item_type = KnowledgeItemType(item_type)
                
                reference = Reference(
                    item_id=item_dict["item_id"],
                    item_type=item_type,
                    context=item_dict.get("context")
                )
                central_refs.append(reference)
        
        # Create the discovery
        discovery = KnowledgeDiscovery(
            title=f"{discovery_type.value.title()} Discovery",
            discovery_type=discovery_type,
            description=description,
            confidence=confidence,
            context_explanation=context_explanation,
            discovery_method=discovery_method,
            related_items=related_refs,
            central_items=central_refs,
            suggested_actions=suggested_actions or [],
            tags=set(tags or [])
        )
        
        # Save the discovery
        discovery_id = self.discovery_storage.save(discovery)
        
        return discovery_id
    
    def mark_discovery_as_reviewed(self,
                                  discovery_id: str,
                                  feedback: Optional[str] = None,
                                  rating: Optional[int] = None) -> None:
        """
        Mark a discovery as reviewed by the user.
        
        Args:
            discovery_id: ID of the discovery
            feedback: User feedback
            rating: User rating (1-5)
            
        Raises:
            ValueError: If the discovery doesn't exist or rating is invalid
        """
        if not self.discovery_storage.exists(discovery_id):
            raise ValueError(f"Discovery with ID {discovery_id} does not exist")
        
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError("Rating must be between 1 and 5")
        
        discovery = self.discovery_storage.get(discovery_id)
        discovery.mark_as_reviewed(feedback, rating)
        self.discovery_storage.save(discovery)
    
    def add_suggested_action(self, discovery_id: str, action: str) -> None:
        """
        Add a suggested action to a discovery.
        
        Args:
            discovery_id: ID of the discovery
            action: Action to suggest
            
        Raises:
            ValueError: If the discovery doesn't exist
        """
        if not self.discovery_storage.exists(discovery_id):
            raise ValueError(f"Discovery with ID {discovery_id} does not exist")
        
        discovery = self.discovery_storage.get(discovery_id)
        discovery.add_suggested_action(action)
        self.discovery_storage.save(discovery)
    
    def complete_action(self, discovery_id: str, action: str) -> None:
        """
        Mark a suggested action as completed.
        
        Args:
            discovery_id: ID of the discovery
            action: Action to mark as completed
            
        Raises:
            ValueError: If the discovery doesn't exist
        """
        if not self.discovery_storage.exists(discovery_id):
            raise ValueError(f"Discovery with ID {discovery_id} does not exist")
        
        discovery = self.discovery_storage.get(discovery_id)
        discovery.complete_action(action)
        self.discovery_storage.save(discovery)
    
    def delete_discovery(self, discovery_id: str) -> bool:
        """
        Delete a discovery.
        
        Args:
            discovery_id: ID of the discovery to delete
            
        Returns:
            True if the discovery was deleted, False if it didn't exist
        """
        return self.discovery_storage.delete(discovery_id)
    
    def get_discovery(self, discovery_id: str) -> KnowledgeDiscovery:
        """
        Get a discovery by ID.
        
        Args:
            discovery_id: ID of the discovery to retrieve
            
        Returns:
            The requested discovery
            
        Raises:
            ValueError: If the discovery doesn't exist
        """
        if not self.discovery_storage.exists(discovery_id):
            raise ValueError(f"Discovery with ID {discovery_id} does not exist")
        
        return self.discovery_storage.get(discovery_id)
    
    def create_knowledge_graph(self,
                              name: str,
                              description: Optional[str] = None,
                              nodes: Optional[Dict[str, Dict[str, Any]]] = None,
                              edges: Optional[List[Dict[str, Any]]] = None,
                              visualization_settings: Optional[Dict[str, Any]] = None,
                              tags: Optional[List[str]] = None) -> str:
        """
        Create a new knowledge graph.
        
        Args:
            name: Graph name
            description: Graph description
            nodes: Dictionary of node IDs to node properties
            edges: List of edge dictionaries
            visualization_settings: Dictionary of visualization settings
            tags: Tags for the graph
            
        Returns:
            ID of the created graph
        """
        # Create the graph
        graph = KnowledgeGraph(
            name=name,
            description=description,
            nodes=nodes or {},
            edges=edges or [],
            visualization_settings=visualization_settings,
            tags=set(tags or [])
        )
        
        # Update metrics
        graph.node_count = len(graph.nodes)
        graph.edge_count = len(graph.edges)
        graph._update_graph_metrics()
        
        # Save the graph
        graph_id = self.graph_storage.save(graph)
        
        return graph_id
    
    def add_node(self,
                graph_id: str,
                node_id: str,
                node_type: Union[str, KnowledgeItemType],
                properties: Dict[str, Any]) -> None:
        """
        Add a node to a knowledge graph.
        
        Args:
            graph_id: ID of the graph
            node_id: ID of the node to add
            node_type: Type of the node
            properties: Node properties
            
        Raises:
            ValueError: If the graph doesn't exist
        """
        if not self.graph_storage.exists(graph_id):
            raise ValueError(f"Graph with ID {graph_id} does not exist")
        
        graph = self.graph_storage.get(graph_id)
        
        # Handle string node type
        if isinstance(node_type, str):
            node_type = KnowledgeItemType(node_type)
        
        graph.add_node(node_id, node_type, properties)
        self.graph_storage.save(graph)
    
    def add_edge(self,
                graph_id: str,
                source_id: str,
                target_id: str,
                relationship_type: str,
                properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an edge to a knowledge graph.
        
        Args:
            graph_id: ID of the graph
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_type: Type of relationship
            properties: Edge properties
            
        Raises:
            ValueError: If the graph doesn't exist
        """
        if not self.graph_storage.exists(graph_id):
            raise ValueError(f"Graph with ID {graph_id} does not exist")
        
        graph = self.graph_storage.get(graph_id)
        graph.add_edge(source_id, target_id, relationship_type, properties)
        self.graph_storage.save(graph)
    
    def delete_graph(self, graph_id: str) -> bool:
        """
        Delete a knowledge graph.
        
        Args:
            graph_id: ID of the graph to delete
            
        Returns:
            True if the graph was deleted, False if it didn't exist
        """
        return self.graph_storage.delete(graph_id)
    
    def get_graph(self, graph_id: str) -> KnowledgeGraph:
        """
        Get a knowledge graph by ID.
        
        Args:
            graph_id: ID of the graph to retrieve
            
        Returns:
            The requested graph
            
        Raises:
            ValueError: If the graph doesn't exist
        """
        if not self.graph_storage.exists(graph_id):
            raise ValueError(f"Graph with ID {graph_id} does not exist")
        
        return self.graph_storage.get(graph_id)
    
    def create_topic_model(self,
                          name: str,
                          algorithm: str,
                          num_topics: int,
                          parameters: Optional[Dict[str, Any]] = None,
                          description: Optional[str] = None) -> str:
        """
        Create a new topic model.
        
        Args:
            name: Model name
            algorithm: Algorithm used
            num_topics: Number of topics
            parameters: Algorithm parameters
            description: Model description
            
        Returns:
            ID of the created model
        """
        # Create the model
        model = TopicModel(
            name=name,
            algorithm=algorithm,
            num_topics=num_topics,
            parameters=parameters or {},
            description=description
        )
        
        # Save the model
        model_id = self.topic_model_storage.save(model)
        
        return model_id
    
    def add_topic(self, model_id: str, topic_id: int, terms: List[Dict[str, float]]) -> None:
        """
        Add a topic to a topic model.
        
        Args:
            model_id: ID of the model
            topic_id: ID of the topic
            terms: List of term dictionaries with term and weight
            
        Raises:
            ValueError: If the model doesn't exist
        """
        if not self.topic_model_storage.exists(model_id):
            raise ValueError(f"Topic model with ID {model_id} does not exist")
        
        model = self.topic_model_storage.get(model_id)
        model.add_topic(topic_id, terms)
        self.topic_model_storage.save(model)
    
    def assign_document_topics(self, model_id: str, document_id: str, topic_weights: List[Dict[str, float]]) -> None:
        """
        Assign topic weights to a document.
        
        Args:
            model_id: ID of the model
            document_id: ID of the document
            topic_weights: List of topic weight dictionaries with id and weight
            
        Raises:
            ValueError: If the model doesn't exist
        """
        if not self.topic_model_storage.exists(model_id):
            raise ValueError(f"Topic model with ID {model_id} does not exist")
        
        model = self.topic_model_storage.get(model_id)
        model.assign_document_topics(document_id, topic_weights)
        self.topic_model_storage.save(model)
    
    def delete_topic_model(self, model_id: str) -> bool:
        """
        Delete a topic model.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            True if the model was deleted, False if it didn't exist
        """
        return self.topic_model_storage.delete(model_id)
    
    def get_topic_model(self, model_id: str) -> TopicModel:
        """
        Get a topic model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            The requested model
            
        Raises:
            ValueError: If the model doesn't exist
        """
        if not self.topic_model_storage.exists(model_id):
            raise ValueError(f"Topic model with ID {model_id} does not exist")
        
        return self.topic_model_storage.get(model_id)
    
    def create_temporal_analysis(self,
                                name: str,
                                start_date: datetime,
                                end_date: datetime,
                                description: Optional[str] = None) -> str:
        """
        Create a new temporal analysis.
        
        Args:
            name: Analysis name
            start_date: Start date of the analysis period
            end_date: End date of the analysis period
            description: Analysis description
            
        Returns:
            ID of the created analysis
        """
        # Create the analysis
        analysis = TemporalAnalysis(
            name=name,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        
        # Save the analysis
        analysis_id = self.temporal_analysis_storage.save(analysis)
        
        return analysis_id
    
    def add_time_interval(self,
                         analysis_id: str,
                         start: datetime,
                         end: datetime,
                         label: Optional[str] = None) -> None:
        """
        Add a time interval to a temporal analysis.
        
        Args:
            analysis_id: ID of the analysis
            start: Start date of the interval
            end: End date of the interval
            label: Label for the interval
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        if not self.temporal_analysis_storage.exists(analysis_id):
            raise ValueError(f"Temporal analysis with ID {analysis_id} does not exist")
        
        analysis = self.temporal_analysis_storage.get(analysis_id)
        analysis.add_time_interval(start, end, label)
        self.temporal_analysis_storage.save(analysis)
    
    def add_tracked_item(self,
                        analysis_id: str,
                        item_id: str,
                        item_type: Union[str, KnowledgeItemType],
                        properties: Dict[str, Any]) -> None:
        """
        Add a tracked item to a temporal analysis.
        
        Args:
            analysis_id: ID of the analysis
            item_id: ID of the item to track
            item_type: Type of the item
            properties: Item properties
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        if not self.temporal_analysis_storage.exists(analysis_id):
            raise ValueError(f"Temporal analysis with ID {analysis_id} does not exist")
        
        analysis = self.temporal_analysis_storage.get(analysis_id)
        
        # Handle string item type
        if isinstance(item_type, str):
            item_type = KnowledgeItemType(item_type)
        
        analysis.add_tracked_item(item_id, item_type, properties)
        self.temporal_analysis_storage.save(analysis)
    
    def add_time_series_data(self, analysis_id: str, series_name: str, data_points: List[Dict[str, Any]]) -> None:
        """
        Add time series data to a temporal analysis.
        
        Args:
            analysis_id: ID of the analysis
            series_name: Name of the time series
            data_points: List of data point dictionaries
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        if not self.temporal_analysis_storage.exists(analysis_id):
            raise ValueError(f"Temporal analysis with ID {analysis_id} does not exist")
        
        analysis = self.temporal_analysis_storage.get(analysis_id)
        analysis.add_time_series_data(series_name, data_points)
        self.temporal_analysis_storage.save(analysis)
    
    def add_trend(self,
                 analysis_id: str,
                 trend_type: str,
                 description: str,
                 significance: float,
                 affected_items: List[str]) -> None:
        """
        Add a trend to a temporal analysis.
        
        Args:
            analysis_id: ID of the analysis
            trend_type: Type of trend
            description: Trend description
            significance: Significance score
            affected_items: List of affected item IDs
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        if not self.temporal_analysis_storage.exists(analysis_id):
            raise ValueError(f"Temporal analysis with ID {analysis_id} does not exist")
        
        analysis = self.temporal_analysis_storage.get(analysis_id)
        analysis.add_trend(trend_type, description, significance, affected_items)
        self.temporal_analysis_storage.save(analysis)
    
    def add_significant_change(self,
                              analysis_id: str,
                              change_type: str,
                              description: str,
                              time_point: datetime,
                              affected_items: List[str],
                              magnitude: float) -> None:
        """
        Add a significant change point to a temporal analysis.
        
        Args:
            analysis_id: ID of the analysis
            change_type: Type of change
            description: Change description
            time_point: Time point of the change
            affected_items: List of affected item IDs
            magnitude: Magnitude of the change
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        if not self.temporal_analysis_storage.exists(analysis_id):
            raise ValueError(f"Temporal analysis with ID {analysis_id} does not exist")
        
        analysis = self.temporal_analysis_storage.get(analysis_id)
        analysis.add_significant_change(change_type, description, time_point, affected_items, magnitude)
        self.temporal_analysis_storage.save(analysis)
    
    def delete_temporal_analysis(self, analysis_id: str) -> bool:
        """
        Delete a temporal analysis.
        
        Args:
            analysis_id: ID of the analysis to delete
            
        Returns:
            True if the analysis was deleted, False if it didn't exist
        """
        return self.temporal_analysis_storage.delete(analysis_id)
    
    def get_temporal_analysis(self, analysis_id: str) -> TemporalAnalysis:
        """
        Get a temporal analysis by ID.
        
        Args:
            analysis_id: ID of the analysis to retrieve
            
        Returns:
            The requested analysis
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        if not self.temporal_analysis_storage.exists(analysis_id):
            raise ValueError(f"Temporal analysis with ID {analysis_id} does not exist")
        
        return self.temporal_analysis_storage.get(analysis_id)
    
    def search_discoveries(self,
                          discovery_type: Optional[Union[str, DiscoveryType]] = None,
                          confidence: Optional[Union[str, DiscoveryConfidence]] = None,
                          reviewed: Optional[bool] = None,
                          related_item_id: Optional[str] = None,
                          text: Optional[str] = None,
                          method: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[str]:
        """
        Search for discoveries based on various criteria.
        
        Args:
            discovery_type: Discovery type to filter by
            confidence: Confidence level to filter by
            reviewed: Review status to filter by
            related_item_id: Related item ID to filter by
            text: Text to search for in descriptions
            method: Discovery method to filter by
            start_date: Only include discoveries after this date
            end_date: Only include discoveries before this date
            
        Returns:
            List of matching discovery IDs
        """
        # Start with all discoveries
        result_ids = set(self.discovery_storage.list_ids())
        
        # Filter by type if specified
        if discovery_type:
            if isinstance(discovery_type, str):
                discovery_type = DiscoveryType(discovery_type)
            
            type_results = set(self.discovery_storage.get_by_type(discovery_type))
            result_ids.intersection_update(type_results)
        
        # Filter by confidence if specified
        if confidence:
            if isinstance(confidence, str):
                confidence = DiscoveryConfidence(confidence)
            
            confidence_results = set(self.discovery_storage.get_by_confidence(confidence))
            result_ids.intersection_update(confidence_results)
        
        # Filter by review status if specified
        if reviewed is not None:
            review_results = set(self.discovery_storage.get_by_review_status(reviewed))
            result_ids.intersection_update(review_results)
        
        # Filter by related item if specified
        if related_item_id:
            related_results = set(self.discovery_storage.get_by_related_item(related_item_id))
            result_ids.intersection_update(related_results)
        
        # Filter by text if specified
        if text:
            text_results = set(self.discovery_storage.search_by_description(text))
            result_ids.intersection_update(text_results)
        
        # Filter by method if specified
        if method:
            method_results = set(self.discovery_storage.search_by_method(method))
            result_ids.intersection_update(method_results)
        
        # Filter by date range if specified
        if start_date or end_date:
            date_results = set(self.discovery_storage.get_by_date_range(start_date, end_date))
            result_ids.intersection_update(date_results)
        
        return list(result_ids)
    
    def search_graphs(self,
                     text: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     min_nodes: Optional[int] = None,
                     max_nodes: Optional[int] = None,
                     contains_node_id: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[str]:
        """
        Search for knowledge graphs based on various criteria.
        
        Args:
            text: Text to search for in graph names
            tags: Tags to filter by
            min_nodes: Minimum number of nodes
            max_nodes: Maximum number of nodes
            contains_node_id: Node ID that must be in the graph
            start_date: Only include graphs created after this date
            end_date: Only include graphs created before this date
            
        Returns:
            List of matching graph IDs
        """
        # Start with all graphs
        result_ids = set(self.graph_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.graph_storage.search_by_name(text))
            result_ids.intersection_update(text_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.graph_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by node count if specified
        if min_nodes is not None or max_nodes is not None:
            min_count = min_nodes if min_nodes is not None else 0
            max_count = max_nodes if max_nodes is not None else float('inf')
            
            count_results = set(self.graph_storage.get_by_node_count_range(min_count, max_count))
            result_ids.intersection_update(count_results)
        
        # Filter by node if specified
        if contains_node_id:
            node_results = set(self.graph_storage.contains_node(contains_node_id))
            result_ids.intersection_update(node_results)
        
        # Filter by date range if specified
        if start_date or end_date:
            date_results = set(self.graph_storage.get_by_date_range(start_date, end_date))
            result_ids.intersection_update(date_results)
        
        return list(result_ids)
    
    def search_topic_models(self,
                           text: Optional[str] = None,
                           algorithm: Optional[str] = None,
                           min_topics: Optional[int] = None,
                           max_topics: Optional[int] = None,
                           document_id: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[str]:
        """
        Search for topic models based on various criteria.
        
        Args:
            text: Text to search for in model names
            algorithm: Algorithm to filter by
            min_topics: Minimum number of topics
            max_topics: Maximum number of topics
            document_id: Document ID that must be in the model
            start_date: Only include models created after this date
            end_date: Only include models created before this date
            
        Returns:
            List of matching model IDs
        """
        # Start with all models
        result_ids = set(self.topic_model_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.topic_model_storage.search_by_name(text))
            result_ids.intersection_update(text_results)
        
        # Filter by algorithm if specified
        if algorithm:
            algorithm_results = set(self.topic_model_storage.get_by_algorithm(algorithm))
            result_ids.intersection_update(algorithm_results)
        
        # Filter by topic count if specified
        if min_topics is not None or max_topics is not None:
            min_count = min_topics if min_topics is not None else 0
            max_count = max_topics if max_topics is not None else float('inf')
            
            count_results = set(self.topic_model_storage.get_by_num_topics(min_count, max_count))
            result_ids.intersection_update(count_results)
        
        # Filter by document if specified
        if document_id:
            document_results = set(self.topic_model_storage.get_models_for_document(document_id))
            result_ids.intersection_update(document_results)
        
        # Filter by date range if specified
        if start_date or end_date:
            date_results = set(self.topic_model_storage.get_by_date_range(start_date, end_date))
            result_ids.intersection_update(date_results)
        
        return list(result_ids)
    
    def search_temporal_analyses(self,
                                text: Optional[str] = None,
                                tracked_item_id: Optional[str] = None,
                                analysis_start_date: Optional[datetime] = None,
                                analysis_end_date: Optional[datetime] = None,
                                created_start_date: Optional[datetime] = None,
                                created_end_date: Optional[datetime] = None) -> List[str]:
        """
        Search for temporal analyses based on various criteria.
        
        Args:
            text: Text to search for in analysis names
            tracked_item_id: Item ID that must be tracked in the analysis
            analysis_start_date: Filter by analysis start date
            analysis_end_date: Filter by analysis end date
            created_start_date: Filter by creation start date
            created_end_date: Filter by creation end date
            
        Returns:
            List of matching analysis IDs
        """
        # Start with all analyses
        result_ids = set(self.temporal_analysis_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.temporal_analysis_storage.search_by_name(text))
            result_ids.intersection_update(text_results)
        
        # Filter by tracked item if specified
        if tracked_item_id:
            item_results = set(self.temporal_analysis_storage.get_analyses_tracking_item(tracked_item_id))
            result_ids.intersection_update(item_results)
        
        # Filter by analysis date range if specified
        if analysis_start_date or analysis_end_date:
            date_results = set(self.temporal_analysis_storage.get_by_date_range(
                analysis_start_date, analysis_end_date, True
            ))
            result_ids.intersection_update(date_results)
        
        # Filter by creation date range if specified
        if created_start_date or created_end_date:
            date_results = set(self.temporal_analysis_storage.get_by_date_range(
                created_start_date, created_end_date, False
            ))
            result_ids.intersection_update(date_results)
        
        return list(result_ids)