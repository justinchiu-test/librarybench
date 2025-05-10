"""
Research question storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for research questions, hypotheses, and evidence.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.research_question import (
    Evidence,
    Hypothesis,
    ResearchQuestion,
    ResearchQuestionCollection,
)
from academic_knowledge_vault.storage.base import JsonFileStorage


class EvidenceStorage(JsonFileStorage[Evidence]):
    """Storage for research evidence."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize evidence storage.
        
        Args:
            base_dir: Base directory for evidence storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, Evidence, create_dir)
    
    def get_by_strength(self, strength: str) -> List[str]:
        """
        Get evidence of a specific strength.
        
        Args:
            strength: Strength value to filter by
            
        Returns:
            List of evidence IDs with the specified strength
        """
        result_ids = []
        
        for evidence_id in self.list_ids():
            try:
                evidence = self.get(evidence_id)
                
                if evidence.strength == strength:
                    result_ids.append(evidence_id)
                    
            except Exception:
                # Skip problematic evidence
                continue
        
        return result_ids
    
    def get_by_type(self, evidence_type: str) -> List[str]:
        """
        Get evidence of a specific type.
        
        Args:
            evidence_type: Evidence type to filter by
            
        Returns:
            List of evidence IDs with the specified type
        """
        result_ids = []
        
        for evidence_id in self.list_ids():
            try:
                evidence = self.get(evidence_id)
                
                if evidence.evidence_type == evidence_type:
                    result_ids.append(evidence_id)
                    
            except Exception:
                # Skip problematic evidence
                continue
        
        return result_ids
    
    def get_supporting(self, item_id: str) -> List[str]:
        """
        Get evidence supporting a specific item.
        
        Args:
            item_id: ID of the supported item
            
        Returns:
            List of evidence IDs supporting the item
        """
        result_ids = []
        
        for evidence_id in self.list_ids():
            try:
                evidence = self.get(evidence_id)
                
                for ref in evidence.supports:
                    if ref.item_id == item_id:
                        result_ids.append(evidence_id)
                        break
                    
            except Exception:
                # Skip problematic evidence
                continue
        
        return result_ids
    
    def get_contradicting(self, item_id: str) -> List[str]:
        """
        Get evidence contradicting a specific item.
        
        Args:
            item_id: ID of the contradicted item
            
        Returns:
            List of evidence IDs contradicting the item
        """
        result_ids = []
        
        for evidence_id in self.list_ids():
            try:
                evidence = self.get(evidence_id)
                
                for ref in evidence.contradicts:
                    if ref.item_id == item_id:
                        result_ids.append(evidence_id)
                        break
                    
            except Exception:
                # Skip problematic evidence
                continue
        
        return result_ids


class HypothesisStorage(JsonFileStorage[Hypothesis]):
    """Storage for research hypotheses."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize hypothesis storage.
        
        Args:
            base_dir: Base directory for hypothesis storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, Hypothesis, create_dir)
    
    def get_by_status(self, status: str) -> List[str]:
        """
        Get hypotheses with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of hypothesis IDs with the specified status
        """
        result_ids = []
        
        for hypothesis_id in self.list_ids():
            try:
                hypothesis = self.get(hypothesis_id)
                
                if hypothesis.status == status:
                    result_ids.append(hypothesis_id)
                    
            except Exception:
                # Skip problematic hypotheses
                continue
        
        return result_ids
    
    def get_by_research_question(self, question_id: str) -> List[str]:
        """
        Get hypotheses for a specific research question.
        
        Args:
            question_id: ID of the research question
            
        Returns:
            List of hypothesis IDs for the research question
        """
        result_ids = []
        
        for hypothesis_id in self.list_ids():
            try:
                hypothesis = self.get(hypothesis_id)
                
                if hypothesis.research_question_id == question_id:
                    result_ids.append(hypothesis_id)
                    
            except Exception:
                # Skip problematic hypotheses
                continue
        
        return result_ids
    
    def get_by_confidence(self, min_confidence: float, max_confidence: float) -> List[str]:
        """
        Get hypotheses within a confidence range.
        
        Args:
            min_confidence: Minimum confidence level (inclusive)
            max_confidence: Maximum confidence level (inclusive)
            
        Returns:
            List of hypothesis IDs in the confidence range
        """
        result_ids = []
        
        for hypothesis_id in self.list_ids():
            try:
                hypothesis = self.get(hypothesis_id)
                
                if min_confidence <= hypothesis.confidence_level <= max_confidence:
                    result_ids.append(hypothesis_id)
                    
            except Exception:
                # Skip problematic hypotheses
                continue
        
        return result_ids
    
    def get_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Get hypotheses with specific tags.
        
        Args:
            tags: Tags to filter by
            match_all: If True, all tags must match; if False, any tag is sufficient
            
        Returns:
            List of hypothesis IDs with the specified tags
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for hypothesis_id in self.list_ids():
            try:
                hypothesis = self.get(hypothesis_id)
                
                if match_all:
                    if all(tag in hypothesis.tags for tag in tags):
                        result_ids.append(hypothesis_id)
                else:
                    if any(tag in hypothesis.tags for tag in tags):
                        result_ids.append(hypothesis_id)
                    
            except Exception:
                # Skip problematic hypotheses
                continue
        
        return result_ids


class ResearchQuestionStorage(JsonFileStorage[ResearchQuestion]):
    """Storage for research questions."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize research question storage.
        
        Args:
            base_dir: Base directory for research question storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, ResearchQuestion, create_dir)
    
    def get_by_status(self, status: str) -> List[str]:
        """
        Get research questions with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of research question IDs with the specified status
        """
        result_ids = []
        
        for question_id in self.list_ids():
            try:
                question = self.get(question_id)
                
                if question.status == status:
                    result_ids.append(question_id)
                    
            except Exception:
                # Skip problematic questions
                continue
        
        return result_ids
    
    def get_by_priority(self, priority: int) -> List[str]:
        """
        Get research questions with a specific priority.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List of research question IDs with the specified priority
        """
        result_ids = []
        
        for question_id in self.list_ids():
            try:
                question = self.get(question_id)
                
                if question.priority == priority:
                    result_ids.append(question_id)
                    
            except Exception:
                # Skip problematic questions
                continue
        
        return result_ids
    
    def get_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Get research questions with specific tags.
        
        Args:
            tags: Tags to filter by
            match_all: If True, all tags must match; if False, any tag is sufficient
            
        Returns:
            List of research question IDs with the specified tags
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for question_id in self.list_ids():
            try:
                question = self.get(question_id)
                
                if match_all:
                    if all(tag in question.tags for tag in tags):
                        result_ids.append(question_id)
                else:
                    if any(tag in question.tags for tag in tags):
                        result_ids.append(question_id)
                    
            except Exception:
                # Skip problematic questions
                continue
        
        return result_ids
    
    def search_by_text(self, search_text: str) -> List[str]:
        """
        Search research questions by text content.
        
        Args:
            search_text: Text to search for
            
        Returns:
            List of research question IDs containing the search text
        """
        search_text = search_text.lower()
        result_ids = []
        
        for question_id in self.list_ids():
            try:
                question = self.get(question_id)
                
                # Check in question text
                if search_text in question.question.lower():
                    result_ids.append(question_id)
                    continue
                
                # Check in description
                if question.description and search_text in question.description.lower():
                    result_ids.append(question_id)
                    continue
                
                # Check in knowledge gaps
                for gap in question.knowledge_gaps:
                    if search_text in gap.lower():
                        result_ids.append(question_id)
                        break
                    
            except Exception:
                # Skip problematic questions
                continue
        
        return result_ids
    
    def get_with_knowledge_gaps(self) -> List[str]:
        """
        Get research questions that have identified knowledge gaps.
        
        Returns:
            List of research question IDs with knowledge gaps
        """
        result_ids = []
        
        for question_id in self.list_ids():
            try:
                question = self.get(question_id)
                
                if question.knowledge_gaps:
                    result_ids.append(question_id)
                    
            except Exception:
                # Skip problematic questions
                continue
        
        return result_ids


class ResearchQuestionCollectionStorage(JsonFileStorage[ResearchQuestionCollection]):
    """Storage for research question collections."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize research question collection storage.
        
        Args:
            base_dir: Base directory for collection storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, ResearchQuestionCollection, create_dir)
    
    def get_collections_containing_question(self, question_id: str) -> List[str]:
        """
        Find collections that contain a specific research question.
        
        Args:
            question_id: ID of the research question
            
        Returns:
            List of collection IDs containing the question
        """
        result_ids = []
        
        for collection_id in self.list_ids():
            try:
                collection = self.get(collection_id)
                
                if question_id in collection.question_ids:
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