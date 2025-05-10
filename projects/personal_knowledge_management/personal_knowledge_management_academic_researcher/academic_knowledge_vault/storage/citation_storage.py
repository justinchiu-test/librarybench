"""
Citation storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for citations and citation collections.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.citation import Citation, CitationCollection
from academic_knowledge_vault.storage.base import JsonFileStorage


class CitationStorage(JsonFileStorage[Citation]):
    """Storage for academic citations."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize citation storage.
        
        Args:
            base_dir: Base directory for citation storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, Citation, create_dir)
    
    def search_by_author(self, author_name: str) -> List[str]:
        """
        Search for citations with a specific author.
        
        Args:
            author_name: Author name to search for (partial match)
            
        Returns:
            List of citation IDs with matching authors
        """
        author_name = author_name.lower()
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                for author in citation.authors:
                    if author_name in author.name.lower():
                        result_ids.append(citation_id)
                        break
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def search_by_year(self, year: int) -> List[str]:
        """
        Search for citations from a specific year.
        
        Args:
            year: Publication year
            
        Returns:
            List of citation IDs from the specified year
        """
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if citation.publication_year == year:
                    result_ids.append(citation_id)
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def search_by_year_range(self, start_year: int, end_year: int) -> List[str]:
        """
        Search for citations from a range of years.
        
        Args:
            start_year: Start of year range (inclusive)
            end_year: End of year range (inclusive)
            
        Returns:
            List of citation IDs in the year range
        """
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if (citation.publication_year is not None and 
                    start_year <= citation.publication_year <= end_year):
                    result_ids.append(citation_id)
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for citations with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, citations must have all tags; if False, any tag is sufficient
            
        Returns:
            List of citation IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in citation.tags for tag in tags):
                        result_ids.append(citation_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in citation.tags for tag in tags):
                        result_ids.append(citation_id)
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def search_by_title(self, title_text: str) -> List[str]:
        """
        Search for citations with titles containing specific text.
        
        Args:
            title_text: Text to search for in titles
            
        Returns:
            List of citation IDs with matching titles
        """
        title_text = title_text.lower()
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if title_text in citation.title.lower():
                    result_ids.append(citation_id)
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def search_by_abstract(self, abstract_text: str) -> List[str]:
        """
        Search for citations with abstracts containing specific text.
        
        Args:
            abstract_text: Text to search for in abstracts
            
        Returns:
            List of citation IDs with matching abstracts
        """
        abstract_text = abstract_text.lower()
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if citation.abstract and abstract_text in citation.abstract.lower():
                    result_ids.append(citation_id)
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def search_by_doi(self, doi: str) -> Optional[str]:
        """
        Search for a citation with a specific DOI.
        
        Args:
            doi: DOI to search for
            
        Returns:
            Citation ID with matching DOI, or None if not found
        """
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if citation.doi == doi:
                    return citation_id
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return None
    
    def search_by_citation_key(self, citation_key: str) -> Optional[str]:
        """
        Search for a citation with a specific citation key.
        
        Args:
            citation_key: Citation key to search for
            
        Returns:
            Citation ID with matching citation key, or None if not found
        """
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if citation.citation_key == citation_key:
                    return citation_id
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return None
    
    def get_citations_by_journal(self, journal_name: str) -> List[str]:
        """
        Get citations from a specific journal.
        
        Args:
            journal_name: Journal name (partial match)
            
        Returns:
            List of citation IDs from the journal
        """
        journal_name = journal_name.lower()
        result_ids = []
        
        for citation_id in self.list_ids():
            try:
                citation = self.get(citation_id)
                
                if (citation.journal_or_conference and 
                    journal_name in citation.journal_or_conference.lower()):
                    result_ids.append(citation_id)
                    
            except Exception:
                # Skip problematic citations
                continue
        
        return result_ids
    
    def export_to_bibtex(self, citation_ids: List[str], file_path: Union[str, Path]) -> None:
        """
        Export citations to a BibTeX file.
        
        Args:
            citation_ids: IDs of citations to export
            file_path: Path to the output file
            
        Raises:
            ValueError: If no citations are provided
            FileNotFoundError: If a citation is not found
        """
        if not citation_ids:
            raise ValueError("No citation IDs provided for export")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for citation_id in citation_ids:
                citation = self.get(citation_id)
                
                if citation.bibtex:
                    f.write(citation.bibtex + "\n\n")
                else:
                    # Generate BibTeX from citation data
                    entry_type = "article"  # Default
                    
                    if citation.type == "conference_paper":
                        entry_type = "inproceedings"
                    elif citation.type == "book":
                        entry_type = "book"
                    elif citation.type == "book_chapter":
                        entry_type = "incollection"
                    elif citation.type == "thesis":
                        entry_type = "phdthesis"
                    
                    key = citation.citation_key or citation.id
                    
                    f.write(f"@{entry_type}{{{key},\n")
                    
                    if citation.authors:
                        authors = " and ".join([author.name for author in citation.authors])
                        f.write(f"  author = {{{authors}}},\n")
                    
                    f.write(f"  title = {{{citation.title}}},\n")
                    
                    if citation.publication_year:
                        f.write(f"  year = {{{citation.publication_year}}},\n")
                    
                    if citation.journal_or_conference:
                        if entry_type == "article":
                            f.write(f"  journal = {{{citation.journal_or_conference}}},\n")
                        elif entry_type == "inproceedings":
                            f.write(f"  booktitle = {{{citation.journal_or_conference}}},\n")
                    
                    if citation.volume:
                        f.write(f"  volume = {{{citation.volume}}},\n")
                    
                    if citation.issue:
                        f.write(f"  number = {{{citation.issue}}},\n")
                    
                    if citation.pages:
                        f.write(f"  pages = {{{citation.pages}}},\n")
                    
                    if citation.doi:
                        f.write(f"  doi = {{{citation.doi}}},\n")
                    
                    f.write("}\n\n")


class CitationCollectionStorage(JsonFileStorage[CitationCollection]):
    """Storage for citation collections."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize citation collection storage.
        
        Args:
            base_dir: Base directory for collection storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, CitationCollection, create_dir)
    
    def get_collections_containing_citation(self, citation_id: str) -> List[str]:
        """
        Find collections that contain a specific citation.
        
        Args:
            citation_id: ID of the citation
            
        Returns:
            List of collection IDs containing the citation
        """
        result_ids = []
        
        for collection_id in self.list_ids():
            try:
                collection = self.get(collection_id)
                
                if citation_id in collection.citation_ids:
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