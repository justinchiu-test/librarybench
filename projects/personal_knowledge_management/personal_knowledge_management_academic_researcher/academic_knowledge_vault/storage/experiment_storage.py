"""
Experiment storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for experiments, protocols, and results.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.experiment import (
    Experiment,
    ExperimentCollection,
    ExperimentProtocol,
    ExperimentResult,
    ExperimentStatus,
    ParameterType,
)
from academic_knowledge_vault.storage.base import JsonFileStorage


class ExperimentStorage(JsonFileStorage[Experiment]):
    """Storage for experiments."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize experiment storage.
        
        Args:
            base_dir: Base directory for experiment storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, Experiment, create_dir)
    
    def get_by_status(self, status: Union[str, ExperimentStatus]) -> List[str]:
        """
        Get experiments with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of experiment IDs with the specified status
        """
        if isinstance(status, str):
            status = ExperimentStatus(status)
        
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                if experiment.status == status:
                    result_ids.append(experiment_id)
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids
    
    def get_by_research_question(self, question_id: str) -> List[str]:
        """
        Get experiments for a specific research question.
        
        Args:
            question_id: ID of the research question
            
        Returns:
            List of experiment IDs for the question
        """
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                if experiment.research_question_id == question_id:
                    result_ids.append(experiment_id)
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids
    
    def get_by_hypothesis(self, hypothesis_id: str) -> List[str]:
        """
        Get experiments for a specific hypothesis.
        
        Args:
            hypothesis_id: ID of the hypothesis
            
        Returns:
            List of experiment IDs for the hypothesis
        """
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                if hypothesis_id in experiment.hypothesis_ids:
                    result_ids.append(experiment_id)
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids
    
    def get_by_researcher(self, researcher_name: str) -> List[str]:
        """
        Get experiments by a specific researcher.
        
        Args:
            researcher_name: Researcher name (partial match)
            
        Returns:
            List of experiment IDs by the researcher
        """
        researcher_name = researcher_name.lower()
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                for researcher in experiment.researchers:
                    if researcher_name in researcher.name.lower():
                        result_ids.append(experiment_id)
                        break
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids
    
    def get_by_protocol(self, protocol_id: str) -> List[str]:
        """
        Get experiments using a specific protocol.
        
        Args:
            protocol_id: ID of the protocol
            
        Returns:
            List of experiment IDs using the protocol
        """
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                if experiment.protocol_id == protocol_id:
                    result_ids.append(experiment_id)
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None,
                         use_start_date: bool = True) -> List[str]:
        """
        Get experiments within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            use_start_date: If True, filter by start_date; if False, filter by end_date
            
        Returns:
            List of experiment IDs in the date range
        """
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                date_field = experiment.start_date if use_start_date else experiment.end_date
                
                if not date_field:
                    continue
                
                include = True
                
                if start_date and date_field < start_date:
                    include = False
                
                if end_date and date_field > end_date:
                    include = False
                
                if include:
                    result_ids.append(experiment_id)
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for experiments with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, experiments must have all tags; if False, any tag is sufficient
            
        Returns:
            List of experiment IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for experiment_id in self.list_ids():
            try:
                experiment = self.get(experiment_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in experiment.tags for tag in tags):
                        result_ids.append(experiment_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in experiment.tags for tag in tags):
                        result_ids.append(experiment_id)
                    
            except Exception:
                # Skip problematic experiments
                continue
        
        return result_ids


class ExperimentProtocolStorage(JsonFileStorage[ExperimentProtocol]):
    """Storage for experiment protocols."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize protocol storage.
        
        Args:
            base_dir: Base directory for protocol storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, ExperimentProtocol, create_dir)
    
    def get_latest_version(self, protocol_name: str) -> Optional[ExperimentProtocol]:
        """
        Get the latest version of a protocol by name.
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            Latest version of the protocol, or None if not found
        """
        matching_protocols = []
        
        for protocol_id in self.list_ids():
            try:
                protocol = self.get(protocol_id)
                
                if protocol.name == protocol_name:
                    matching_protocols.append(protocol)
                    
            except Exception:
                # Skip problematic protocols
                continue
        
        if not matching_protocols:
            return None
        
        # Sort by version (descending) and return the first one
        return sorted(matching_protocols, key=lambda p: p.version, reverse=True)[0]
    
    def get_protocol_versions(self, protocol_name: str) -> List[str]:
        """
        Get all versions of a protocol by name.
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            List of protocol IDs for the different versions
        """
        result_ids = []
        
        for protocol_id in self.list_ids():
            try:
                protocol = self.get(protocol_id)
                
                if protocol.name == protocol_name:
                    result_ids.append(protocol_id)
                    
            except Exception:
                # Skip problematic protocols
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for protocols with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, protocols must have all tags; if False, any tag is sufficient
            
        Returns:
            List of protocol IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for protocol_id in self.list_ids():
            try:
                protocol = self.get(protocol_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in protocol.tags for tag in tags):
                        result_ids.append(protocol_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in protocol.tags for tag in tags):
                        result_ids.append(protocol_id)
                    
            except Exception:
                # Skip problematic protocols
                continue
        
        return result_ids
    
    def search_by_author(self, author_id: str) -> List[str]:
        """
        Search for protocols by author.
        
        Args:
            author_id: ID of the author
            
        Returns:
            List of protocol IDs by the author
        """
        result_ids = []
        
        for protocol_id in self.list_ids():
            try:
                protocol = self.get(protocol_id)
                
                if protocol.author_id == author_id:
                    result_ids.append(protocol_id)
                    
            except Exception:
                # Skip problematic protocols
                continue
        
        return result_ids


class ExperimentCollectionStorage(JsonFileStorage[ExperimentCollection]):
    """Storage for experiment collections."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize experiment collection storage.
        
        Args:
            base_dir: Base directory for collection storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, ExperimentCollection, create_dir)
    
    def get_collections_containing_experiment(self, experiment_id: str) -> List[str]:
        """
        Find collections that contain a specific experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            List of collection IDs containing the experiment
        """
        result_ids = []
        
        for collection_id in self.list_ids():
            try:
                collection = self.get(collection_id)
                
                if experiment_id in collection.experiment_ids:
                    result_ids.append(collection_id)
                    
            except Exception:
                # Skip problematic collections
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for collections with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, collections must have all tags; if False, any tag is sufficient
            
        Returns:
            List of collection IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for collection_id in self.list_ids():
            try:
                collection = self.get(collection_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in collection.tags for tag in tags):
                        result_ids.append(collection_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in collection.tags for tag in tags):
                        result_ids.append(collection_id)
                    
            except Exception:
                # Skip problematic collections
                continue
        
        return result_ids