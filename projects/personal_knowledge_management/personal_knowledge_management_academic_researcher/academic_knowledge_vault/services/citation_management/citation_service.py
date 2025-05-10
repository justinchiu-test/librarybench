"""
Citation management service for the Academic Knowledge Vault system.

This module provides functionality for managing academic citations and references.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from academic_knowledge_vault.models.base import KnowledgeItemType, Person, Reference
from academic_knowledge_vault.models.citation import Citation, CitationCollection, PublicationType
from academic_knowledge_vault.storage.citation_storage import CitationStorage, CitationCollectionStorage


class CitationService:
    """Service for managing academic citations."""
    
    def __init__(self, 
                 citation_storage: CitationStorage,
                 collection_storage: CitationCollectionStorage):
        """
        Initialize the citation service.
        
        Args:
            citation_storage: Storage for individual citations
            collection_storage: Storage for citation collections
        """
        self.citation_storage = citation_storage
        self.collection_storage = collection_storage
    
    def create_citation(self,
                       title: str,
                       authors: List[Dict[str, str]],
                       publication_year: Optional[int] = None,
                       publication_type: Union[str, PublicationType] = PublicationType.JOURNAL_ARTICLE,
                       journal_or_conference: Optional[str] = None,
                       doi: Optional[str] = None,
                       citation_key: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       **kwargs) -> str:
        """
        Create a new citation.
        
        Args:
            title: Citation title
            authors: List of author dictionaries with 'name', optional 'email' and 'affiliation'
            publication_year: Year of publication
            publication_type: Type of publication
            journal_or_conference: Journal or conference name
            doi: Digital Object Identifier
            citation_key: Unique citation key for referencing
            tags: Tags for the citation
            **kwargs: Additional citation fields
            
        Returns:
            ID of the created citation
        """
        # Handle string publication type
        if isinstance(publication_type, str):
            publication_type = PublicationType(publication_type)
        
        # Create author objects
        author_objects = []
        for author_dict in authors:
            author = Person(
                name=author_dict["name"],
                email=author_dict.get("email"),
                affiliation=author_dict.get("affiliation"),
                role=author_dict.get("role", "author")
            )
            author_objects.append(author)
        
        # Create the citation
        citation = Citation(
            title=title,
            authors=author_objects,
            publication_year=publication_year,
            type=publication_type,
            journal_or_conference=journal_or_conference,
            doi=doi,
            citation_key=citation_key or self._generate_citation_key(title, author_objects, publication_year),
            tags=set(tags or []),
            **kwargs
        )
        
        # Save the citation
        citation_id = self.citation_storage.save(citation)
        
        return citation_id
    
    def _generate_citation_key(self, 
                              title: str, 
                              authors: List[Person], 
                              year: Optional[int] = None) -> str:
        """
        Generate a citation key from the title, authors, and year.
        
        Args:
            title: Citation title
            authors: List of authors
            year: Publication year
            
        Returns:
            Generated citation key
        """
        # Get first author's last name, or use 'unknown' if no authors
        author_part = "unknown"
        if authors:
            # Extract last name from first author
            name_parts = authors[0].name.split()
            if name_parts:
                author_part = name_parts[-1].lower()
        
        # Clean author part (remove non-alphanumeric characters)
        author_part = re.sub(r'[^a-z0-9]', '', author_part)
        
        # Get the first significant word from the title (skip common articles)
        title_words = title.lower().split()
        title_part = "untitled"
        skip_words = {'a', 'an', 'the', 'on', 'of', 'in', 'and', 'for', 'to'}
        
        for word in title_words:
            # Clean word (remove non-alphanumeric characters)
            word = re.sub(r'[^a-z0-9]', '', word)
            if word and word not in skip_words:
                title_part = word
                break
        
        # Use year if provided, otherwise 'nodate'
        year_part = str(year) if year else "nodate"
        
        # Combine the parts
        key = f"{author_part}{year_part}{title_part}"
        
        return key
    
    def update_citation(self,
                       citation_id: str,
                       title: Optional[str] = None,
                       authors: Optional[List[Dict[str, str]]] = None,
                       publication_year: Optional[int] = None,
                       journal_or_conference: Optional[str] = None,
                       doi: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       add_tags: Optional[List[str]] = None,
                       remove_tags: Optional[List[str]] = None,
                       **kwargs) -> None:
        """
        Update an existing citation.
        
        Args:
            citation_id: ID of the citation to update
            title: New title (if None, keep existing)
            authors: New list of authors (if None, keep existing)
            publication_year: New publication year (if None, keep existing)
            journal_or_conference: New journal or conference (if None, keep existing)
            doi: New DOI (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            **kwargs: Additional fields to update
            
        Raises:
            ValueError: If the citation doesn't exist
        """
        if not self.citation_storage.exists(citation_id):
            raise ValueError(f"Citation with ID {citation_id} does not exist")
        
        citation = self.citation_storage.get(citation_id)
        
        # Update title if provided
        if title is not None:
            citation.title = title
        
        # Update authors if provided
        if authors is not None:
            author_objects = []
            for author_dict in authors:
                author = Person(
                    name=author_dict["name"],
                    email=author_dict.get("email"),
                    affiliation=author_dict.get("affiliation"),
                    role=author_dict.get("role", "author")
                )
                author_objects.append(author)
            citation.authors = author_objects
        
        # Update publication year if provided
        if publication_year is not None:
            citation.publication_year = publication_year
        
        # Update journal/conference if provided
        if journal_or_conference is not None:
            citation.journal_or_conference = journal_or_conference
        
        # Update DOI if provided
        if doi is not None:
            citation.doi = doi
        
        # Update tags if provided
        if tags is not None:
            citation.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            citation.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            citation.tags.difference_update(remove_tags)
        
        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(citation, key):
                setattr(citation, key, value)
        
        # Save the updated citation
        self.citation_storage.save(citation)
    
    def delete_citation(self, citation_id: str) -> bool:
        """
        Delete a citation.
        
        Args:
            citation_id: ID of the citation to delete
            
        Returns:
            True if the citation was deleted, False if it didn't exist
        """
        return self.citation_storage.delete(citation_id)
    
    def get_citation(self, citation_id: str) -> Citation:
        """
        Get a citation by ID.
        
        Args:
            citation_id: ID of the citation to retrieve
            
        Returns:
            The requested citation
            
        Raises:
            ValueError: If the citation doesn't exist
        """
        if not self.citation_storage.exists(citation_id):
            raise ValueError(f"Citation with ID {citation_id} does not exist")
        
        return self.citation_storage.get(citation_id)
    
    def add_reference(self, 
                     citation_id: str, 
                     referenced_item_id: str,
                     item_type: KnowledgeItemType) -> None:
        """
        Add a reference from a citation to another knowledge item.
        
        Args:
            citation_id: ID of the citation
            referenced_item_id: ID of the referenced item
            item_type: Type of the referenced item
            
        Raises:
            ValueError: If the citation doesn't exist
        """
        if not self.citation_storage.exists(citation_id):
            raise ValueError(f"Citation with ID {citation_id} does not exist")
        
        citation = self.citation_storage.get(citation_id)
        
        reference = Reference(
            item_id=referenced_item_id,
            item_type=item_type
        )
        
        citation.add_reference(reference)
        self.citation_storage.save(citation)
    
    def add_citation_relationship(self, 
                                citing_id: str, 
                                cited_id: str) -> None:
        """
        Add a citation relationship between two papers.
        
        Args:
            citing_id: ID of the citing paper
            cited_id: ID of the cited paper
            
        Raises:
            ValueError: If either citation doesn't exist
        """
        if not self.citation_storage.exists(citing_id):
            raise ValueError(f"Citing paper with ID {citing_id} does not exist")
        
        if not self.citation_storage.exists(cited_id):
            raise ValueError(f"Cited paper with ID {cited_id} does not exist")
        
        citing_paper = self.citation_storage.get(citing_id)
        cited_paper = self.citation_storage.get(cited_id)
        
        # Create references in both directions
        citing_reference = Reference(
            item_id=cited_id,
            item_type=KnowledgeItemType.CITATION
        )
        
        cited_by_reference = Reference(
            item_id=citing_id,
            item_type=KnowledgeItemType.CITATION
        )
        
        # Add references
        citing_paper.add_reference(citing_reference)
        cited_paper.add_citing_paper(cited_by_reference)
        
        # Save both citations
        self.citation_storage.save(citing_paper)
        self.citation_storage.save(cited_paper)
    
    def create_collection(self,
                         name: str,
                         description: Optional[str] = None,
                         citation_ids: Optional[List[str]] = None,
                         tags: Optional[List[str]] = None) -> str:
        """
        Create a citation collection.
        
        Args:
            name: Collection name
            description: Collection description
            citation_ids: IDs of citations to include
            tags: Tags for the collection
            
        Returns:
            ID of the created collection
            
        Raises:
            ValueError: If any of the specified citations don't exist
        """
        # Validate citation IDs if provided
        if citation_ids:
            for citation_id in citation_ids:
                if not self.citation_storage.exists(citation_id):
                    raise ValueError(f"Citation with ID {citation_id} does not exist")
        
        # Create the collection
        collection = CitationCollection(
            name=name,
            description=description,
            citation_ids=set(citation_ids or []),
            tags=set(tags or [])
        )
        
        # Save the collection
        collection_id = self.collection_storage.save(collection)
        
        return collection_id
    
    def add_citation_to_collection(self, collection_id: str, citation_id: str) -> None:
        """
        Add a citation to a collection.
        
        Args:
            collection_id: ID of the collection
            citation_id: ID of the citation to add
            
        Raises:
            ValueError: If the collection or citation doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        if not self.citation_storage.exists(citation_id):
            raise ValueError(f"Citation with ID {citation_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.add_citation(citation_id)
        self.collection_storage.save(collection)
    
    def remove_citation_from_collection(self, collection_id: str, citation_id: str) -> None:
        """
        Remove a citation from a collection.
        
        Args:
            collection_id: ID of the collection
            citation_id: ID of the citation to remove
            
        Raises:
            ValueError: If the collection doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.remove_citation(citation_id)
        self.collection_storage.save(collection)
    
    def import_bibtex(self, bibtex_content: str) -> List[str]:
        """
        Import citations from BibTeX content.
        
        Args:
            bibtex_content: BibTeX content as a string
            
        Returns:
            List of imported citation IDs
        """
        # Parse BibTeX
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.loads(bibtex_content, parser=parser)
        
        imported_ids = []
        
        for entry in bib_database.entries:
            # Extract key fields
            title = entry.get('title', 'Untitled')
            
            # Extract authors
            authors = []
            if 'author' in entry:
                author_names = entry['author'].split(' and ')
                for name in author_names:
                    authors.append({"name": name.strip()})
            
            # Determine publication type
            pub_type = PublicationType.JOURNAL_ARTICLE  # Default
            entry_type = entry.get('ENTRYTYPE', '').lower()
            
            if entry_type == 'inproceedings' or entry_type == 'conference':
                pub_type = PublicationType.CONFERENCE_PAPER
            elif entry_type == 'book':
                pub_type = PublicationType.BOOK
            elif entry_type == 'incollection':
                pub_type = PublicationType.BOOK_CHAPTER
            elif entry_type == 'phdthesis' or entry_type == 'mastersthesis':
                pub_type = PublicationType.THESIS
            
            # Extract publication year
            year = None
            if 'year' in entry:
                try:
                    year = int(entry['year'])
                except ValueError:
                    pass
            
            # Extract journal or conference
            journal = None
            if 'journal' in entry:
                journal = entry['journal']
            elif 'booktitle' in entry:
                journal = entry['booktitle']
            
            # Extract DOI
            doi = entry.get('doi')
            
            # Extract volume, issue, pages
            volume = entry.get('volume')
            issue = entry.get('number')
            pages = entry.get('pages')
            
            # Extract citation key
            citation_key = entry.get('ID')
            
            # Store the full BibTeX entry for later reference
            bib_db = bibtexparser.bibdatabase.BibDatabase()
            bib_db.entries = [entry]
            bibtex = bibtexparser.dumps(bib_db)
            
            # Create the citation
            citation_id = self.create_citation(
                title=title,
                authors=authors,
                publication_year=year,
                publication_type=pub_type,
                journal_or_conference=journal,
                doi=doi,
                citation_key=citation_key,
                volume=volume,
                issue=issue,
                pages=pages,
                bibtex=bibtex
            )
            
            imported_ids.append(citation_id)
        
        return imported_ids
    
    def import_bibtex_file(self, file_path: Union[str, Path]) -> List[str]:
        """
        Import citations from a BibTeX file.
        
        Args:
            file_path: Path to the BibTeX file
            
        Returns:
            List of imported citation IDs
            
        Raises:
            FileNotFoundError: If the file doesn't exist or can't be read
        """
        with open(file_path, 'r', encoding='utf-8') as bibtex_file:
            bibtex_content = bibtex_file.read()
        
        return self.import_bibtex(bibtex_content)
    
    def export_bibtex(self, citation_ids: List[str]) -> str:
        """
        Export citations to BibTeX format.
        
        Args:
            citation_ids: IDs of citations to export
            
        Returns:
            BibTeX content as a string
            
        Raises:
            ValueError: If any citation doesn't exist
        """
        bibtex_entries = []
        
        for citation_id in citation_ids:
            citation = self.get_citation(citation_id)
            
            if citation.bibtex:
                # Use existing BibTeX if available
                parser = BibTexParser(common_strings=True)
                bib_database = bibtexparser.loads(citation.bibtex, parser=parser)
                bibtex_entries.extend(bib_database.entries)
            else:
                # Generate BibTeX entry
                entry = {}
                
                # Set entry type
                if citation.type == PublicationType.JOURNAL_ARTICLE:
                    entry_type = "article"
                elif citation.type == PublicationType.CONFERENCE_PAPER:
                    entry_type = "inproceedings"
                elif citation.type == PublicationType.BOOK:
                    entry_type = "book"
                elif citation.type == PublicationType.BOOK_CHAPTER:
                    entry_type = "incollection"
                elif citation.type == PublicationType.THESIS:
                    entry_type = "phdthesis"
                else:
                    entry_type = "misc"
                
                entry["ENTRYTYPE"] = entry_type
                entry["ID"] = citation.citation_key or citation.id
                
                # Add basic fields
                entry["title"] = citation.title
                
                if citation.authors:
                    entry["author"] = " and ".join([author.name for author in citation.authors])
                
                if citation.publication_year:
                    entry["year"] = str(citation.publication_year)
                
                if citation.journal_or_conference:
                    if entry_type == "article":
                        entry["journal"] = citation.journal_or_conference
                    elif entry_type == "inproceedings":
                        entry["booktitle"] = citation.journal_or_conference
                
                if citation.volume:
                    entry["volume"] = citation.volume
                
                if citation.issue:
                    entry["number"] = citation.issue
                
                if citation.pages:
                    entry["pages"] = citation.pages
                
                if citation.doi:
                    entry["doi"] = citation.doi
                
                bibtex_entries.append(entry)
        
        # Create BibTeX database and convert to string
        bib_database = bibtexparser.bibdatabase.BibDatabase()
        bib_database.entries = bibtex_entries
        
        return bibtexparser.dumps(bib_database)
    
    def export_bibtex_file(self, citation_ids: List[str], file_path: Union[str, Path]) -> None:
        """
        Export citations to a BibTeX file.
        
        Args:
            citation_ids: IDs of citations to export
            file_path: Path to the output file
            
        Raises:
            ValueError: If any citation doesn't exist
        """
        bibtex_content = self.export_bibtex(citation_ids)
        
        with open(file_path, 'w', encoding='utf-8') as bibtex_file:
            bibtex_file.write(bibtex_content)
    
    def search_citations(self,
                        text: Optional[str] = None,
                        authors: Optional[List[str]] = None,
                        year_range: Optional[Tuple[int, int]] = None,
                        publication_type: Optional[Union[str, PublicationType]] = None,
                        journal: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        doi: Optional[str] = None) -> List[str]:
        """
        Search for citations based on various criteria.
        
        Args:
            text: Text to search for in title and abstract
            authors: Author names to search for
            year_range: Range of publication years (min, max)
            publication_type: Type of publications to find
            journal: Journal or conference name
            tags: Tags to filter by
            doi: DOI to search for
            
        Returns:
            List of matching citation IDs
        """
        # Start with all citations
        result_ids = set(self.citation_storage.list_ids())
        
        # Filter by text if specified
        if text:
            title_results = set(self.citation_storage.search_by_title(text))
            abstract_results = set(self.citation_storage.search_by_abstract(text))
            text_results = title_results.union(abstract_results)
            result_ids.intersection_update(text_results)
        
        # Filter by authors if specified
        if authors:
            author_results = set()
            for author in authors:
                author_results.update(self.citation_storage.search_by_author(author))
            result_ids.intersection_update(author_results)
        
        # Filter by year range if specified
        if year_range:
            min_year, max_year = year_range
            year_results = set(self.citation_storage.search_by_year_range(min_year, max_year))
            result_ids.intersection_update(year_results)
        
        # Filter by publication type if specified
        if publication_type:
            if isinstance(publication_type, str):
                publication_type = PublicationType(publication_type)
            
            type_results = set()
            for citation_id in result_ids:
                try:
                    citation = self.citation_storage.get(citation_id)
                    if citation.type == publication_type:
                        type_results.add(citation_id)
                except Exception:
                    continue
            
            result_ids.intersection_update(type_results)
        
        # Filter by journal if specified
        if journal:
            journal_results = set(self.citation_storage.get_citations_by_journal(journal))
            result_ids.intersection_update(journal_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.citation_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by DOI if specified
        if doi:
            doi_result = self.citation_storage.search_by_doi(doi)
            if doi_result:
                result_ids.intersection_update({doi_result})
            else:
                result_ids = set()
        
        return list(result_ids)
    
    def find_by_citation_key(self, citation_key: str) -> Optional[str]:
        """
        Find a citation by its citation key.

        Args:
            citation_key: Citation key to search for

        Returns:
            Citation ID if found, None otherwise
        """
        return self.citation_storage.search_by_citation_key(citation_key)

    def get_collection(self, collection_id: str) -> CitationCollection:
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