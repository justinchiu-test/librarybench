"""Main ResearchBrain class that orchestrates the knowledge management system."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

import networkx as nx
from pydantic import BaseModel

from researchbrain.core.models import (
    Annotation, Citation, CitationFormat, Collaborator, CollaboratorRole,
    Evidence, EvidenceStrength, EvidenceType, Experiment, ExperimentStatus,
    GrantProposal, GrantStatus, KnowledgeNode, Note, ResearchQuestion
)
from researchbrain.core.storage import LocalStorage


class ResearchBrain:
    """Main class for the ResearchBrain knowledge management system."""
    
    def __init__(self, storage_path: Union[str, Path]):
        """Initialize the ResearchBrain system.
        
        Args:
            storage_path: Path to the directory where data will be stored.
        """
        self.storage = LocalStorage(storage_path)
        self._knowledge_graph = None
        self._build_knowledge_graph()
    
    def _build_knowledge_graph(self) -> None:
        """Build the internal knowledge graph from stored data."""
        self._knowledge_graph = nx.DiGraph()
        
        # Add nodes for all knowledge objects
        for note in self.storage.list_all(Note):
            self._knowledge_graph.add_node(str(note.id), type='note', title=note.title)
        
        for citation in self.storage.list_all(Citation):
            self._knowledge_graph.add_node(str(citation.id), type='citation', title=citation.title)
        
        for question in self.storage.list_all(ResearchQuestion):
            self._knowledge_graph.add_node(str(question.id), type='question', title=question.question)
        
        for experiment in self.storage.list_all(Experiment):
            self._knowledge_graph.add_node(str(experiment.id), type='experiment', title=experiment.title)
        
        for grant in self.storage.list_all(GrantProposal):
            self._knowledge_graph.add_node(str(grant.id), type='grant', title=grant.title)
        
        # Add edges for relationships
        for note in self.storage.list_all(Note):
            # Note to citation edges
            for citation_id in note.citations:
                self._knowledge_graph.add_edge(str(note.id), str(citation_id), type='cites')
            
            # Note to source edges
            if note.source:
                self._knowledge_graph.add_edge(str(note.id), str(note.source), type='references', page=note.page_reference)
        
        for citation in self.storage.list_all(Citation):
            # Citation to note edges
            for note_id in citation.notes:
                self._knowledge_graph.add_edge(str(citation.id), str(note_id), type='cited_in')
        
        for question in self.storage.list_all(ResearchQuestion):
            # Question to evidence edges
            for evidence in question.evidence:
                self._knowledge_graph.add_edge(
                    str(question.id), 
                    str(evidence.note_id), 
                    type='evidence',
                    evidence_type=evidence.evidence_type,
                    strength=evidence.strength
                )
        
        for experiment in self.storage.list_all(Experiment):
            # Experiment to research question edges
            if experiment.research_question_id:
                self._knowledge_graph.add_edge(str(experiment.id), str(experiment.research_question_id), type='investigates')
            
            # Experiment to note edges
            for note_id in experiment.notes:
                self._knowledge_graph.add_edge(str(experiment.id), str(note_id), type='documents')
        
        for grant in self.storage.list_all(GrantProposal):
            # Grant to note edges
            for note_id in grant.notes:
                self._knowledge_graph.add_edge(str(grant.id), str(note_id), type='includes')
            
            # Grant to experiment edges
            for experiment_id in grant.experiments:
                self._knowledge_graph.add_edge(str(grant.id), str(experiment_id), type='proposes')
            
            # Grant to research question edges
            for question_id in grant.research_questions:
                self._knowledge_graph.add_edge(str(grant.id), str(question_id), type='addresses')
    
    def create_note(self, title: str, content: str, tags: Optional[Set[str]] = None, 
                   source_id: Optional[UUID] = None, page_reference: Optional[int] = None) -> UUID:
        """Create a new research note.
        
        Args:
            title: Title of the note.
            content: Content of the note in Markdown format.
            tags: Optional set of tags for categorization.
            source_id: Optional ID of the source citation.
            page_reference: Optional page reference in the source.
            
        Returns:
            ID of the created note.
        """
        note = Note(
            title=title,
            content=content,
            tags=tags or set(),
            source=source_id,
            page_reference=page_reference
        )
        
        # Extract citation keys from content
        citation_keys = self._extract_citation_keys(content)
        if citation_keys:
            citations = []
            for key in citation_keys:
                citation_id = self._find_citation_by_key(key)
                if citation_id:
                    citations.append(citation_id)
            note.citations = citations
        
        self.storage.save(note)
        
        # Update the knowledge graph
        self._knowledge_graph.add_node(str(note.id), type='note', title=note.title)
        
        if note.source:
            self._knowledge_graph.add_edge(str(note.id), str(note.source), type='references', page=note.page_reference)
        
        for citation_id in note.citations:
            self._knowledge_graph.add_edge(str(note.id), str(citation_id), type='cites')
            
            # Also update the Citation object to reflect this relationship
            citation = self.storage.get(Citation, citation_id)
            if citation and note.id not in citation.notes:
                citation.notes.append(note.id)
                self.storage.save(citation)
                self._knowledge_graph.add_edge(str(citation_id), str(note.id), type='cited_in')
        
        return note.id
    
    def update_note(self, note_id: UUID, title: Optional[str] = None, content: Optional[str] = None, 
                   tags: Optional[Set[str]] = None, source_id: Optional[UUID] = None, 
                   page_reference: Optional[int] = None) -> bool:
        """Update an existing note.
        
        Args:
            note_id: ID of the note to update.
            title: New title (if provided).
            content: New content (if provided).
            tags: New tags (if provided).
            source_id: New source ID (if provided).
            page_reference: New page reference (if provided).
            
        Returns:
            True if the note was updated, False if it wasn't found.
        """
        note = self.storage.get(Note, note_id)
        if not note:
            return False
        
        if title is not None:
            note.title = title
        
        if content is not None:
            note.content = content
            # Re-extract citation keys
            citation_keys = self._extract_citation_keys(content)
            if citation_keys:
                old_citations = set(note.citations)
                new_citations = []
                for key in citation_keys:
                    citation_id = self._find_citation_by_key(key)
                    if citation_id:
                        new_citations.append(citation_id)
                
                # Add new citations and remove those no longer referenced
                note.citations = new_citations
                
                # Update the knowledge graph for citation changes
                new_citation_set = set(new_citations)
                removed_citations = old_citations - new_citation_set
                added_citations = new_citation_set - old_citations
                
                for citation_id in removed_citations:
                    citation = self.storage.get(Citation, citation_id)
                    if citation and note_id in citation.notes:
                        citation.notes.remove(note_id)
                        self.storage.save(citation)
                    
                    if self._knowledge_graph.has_edge(str(note_id), str(citation_id)):
                        self._knowledge_graph.remove_edge(str(note_id), str(citation_id))
                    
                    if self._knowledge_graph.has_edge(str(citation_id), str(note_id)):
                        self._knowledge_graph.remove_edge(str(citation_id), str(note_id))
                
                for citation_id in added_citations:
                    citation = self.storage.get(Citation, citation_id)
                    if citation and note_id not in citation.notes:
                        citation.notes.append(note_id)
                        self.storage.save(citation)
                    
                    self._knowledge_graph.add_edge(str(note_id), str(citation_id), type='cites')
                    self._knowledge_graph.add_edge(str(citation_id), str(note_id), type='cited_in')
        
        if tags is not None:
            note.tags = tags
        
        if source_id is not None:
            old_source = note.source
            note.source = source_id
            
            # Update knowledge graph
            if old_source and self._knowledge_graph.has_edge(str(note_id), str(old_source)):
                self._knowledge_graph.remove_edge(str(note_id), str(old_source))
            
            if source_id:
                self._knowledge_graph.add_edge(str(note_id), str(source_id), type='references', page=note.page_reference)
        
        if page_reference is not None:
            note.page_reference = page_reference
            
            # Update edge attribute in knowledge graph
            if note.source and self._knowledge_graph.has_edge(str(note_id), str(note.source)):
                self._knowledge_graph.edges[str(note_id), str(note.source)]['page'] = page_reference
        
        note.update()
        self.storage.save(note)
        
        # Update node attributes in knowledge graph
        if title is not None:
            self._knowledge_graph.nodes[str(note_id)]['title'] = title
        
        return True
    
    def delete_note(self, note_id: UUID) -> bool:
        """Delete a note.
        
        Args:
            note_id: ID of the note to delete.
            
        Returns:
            True if the note was deleted, False if it wasn't found.
        """
        note = self.storage.get(Note, note_id)
        if not note:
            return False
        
        # Update citations that reference this note
        for citation_id in note.citations:
            citation = self.storage.get(Citation, citation_id)
            if citation and note_id in citation.notes:
                citation.notes.remove(note_id)
                self.storage.save(citation)
        
        # Update research questions that use this note as evidence
        for question in self.storage.list_all(ResearchQuestion):
            updated = False
            new_evidence = []
            for evidence in question.evidence:
                if evidence.note_id != note_id:
                    new_evidence.append(evidence)
                else:
                    updated = True
            
            if updated:
                question.evidence = new_evidence
                self.storage.save(question)
        
        # Update experiments that reference this note
        for experiment in self.storage.list_all(Experiment):
            if note_id in experiment.notes:
                experiment.notes.remove(note_id)
                self.storage.save(experiment)
        
        # Update grant proposals that reference this note
        for grant in self.storage.list_all(GrantProposal):
            if note_id in grant.notes:
                grant.notes.remove(note_id)
                self.storage.save(grant)
        
        # Remove from knowledge graph
        if self._knowledge_graph.has_node(str(note_id)):
            self._knowledge_graph.remove_node(str(note_id))
        
        # Delete the note
        return self.storage.delete(Note, note_id)
    
    def get_note(self, note_id: UUID) -> Optional[Note]:
        """Get a note by ID.
        
        Args:
            note_id: ID of the note to retrieve.
            
        Returns:
            The note if found, None otherwise.
        """
        return self.storage.get(Note, note_id)
    
    def link_note_to_paper(self, note_id: UUID, citation_id: UUID, page: Optional[int] = None) -> bool:
        """Link a note to a specific paper (citation).
        
        Args:
            note_id: ID of the note.
            citation_id: ID of the citation (paper).
            page: Optional page reference.
            
        Returns:
            True if the link was created, False if either the note or citation wasn't found.
        """
        note = self.storage.get(Note, note_id)
        citation = self.storage.get(Citation, citation_id)
        
        if not note or not citation:
            return False
        
        # Update the note
        if citation_id not in note.citations:
            note.citations.append(citation_id)
        
        note.source = citation_id
        note.page_reference = page
        note.update()
        self.storage.save(note)
        
        # Update the citation
        if note_id not in citation.notes:
            citation.notes.append(note_id)
            citation.update()
            self.storage.save(citation)
        
        # Update the knowledge graph
        self._knowledge_graph.add_edge(str(note_id), str(citation_id), type='cites')
        self._knowledge_graph.add_edge(str(note_id), str(citation_id), type='references', page=page)
        self._knowledge_graph.add_edge(str(citation_id), str(note_id), type='cited_in')
        
        return True
    
    def create_citation(self, title: str, authors: List[str], **kwargs) -> UUID:
        """Create a new citation.
        
        Args:
            title: Title of the paper or source.
            authors: List of authors.
            **kwargs: Additional citation metadata.
            
        Returns:
            ID of the created citation.
        """
        citation = Citation(title=title, authors=authors, **kwargs)
        self.storage.save(citation)
        
        # Update the knowledge graph
        self._knowledge_graph.add_node(str(citation.id), type='citation', title=citation.title)
        
        return citation.id
    
    def import_paper(self, file_path: Union[str, Path], extract_metadata: bool = True) -> Optional[UUID]:
        """Import a paper from a PDF or BibTeX file.
        
        Args:
            file_path: Path to the paper file.
            extract_metadata: Whether to attempt metadata extraction from PDF.
            
        Returns:
            ID of the created citation if successful, None otherwise.
        """
        from researchbrain.citations.parsers import (
            extract_pdf_metadata, parse_bibtex_file, parse_ris_file
        )
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        metadata = {}
        if file_path.suffix.lower() == '.pdf':
            if extract_metadata:
                metadata = extract_pdf_metadata(file_path)
            
            # Save the PDF as an attachment
            target_path = self.storage.save_attachment(file_path)
            metadata['file_path'] = target_path
            
        elif file_path.suffix.lower() == '.bib':
            entries = parse_bibtex_file(file_path)
            if entries:
                # Use the first entry
                metadata = entries[0]
                metadata['bibtex'] = entries[0].get('bibtex')
                
        elif file_path.suffix.lower() == '.ris':
            entries = parse_ris_file(file_path)
            if entries:
                metadata = entries[0]
        
        if not metadata or 'title' not in metadata or 'authors' not in metadata:
            # Minimum required fields are missing
            return None
        
        return self.create_citation(**metadata)
    
    def create_research_question(self, question: str, description: Optional[str] = None, 
                                tags: Optional[Set[str]] = None, status: str = "open", 
                                priority: int = 0) -> UUID:
        """Create a new research question or hypothesis.
        
        Args:
            question: The research question text.
            description: Optional detailed description.
            tags: Optional set of tags for categorization.
            status: Status of the question (open, resolved, abandoned).
            priority: Priority level (0-10).
            
        Returns:
            ID of the created research question.
        """
        research_question = ResearchQuestion(
            question=question,
            description=description,
            tags=tags or set(),
            status=status,
            priority=priority
        )
        
        self.storage.save(research_question)
        
        # Update the knowledge graph
        self._knowledge_graph.add_node(str(research_question.id), type='question', title=question)
        
        return research_question.id
    
    def add_evidence_to_question(self, question_id: UUID, note_id: UUID, 
                               evidence_type: Union[str, EvidenceType], 
                               strength: Union[str, EvidenceStrength], 
                               description: Optional[str] = None,
                               citation_ids: Optional[List[UUID]] = None) -> Optional[UUID]:
        """Add evidence to a research question.
        
        Args:
            question_id: ID of the research question.
            note_id: ID of the note containing the evidence.
            evidence_type: Type of evidence (supporting, contradicting, etc.).
            strength: Strength of the evidence.
            description: Optional description of the evidence.
            citation_ids: Optional list of citation IDs supporting this evidence.
            
        Returns:
            ID of the created evidence if successful, None otherwise.
        """
        question = self.storage.get(ResearchQuestion, question_id)
        note = self.storage.get(Note, note_id)
        
        if not question or not note:
            return None
        
        # Convert string values to enum values if needed
        if isinstance(evidence_type, str):
            evidence_type = EvidenceType(evidence_type)
        
        if isinstance(strength, str):
            strength = EvidenceStrength(strength)
        
        evidence = Evidence(
            note_id=note_id,
            evidence_type=evidence_type,
            strength=strength,
            description=description,
            citation_ids=citation_ids or []
        )
        
        question.evidence.append(evidence)
        question.update()
        self.storage.save(question)
        
        # Update the knowledge graph
        self._knowledge_graph.add_edge(
            str(question_id), 
            str(note_id), 
            type='evidence',
            evidence_type=evidence_type,
            strength=strength
        )
        
        return evidence.id
    
    def create_experiment(self, title: str, hypothesis: str, methodology: str, 
                        status: Union[str, ExperimentStatus] = ExperimentStatus.PLANNED,
                        tags: Optional[Set[str]] = None, 
                        research_question_id: Optional[UUID] = None,
                        **kwargs) -> UUID:
        """Create a new experiment.
        
        Args:
            title: Title of the experiment.
            hypothesis: The hypothesis being tested.
            methodology: Description of the methodology.
            status: Status of the experiment.
            tags: Optional set of tags for categorization.
            research_question_id: Optional ID of the related research question.
            **kwargs: Additional experiment metadata.
            
        Returns:
            ID of the created experiment.
        """
        if isinstance(status, str):
            status = ExperimentStatus(status)
        
        experiment = Experiment(
            title=title,
            hypothesis=hypothesis,
            methodology=methodology,
            status=status,
            tags=tags or set(),
            research_question_id=research_question_id,
            **kwargs
        )
        
        self.storage.save(experiment)
        
        # Update the knowledge graph
        self._knowledge_graph.add_node(str(experiment.id), type='experiment', title=title)
        
        if research_question_id:
            self._knowledge_graph.add_edge(str(experiment.id), str(research_question_id), type='investigates')
        
        return experiment.id
    
    def create_grant_proposal(self, title: str, funding_agency: str, description: str,
                            deadline: Optional[datetime] = None,
                            status: Union[str, GrantStatus] = GrantStatus.DRAFTING,
                            tags: Optional[Set[str]] = None,
                            **kwargs) -> UUID:
        """Create a new grant proposal workspace.
        
        Args:
            title: Title of the proposal.
            funding_agency: Name of the funding agency.
            description: Description of the proposal.
            deadline: Optional submission deadline.
            status: Status of the proposal.
            tags: Optional set of tags for categorization.
            **kwargs: Additional grant metadata.
            
        Returns:
            ID of the created grant proposal.
        """
        if isinstance(status, str):
            status = GrantStatus(status)
        
        grant = GrantProposal(
            title=title,
            funding_agency=funding_agency,
            description=description,
            deadline=deadline,
            status=status,
            tags=tags or set(),
            **kwargs
        )
        
        self.storage.save(grant)
        
        # Update the knowledge graph
        self._knowledge_graph.add_node(str(grant.id), type='grant', title=title)
        
        return grant.id
    
    def add_to_grant_workspace(self, grant_id: UUID, 
                             note_ids: Optional[List[UUID]] = None,
                             experiment_ids: Optional[List[UUID]] = None,
                             question_ids: Optional[List[UUID]] = None) -> bool:
        """Add items to a grant proposal workspace.
        
        Args:
            grant_id: ID of the grant proposal.
            note_ids: Optional list of note IDs to add.
            experiment_ids: Optional list of experiment IDs to add.
            question_ids: Optional list of research question IDs to add.
            
        Returns:
            True if successful, False if the grant wasn't found.
        """
        grant = self.storage.get(GrantProposal, grant_id)
        
        if not grant:
            return False
        
        if note_ids:
            for note_id in note_ids:
                if note_id not in grant.notes and self.storage.get(Note, note_id):
                    grant.notes.append(note_id)
                    # Update the knowledge graph
                    self._knowledge_graph.add_edge(str(grant_id), str(note_id), type='includes')
        
        if experiment_ids:
            for experiment_id in experiment_ids:
                if experiment_id not in grant.experiments and self.storage.get(Experiment, experiment_id):
                    grant.experiments.append(experiment_id)
                    # Update the knowledge graph
                    self._knowledge_graph.add_edge(str(grant_id), str(experiment_id), type='proposes')
        
        if question_ids:
            for question_id in question_ids:
                if question_id not in grant.research_questions and self.storage.get(ResearchQuestion, question_id):
                    grant.research_questions.append(question_id)
                    # Update the knowledge graph
                    self._knowledge_graph.add_edge(str(grant_id), str(question_id), type='addresses')

        grant.update()
        self.storage.save(grant)
        return True

    def update_experiment(self, experiment_id: UUID, **kwargs) -> bool:
        """Update an existing experiment.

        Args:
            experiment_id: ID of the experiment to update.
            **kwargs: Fields to update.

        Returns:
            True if the experiment was updated, False if it wasn't found.
        """
        experiment = self.storage.get(Experiment, experiment_id)
        if not experiment:
            return False

        updated = False

        # Update research question link if provided
        if 'research_question_id' in kwargs and kwargs['research_question_id'] != experiment.research_question_id:
            old_question_id = experiment.research_question_id
            new_question_id = kwargs['research_question_id']

            # Update the experiment
            experiment.research_question_id = new_question_id
            updated = True

            # Update the knowledge graph
            if old_question_id and self._knowledge_graph.has_edge(str(experiment_id), str(old_question_id)):
                self._knowledge_graph.remove_edge(str(experiment_id), str(old_question_id))

            if new_question_id:
                self._knowledge_graph.add_edge(str(experiment_id), str(new_question_id), type='investigates')

        # Update other fields as needed
        for field, value in kwargs.items():
            if field != 'research_question_id' and hasattr(experiment, field) and getattr(experiment, field) != value:
                setattr(experiment, field, value)
                updated = True

        if updated:
            experiment.update()
            self.storage.save(experiment)

        return True

    def add_notes_to_experiment(self, experiment_id: UUID, note_ids: List[UUID]) -> bool:
        """Add notes to an experiment.

        Args:
            experiment_id: ID of the experiment.
            note_ids: List of note IDs to add.

        Returns:
            True if successful, False if the experiment wasn't found.
        """
        experiment = self.storage.get(Experiment, experiment_id)
        if not experiment:
            return False

        for note_id in note_ids:
            if note_id not in experiment.notes and self.storage.get(Note, note_id):
                experiment.notes.append(note_id)

                # Update the knowledge graph
                self._knowledge_graph.add_edge(str(experiment_id), str(note_id), type='documents')

        experiment.update()
        self.storage.save(experiment)
        return True

    def create_collaborator(self, name: str, email: Optional[str] = None,
                          affiliation: Optional[str] = None,
                          role: Union[str, CollaboratorRole] = CollaboratorRole.COLLABORATOR) -> UUID:
        """Create a new collaborator.
        
        Args:
            name: Name of the collaborator.
            email: Optional email address.
            affiliation: Optional institutional affiliation.
            role: Role of the collaborator.
            
        Returns:
            ID of the created collaborator.
        """
        if isinstance(role, str):
            role = CollaboratorRole(role)
        
        collaborator = Collaborator(
            name=name,
            email=email,
            affiliation=affiliation,
            role=role
        )
        
        self.storage.save(collaborator)
        return collaborator.id
    
    def add_annotation(self, node_id: UUID, collaborator_id: UUID, content: str,
                     position: Optional[str] = None) -> Optional[UUID]:
        """Add an annotation to a knowledge node.
        
        Args:
            node_id: ID of the knowledge node to annotate.
            collaborator_id: ID of the collaborator making the annotation.
            content: Content of the annotation.
            position: Optional position information (e.g., for PDF annotations).
            
        Returns:
            ID of the created annotation if successful, None otherwise.
        """
        # Check that the knowledge node exists
        if not self._node_exists(node_id):
            return None
        
        # Check that the collaborator exists
        collaborator = self.storage.get(Collaborator, collaborator_id)
        if not collaborator:
            return None
        
        annotation = Annotation(
            node_id=node_id,
            collaborator_id=collaborator_id,
            content=content,
            position=position
        )
        
        self.storage.save(annotation)
        return annotation.id
    
    def get_annotations_for_node(self, node_id: UUID) -> List[Annotation]:
        """Get all annotations for a specific knowledge node.
        
        Args:
            node_id: ID of the knowledge node.
            
        Returns:
            List of annotations for the node.
        """
        return self.storage.query(Annotation, node_id=node_id)
    
    def import_collaborator_annotations(self, collaborator_id: UUID, annotations_file: Union[str, Path]) -> int:
        """Import annotations from a collaborator's file.
        
        Args:
            collaborator_id: ID of the collaborator.
            annotations_file: Path to the annotations file.
            
        Returns:
            Number of annotations successfully imported.
        """
        import json
        
        file_path = Path(annotations_file)
        if not file_path.exists():
            return 0
        
        collaborator = self.storage.get(Collaborator, collaborator_id)
        if not collaborator:
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            for item in data:
                if 'node_id' in item and 'content' in item:
                    try:
                        node_id = UUID(item['node_id'])
                        if self._node_exists(node_id):
                            annotation = Annotation(
                                node_id=node_id,
                                collaborator_id=collaborator_id,
                                content=item['content'],
                                position=item.get('position')
                            )
                            self.storage.save(annotation)
                            count += 1
                    except (ValueError, TypeError):
                        # Invalid UUID format, skip this item
                        continue
            
            return count
        except (json.JSONDecodeError, IOError):
            return 0
    
    def search(self, query: str, node_types: Optional[List[str]] = None) -> Dict[str, List[Any]]:
        """Search for knowledge nodes containing a specific text.
        
        Args:
            query: The search query.
            node_types: Optional list of node types to search (notes, citations, questions, etc.).
            
        Returns:
            Dictionary with node types as keys and lists of matching nodes as values.
        """
        results = {}
        
        if node_types is None or 'notes' in node_types:
            notes = self.storage.search_text(Note, query, ['title', 'content'])
            results['notes'] = notes
        
        if node_types is None or 'citations' in node_types:
            citations = self.storage.search_text(Citation, query, ['title', 'abstract', 'authors'])
            results['citations'] = citations
        
        if node_types is None or 'questions' in node_types:
            questions = self.storage.search_text(ResearchQuestion, query, ['question', 'description'])
            results['questions'] = questions
        
        if node_types is None or 'experiments' in node_types:
            experiments = self.storage.search_text(Experiment, query, ['title', 'hypothesis', 'methodology', 'results', 'conclusion'])
            results['experiments'] = experiments
        
        if node_types is None or 'grants' in node_types:
            grants = self.storage.search_text(GrantProposal, query, ['title', 'description', 'funding_agency'])
            results['grants'] = grants
        
        return results
    
    def get_related_nodes(self, node_id: UUID, relation_types: Optional[List[str]] = None) -> Dict[str, List[Any]]:
        """Get nodes related to a specific knowledge node.
        
        Args:
            node_id: ID of the knowledge node.
            relation_types: Optional list of relation types to include.
            
        Returns:
            Dictionary with relation types as keys and lists of related nodes as values.
        """
        if not self._knowledge_graph.has_node(str(node_id)):
            return {}
        
        results = {}
        
        # Get outgoing edges (relations from this node to others)
        # Use out_edges to get edges where this node is the source
        for source, target, data in self._knowledge_graph.out_edges(str(node_id), data=True):
            relation_type = data.get('type')
            if relation_types is None or relation_type in relation_types:
                if relation_type not in results:
                    results[relation_type] = []

                # Get the actual node object
                node_type = self._knowledge_graph.nodes[target].get('type')
                if node_type == 'note':
                    node = self.storage.get(Note, UUID(target))
                elif node_type == 'citation':
                    node = self.storage.get(Citation, UUID(target))
                elif node_type == 'question':
                    node = self.storage.get(ResearchQuestion, UUID(target))
                elif node_type == 'experiment':
                    node = self.storage.get(Experiment, UUID(target))
                elif node_type == 'grant':
                    node = self.storage.get(GrantProposal, UUID(target))
                else:
                    continue

                if node:
                    results[relation_type].append(node)
        
        # Get incoming edges (relations from others to this node)
        incoming_edges = []
        for source in self._knowledge_graph.predecessors(str(node_id)):
            data = self._knowledge_graph.edges[source, str(node_id)]
            relation_type = data.get('type')
            if relation_types is None or relation_type in relation_types:
                incoming_type = f"incoming_{relation_type}"
                if incoming_type not in results:
                    results[incoming_type] = []
                
                # Get the actual node object
                node_type = self._knowledge_graph.nodes[source].get('type')
                if node_type == 'note':
                    node = self.storage.get(Note, UUID(source))
                elif node_type == 'citation':
                    node = self.storage.get(Citation, UUID(source))
                elif node_type == 'question':
                    node = self.storage.get(ResearchQuestion, UUID(source))
                elif node_type == 'experiment':
                    node = self.storage.get(Experiment, UUID(source))
                elif node_type == 'grant':
                    node = self.storage.get(GrantProposal, UUID(source))
                else:
                    continue
                
                if node:
                    results[incoming_type].append(node)
        
        return results
    
    def generate_citation(self, citation_id: UUID, format: Union[str, CitationFormat]) -> Optional[str]:
        """Generate a formatted citation.
        
        Args:
            citation_id: ID of the citation.
            format: Desired citation format.
            
        Returns:
            Formatted citation string if successful, None otherwise.
        """
        from researchbrain.citations.formatters import format_citation
        
        citation = self.storage.get(Citation, citation_id)
        if not citation:
            return None
        
        if isinstance(format, str):
            format = CitationFormat(format)
        
        return format_citation(citation, format)
    
    def export_grant_proposal(self, grant_id: UUID, output_path: Union[str, Path]) -> bool:
        """Export a grant proposal to a structured document.
        
        Args:
            grant_id: ID of the grant proposal.
            output_path: Path where the document will be saved.
            
        Returns:
            True if the export was successful, False otherwise.
        """
        from researchbrain.grants.export import export_proposal
        
        grant = self.storage.get(GrantProposal, grant_id)
        if not grant:
            return False
        
        # Collect all related items
        notes = [self.storage.get(Note, note_id) for note_id in grant.notes if self.storage.get(Note, note_id)]
        experiments = [self.storage.get(Experiment, exp_id) for exp_id in grant.experiments if self.storage.get(Experiment, exp_id)]
        questions = [self.storage.get(ResearchQuestion, q_id) for q_id in grant.research_questions if self.storage.get(ResearchQuestion, q_id)]
        
        return export_proposal(grant, notes, experiments, questions, output_path)
    
    def create_experiment_from_template(self, template_name: str, **values) -> Optional[UUID]:
        """Create a new experiment from a template.
        
        Args:
            template_name: Name of the experiment template.
            **values: Values to fill in the template.
            
        Returns:
            ID of the created experiment if successful, None otherwise.
        """
        from researchbrain.experiments.templates import get_template, apply_template
        
        template = get_template(template_name)
        if not template:
            return None
        
        experiment_data = apply_template(template, values)
        if not experiment_data:
            return None
        
        return self.create_experiment(**experiment_data)
    
    def backup_knowledge_base(self, backup_dir: Union[str, Path]) -> Optional[Path]:
        """Create a backup of the entire knowledge base.

        Args:
            backup_dir: Directory where the backup will be stored.

        Returns:
            Path to the backup if successful, None otherwise.
        """
        # Make sure the backup directory exists
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        try:
            return self.storage.backup(backup_dir)
        except Exception as e:
            print(f"Backup error: {e}")
            return None
    
    def restore_from_backup(self, backup_path: Union[str, Path]) -> bool:
        """Restore the knowledge base from a backup.
        
        Args:
            backup_path: Path to the backup directory.
            
        Returns:
            True if the restore was successful, False otherwise.
        """
        try:
            self.storage.restore(backup_path)
            self._build_knowledge_graph()  # Rebuild the knowledge graph
            return True
        except Exception:
            return False
    
    def _extract_citation_keys(self, text: str) -> List[str]:
        """Extract citation keys from text.
        
        Args:
            text: Text to search for citation keys.
            
        Returns:
            List of citation keys found in the text.
        """
        # Look for citation keys in the format [@key] or @key
        keys = []
        
        # Pattern for [@key] format
        pattern1 = r'\[@([^\]]+)\]'
        matches1 = re.findall(pattern1, text)
        keys.extend(matches1)
        
        # Pattern for @key format
        pattern2 = r'(?<!\[)@(\w+)'
        matches2 = re.findall(pattern2, text)
        keys.extend(matches2)
        
        return list(set(keys))  # Remove duplicates
    
    def _find_citation_by_key(self, key: str) -> Optional[UUID]:
        """Find a citation by its key.
        
        Args:
            key: Citation key to search for.
            
        Returns:
            ID of the citation if found, None otherwise.
        """
        # First try to find by DOI
        citations = self.storage.query(Citation, doi=key)
        if citations:
            return citations[0].id
        
        # Then try by BibTeX key in the BibTeX data
        all_citations = self.storage.list_all(Citation)
        for citation in all_citations:
            if citation.bibtex and key in citation.bibtex:
                return citation.id
        
        # Finally, try to match by last name and year
        if key and len(key) > 4:
            # Assuming key format is something like "smith2023"
            # Try to extract name and year
            match = re.match(r'([a-z]+)(\d{4})', key.lower())
            if match:
                name, year = match.groups()
                year_int = int(year)
                
                for citation in all_citations:
                    if citation.year == year_int:
                        # Check if any author's last name matches
                        for author in citation.authors:
                            last_name = author.split(',')[0] if ',' in author else author.split()[-1]
                            if name.lower() == last_name.lower():
                                return citation.id
        
        return None
    
    def _node_exists(self, node_id: UUID) -> bool:
        """Check if a knowledge node exists.
        
        Args:
            node_id: ID of the node to check.
            
        Returns:
            True if the node exists, False otherwise.
        """
        # Check all possible node types
        if self.storage.get(Note, node_id):
            return True
        if self.storage.get(Citation, node_id):
            return True
        if self.storage.get(ResearchQuestion, node_id):
            return True
        if self.storage.get(Experiment, node_id):
            return True
        if self.storage.get(GrantProposal, node_id):
            return True
        
        return False