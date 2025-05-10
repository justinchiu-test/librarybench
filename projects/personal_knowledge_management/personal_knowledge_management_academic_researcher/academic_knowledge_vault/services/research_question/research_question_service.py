"""
Research Question service for the Academic Knowledge Vault system.

This module provides functionality for managing research questions, hypotheses, and evidence.
"""

import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType, Reference
from academic_knowledge_vault.models.research_question import (
    Evidence,
    EvidenceStrength,
    EvidenceType,
    Hypothesis,
    HypothesisStatus,
    ResearchQuestion,
    ResearchQuestionCollection,
    ResearchQuestionStatus,
)
from academic_knowledge_vault.storage.research_question_storage import (
    EvidenceStorage,
    HypothesisStorage,
    ResearchQuestionStorage,
    ResearchQuestionCollectionStorage,
)


class ResearchQuestionService:
    """Service for managing research questions, hypotheses, and evidence."""
    
    def __init__(self,
                question_storage: ResearchQuestionStorage,
                hypothesis_storage: HypothesisStorage,
                evidence_storage: EvidenceStorage,
                collection_storage: ResearchQuestionCollectionStorage):
        """
        Initialize the research question service.
        
        Args:
            question_storage: Storage for research questions
            hypothesis_storage: Storage for hypotheses
            evidence_storage: Storage for evidence
            collection_storage: Storage for question collections
        """
        self.question_storage = question_storage
        self.hypothesis_storage = hypothesis_storage
        self.evidence_storage = evidence_storage
        self.collection_storage = collection_storage
    
    def create_research_question(self,
                               question: str,
                               description: Optional[str] = None,
                               tags: Optional[List[str]] = None,
                               priority: int = 3,
                               status: Union[str, ResearchQuestionStatus] = ResearchQuestionStatus.ACTIVE,
                               related_citations: Optional[List[str]] = None,
                               knowledge_gaps: Optional[List[str]] = None,
                               deadline: Optional[datetime] = None) -> str:
        """
        Create a new research question.
        
        Args:
            question: The research question text
            description: Detailed description of the question
            tags: Tags for the question
            priority: Priority level (1-5, with 1 being highest)
            status: Status of the question
            related_citations: IDs of related citations
            knowledge_gaps: List of identified knowledge gaps
            deadline: Optional deadline for addressing the question
            
        Returns:
            ID of the created research question
        """
        # Handle string status
        if isinstance(status, str):
            status = ResearchQuestionStatus(status)
        
        # Create citation references if provided
        citation_refs = []
        if related_citations:
            for citation_id in related_citations:
                citation_refs.append(Reference(
                    item_id=citation_id,
                    item_type=KnowledgeItemType.CITATION
                ))
        
        # Create the research question
        research_question = ResearchQuestion(
            title=question[:100],  # Use first 100 chars of question as title
            question=question,
            description=description,
            tags=set(tags or []),
            priority=priority,
            status=status,
            related_citations=citation_refs,
            knowledge_gaps=knowledge_gaps or [],
            deadline=deadline
        )
        
        # Save the research question
        question_id = self.question_storage.save(research_question)
        
        return question_id
    
    def update_research_question(self,
                               question_id: str,
                               question: Optional[str] = None,
                               description: Optional[str] = None,
                               tags: Optional[List[str]] = None,
                               add_tags: Optional[List[str]] = None,
                               remove_tags: Optional[List[str]] = None,
                               priority: Optional[int] = None,
                               status: Optional[Union[str, ResearchQuestionStatus]] = None,
                               deadline: Optional[datetime] = None) -> None:
        """
        Update an existing research question.
        
        Args:
            question_id: ID of the question to update
            question: New question text (if None, keep existing)
            description: New description (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            priority: New priority level (if None, keep existing)
            status: New status (if None, keep existing)
            deadline: New deadline (if None, keep existing)
            
        Raises:
            ValueError: If the research question doesn't exist
        """
        if not self.question_storage.exists(question_id):
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        research_question = self.question_storage.get(question_id)
        
        # Update question text if provided
        if question is not None:
            research_question.question = question
            # Also update title based on question
            research_question.title = question[:100]
        
        # Update description if provided
        if description is not None:
            research_question.description = description
        
        # Update tags if provided
        if tags is not None:
            research_question.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            research_question.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            research_question.tags.difference_update(remove_tags)
        
        # Update priority if provided
        if priority is not None:
            research_question.priority = priority
        
        # Update status if provided
        if status is not None:
            if isinstance(status, str):
                status = ResearchQuestionStatus(status)
            research_question.status = status
        
        # Update deadline if provided
        if deadline is not None:
            research_question.deadline = deadline
        
        # Save the updated research question
        self.question_storage.save(research_question)
    
    def delete_research_question(self, question_id: str) -> bool:
        """
        Delete a research question.
        
        Args:
            question_id: ID of the question to delete
            
        Returns:
            True if the question was deleted, False if it didn't exist
        """
        return self.question_storage.delete(question_id)
    
    def get_research_question(self, question_id: str) -> ResearchQuestion:
        """
        Get a research question by ID.
        
        Args:
            question_id: ID of the question to retrieve
            
        Returns:
            The requested research question
            
        Raises:
            ValueError: If the research question doesn't exist
        """
        if not self.question_storage.exists(question_id):
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        return self.question_storage.get(question_id)
    
    def add_knowledge_gap(self, question_id: str, gap_description: str) -> None:
        """
        Add a knowledge gap to a research question.
        
        Args:
            question_id: ID of the research question
            gap_description: Description of the knowledge gap
            
        Raises:
            ValueError: If the research question doesn't exist
        """
        if not self.question_storage.exists(question_id):
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        research_question = self.question_storage.get(question_id)
        research_question.add_knowledge_gap(gap_description)
        self.question_storage.save(research_question)
    
    def add_related_citation(self, question_id: str, citation_id: str) -> None:
        """
        Add a related citation to a research question.
        
        Args:
            question_id: ID of the research question
            citation_id: ID of the citation
            
        Raises:
            ValueError: If the research question doesn't exist
        """
        if not self.question_storage.exists(question_id):
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        research_question = self.question_storage.get(question_id)
        citation_ref = Reference(
            item_id=citation_id,
            item_type=KnowledgeItemType.CITATION
        )
        
        # Check if the citation is already linked
        for ref in research_question.related_citations:
            if ref.item_id == citation_id:
                return  # Already linked
        
        research_question.related_citations.append(citation_ref)
        self.question_storage.save(research_question)
    
    def create_hypothesis(self,
                         statement: str,
                         research_question_id: Optional[str] = None,
                         status: Union[str, HypothesisStatus] = HypothesisStatus.PROPOSED,
                         tags: Optional[List[str]] = None,
                         related_citations: Optional[List[str]] = None,
                         confidence_level: float = 0.0,
                         parent_hypothesis_id: Optional[str] = None) -> str:
        """
        Create a new hypothesis.
        
        Args:
            statement: The hypothesis statement
            research_question_id: ID of the related research question
            status: Status of the hypothesis
            tags: Tags for the hypothesis
            related_citations: IDs of related citations
            confidence_level: Initial confidence level (0.0 to 1.0)
            parent_hypothesis_id: ID of the parent hypothesis (for revisions)
            
        Returns:
            ID of the created hypothesis
            
        Raises:
            ValueError: If the research question doesn't exist
        """
        # Validate research question if provided
        if research_question_id and not self.question_storage.exists(research_question_id):
            raise ValueError(f"Research question with ID {research_question_id} does not exist")
        
        # Validate parent hypothesis if provided
        if parent_hypothesis_id and not self.hypothesis_storage.exists(parent_hypothesis_id):
            raise ValueError(f"Parent hypothesis with ID {parent_hypothesis_id} does not exist")
        
        # Handle string status
        if isinstance(status, str):
            status = HypothesisStatus(status)
        
        # Create citation references if provided
        citation_refs = []
        if related_citations:
            for citation_id in related_citations:
                citation_refs.append(Reference(
                    item_id=citation_id,
                    item_type=KnowledgeItemType.CITATION
                ))
        
        # Create the hypothesis
        hypothesis = Hypothesis(
            title=statement[:100],  # Use first 100 chars of statement as title
            statement=statement,
            research_question_id=research_question_id,
            status=status,
            tags=set(tags or []),
            related_citations=citation_refs,
            confidence_level=confidence_level,
            parent_hypothesis_id=parent_hypothesis_id
        )
        
        # Save the hypothesis
        hypothesis_id = self.hypothesis_storage.save(hypothesis)
        
        # Add hypothesis reference to the research question if provided
        if research_question_id:
            research_question = self.question_storage.get(research_question_id)
            hypothesis_ref = Reference(
                item_id=hypothesis_id,
                item_type=KnowledgeItemType.HYPOTHESIS
            )
            research_question.add_hypothesis(hypothesis_ref)
            self.question_storage.save(research_question)
        
        return hypothesis_id
    
    def update_hypothesis(self,
                         hypothesis_id: str,
                         statement: Optional[str] = None,
                         status: Optional[Union[str, HypothesisStatus]] = None,
                         tags: Optional[List[str]] = None,
                         add_tags: Optional[List[str]] = None,
                         remove_tags: Optional[List[str]] = None,
                         confidence_level: Optional[float] = None) -> None:
        """
        Update an existing hypothesis.
        
        Args:
            hypothesis_id: ID of the hypothesis to update
            statement: New statement (if None, keep existing)
            status: New status (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            confidence_level: New confidence level (if None, keep existing)
            
        Raises:
            ValueError: If the hypothesis doesn't exist
        """
        if not self.hypothesis_storage.exists(hypothesis_id):
            raise ValueError(f"Hypothesis with ID {hypothesis_id} does not exist")
        
        hypothesis = self.hypothesis_storage.get(hypothesis_id)
        
        # Update statement if provided
        if statement is not None:
            hypothesis.statement = statement
            # Also update title based on statement
            hypothesis.title = statement[:100]
        
        # Update status if provided
        if status is not None:
            if isinstance(status, str):
                status = HypothesisStatus(status)
            hypothesis.update_status(status)
        
        # Update tags if provided
        if tags is not None:
            hypothesis.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            hypothesis.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            hypothesis.tags.difference_update(remove_tags)
        
        # Update confidence level if provided
        if confidence_level is not None:
            hypothesis.confidence_level = max(0.0, min(1.0, confidence_level))
        
        # Save the updated hypothesis
        self.hypothesis_storage.save(hypothesis)
    
    def delete_hypothesis(self, hypothesis_id: str) -> bool:
        """
        Delete a hypothesis.
        
        Args:
            hypothesis_id: ID of the hypothesis to delete
            
        Returns:
            True if the hypothesis was deleted, False if it didn't exist
        """
        return self.hypothesis_storage.delete(hypothesis_id)
    
    def get_hypothesis(self, hypothesis_id: str) -> Hypothesis:
        """
        Get a hypothesis by ID.
        
        Args:
            hypothesis_id: ID of the hypothesis to retrieve
            
        Returns:
            The requested hypothesis
            
        Raises:
            ValueError: If the hypothesis doesn't exist
        """
        if not self.hypothesis_storage.exists(hypothesis_id):
            raise ValueError(f"Hypothesis with ID {hypothesis_id} does not exist")
        
        return self.hypothesis_storage.get(hypothesis_id)
    
    def create_evidence(self,
                       description: str,
                       evidence_type: Union[str, EvidenceType],
                       strength: Union[str, EvidenceStrength] = EvidenceStrength.UNKNOWN,
                       source_id: Optional[str] = None,
                       source_type: Optional[KnowledgeItemType] = None,
                       supports_ids: Optional[List[str]] = None,
                       contradicts_ids: Optional[List[str]] = None,
                       confidence_score: float = 0.5,
                       methodology_notes: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> str:
        """
        Create new evidence for research questions or hypotheses.
        
        Args:
            description: Description of the evidence
            evidence_type: Type of evidence
            strength: Strength assessment of the evidence
            source_id: ID of the source item (e.g., citation, note, experiment)
            source_type: Type of the source item
            supports_ids: IDs of items this evidence supports
            contradicts_ids: IDs of items this evidence contradicts
            confidence_score: Confidence score for the evidence (0.0 to 1.0)
            methodology_notes: Notes about the methodology
            tags: Tags for the evidence
            
        Returns:
            ID of the created evidence
        """
        # Handle string types
        if isinstance(evidence_type, str):
            evidence_type = EvidenceType(evidence_type)
        
        if isinstance(strength, str):
            strength = EvidenceStrength(strength)
        
        # Create source reference if provided
        source_ref = None
        if source_id and source_type:
            source_ref = Reference(
                item_id=source_id,
                item_type=source_type
            )
        
        # Create supported item references
        supports_refs = []
        if supports_ids:
            for item_id in supports_ids:
                # Determine item type
                item_type = None
                if self.question_storage.exists(item_id):
                    item_type = KnowledgeItemType.RESEARCH_QUESTION
                elif self.hypothesis_storage.exists(item_id):
                    item_type = KnowledgeItemType.HYPOTHESIS
                else:
                    continue  # Skip if item doesn't exist or type is unknown
                
                supports_refs.append(Reference(
                    item_id=item_id,
                    item_type=item_type
                ))
        
        # Create contradicted item references
        contradicts_refs = []
        if contradicts_ids:
            for item_id in contradicts_ids:
                # Determine item type
                item_type = None
                if self.question_storage.exists(item_id):
                    item_type = KnowledgeItemType.RESEARCH_QUESTION
                elif self.hypothesis_storage.exists(item_id):
                    item_type = KnowledgeItemType.HYPOTHESIS
                else:
                    continue  # Skip if item doesn't exist or type is unknown
                
                contradicts_refs.append(Reference(
                    item_id=item_id,
                    item_type=item_type
                ))
        
        # Create the evidence
        evidence = Evidence(
            title=description[:100],  # Use first 100 chars of description as title
            description=description,
            evidence_type=evidence_type,
            strength=strength,
            source=source_ref,
            supports=supports_refs,
            contradicts=contradicts_refs,
            confidence_score=confidence_score,
            methodology_notes=methodology_notes,
            tags=set(tags or [])
        )
        
        # Save the evidence
        evidence_id = self.evidence_storage.save(evidence)
        
        # Add evidence references to supported items
        if supports_ids:
            for item_id in supports_ids:
                evidence_ref = Reference(
                    item_id=evidence_id,
                    item_type=KnowledgeItemType.EVIDENCE
                )
                
                if self.question_storage.exists(item_id):
                    question = self.question_storage.get(item_id)
                    question.add_supporting_evidence(evidence_ref)
                    self.question_storage.save(question)
                elif self.hypothesis_storage.exists(item_id):
                    hypothesis = self.hypothesis_storage.get(item_id)
                    hypothesis.add_supporting_evidence(evidence_ref)
                    self.hypothesis_storage.save(hypothesis)
        
        # Add evidence references to contradicted items
        if contradicts_ids:
            for item_id in contradicts_ids:
                evidence_ref = Reference(
                    item_id=evidence_id,
                    item_type=KnowledgeItemType.EVIDENCE
                )
                
                if self.question_storage.exists(item_id):
                    question = self.question_storage.get(item_id)
                    question.add_contradicting_evidence(evidence_ref)
                    self.question_storage.save(question)
                elif self.hypothesis_storage.exists(item_id):
                    hypothesis = self.hypothesis_storage.get(item_id)
                    hypothesis.add_contradicting_evidence(evidence_ref)
                    self.hypothesis_storage.save(hypothesis)
        
        return evidence_id
    
    def update_evidence(self,
                       evidence_id: str,
                       description: Optional[str] = None,
                       evidence_type: Optional[Union[str, EvidenceType]] = None,
                       strength: Optional[Union[str, EvidenceStrength]] = None,
                       confidence_score: Optional[float] = None,
                       methodology_notes: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       add_tags: Optional[List[str]] = None,
                       remove_tags: Optional[List[str]] = None) -> None:
        """
        Update existing evidence.
        
        Args:
            evidence_id: ID of the evidence to update
            description: New description (if None, keep existing)
            evidence_type: New evidence type (if None, keep existing)
            strength: New strength assessment (if None, keep existing)
            confidence_score: New confidence score (if None, keep existing)
            methodology_notes: New methodology notes (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the evidence doesn't exist
        """
        if not self.evidence_storage.exists(evidence_id):
            raise ValueError(f"Evidence with ID {evidence_id} does not exist")
        
        evidence = self.evidence_storage.get(evidence_id)
        
        # Update description if provided
        if description is not None:
            evidence.description = description
            # Also update title based on description
            evidence.title = description[:100]
        
        # Update evidence type if provided
        if evidence_type is not None:
            if isinstance(evidence_type, str):
                evidence_type = EvidenceType(evidence_type)
            evidence.evidence_type = evidence_type
        
        # Update strength if provided
        if strength is not None:
            if isinstance(strength, str):
                strength = EvidenceStrength(strength)
            evidence.update_strength(strength)
        
        # Update confidence score if provided
        if confidence_score is not None:
            evidence.confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Update methodology notes if provided
        if methodology_notes is not None:
            evidence.methodology_notes = methodology_notes
        
        # Update tags if provided
        if tags is not None:
            evidence.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            evidence.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            evidence.tags.difference_update(remove_tags)
        
        # Save the updated evidence
        self.evidence_storage.save(evidence)
    
    def delete_evidence(self, evidence_id: str) -> bool:
        """
        Delete evidence.
        
        Args:
            evidence_id: ID of the evidence to delete
            
        Returns:
            True if the evidence was deleted, False if it didn't exist
        """
        return self.evidence_storage.delete(evidence_id)
    
    def get_evidence(self, evidence_id: str) -> Evidence:
        """
        Get evidence by ID.
        
        Args:
            evidence_id: ID of the evidence to retrieve
            
        Returns:
            The requested evidence
            
        Raises:
            ValueError: If the evidence doesn't exist
        """
        if not self.evidence_storage.exists(evidence_id):
            raise ValueError(f"Evidence with ID {evidence_id} does not exist")
        
        return self.evidence_storage.get(evidence_id)
    
    def create_collection(self,
                         name: str,
                         description: Optional[str] = None,
                         question_ids: Optional[List[str]] = None,
                         tags: Optional[List[str]] = None) -> str:
        """
        Create a research question collection.
        
        Args:
            name: Collection name
            description: Collection description
            question_ids: IDs of questions to include
            tags: Tags for the collection
            
        Returns:
            ID of the created collection
            
        Raises:
            ValueError: If any of the specified questions don't exist
        """
        # Validate question IDs if provided
        if question_ids:
            for question_id in question_ids:
                if not self.question_storage.exists(question_id):
                    raise ValueError(f"Research question with ID {question_id} does not exist")
        
        # Create the collection
        collection = ResearchQuestionCollection(
            name=name,
            description=description,
            question_ids=set(question_ids or []),
            tags=set(tags or [])
        )
        
        # Save the collection
        collection_id = self.collection_storage.save(collection)
        
        return collection_id
    
    def add_question_to_collection(self, collection_id: str, question_id: str) -> None:
        """
        Add a research question to a collection.
        
        Args:
            collection_id: ID of the collection
            question_id: ID of the question to add
            
        Raises:
            ValueError: If the collection or question doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        if not self.question_storage.exists(question_id):
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.add_question(question_id)
        self.collection_storage.save(collection)
    
    def remove_question_from_collection(self, collection_id: str, question_id: str) -> None:
        """
        Remove a research question from a collection.
        
        Args:
            collection_id: ID of the collection
            question_id: ID of the question to remove
            
        Raises:
            ValueError: If the collection doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.remove_question(question_id)
        self.collection_storage.save(collection)
    
    def get_collection(self, collection_id: str) -> ResearchQuestionCollection:
        """
        Get a collection by ID.
        
        Args:
            collection_id: ID of the collection to retrieve
            
        Returns:
            The requested collection
            
        Raises:
            ValueError: If the collection doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        return self.collection_storage.get(collection_id)
    
    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_id: ID of the collection to delete
            
        Returns:
            True if the collection was deleted, False if it didn't exist
        """
        return self.collection_storage.delete(collection_id)
    
    def get_hypotheses_for_question(self, question_id: str) -> List[str]:
        """
        Get hypotheses associated with a research question.
        
        Args:
            question_id: ID of the research question
            
        Returns:
            List of hypothesis IDs for the question
            
        Raises:
            ValueError: If the research question doesn't exist
        """
        if not self.question_storage.exists(question_id):
            raise ValueError(f"Research question with ID {question_id} does not exist")
        
        return self.hypothesis_storage.get_by_research_question(question_id)
    
    def get_supporting_evidence(self, item_id: str) -> List[str]:
        """
        Get evidence supporting a research question or hypothesis.
        
        Args:
            item_id: ID of the research question or hypothesis
            
        Returns:
            List of evidence IDs supporting the item
        """
        return self.evidence_storage.get_supporting(item_id)
    
    def get_contradicting_evidence(self, item_id: str) -> List[str]:
        """
        Get evidence contradicting a research question or hypothesis.
        
        Args:
            item_id: ID of the research question or hypothesis
            
        Returns:
            List of evidence IDs contradicting the item
        """
        return self.evidence_storage.get_contradicting(item_id)
    
    def calculate_evidence_strength(self, hypothesis_id: str) -> float:
        """
        Calculate the overall evidence strength for a hypothesis.
        
        Args:
            hypothesis_id: ID of the hypothesis
            
        Returns:
            Strength score between 0.0 and 1.0
            
        Raises:
            ValueError: If the hypothesis doesn't exist
        """
        if not self.hypothesis_storage.exists(hypothesis_id):
            raise ValueError(f"Hypothesis with ID {hypothesis_id} does not exist")
        
        hypothesis = self.hypothesis_storage.get(hypothesis_id)
        
        supporting_evidence_ids = self.evidence_storage.get_supporting(hypothesis_id)
        contradicting_evidence_ids = self.evidence_storage.get_contradicting(hypothesis_id)
        
        if not supporting_evidence_ids and not contradicting_evidence_ids:
            return 0.0  # No evidence
        
        # Calculate weighted evidence scores
        supporting_score = 0.0
        for evidence_id in supporting_evidence_ids:
            try:
                evidence = self.evidence_storage.get(evidence_id)
                # Weight by strength and confidence
                strength_weight = 0.2  # Default for unknown
                if evidence.strength == EvidenceStrength.STRONG:
                    strength_weight = 1.0
                elif evidence.strength == EvidenceStrength.MODERATE:
                    strength_weight = 0.7
                elif evidence.strength == EvidenceStrength.WEAK:
                    strength_weight = 0.4
                elif evidence.strength == EvidenceStrength.ANECDOTAL:
                    strength_weight = 0.2
                
                supporting_score += strength_weight * evidence.confidence_score
            except:
                continue
        
        contradicting_score = 0.0
        for evidence_id in contradicting_evidence_ids:
            try:
                evidence = self.evidence_storage.get(evidence_id)
                # Weight by strength and confidence
                strength_weight = 0.2  # Default for unknown
                if evidence.strength == EvidenceStrength.STRONG:
                    strength_weight = 1.0
                elif evidence.strength == EvidenceStrength.MODERATE:
                    strength_weight = 0.7
                elif evidence.strength == EvidenceStrength.WEAK:
                    strength_weight = 0.4
                elif evidence.strength == EvidenceStrength.ANECDOTAL:
                    strength_weight = 0.2
                
                contradicting_score += strength_weight * evidence.confidence_score
            except:
                continue
        
        # Normalize the scores by the number of evidence items
        if supporting_evidence_ids:
            supporting_score /= len(supporting_evidence_ids)
        
        if contradicting_evidence_ids:
            contradicting_score /= len(contradicting_evidence_ids)
        
        # Calculate final score
        total_score = supporting_score + contradicting_score
        if total_score == 0:
            return 0.0
        
        # Return a score between 0 and 1
        evidence_strength = supporting_score / total_score
        
        # Update the hypothesis with the calculated strength
        hypothesis.evidence_strength_score = evidence_strength
        self.hypothesis_storage.save(hypothesis)
        
        return evidence_strength
    
    def search_questions(self,
                        text: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        status: Optional[Union[str, ResearchQuestionStatus]] = None,
                        priority: Optional[int] = None,
                        has_knowledge_gaps: Optional[bool] = None) -> List[str]:
        """
        Search for research questions based on various criteria.
        
        Args:
            text: Text to search for in question and description
            tags: Tags to filter by
            status: Status to filter by
            priority: Priority level to filter by
            has_knowledge_gaps: If True, only return questions with knowledge gaps
            
        Returns:
            List of matching research question IDs
        """
        # Start with all questions
        result_ids = set(self.question_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.question_storage.search_by_text(text))
            result_ids.intersection_update(text_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.question_storage.get_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by status if specified
        if status:
            if isinstance(status, str):
                status = ResearchQuestionStatus(status)
            
            status_results = set(self.question_storage.get_by_status(status))
            result_ids.intersection_update(status_results)
        
        # Filter by priority if specified
        if priority is not None:
            priority_results = set(self.question_storage.get_by_priority(priority))
            result_ids.intersection_update(priority_results)
        
        # Filter by knowledge gaps if specified
        if has_knowledge_gaps is True:
            gap_results = set(self.question_storage.get_with_knowledge_gaps())
            result_ids.intersection_update(gap_results)
        elif has_knowledge_gaps is False:
            gap_results = set(self.question_storage.get_with_knowledge_gaps())
            result_ids.difference_update(gap_results)
        
        return list(result_ids)
    
    def search_hypotheses(self,
                         text: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         status: Optional[Union[str, HypothesisStatus]] = None,
                         research_question_id: Optional[str] = None,
                         min_confidence: Optional[float] = None,
                         max_confidence: Optional[float] = None) -> List[str]:
        """
        Search for hypotheses based on various criteria.
        
        Args:
            text: Text to search for in the statement
            tags: Tags to filter by
            status: Status to filter by
            research_question_id: ID of the associated research question
            min_confidence: Minimum confidence level
            max_confidence: Maximum confidence level
            
        Returns:
            List of matching hypothesis IDs
        """
        # Start with all hypotheses
        result_ids = set(self.hypothesis_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set()
            for hypothesis_id in result_ids:
                try:
                    hypothesis = self.hypothesis_storage.get(hypothesis_id)
                    if text.lower() in hypothesis.statement.lower():
                        text_results.add(hypothesis_id)
                except:
                    continue
            
            result_ids.intersection_update(text_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.hypothesis_storage.get_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by status if specified
        if status:
            if isinstance(status, str):
                status = HypothesisStatus(status)
            
            status_results = set(self.hypothesis_storage.get_by_status(status))
            result_ids.intersection_update(status_results)
        
        # Filter by research question if specified
        if research_question_id:
            question_results = set(self.hypothesis_storage.get_by_research_question(research_question_id))
            result_ids.intersection_update(question_results)
        
        # Filter by confidence range if specified
        if min_confidence is not None or max_confidence is not None:
            min_conf = min_confidence if min_confidence is not None else 0.0
            max_conf = max_confidence if max_confidence is not None else 1.0
            
            confidence_results = set(self.hypothesis_storage.get_by_confidence(min_conf, max_conf))
            result_ids.intersection_update(confidence_results)
        
        return list(result_ids)