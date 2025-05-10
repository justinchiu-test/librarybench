"""
Collaboration storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for annotations and collaboration sessions.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType
from academic_knowledge_vault.models.collaboration import (
    Annotation,
    AnnotationStatus,
    AnnotationType,
    CollaborationPermission,
    CollaborationSession,
    Collaborator,
    ImportedAnnotation,
)
from academic_knowledge_vault.storage.base import JsonFileStorage


class AnnotationStorage(JsonFileStorage[Annotation]):
    """Storage for annotations."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize annotation storage.
        
        Args:
            base_dir: Base directory for annotation storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, Annotation, create_dir)
    
    def get_by_author(self, author_id: str) -> List[str]:
        """
        Get annotations by a specific author.
        
        Args:
            author_id: ID of the author
            
        Returns:
            List of annotation IDs by the author
        """
        result_ids = []
        
        for annotation_id in self.list_ids():
            try:
                annotation = self.get(annotation_id)
                
                if annotation.author.id == author_id:
                    result_ids.append(annotation_id)
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids
    
    def get_by_status(self, status: Union[str, AnnotationStatus]) -> List[str]:
        """
        Get annotations with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of annotation IDs with the specified status
        """
        if isinstance(status, str):
            status = AnnotationStatus(status)
        
        result_ids = []
        
        for annotation_id in self.list_ids():
            try:
                annotation = self.get(annotation_id)
                
                if annotation.status == status:
                    result_ids.append(annotation_id)
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids
    
    def get_by_type(self, annotation_type: Union[str, AnnotationType]) -> List[str]:
        """
        Get annotations of a specific type.
        
        Args:
            annotation_type: Type to filter by
            
        Returns:
            List of annotation IDs of the specified type
        """
        if isinstance(annotation_type, str):
            annotation_type = AnnotationType(annotation_type)
        
        result_ids = []
        
        for annotation_id in self.list_ids():
            try:
                annotation = self.get(annotation_id)
                
                if annotation.annotation_type == annotation_type:
                    result_ids.append(annotation_id)
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids
    
    def get_by_target_item(self, target_id: str, target_type: Optional[KnowledgeItemType] = None) -> List[str]:
        """
        Get annotations for a specific target item.
        
        Args:
            target_id: ID of the target item
            target_type: Type of the target item (if None, don't filter by type)
            
        Returns:
            List of annotation IDs for the target item
        """
        result_ids = []
        
        for annotation_id in self.list_ids():
            try:
                annotation = self.get(annotation_id)
                
                if annotation.target_item_id == target_id:
                    if target_type is None or annotation.target_item_type == target_type:
                        result_ids.append(annotation_id)
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> List[str]:
        """
        Get annotations created within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of annotation IDs in the date range
        """
        result_ids = []
        
        for annotation_id in self.list_ids():
            try:
                annotation = self.get(annotation_id)
                
                created_at = annotation.created_at
                
                include = True
                
                if start_date and created_at < start_date:
                    include = False
                
                if end_date and created_at > end_date:
                    include = False
                
                if include:
                    result_ids.append(annotation_id)
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids
    
    def search_by_content(self, text: str) -> List[str]:
        """
        Search for annotations by content.
        
        Args:
            text: Text to search for in annotation content
            
        Returns:
            List of annotation IDs with matching content
        """
        text = text.lower()
        result_ids = []
        
        for annotation_id in self.list_ids():
            try:
                annotation = self.get(annotation_id)
                
                if text in annotation.content.lower():
                    result_ids.append(annotation_id)
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids
    
    def get_responses(self, annotation_id: str) -> List[str]:
        """
        Get responses to a specific annotation.
        
        Args:
            annotation_id: ID of the annotation
            
        Returns:
            List of annotation IDs that are responses to the specified annotation
        """
        result_ids = []
        
        for response_id in self.list_ids():
            try:
                response = self.get(response_id)
                
                for ref in response.references:
                    if ref.item_id == annotation_id and ref.item_type == KnowledgeItemType.ANNOTATION:
                        result_ids.append(response_id)
                        break
                    
            except Exception:
                # Skip problematic annotations
                continue
        
        return result_ids


class ImportedAnnotationStorage(JsonFileStorage[ImportedAnnotation]):
    """Storage for imported annotations."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize imported annotation storage.
        
        Args:
            base_dir: Base directory for imported annotation storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, ImportedAnnotation, create_dir)
    
    def get_by_original_id(self, original_id: str) -> Optional[str]:
        """
        Find an imported annotation by its original ID.
        
        Args:
            original_id: Original ID of the annotation
            
        Returns:
            ID of the imported annotation if found, None otherwise
        """
        for imported_id in self.list_ids():
            try:
                imported = self.get(imported_id)
                
                if imported.original_annotation_id == original_id:
                    return imported_id
                    
            except Exception:
                # Skip problematic imported annotations
                continue
        
        return None
    
    def get_by_integration_status(self, status: str) -> List[str]:
        """
        Get imported annotations with a specific integration status.
        
        Args:
            status: Integration status to filter by
            
        Returns:
            List of imported annotation IDs with the specified integration status
        """
        result_ids = []
        
        for imported_id in self.list_ids():
            try:
                imported = self.get(imported_id)
                
                if imported.integration_status == status:
                    result_ids.append(imported_id)
                    
            except Exception:
                # Skip problematic imported annotations
                continue
        
        return result_ids
    
    def get_by_importer(self, importer_id: str) -> List[str]:
        """
        Get annotations imported by a specific user.
        
        Args:
            importer_id: ID of the importer
            
        Returns:
            List of annotation IDs imported by the user
        """
        result_ids = []
        
        for imported_id in self.list_ids():
            try:
                imported = self.get(imported_id)
                
                if imported.importer_id == importer_id:
                    result_ids.append(imported_id)
                    
            except Exception:
                # Skip problematic imported annotations
                continue
        
        return result_ids
    
    def get_by_target_item(self, local_item_id: str) -> List[str]:
        """
        Get imported annotations for a specific local item.
        
        Args:
            local_item_id: ID of the local item
            
        Returns:
            List of imported annotation IDs for the local item
        """
        result_ids = []
        
        for imported_id in self.list_ids():
            try:
                imported = self.get(imported_id)
                
                if imported.local_item_id == local_item_id:
                    result_ids.append(imported_id)
                    
            except Exception:
                # Skip problematic imported annotations
                continue
        
        return result_ids
    
    def get_by_date_range(self, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> List[str]:
        """
        Get imported annotations within a specific date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of imported annotation IDs in the date range
        """
        result_ids = []
        
        for imported_id in self.list_ids():
            try:
                imported = self.get(imported_id)
                
                imported_at = imported.imported_at
                
                include = True
                
                if start_date and imported_at < start_date:
                    include = False
                
                if end_date and imported_at > end_date:
                    include = False
                
                if include:
                    result_ids.append(imported_id)
                    
            except Exception:
                # Skip problematic imported annotations
                continue
        
        return result_ids


class CollaborationSessionStorage(JsonFileStorage[CollaborationSession]):
    """Storage for collaboration sessions."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize collaboration session storage.
        
        Args:
            base_dir: Base directory for session storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, CollaborationSession, create_dir)
    
    def get_by_owner(self, owner_id: str) -> List[str]:
        """
        Get sessions owned by a specific user.
        
        Args:
            owner_id: ID of the owner
            
        Returns:
            List of session IDs owned by the user
        """
        result_ids = []
        
        for session_id in self.list_ids():
            try:
                session = self.get(session_id)
                
                if session.owner.id == owner_id:
                    result_ids.append(session_id)
                    
            except Exception:
                # Skip problematic sessions
                continue
        
        return result_ids
    
    def get_by_collaborator(self, collaborator_id: str) -> List[str]:
        """
        Get sessions that include a specific collaborator.
        
        Args:
            collaborator_id: ID of the collaborator
            
        Returns:
            List of session IDs including the collaborator
        """
        result_ids = []
        
        for session_id in self.list_ids():
            try:
                session = self.get(session_id)
                
                for collaborator in session.collaborators:
                    if collaborator.person.id == collaborator_id:
                        result_ids.append(session_id)
                        break
                    
            except Exception:
                # Skip problematic sessions
                continue
        
        return result_ids
    
    def get_by_status(self, status: str) -> List[str]:
        """
        Get sessions with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of session IDs with the specified status
        """
        result_ids = []
        
        for session_id in self.list_ids():
            try:
                session = self.get(session_id)
                
                if session.status == status:
                    result_ids.append(session_id)
                    
            except Exception:
                # Skip problematic sessions
                continue
        
        return result_ids
    
    def get_by_shared_item(self, item_id: str, item_type: Optional[KnowledgeItemType] = None) -> List[str]:
        """
        Get sessions that share a specific item.
        
        Args:
            item_id: ID of the shared item
            item_type: Type of the shared item (if None, don't filter by type)
            
        Returns:
            List of session IDs sharing the item
        """
        result_ids = []
        
        for session_id in self.list_ids():
            try:
                session = self.get(session_id)
                
                if item_id in session.shared_items:
                    if item_type is None or session.shared_items[item_id] == item_type:
                        result_ids.append(session_id)
                    
            except Exception:
                # Skip problematic sessions
                continue
        
        return result_ids
    
    def get_active_sessions(self) -> List[str]:
        """
        Get all active collaboration sessions.
        
        Returns:
            List of active session IDs
        """
        return self.get_by_status("active")
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for sessions with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, sessions must have all tags; if False, any tag is sufficient
            
        Returns:
            List of session IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for session_id in self.list_ids():
            try:
                session = self.get(session_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in session.tags for tag in tags):
                        result_ids.append(session_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in session.tags for tag in tags):
                        result_ids.append(session_id)
                    
            except Exception:
                # Skip problematic sessions
                continue
        
        return result_ids
    
    def search_by_name(self, text: str) -> List[str]:
        """
        Search for sessions by name.
        
        Args:
            text: Text to search for in session names
            
        Returns:
            List of session IDs with matching names
        """
        text = text.lower()
        result_ids = []
        
        for session_id in self.list_ids():
            try:
                session = self.get(session_id)
                
                if text in session.name.lower():
                    result_ids.append(session_id)
                    
            except Exception:
                # Skip problematic sessions
                continue
        
        return result_ids