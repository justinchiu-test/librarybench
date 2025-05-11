from datetime import datetime
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from .models import Author, AuthorType, Reference, ReferenceType, TaskReferenceLink, CitationStyle
from .storage import BibliographyStorageInterface
from .formatter import format_citation


class BibliographyService:
    """Service for managing bibliographic references."""
    
    def __init__(self, storage: BibliographyStorageInterface):
        """
        Initialize the bibliography service.
        
        Args:
            storage: The storage implementation to use
        """
        self._storage = storage
    
    # Reference operations
    
    def create_reference(
        self,
        title: str,
        type: ReferenceType = ReferenceType.JOURNAL_ARTICLE,
        authors: Optional[List[Union[str, Author]]] = None,
        year: Optional[int] = None,
        journal_name: Optional[str] = None,
        volume: Optional[str] = None,
        issue: Optional[str] = None,
        pages: Optional[str] = None,
        doi: Optional[str] = None,
        publisher: Optional[str] = None,
        isbn: Optional[str] = None,
        url: Optional[str] = None,
        abstract: Optional[str] = None,
        keywords: Optional[Set[str]] = None,
    ) -> Reference:
        """
        Create a new bibliographic reference.
        
        Args:
            title: The title of the work
            type: The type of reference
            authors: List of authors (strings or Author objects)
            year: Publication year
            journal_name: Name of the journal (for articles)
            volume: Volume number
            issue: Issue number
            pages: Page range
            doi: Digital Object Identifier
            publisher: Publisher name
            isbn: ISBN number
            url: URL for online resources
            abstract: Abstract or summary
            keywords: Set of keywords
            
        Returns:
            Reference: The created reference
        """
        # Process authors
        author_objects = []
        if authors:
            for author in authors:
                if isinstance(author, Author):
                    author_objects.append(author)
                elif isinstance(author, str):
                    # Parse author string (Last, First or First Last)
                    parts = author.split(",")
                    if len(parts) > 1:
                        last_name = parts[0].strip()
                        first_name = parts[1].strip()
                    else:
                        name_parts = author.strip().split()
                        if len(name_parts) > 1:
                            first_name = " ".join(name_parts[:-1])
                            last_name = name_parts[-1]
                        else:
                            first_name = ""
                            last_name = author.strip()
                    
                    author_objects.append(Author(
                        type=AuthorType.PERSON,
                        first_name=first_name,
                        last_name=last_name
                    ))
        
        # Create the reference
        reference = Reference(
            type=type,
            title=title,
            authors=author_objects,
            year=year,
            journal_name=journal_name,
            volume=volume,
            issue=issue,
            pages=pages,
            doi=doi,
            publisher=publisher,
            isbn=isbn,
            url=url,
            abstract=abstract,
            keywords=keywords or set(),
        )
        
        # Save the reference
        self._storage.create_reference(reference)
        
        return reference
    
    def get_reference(self, reference_id: UUID) -> Optional[Reference]:
        """
        Retrieve a reference by ID.
        
        Args:
            reference_id: The ID of the reference to retrieve
            
        Returns:
            Optional[Reference]: The reference if found, None otherwise
        """
        return self._storage.get_reference(reference_id)
    
    def update_reference(
        self,
        reference_id: UUID,
        title: Optional[str] = None,
        year: Optional[int] = None,
        journal_name: Optional[str] = None,
        volume: Optional[str] = None,
        issue: Optional[str] = None,
        pages: Optional[str] = None,
        doi: Optional[str] = None,
        publisher: Optional[str] = None,
        isbn: Optional[str] = None,
        url: Optional[str] = None,
        abstract: Optional[str] = None,
    ) -> bool:
        """
        Update an existing reference.
        
        Args:
            reference_id: The ID of the reference to update
            title: New title
            year: New year
            journal_name: New journal name
            volume: New volume
            issue: New issue
            pages: New pages
            doi: New DOI
            publisher: New publisher
            isbn: New ISBN
            url: New URL
            abstract: New abstract
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if year is not None:
            update_data["year"] = year
        if journal_name is not None:
            update_data["journal_name"] = journal_name
        if volume is not None:
            update_data["volume"] = volume
        if issue is not None:
            update_data["issue"] = issue
        if pages is not None:
            update_data["pages"] = pages
        if doi is not None:
            update_data["doi"] = doi
        if publisher is not None:
            update_data["publisher"] = publisher
        if isbn is not None:
            update_data["isbn"] = isbn
        if url is not None:
            update_data["url"] = url
        if abstract is not None:
            update_data["abstract"] = abstract
        
        reference.update(**update_data)
        return self._storage.update_reference(reference)
    
    def delete_reference(self, reference_id: UUID) -> bool:
        """
        Delete a reference by ID.
        
        Args:
            reference_id: The ID of the reference to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_reference(reference_id)
    
    def add_author_to_reference(
        self, 
        reference_id: UUID, 
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization_name: Optional[str] = None,
        type: AuthorType = AuthorType.PERSON,
        orcid_id: Optional[str] = None,
    ) -> bool:
        """
        Add an author to a reference.
        
        Args:
            reference_id: The ID of the reference
            first_name: First name of the author (for persons)
            last_name: Last name of the author (for persons)
            organization_name: Name of the organization (for organizations)
            type: Type of author (person or organization)
            orcid_id: ORCID identifier for the author
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If reference doesn't exist or author information is invalid
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        # Validate author information
        if type == AuthorType.PERSON and not (first_name or last_name):
            raise ValueError("First name or last name must be provided for person authors")
        if type == AuthorType.ORGANIZATION and not organization_name:
            raise ValueError("Organization name must be provided for organization authors")
        
        # Create author
        author = Author(
            type=type,
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name,
            orcid_id=orcid_id,
        )
        
        reference.add_author(author)
        return self._storage.update_reference(reference)
    
    def remove_author_from_reference(self, reference_id: UUID, author_id: UUID) -> bool:
        """
        Remove an author from a reference.
        
        Args:
            reference_id: The ID of the reference
            author_id: The ID of the author to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        result = reference.remove_author(author_id)
        if result:
            return self._storage.update_reference(reference)
        return False
    
    def add_keyword_to_reference(self, reference_id: UUID, keyword: str) -> bool:
        """
        Add a keyword to a reference.
        
        Args:
            reference_id: The ID of the reference
            keyword: The keyword to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        reference.add_keyword(keyword)
        return self._storage.update_reference(reference)
    
    def remove_keyword_from_reference(self, reference_id: UUID, keyword: str) -> bool:
        """
        Remove a keyword from a reference.
        
        Args:
            reference_id: The ID of the reference
            keyword: The keyword to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        reference.remove_keyword(keyword)
        return self._storage.update_reference(reference)
    
    def add_note_to_reference(self, reference_id: UUID, note: str) -> bool:
        """
        Add a note to a reference.
        
        Args:
            reference_id: The ID of the reference
            note: The note to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        reference.add_note(note)
        return self._storage.update_reference(reference)
    
    def search_references(
        self, 
        author_name: Optional[str] = None, 
        year: Optional[int] = None,
        keywords: Optional[Set[str]] = None,
    ) -> List[Reference]:
        """
        Search for references with optional filtering.
        
        Args:
            author_name: Filter by author name (partial match)
            year: Filter by publication year
            keywords: Filter by keywords (references must have all specified keywords)
            
        Returns:
            List[Reference]: List of references matching the criteria
        """
        return self._storage.list_references(
            author_name=author_name,
            year=year,
            keywords=keywords,
        )
    
    # Task-Reference link operations
    
    def link_task_to_reference(
        self, 
        task_id: UUID, 
        reference_id: UUID,
        relevance: Optional[str] = None,
    ) -> UUID:
        """
        Link a task to a reference.
        
        Args:
            task_id: The ID of the task
            reference_id: The ID of the reference
            relevance: Description of the relevance of this reference to the task
            
        Returns:
            UUID: The ID of the created link
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        # Check if link already exists
        existing_links = self._storage.get_references_for_task(task_id)
        for ref in existing_links:
            if ref.id == reference_id:
                # Link already exists
                return UUID('00000000-0000-0000-0000-000000000000')
        
        # Create the link
        link = TaskReferenceLink(
            task_id=task_id,
            reference_id=reference_id,
            relevance=relevance,
        )
        
        return self._storage.create_task_reference_link(link)
    
    def unlink_task_from_reference(self, task_id: UUID, reference_id: UUID) -> bool:
        """
        Remove a link between a task and a reference.
        
        Args:
            task_id: The ID of the task
            reference_id: The ID of the reference
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the link
        links = [
            link for link_id, link in self._storage._task_reference_links.items()
            if link.task_id == task_id and link.reference_id == reference_id
        ]
        
        if not links:
            return False
        
        # Delete the link
        return self._storage.delete_task_reference_link(links[0].id)
    
    def get_references_for_task(self, task_id: UUID) -> List[Reference]:
        """
        Get all references associated with a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List[Reference]: List of associated references
        """
        return self._storage.get_references_for_task(task_id)
    
    def get_tasks_for_reference(self, reference_id: UUID) -> List[UUID]:
        """
        Get all task IDs associated with a reference.
        
        Args:
            reference_id: The ID of the reference
            
        Returns:
            List[UUID]: List of associated task IDs
        """
        return self._storage.get_tasks_for_reference(reference_id)
    
    def add_note_to_link(self, task_id: UUID, reference_id: UUID, note: str) -> bool:
        """
        Add a note to the link between a task and a reference.
        
        Args:
            task_id: The ID of the task
            reference_id: The ID of the reference
            note: The note to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the link
        links = [
            link for link_id, link in self._storage._task_reference_links.items()
            if link.task_id == task_id and link.reference_id == reference_id
        ]
        
        if not links:
            return False
        
        link = links[0]
        link.add_note(note)
        return self._storage.update_task_reference_link(link)
    
    def format_citation(self, reference_id: UUID, style: CitationStyle = CitationStyle.APA) -> str:
        """
        Format a reference in a specific citation style.
        
        Args:
            reference_id: The ID of the reference to format
            style: The citation style to use
            
        Returns:
            str: Formatted citation string
            
        Raises:
            ValueError: If reference doesn't exist
        """
        reference = self._storage.get_reference(reference_id)
        if not reference:
            raise ValueError(f"Reference with ID {reference_id} does not exist")
        
        return format_citation(reference, style)
    
    def format_citations(self, reference_ids: List[UUID], style: CitationStyle = CitationStyle.APA) -> List[str]:
        """
        Format multiple references in a specific citation style.
        
        Args:
            reference_ids: The IDs of the references to format
            style: The citation style to use
            
        Returns:
            List[str]: List of formatted citation strings
        """
        citations = []
        for ref_id in reference_ids:
            reference = self._storage.get_reference(ref_id)
            if reference:
                citations.append(format_citation(reference, style))
        
        return citations
    
    def format_bibliography(self, reference_ids: List[UUID], style: CitationStyle = CitationStyle.APA) -> str:
        """
        Format a complete bibliography in a specific citation style.
        
        Args:
            reference_ids: The IDs of the references to include
            style: The citation style to use
            
        Returns:
            str: Formatted bibliography
        """
        citations = self.format_citations(reference_ids, style)
        return "\n\n".join(citations)