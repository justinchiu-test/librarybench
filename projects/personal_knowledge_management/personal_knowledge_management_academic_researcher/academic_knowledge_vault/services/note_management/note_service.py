"""
Note management service for the Academic Knowledge Vault system.

This module provides functionality for creating, updating, and organizing research notes.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType, Reference, LinkedItem
from academic_knowledge_vault.models.note import Note, NoteContent, NoteCollection, NoteType
from academic_knowledge_vault.storage.note_storage import NoteStorage, NoteCollectionStorage


class CitationExtractor:
    """Utility class for extracting citation keys from note content."""
    
    # Regular expression pattern for citation keys in markdown text
    # This pattern matches:
    # - @citation_key
    # - [@citation_key]
    # - [@citation_key, p. 123]
    # - Multiple citation keys: [@key1; @key2]
    CITATION_KEY_PATTERN = r'@([a-zA-Z0-9_-]+)|\[@([a-zA-Z0-9_-]+)(?:;\s*@([a-zA-Z0-9_-]+))*\]'
    
    @classmethod
    def extract_citation_keys(cls, text: str) -> Set[str]:
        """
        Extract citation keys from text.
        
        Args:
            text: Text to extract citation keys from
            
        Returns:
            Set of extracted citation keys
        """
        keys = set()
        
        # Find all matches of the citation key pattern
        for match in re.finditer(cls.CITATION_KEY_PATTERN, text):
            # Add direct @citation_key matches
            if match.group(1):
                keys.add(match.group(1))
            
            # Add citation keys from [@key] format
            for i in range(2, len(match.groups()) + 1):
                if match.group(i):
                    keys.add(match.group(i))
        
        return keys
    
    # Regular expression pattern for DOIs in text
    DOI_PATTERN = r'(?:doi:|DOI:|https?://doi\.org/)?(10\.\d{4,}(?:\.\d+)*\/(?:(?!["&\'])\S)+)'

    @classmethod
    def extract_dois(cls, text: str) -> Set[str]:
        """
        Extract DOIs from text.

        Args:
            text: Text to extract DOIs from

        Returns:
            Set of extracted DOIs
        """
        dois = set()

        # Find all matches of the DOI pattern
        for match in re.finditer(cls.DOI_PATTERN, text):
            if match.group(1):
                # Remove trailing periods which might be part of sentences
                doi = match.group(1)
                if doi.endswith('.'):
                    doi = doi[:-1]
                dois.add(doi)

        return dois


class NoteService:
    """Service for managing research notes."""
    
    def __init__(self, 
                 note_storage: NoteStorage,
                 collection_storage: NoteCollectionStorage):
        """
        Initialize the note service.
        
        Args:
            note_storage: Storage for individual notes
            collection_storage: Storage for note collections
        """
        self.note_storage = note_storage
        self.collection_storage = collection_storage
    
    def create_note(self, 
                   title: str,
                   content: str,
                   note_type: Union[str, NoteType] = NoteType.CONCEPT,
                   tags: Optional[List[str]] = None,
                   parent_id: Optional[str] = None,
                   project: Optional[str] = None,
                   path: Optional[List[str]] = None) -> str:
        """
        Create a new research note.
        
        Args:
            title: Note title
            content: Note content
            note_type: Type of note
            tags: Tags for the note
            parent_id: ID of parent note
            project: Project the note belongs to
            path: Path components for hierarchical organization
            
        Returns:
            ID of the created note
            
        Raises:
            ValueError: If a parent note is specified but doesn't exist
        """
        # Validate parent note if specified
        if parent_id and not self.note_storage.exists(parent_id):
            raise ValueError(f"Parent note with ID {parent_id} does not exist")
        
        # Handle string note type
        if isinstance(note_type, str):
            note_type = NoteType(note_type)
        
        # Extract citation keys from content
        citation_keys = CitationExtractor.extract_citation_keys(content)
        
        # Extract DOIs from content
        doi_references = CitationExtractor.extract_dois(content)
        
        # Create the note
        note = Note(
            title=title,
            content=NoteContent(content=content, format="markdown"),
            type=note_type,
            tags=set(tags or []),
            parent_id=parent_id,
            project=project,
            path=path or [],
            citation_keys=citation_keys,
            doi_references=doi_references
        )
        
        # Save the note
        note_id = self.note_storage.save(note)
        
        return note_id
    
    def update_note(self,
                   note_id: str,
                   title: Optional[str] = None,
                   content: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   add_tags: Optional[List[str]] = None,
                   remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing note.
        
        Args:
            note_id: ID of the note to update
            title: New title (if None, keep existing)
            content: New content (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the note doesn't exist
        """
        if not self.note_storage.exists(note_id):
            raise ValueError(f"Note with ID {note_id} does not exist")
        
        note = self.note_storage.get(note_id)
        
        # Update title if provided
        if title is not None:
            note.title = title
        
        # Update content if provided
        if content is not None:
            # Extract citation keys and DOIs from new content
            citation_keys = CitationExtractor.extract_citation_keys(content)
            doi_references = CitationExtractor.extract_dois(content)
            
            # Update the content
            note.update_content(content)
            
            # Update citation keys and DOIs
            note.citation_keys = citation_keys
            note.doi_references = doi_references
        
        # Update tags if provided
        if tags is not None:
            note.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            note.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            note.tags.difference_update(remove_tags)
        
        # Save the updated note
        self.note_storage.save(note)
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.
        
        Args:
            note_id: ID of the note to delete
            
        Returns:
            True if the note was deleted, False if it didn't exist
        """
        return self.note_storage.delete(note_id)
    
    def get_note(self, note_id: str) -> Note:
        """
        Get a note by ID.
        
        Args:
            note_id: ID of the note to retrieve
            
        Returns:
            The requested note
            
        Raises:
            ValueError: If the note doesn't exist
        """
        if not self.note_storage.exists(note_id):
            raise ValueError(f"Note with ID {note_id} does not exist")
        
        return self.note_storage.get(note_id)
    
    def add_reference(self, 
                     note_id: str, 
                     referenced_item_id: str,
                     item_type: KnowledgeItemType,
                     context: Optional[str] = None) -> None:
        """
        Add a reference from a note to another knowledge item.
        
        Args:
            note_id: ID of the note
            referenced_item_id: ID of the referenced item
            item_type: Type of the referenced item
            context: Optional context for the reference
            
        Raises:
            ValueError: If the note doesn't exist
        """
        if not self.note_storage.exists(note_id):
            raise ValueError(f"Note with ID {note_id} does not exist")
        
        note = self.note_storage.get(note_id)
        
        reference = Reference(
            item_id=referenced_item_id,
            item_type=item_type,
            context=context
        )
        
        note.add_reference(reference)
        self.note_storage.save(note)
    
    def remove_reference(self, note_id: str, referenced_item_id: str) -> None:
        """
        Remove a reference from a note.
        
        Args:
            note_id: ID of the note
            referenced_item_id: ID of the referenced item
            
        Raises:
            ValueError: If the note doesn't exist
        """
        if not self.note_storage.exists(note_id):
            raise ValueError(f"Note with ID {note_id} does not exist")
        
        note = self.note_storage.get(note_id)
        note.remove_reference(referenced_item_id)
        self.note_storage.save(note)
    
    def add_link(self,
                source_id: str,
                target_id: str,
                relationship_type: str,
                strength: float = 1.0,
                context: Optional[str] = None) -> None:
        """
        Add a bidirectional link between two notes.
        
        Args:
            source_id: ID of the source note
            target_id: ID of the target note
            relationship_type: Type of relationship
            strength: Strength of the relationship (0.0 to 1.0)
            context: Optional context for the link
            
        Raises:
            ValueError: If either note doesn't exist
        """
        if not self.note_storage.exists(source_id):
            raise ValueError(f"Source note with ID {source_id} does not exist")
        
        if not self.note_storage.exists(target_id):
            raise ValueError(f"Target note with ID {target_id} does not exist")
        
        source_note = self.note_storage.get(source_id)
        target_note = self.note_storage.get(target_id)
        
        # Create the bidirectional link
        source_to_target = LinkedItem(
            source_id=source_id,
            target_id=target_id,
            source_type=KnowledgeItemType.NOTE,
            target_type=KnowledgeItemType.NOTE,
            relationship_type=relationship_type,
            strength=strength,
            context=context
        )
        
        target_to_source = LinkedItem(
            source_id=target_id,
            target_id=source_id,
            source_type=KnowledgeItemType.NOTE,
            target_type=KnowledgeItemType.NOTE,
            relationship_type=relationship_type,
            strength=strength,
            context=context
        )
        
        # Add links to both notes
        source_note.add_linked_item(source_to_target)
        target_note.add_linked_item(target_to_source)
        
        # Save both notes
        self.note_storage.save(source_note)
        self.note_storage.save(target_note)
    
    def remove_link(self, source_id: str, target_id: str) -> None:
        """
        Remove a bidirectional link between two notes.
        
        Args:
            source_id: ID of the source note
            target_id: ID of the target note
            
        Raises:
            ValueError: If either note doesn't exist
        """
        if not self.note_storage.exists(source_id):
            raise ValueError(f"Source note with ID {source_id} does not exist")
        
        if not self.note_storage.exists(target_id):
            raise ValueError(f"Target note with ID {target_id} does not exist")
        
        source_note = self.note_storage.get(source_id)
        target_note = self.note_storage.get(target_id)
        
        # Remove links from both notes
        source_note.remove_linked_item(target_id)
        target_note.remove_linked_item(source_id)
        
        # Save both notes
        self.note_storage.save(source_note)
        self.note_storage.save(target_note)
    
    def create_collection(self,
                         name: str,
                         description: Optional[str] = None,
                         note_ids: Optional[List[str]] = None,
                         tags: Optional[List[str]] = None) -> str:
        """
        Create a note collection.
        
        Args:
            name: Collection name
            description: Collection description
            note_ids: IDs of notes to include
            tags: Tags for the collection
            
        Returns:
            ID of the created collection
            
        Raises:
            ValueError: If any of the specified notes don't exist
        """
        # Validate note IDs if provided
        if note_ids:
            for note_id in note_ids:
                if not self.note_storage.exists(note_id):
                    raise ValueError(f"Note with ID {note_id} does not exist")
        
        # Create the collection
        collection = NoteCollection(
            name=name,
            description=description,
            note_ids=set(note_ids or []),
            tags=set(tags or [])
        )
        
        # Save the collection
        collection_id = self.collection_storage.save(collection)
        
        return collection_id
    
    def add_note_to_collection(self, collection_id: str, note_id: str) -> None:
        """
        Add a note to a collection.
        
        Args:
            collection_id: ID of the collection
            note_id: ID of the note to add
            
        Raises:
            ValueError: If the collection or note doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        if not self.note_storage.exists(note_id):
            raise ValueError(f"Note with ID {note_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.add_note(note_id)
        self.collection_storage.save(collection)
    
    def remove_note_from_collection(self, collection_id: str, note_id: str) -> None:
        """
        Remove a note from a collection.
        
        Args:
            collection_id: ID of the collection
            note_id: ID of the note to remove
            
        Raises:
            ValueError: If the collection doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.remove_note(note_id)
        self.collection_storage.save(collection)
    
    def get_collection(self, collection_id: str) -> NoteCollection:
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
    
    def search_notes(self,
                    text: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    note_type: Optional[Union[str, NoteType]] = None,
                    project: Optional[str] = None,
                    citation_key: Optional[str] = None,
                    doi: Optional[str] = None) -> List[str]:
        """
        Search for notes based on various criteria.
        
        Args:
            text: Text to search for in note title and content
            tags: Tags to filter by
            note_type: Type of notes to filter by
            project: Project to filter by
            citation_key: Citation key to filter by
            doi: DOI to filter by
            
        Returns:
            List of matching note IDs
        """
        # Start with all notes
        result_ids = set(self.note_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.note_storage.search_by_content(text))
            result_ids.intersection_update(text_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.note_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by type if specified
        if note_type:
            if isinstance(note_type, str):
                note_type = NoteType(note_type)
            
            type_results = set()
            for note_id in result_ids:
                try:
                    note = self.note_storage.get(note_id)
                    if note.type == note_type:
                        type_results.add(note_id)
                except Exception:
                    continue
            
            result_ids.intersection_update(type_results)
        
        # Filter by project if specified
        if project:
            project_results = set(self.note_storage.get_notes_by_project(project))
            result_ids.intersection_update(project_results)
        
        # Filter by citation key if specified
        if citation_key:
            citation_results = set(self.note_storage.search_by_citation_key(citation_key))
            result_ids.intersection_update(citation_results)
        
        # Filter by DOI if specified
        if doi:
            doi_results = set()
            for note_id in result_ids:
                try:
                    note = self.note_storage.get(note_id)
                    if doi in note.doi_references:
                        doi_results.add(note_id)
                except Exception:
                    continue
            
            result_ids.intersection_update(doi_results)
        
        return list(result_ids)
    
    def export_notes_to_markdown(self, 
                                note_ids: List[str], 
                                export_dir: Union[str, Path]) -> List[Path]:
        """
        Export notes to Markdown files.
        
        Args:
            note_ids: IDs of notes to export
            export_dir: Directory to export to
            
        Returns:
            List of paths to exported files
            
        Raises:
            ValueError: If any of the specified notes don't exist
        """
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        for note_id in note_ids:
            if not self.note_storage.exists(note_id):
                raise ValueError(f"Note with ID {note_id} does not exist")
            
            file_path = self.note_storage.export_to_markdown(note_id, export_path)
            exported_files.append(file_path)
        
        return exported_files