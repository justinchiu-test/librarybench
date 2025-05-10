"""
Collaboration service for the Academic Knowledge Vault system.

This module provides functionality for collaborative annotations and knowledge sharing.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType, Person, Reference
from academic_knowledge_vault.models.collaboration import (
    Annotation,
    AnnotationStatus,
    AnnotationType,
    CollaborationPermission,
    CollaborationSession,
    Collaborator,
    ImportedAnnotation,
)
from academic_knowledge_vault.storage.collaboration_storage import (
    AnnotationStorage,
    ImportedAnnotationStorage,
    CollaborationSessionStorage,
)


class CollaborationService:
    """Service for managing collaborative annotations and sessions."""
    
    def __init__(self,
                annotation_storage: AnnotationStorage,
                imported_annotation_storage: ImportedAnnotationStorage,
                session_storage: CollaborationSessionStorage):
        """
        Initialize the collaboration service.
        
        Args:
            annotation_storage: Storage for annotations
            imported_annotation_storage: Storage for imported annotations
            session_storage: Storage for collaboration sessions
        """
        self.annotation_storage = annotation_storage
        self.imported_annotation_storage = imported_annotation_storage
        self.session_storage = session_storage
    
    def create_annotation(self,
                         content: str,
                         author: Dict[str, str],
                         target_item_id: str,
                         target_item_type: Union[str, KnowledgeItemType],
                         annotation_type: Union[str, AnnotationType] = AnnotationType.COMMENT,
                         target_context: Optional[str] = None,
                         references: Optional[List[Dict[str, Any]]] = None,
                         tags: Optional[List[str]] = None) -> str:
        """
        Create a new annotation.
        
        Args:
            content: Annotation content
            author: Author dictionary with 'name', optional 'email' and 'affiliation'
            target_item_id: ID of the target item
            target_item_type: Type of the target item
            annotation_type: Type of annotation
            target_context: Specific context within the target item
            references: List of reference dictionaries
            tags: Tags for the annotation
            
        Returns:
            ID of the created annotation
        """
        # Handle string item type
        if isinstance(target_item_type, str):
            target_item_type = KnowledgeItemType(target_item_type)
        
        # Handle string annotation type
        if isinstance(annotation_type, str):
            annotation_type = AnnotationType(annotation_type)
        
        # Create author object
        author_obj = Person(
            name=author["name"],
            email=author.get("email"),
            affiliation=author.get("affiliation"),
            role=author.get("role", "author")
        )
        
        # Create reference objects
        reference_objs = []
        if references:
            for ref_dict in references:
                ref_type = ref_dict.get("item_type")
                if isinstance(ref_type, str):
                    ref_type = KnowledgeItemType(ref_type)
                
                reference = Reference(
                    item_id=ref_dict["item_id"],
                    item_type=ref_type,
                    context=ref_dict.get("context")
                )
                reference_objs.append(reference)
        
        # Create the annotation
        annotation = Annotation(
            title=f"Annotation on {target_item_id[:8]}",
            content=content,
            author=author_obj,
            target_item_id=target_item_id,
            target_item_type=target_item_type,
            annotation_type=annotation_type,
            target_context=target_context,
            references=reference_objs,
            tags=set(tags or [])
        )
        
        # Save the annotation
        annotation_id = self.annotation_storage.save(annotation)
        
        return annotation_id
    
    def update_annotation(self,
                         annotation_id: str,
                         content: Optional[str] = None,
                         annotation_type: Optional[Union[str, AnnotationType]] = None,
                         status: Optional[Union[str, AnnotationStatus]] = None,
                         tags: Optional[List[str]] = None,
                         add_tags: Optional[List[str]] = None,
                         remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing annotation.
        
        Args:
            annotation_id: ID of the annotation to update
            content: New content (if None, keep existing)
            annotation_type: New annotation type (if None, keep existing)
            status: New status (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the annotation doesn't exist
        """
        if not self.annotation_storage.exists(annotation_id):
            raise ValueError(f"Annotation with ID {annotation_id} does not exist")
        
        annotation = self.annotation_storage.get(annotation_id)
        
        # Update content if provided
        if content is not None:
            annotation.content = content
        
        # Update annotation type if provided
        if annotation_type is not None:
            if isinstance(annotation_type, str):
                annotation_type = AnnotationType(annotation_type)
            annotation.annotation_type = annotation_type
        
        # Update status if provided
        if status is not None:
            if isinstance(status, str):
                status = AnnotationStatus(status)
            annotation.update_status(status)
        
        # Update tags if provided
        if tags is not None:
            annotation.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            annotation.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            annotation.tags.difference_update(remove_tags)
        
        # Update timestamp
        annotation.update_timestamp()
        
        # Save the updated annotation
        self.annotation_storage.save(annotation)
    
    def mark_annotation_as_integrated(self,
                                     annotation_id: str,
                                     item_id: str,
                                     notes: Optional[str] = None) -> None:
        """
        Mark an annotation as integrated into a knowledge item.
        
        Args:
            annotation_id: ID of the annotation
            item_id: ID of the item that integrated the annotation
            notes: Optional integration notes
            
        Raises:
            ValueError: If the annotation doesn't exist
        """
        if not self.annotation_storage.exists(annotation_id):
            raise ValueError(f"Annotation with ID {annotation_id} does not exist")
        
        annotation = self.annotation_storage.get(annotation_id)
        annotation.mark_as_integrated(item_id, notes)
        self.annotation_storage.save(annotation)
    
    def add_response(self, annotation_id: str, response_id: str) -> None:
        """
        Add a response to an annotation.
        
        Args:
            annotation_id: ID of the annotation
            response_id: ID of the response annotation
            
        Raises:
            ValueError: If either annotation doesn't exist
        """
        if not self.annotation_storage.exists(annotation_id):
            raise ValueError(f"Annotation with ID {annotation_id} does not exist")
        
        if not self.annotation_storage.exists(response_id):
            raise ValueError(f"Response with ID {response_id} does not exist")
        
        annotation = self.annotation_storage.get(annotation_id)
        response_ref = Reference(
            item_id=response_id,
            item_type=KnowledgeItemType.ANNOTATION
        )
        
        annotation.add_response(response_ref)
        self.annotation_storage.save(annotation)
    
    def delete_annotation(self, annotation_id: str) -> bool:
        """
        Delete an annotation.
        
        Args:
            annotation_id: ID of the annotation to delete
            
        Returns:
            True if the annotation was deleted, False if it didn't exist
        """
        return self.annotation_storage.delete(annotation_id)
    
    def get_annotation(self, annotation_id: str) -> Annotation:
        """
        Get an annotation by ID.
        
        Args:
            annotation_id: ID of the annotation to retrieve
            
        Returns:
            The requested annotation
            
        Raises:
            ValueError: If the annotation doesn't exist
        """
        if not self.annotation_storage.exists(annotation_id):
            raise ValueError(f"Annotation with ID {annotation_id} does not exist")
        
        return self.annotation_storage.get(annotation_id)
    
    def get_annotations_for_item(self, item_id: str, item_type: Optional[Union[str, KnowledgeItemType]] = None) -> List[str]:
        """
        Get annotations for a specific item.
        
        Args:
            item_id: ID of the item
            item_type: Type of the item (if None, don't filter by type)
            
        Returns:
            List of annotation IDs for the item
        """
        if item_type is not None and isinstance(item_type, str):
            item_type = KnowledgeItemType(item_type)
        
        return self.annotation_storage.get_by_target_item(item_id, item_type)
    
    def import_annotation(self,
                         annotation: Dict[str, Any],
                         original_id: str,
                         importer_id: str,
                         source_system: Optional[str] = None,
                         import_notes: Optional[str] = None) -> str:
        """
        Import an annotation from an external source.
        
        Args:
            annotation: Annotation data dictionary
            original_id: Original ID of the annotation
            importer_id: ID of the user importing the annotation
            source_system: Name of the source system
            import_notes: Notes about the import
            
        Returns:
            ID of the imported annotation
        """
        # Convert annotation data to an Annotation object
        author_data = annotation.get("author", {})
        author = Person(
            id=author_data.get("id", "unknown"),
            name=author_data.get("name", "Unknown Author"),
            email=author_data.get("email"),
            affiliation=author_data.get("affiliation"),
            role=author_data.get("role", "author")
        )
        
        target_item_type = annotation.get("target_item_type")
        if isinstance(target_item_type, str):
            target_item_type = KnowledgeItemType(target_item_type)
        
        annotation_type = annotation.get("annotation_type", "comment")
        if isinstance(annotation_type, str):
            annotation_type = AnnotationType(annotation_type)
        
        # Create references
        references = []
        for ref_data in annotation.get("references", []):
            ref_type = ref_data.get("item_type")
            if isinstance(ref_type, str):
                ref_type = KnowledgeItemType(ref_type)
            
            reference = Reference(
                item_id=ref_data["item_id"],
                item_type=ref_type,
                context=ref_data.get("context")
            )
            references.append(reference)
        
        # Create the annotation object
        annotation_obj = Annotation(
            title=annotation.get("title", f"Imported Annotation {original_id[:8]}"),
            content=annotation["content"],
            author=author,
            target_item_id=annotation["target_item_id"],
            target_item_type=target_item_type,
            annotation_type=annotation_type,
            target_context=annotation.get("target_context"),
            references=references,
            tags=set(annotation.get("tags", [])),
            created_at=datetime.fromisoformat(annotation.get("created_at", datetime.now().isoformat())),
            status=AnnotationStatus.NEW
        )
        
        # Create the imported annotation
        imported_annotation = ImportedAnnotation(
            original_annotation_id=original_id,
            source_system=source_system,
            annotation=annotation_obj,
            import_notes=import_notes,
            importer_id=importer_id
        )
        
        # Save the imported annotation
        imported_id = self.imported_annotation_storage.save(imported_annotation)
        
        return imported_id
    
    def get_imported_annotation(self, imported_id: str) -> ImportedAnnotation:
        """
        Get an imported annotation by ID.
        
        Args:
            imported_id: ID of the imported annotation to retrieve
            
        Returns:
            The requested imported annotation
            
        Raises:
            ValueError: If the imported annotation doesn't exist
        """
        if not self.imported_annotation_storage.exists(imported_id):
            raise ValueError(f"Imported annotation with ID {imported_id} does not exist")
        
        return self.imported_annotation_storage.get(imported_id)
    
    def mark_imported_as_integrated(self, imported_id: str, local_item_id: str) -> None:
        """
        Mark an imported annotation as integrated.
        
        Args:
            imported_id: ID of the imported annotation
            local_item_id: ID of the local item it was integrated into
            
        Raises:
            ValueError: If the imported annotation doesn't exist
        """
        if not self.imported_annotation_storage.exists(imported_id):
            raise ValueError(f"Imported annotation with ID {imported_id} does not exist")
        
        imported = self.imported_annotation_storage.get(imported_id)
        imported.mark_as_integrated(local_item_id)
        self.imported_annotation_storage.save(imported)
    
    def reject_imported_annotation(self, imported_id: str) -> None:
        """
        Mark an imported annotation as rejected.
        
        Args:
            imported_id: ID of the imported annotation
            
        Raises:
            ValueError: If the imported annotation doesn't exist
        """
        if not self.imported_annotation_storage.exists(imported_id):
            raise ValueError(f"Imported annotation with ID {imported_id} does not exist")
        
        imported = self.imported_annotation_storage.get(imported_id)
        imported.reject()
        self.imported_annotation_storage.save(imported)
    
    def create_collaboration_session(self,
                                    name: str,
                                    owner: Dict[str, str],
                                    description: Optional[str] = None,
                                    collaborators: Optional[List[Dict[str, Any]]] = None,
                                    shared_items: Optional[Dict[str, str]] = None,
                                    tags: Optional[List[str]] = None) -> str:
        """
        Create a new collaboration session.
        
        Args:
            name: Session name
            owner: Owner dictionary with 'name', optional 'email' and 'affiliation'
            description: Session description
            collaborators: List of collaborator dictionaries
            shared_items: Dictionary mapping item IDs to item types
            tags: Tags for the session
            
        Returns:
            ID of the created session
        """
        # Create owner object
        owner_obj = Person(
            name=owner["name"],
            email=owner.get("email"),
            affiliation=owner.get("affiliation"),
            role=owner.get("role", "owner")
        )
        
        # Create collaborator objects
        collaborator_objs = []
        if collaborators:
            for collab_dict in collaborators:
                person_dict = collab_dict.get("person", {})
                person = Person(
                    name=person_dict["name"],
                    email=person_dict.get("email"),
                    affiliation=person_dict.get("affiliation"),
                    role=person_dict.get("role", "collaborator")
                )
                
                permission = collab_dict.get("permission", "view")
                if isinstance(permission, str):
                    permission = CollaborationPermission(permission)
                
                collaborator = Collaborator(
                    person=person,
                    permissions=permission,
                    notes=collab_dict.get("notes")
                )
                collaborator_objs.append(collaborator)
        
        # Convert shared item types
        shared_items_dict = {}
        if shared_items:
            for item_id, item_type in shared_items.items():
                if isinstance(item_type, str):
                    item_type = KnowledgeItemType(item_type)
                shared_items_dict[item_id] = item_type
        
        # Create the session
        session = CollaborationSession(
            name=name,
            description=description,
            owner=owner_obj,
            collaborators=collaborator_objs,
            shared_items=shared_items_dict,
            tags=set(tags or [])
        )
        
        # Save the session
        session_id = self.session_storage.save(session)
        
        return session_id
    
    def update_session(self,
                      session_id: str,
                      name: Optional[str] = None,
                      description: Optional[str] = None,
                      status: Optional[str] = None,
                      tags: Optional[List[str]] = None,
                      add_tags: Optional[List[str]] = None,
                      remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing collaboration session.
        
        Args:
            session_id: ID of the session to update
            name: New name (if None, keep existing)
            description: New description (if None, keep existing)
            status: New status (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the session doesn't exist
        """
        if not self.session_storage.exists(session_id):
            raise ValueError(f"Session with ID {session_id} does not exist")
        
        session = self.session_storage.get(session_id)
        
        # Update name if provided
        if name is not None:
            session.name = name
        
        # Update description if provided
        if description is not None:
            session.description = description
        
        # Update status if provided
        if status is not None:
            session.status = status
        
        # Update tags if provided
        if tags is not None:
            session.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            session.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            session.tags.difference_update(remove_tags)
        
        # Update timestamp
        session.updated_at = datetime.now()
        
        # Save the updated session
        self.session_storage.save(session)
    
    def add_collaborator(self,
                        session_id: str,
                        person: Dict[str, str],
                        permission: Union[str, CollaborationPermission] = CollaborationPermission.VIEW,
                        notes: Optional[str] = None) -> None:
        """
        Add a collaborator to a session.
        
        Args:
            session_id: ID of the session
            person: Person dictionary with 'name', optional 'email' and 'affiliation'
            permission: Permission level for the collaborator
            notes: Additional notes
            
        Raises:
            ValueError: If the session doesn't exist
        """
        if not self.session_storage.exists(session_id):
            raise ValueError(f"Session with ID {session_id} does not exist")
        
        session = self.session_storage.get(session_id)
        
        # Create person object
        person_obj = Person(
            name=person["name"],
            email=person.get("email"),
            affiliation=person.get("affiliation"),
            role=person.get("role", "collaborator")
        )
        
        # Handle string permission
        if isinstance(permission, str):
            permission = CollaborationPermission(permission)
        
        # Create collaborator object
        collaborator = Collaborator(
            person=person_obj,
            permissions=permission,
            notes=notes
        )
        
        session.add_collaborator(collaborator)
        self.session_storage.save(session)
    
    def add_shared_item(self,
                       session_id: str,
                       item_id: str,
                       item_type: Union[str, KnowledgeItemType]) -> None:
        """
        Add a shared item to a session.
        
        Args:
            session_id: ID of the session
            item_id: ID of the item to share
            item_type: Type of the item
            
        Raises:
            ValueError: If the session doesn't exist
        """
        if not self.session_storage.exists(session_id):
            raise ValueError(f"Session with ID {session_id} does not exist")
        
        session = self.session_storage.get(session_id)
        
        # Handle string item type
        if isinstance(item_type, str):
            item_type = KnowledgeItemType(item_type)
        
        session.add_shared_item(item_id, item_type)
        self.session_storage.save(session)
    
    def remove_shared_item(self, session_id: str, item_id: str) -> None:
        """
        Remove a shared item from a session.
        
        Args:
            session_id: ID of the session
            item_id: ID of the item to remove
            
        Raises:
            ValueError: If the session doesn't exist
        """
        if not self.session_storage.exists(session_id):
            raise ValueError(f"Session with ID {session_id} does not exist")
        
        session = self.session_storage.get(session_id)
        session.remove_shared_item(item_id)
        self.session_storage.save(session)
    
    def add_annotation_to_session(self, session_id: str, annotation_id: str) -> None:
        """
        Add an annotation to a session.
        
        Args:
            session_id: ID of the session
            annotation_id: ID of the annotation to add
            
        Raises:
            ValueError: If the session or annotation doesn't exist
        """
        if not self.session_storage.exists(session_id):
            raise ValueError(f"Session with ID {session_id} does not exist")
        
        if not self.annotation_storage.exists(annotation_id):
            raise ValueError(f"Annotation with ID {annotation_id} does not exist")
        
        session = self.session_storage.get(session_id)
        session.add_annotation(annotation_id)
        self.session_storage.save(session)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a collaboration session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if the session was deleted, False if it didn't exist
        """
        return self.session_storage.delete(session_id)
    
    def get_session(self, session_id: str) -> CollaborationSession:
        """
        Get a collaboration session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            The requested session
            
        Raises:
            ValueError: If the session doesn't exist
        """
        if not self.session_storage.exists(session_id):
            raise ValueError(f"Session with ID {session_id} does not exist")
        
        return self.session_storage.get(session_id)
    
    def get_sessions_for_user(self, user_id: str) -> List[str]:
        """
        Get sessions where a user is the owner or a collaborator.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of session IDs for the user
        """
        owned_sessions = self.session_storage.get_by_owner(user_id)
        collaborative_sessions = self.session_storage.get_by_collaborator(user_id)
        
        # Combine and remove duplicates
        return list(set(owned_sessions + collaborative_sessions))
    
    def search_annotations(self,
                          text: Optional[str] = None,
                          author_id: Optional[str] = None,
                          target_item_id: Optional[str] = None,
                          target_item_type: Optional[Union[str, KnowledgeItemType]] = None,
                          annotation_type: Optional[Union[str, AnnotationType]] = None,
                          status: Optional[Union[str, AnnotationStatus]] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[str]:
        """
        Search for annotations based on various criteria.
        
        Args:
            text: Text to search for in annotation content
            author_id: Author ID to filter by
            target_item_id: Target item ID to filter by
            target_item_type: Target item type to filter by
            annotation_type: Annotation type to filter by
            status: Status to filter by
            start_date: Only include annotations created after this date
            end_date: Only include annotations created before this date
            
        Returns:
            List of matching annotation IDs
        """
        # Start with all annotations
        result_ids = set(self.annotation_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.annotation_storage.search_by_content(text))
            result_ids.intersection_update(text_results)
        
        # Filter by author if specified
        if author_id:
            author_results = set(self.annotation_storage.get_by_author(author_id))
            result_ids.intersection_update(author_results)
        
        # Filter by target item if specified
        if target_item_id:
            if target_item_type is not None and isinstance(target_item_type, str):
                target_item_type = KnowledgeItemType(target_item_type)
            
            target_results = set(self.annotation_storage.get_by_target_item(target_item_id, target_item_type))
            result_ids.intersection_update(target_results)
        
        # Filter by annotation type if specified
        if annotation_type:
            if isinstance(annotation_type, str):
                annotation_type = AnnotationType(annotation_type)
            
            type_results = set(self.annotation_storage.get_by_type(annotation_type))
            result_ids.intersection_update(type_results)
        
        # Filter by status if specified
        if status:
            if isinstance(status, str):
                status = AnnotationStatus(status)
            
            status_results = set(self.annotation_storage.get_by_status(status))
            result_ids.intersection_update(status_results)
        
        # Filter by date range if specified
        if start_date or end_date:
            date_results = set(self.annotation_storage.get_by_date_range(start_date, end_date))
            result_ids.intersection_update(date_results)
        
        return list(result_ids)
    
    def search_imported_annotations(self,
                                  original_id: Optional[str] = None,
                                  importer_id: Optional[str] = None,
                                  integration_status: Optional[str] = None,
                                  local_item_id: Optional[str] = None,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> List[str]:
        """
        Search for imported annotations based on various criteria.
        
        Args:
            original_id: Original annotation ID to filter by
            importer_id: Importer ID to filter by
            integration_status: Integration status to filter by
            local_item_id: Local item ID to filter by
            start_date: Only include annotations imported after this date
            end_date: Only include annotations imported before this date
            
        Returns:
            List of matching imported annotation IDs
        """
        # Start with all imported annotations
        result_ids = set(self.imported_annotation_storage.list_ids())
        
        # Filter by original ID if specified
        if original_id:
            original_id_result = self.imported_annotation_storage.get_by_original_id(original_id)
            if original_id_result:
                result_ids.intersection_update({original_id_result})
            else:
                return []
        
        # Filter by importer if specified
        if importer_id:
            importer_results = set(self.imported_annotation_storage.get_by_importer(importer_id))
            result_ids.intersection_update(importer_results)
        
        # Filter by integration status if specified
        if integration_status:
            status_results = set(self.imported_annotation_storage.get_by_integration_status(integration_status))
            result_ids.intersection_update(status_results)
        
        # Filter by local item if specified
        if local_item_id:
            item_results = set(self.imported_annotation_storage.get_by_target_item(local_item_id))
            result_ids.intersection_update(item_results)
        
        # Filter by date range if specified
        if start_date or end_date:
            date_results = set(self.imported_annotation_storage.get_by_date_range(start_date, end_date))
            result_ids.intersection_update(date_results)
        
        return list(result_ids)
    
    def search_sessions(self,
                       text: Optional[str] = None,
                       owner_id: Optional[str] = None,
                       collaborator_id: Optional[str] = None,
                       status: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       shared_item_id: Optional[str] = None,
                       shared_item_type: Optional[Union[str, KnowledgeItemType]] = None,
                       active_only: bool = False) -> List[str]:
        """
        Search for collaboration sessions based on various criteria.
        
        Args:
            text: Text to search for in session name and description
            owner_id: Owner ID to filter by
            collaborator_id: Collaborator ID to filter by
            status: Status to filter by
            tags: Tags to filter by
            shared_item_id: Shared item ID to filter by
            shared_item_type: Shared item type to filter by
            active_only: If True, only return active sessions
            
        Returns:
            List of matching session IDs
        """
        # Start with all sessions
        result_ids = set(self.session_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.session_storage.search_by_name(text))
            result_ids.intersection_update(text_results)
        
        # Filter by owner if specified
        if owner_id:
            owner_results = set(self.session_storage.get_by_owner(owner_id))
            result_ids.intersection_update(owner_results)
        
        # Filter by collaborator if specified
        if collaborator_id:
            collaborator_results = set(self.session_storage.get_by_collaborator(collaborator_id))
            result_ids.intersection_update(collaborator_results)
        
        # Filter by status if specified
        if status:
            status_results = set(self.session_storage.get_by_status(status))
            result_ids.intersection_update(status_results)
        
        # Filter by active only if specified
        if active_only:
            active_results = set(self.session_storage.get_active_sessions())
            result_ids.intersection_update(active_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.session_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by shared item if specified
        if shared_item_id:
            if shared_item_type is not None and isinstance(shared_item_type, str):
                shared_item_type = KnowledgeItemType(shared_item_type)
            
            shared_results = set(self.session_storage.get_by_shared_item(shared_item_id, shared_item_type))
            result_ids.intersection_update(shared_results)
        
        return list(result_ids)