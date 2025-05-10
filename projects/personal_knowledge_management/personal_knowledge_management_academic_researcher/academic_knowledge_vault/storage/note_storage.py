"""
Note storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for notes and note collections.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.note import Note, NoteCollection
from academic_knowledge_vault.storage.base import JsonFileStorage


class NoteStorage(JsonFileStorage[Note]):
    """Storage for research notes."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize note storage.
        
        Args:
            base_dir: Base directory for note storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, Note, create_dir)
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for notes with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, notes must have all tags; if False, any tag is sufficient
            
        Returns:
            List of note IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for note_id in self.list_ids():
            try:
                note = self.get(note_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in note.tags for tag in tags):
                        result_ids.append(note_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in note.tags for tag in tags):
                        result_ids.append(note_id)
                    
            except Exception:
                # Skip problematic notes
                continue
        
        return result_ids
    
    def search_by_content(self, text: str) -> List[str]:
        """
        Search for notes containing specific text.
        
        Args:
            text: Text to search for
            
        Returns:
            List of note IDs containing the text
        """
        text = text.lower()
        result_ids = []
        
        for note_id in self.list_ids():
            try:
                note = self.get(note_id)
                
                # Check title
                if text in note.title.lower():
                    result_ids.append(note_id)
                    continue
                
                # Check content
                if hasattr(note, 'content') and note.content and hasattr(note.content, 'content'):
                    if text in note.content.content.lower():
                        result_ids.append(note_id)
                        continue
                
            except Exception:
                # Skip problematic notes
                continue
        
        return result_ids
    
    def search_by_citation_key(self, citation_key: str) -> List[str]:
        """
        Search for notes referencing a specific citation key.
        
        Args:
            citation_key: Citation key to search for
            
        Returns:
            List of note IDs referencing the citation key
        """
        result_ids = []
        
        for note_id in self.list_ids():
            try:
                note = self.get(note_id)
                
                if citation_key in note.citation_keys:
                    result_ids.append(note_id)
                    
            except Exception:
                # Skip problematic notes
                continue
        
        return result_ids
    
    def get_notes_by_project(self, project: str) -> List[str]:
        """
        Get notes belonging to a specific project.
        
        Args:
            project: Project name
            
        Returns:
            List of note IDs belonging to the project
        """
        result_ids = []
        
        for note_id in self.list_ids():
            try:
                note = self.get(note_id)
                
                if note.project == project:
                    result_ids.append(note_id)
                    
            except Exception:
                # Skip problematic notes
                continue
        
        return result_ids
    
    def get_notes_by_path(self, path_components: List[str]) -> List[str]:
        """
        Get notes at a specific path in the hierarchy.
        
        Args:
            path_components: List of path components
            
        Returns:
            List of note IDs at the specified path
        """
        if not path_components:
            return []
        
        result_ids = []
        
        for note_id in self.list_ids():
            try:
                note = self.get(note_id)
                
                if note.path == path_components:
                    result_ids.append(note_id)
                    
            except Exception:
                # Skip problematic notes
                continue
        
        return result_ids
    
    def get_child_notes(self, parent_id: str) -> List[str]:
        """
        Get notes that have a specific parent note.
        
        Args:
            parent_id: ID of the parent note
            
        Returns:
            List of child note IDs
        """
        result_ids = []
        
        for note_id in self.list_ids():
            try:
                note = self.get(note_id)
                
                if note.parent_id == parent_id:
                    result_ids.append(note_id)
                    
            except Exception:
                # Skip problematic notes
                continue
        
        return result_ids
    
    def export_to_markdown(self, note_id: str, target_dir: Union[str, Path]) -> Path:
        """
        Export a note to a Markdown file.
        
        Args:
            note_id: ID of the note to export
            target_dir: Directory to export to
            
        Returns:
            Path to the exported file
            
        Raises:
            ItemNotFoundError: If the note is not found
        """
        note = self.get(note_id)
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        file_path = target_path / f"{note_id}.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Write title as heading
            f.write(f"# {note.title}\n\n")
            
            # Write metadata
            f.write(f"**Created:** {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Updated:** {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if note.tags:
                f.write(f"**Tags:** {', '.join(note.tags)}\n")
            
            if note.citation_keys:
                f.write(f"**Citations:** {', '.join(note.citation_keys)}\n")
            
            f.write("\n---\n\n")
            
            # Write content
            if hasattr(note, 'content') and note.content and hasattr(note.content, 'content'):
                f.write(note.content.content)
        
        return file_path


class NoteCollectionStorage(JsonFileStorage[NoteCollection]):
    """Storage for note collections."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize note collection storage.
        
        Args:
            base_dir: Base directory for collection storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, NoteCollection, create_dir)
    
    def get_collections_containing_note(self, note_id: str) -> List[str]:
        """
        Find collections that contain a specific note.
        
        Args:
            note_id: ID of the note
            
        Returns:
            List of collection IDs containing the note
        """
        result_ids = []
        
        for collection_id in self.list_ids():
            try:
                collection = self.get(collection_id)
                
                if note_id in collection.note_ids:
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