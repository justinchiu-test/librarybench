"""
Unit tests for the citation management functionality.
"""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from academic_knowledge_vault.models.base import KnowledgeItemType, Person, Reference
from academic_knowledge_vault.models.citation import Citation, CitationCollection, PublicationType
from academic_knowledge_vault.storage.citation_storage import CitationStorage, CitationCollectionStorage
from academic_knowledge_vault.services.citation_management.citation_service import CitationService


class TestCitationStorage:
    """Tests for the CitationStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def citation_storage(self, storage_dir):
        """Create a CitationStorage instance."""
        return CitationStorage(storage_dir)
    
    def test_save_and_get_citation(self, citation_storage):
        """Test saving and retrieving a citation."""
        # Create a test citation
        citation = Citation(
            title="Machine Learning Techniques",
            authors=[
                Person(name="John Smith", email="smith@example.com", affiliation="University A"),
                Person(name="Jane Doe", affiliation="University B")
            ],
            publication_year=2020,
            type=PublicationType.JOURNAL_ARTICLE,
            journal_or_conference="Journal of Machine Learning",
            volume="42",
            issue="3",
            pages="123-145",
            doi="10.1234/jml.2020.42.3.123",
            citation_key="smith2020ml",
            tags={"machine_learning", "research"}
        )
        
        # Save the citation
        citation_id = citation_storage.save(citation)
        
        # Retrieve the citation
        retrieved_citation = citation_storage.get(citation_id)
        
        # Verify the citation
        assert retrieved_citation.id == citation_id
        assert retrieved_citation.title == "Machine Learning Techniques"
        assert len(retrieved_citation.authors) == 2
        assert retrieved_citation.authors[0].name == "John Smith"
        assert retrieved_citation.authors[1].name == "Jane Doe"
        assert retrieved_citation.publication_year == 2020
        assert retrieved_citation.type == PublicationType.JOURNAL_ARTICLE
        assert retrieved_citation.journal_or_conference == "Journal of Machine Learning"
        assert retrieved_citation.doi == "10.1234/jml.2020.42.3.123"
        assert retrieved_citation.citation_key == "smith2020ml"
        assert retrieved_citation.tags == {"machine_learning", "research"}
    
    def test_search_by_author(self, citation_storage):
        """Test searching citations by author."""
        # Create test citations with different authors
        citation1 = Citation(
            title="Paper 1",
            authors=[Person(name="John Smith"), Person(name="Jane Doe")]
        )
        citation2 = Citation(
            title="Paper 2",
            authors=[Person(name="Jane Doe"), Person(name="Bob Johnson")]
        )
        citation3 = Citation(
            title="Paper 3",
            authors=[Person(name="Alice Williams")]
        )
        
        # Save the citations
        citation_id1 = citation_storage.save(citation1)
        citation_id2 = citation_storage.save(citation2)
        citation_id3 = citation_storage.save(citation3)
        
        # Search by author
        results = citation_storage.search_by_author("Jane Doe")
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id2 in results
        
        # Search by partial author name
        results = citation_storage.search_by_author("Smith")
        assert len(results) == 1
        assert citation_id1 in results
        
        # Search by case-insensitive author name
        results = citation_storage.search_by_author("alice")
        assert len(results) == 1
        assert citation_id3 in results
    
    def test_search_by_year_range(self, citation_storage):
        """Test searching citations by year range."""
        # Create test citations with different years
        citation1 = Citation(title="Paper 2018", publication_year=2018)
        citation2 = Citation(title="Paper 2020", publication_year=2020)
        citation3 = Citation(title="Paper 2022", publication_year=2022)
        
        # Save the citations
        citation_id1 = citation_storage.save(citation1)
        citation_id2 = citation_storage.save(citation2)
        citation_id3 = citation_storage.save(citation3)
        
        # Search by year range
        results = citation_storage.search_by_year_range(2019, 2021)
        assert len(results) == 1
        assert citation_id2 in results
        
        # Search by broader year range
        results = citation_storage.search_by_year_range(2018, 2022)
        assert len(results) == 3
        assert citation_id1 in results
        assert citation_id2 in results
        assert citation_id3 in results
    
    def test_search_by_doi(self, citation_storage):
        """Test searching citations by DOI."""
        # Create test citations with DOIs
        citation1 = Citation(
            title="Paper with DOI",
            doi="10.1234/abcd.5678"
        )
        citation2 = Citation(
            title="Another Paper",
            doi="10.5678/efgh.9012"
        )
        
        # Save the citations
        citation_id1 = citation_storage.save(citation1)
        citation_id2 = citation_storage.save(citation2)
        
        # Search by DOI
        result = citation_storage.search_by_doi("10.1234/abcd.5678")
        assert result == citation_id1
        
        # Search by nonexistent DOI
        result = citation_storage.search_by_doi("10.9999/nonexistent")
        assert result is None
    
    def test_search_by_title(self, citation_storage):
        """Test searching citations by title."""
        # Create test citations
        citation1 = Citation(title="Machine Learning Techniques")
        citation2 = Citation(title="Deep Learning Methods")
        citation3 = Citation(title="Statistical Analysis")
        
        # Save the citations
        citation_id1 = citation_storage.save(citation1)
        citation_id2 = citation_storage.save(citation2)
        citation_id3 = citation_storage.save(citation3)
        
        # Search by title
        results = citation_storage.search_by_title("learning")
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id2 in results
        
        # Search by case-insensitive title
        results = citation_storage.search_by_title("MACHINE")
        assert len(results) == 1
        assert citation_id1 in results


class TestCitationCollectionStorage:
    """Tests for the CitationCollectionStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def collection_storage(self, storage_dir):
        """Create a CitationCollectionStorage instance."""
        return CitationCollectionStorage(storage_dir)
    
    def test_save_and_get_collection(self, collection_storage):
        """Test saving and retrieving a collection."""
        # Create a test collection
        collection = CitationCollection(
            name="ML Papers",
            description="Machine learning papers",
            citation_ids={"citation1", "citation2"},
            tags={"machine_learning", "papers"}
        )
        
        # Save the collection
        collection_id = collection_storage.save(collection)
        
        # Retrieve the collection
        retrieved_collection = collection_storage.get(collection_id)
        
        # Verify the collection
        assert retrieved_collection.id == collection_id
        assert retrieved_collection.name == "ML Papers"
        assert retrieved_collection.description == "Machine learning papers"
        assert retrieved_collection.citation_ids == {"citation1", "citation2"}
        assert retrieved_collection.tags == {"machine_learning", "papers"}
    
    def test_get_collections_containing_citation(self, collection_storage):
        """Test finding collections containing a specific citation."""
        # Create test collections
        collection1 = CitationCollection(name="Collection 1", citation_ids={"citation1", "citation2"})
        collection2 = CitationCollection(name="Collection 2", citation_ids={"citation2", "citation3"})
        collection3 = CitationCollection(name="Collection 3", citation_ids={"citation4"})
        
        # Save the collections
        collection_id1 = collection_storage.save(collection1)
        collection_id2 = collection_storage.save(collection2)
        collection_id3 = collection_storage.save(collection3)
        
        # Find collections containing a specific citation
        results = collection_storage.get_collections_containing_citation("citation2")
        assert len(results) == 2
        assert collection_id1 in results
        assert collection_id2 in results
        
        # Find collections containing a citation that's only in one collection
        results = collection_storage.get_collections_containing_citation("citation4")
        assert len(results) == 1
        assert collection_id3 in results
        
        # Find collections containing a nonexistent citation
        results = collection_storage.get_collections_containing_citation("nonexistent")
        assert len(results) == 0


class TestCitationService:
    """Tests for the CitationService class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def citation_service(self, storage_dir):
        """Create a CitationService instance."""
        citation_storage = CitationStorage(Path(storage_dir) / "citations")
        collection_storage = CitationCollectionStorage(Path(storage_dir) / "collections")
        return CitationService(citation_storage, collection_storage)
    
    def test_create_citation(self, citation_service):
        """Test creating a citation."""
        # Create a citation
        citation_id = citation_service.create_citation(
            title="Machine Learning Techniques",
            authors=[
                {"name": "John Smith", "email": "smith@example.com", "affiliation": "University A"},
                {"name": "Jane Doe", "affiliation": "University B"}
            ],
            publication_year=2020,
            publication_type=PublicationType.JOURNAL_ARTICLE,
            journal_or_conference="Journal of Machine Learning",
            doi="10.1234/jml.2020.42.3.123",
            citation_key="smith2020ml",
            tags=["machine_learning", "research"],
            volume="42",
            issue="3",
            pages="123-145"
        )
        
        # Retrieve the citation
        citation = citation_service.get_citation(citation_id)
        
        # Verify the citation
        assert citation.title == "Machine Learning Techniques"
        assert len(citation.authors) == 2
        assert citation.authors[0].name == "John Smith"
        assert citation.authors[1].name == "Jane Doe"
        assert citation.publication_year == 2020
        assert citation.type == PublicationType.JOURNAL_ARTICLE
        assert citation.journal_or_conference == "Journal of Machine Learning"
        assert citation.doi == "10.1234/jml.2020.42.3.123"
        assert citation.citation_key == "smith2020ml"
        assert citation.tags == {"machine_learning", "research"}
        assert citation.volume == "42"
        assert citation.issue == "3"
        assert citation.pages == "123-145"
    
    def test_update_citation(self, citation_service):
        """Test updating a citation."""
        # Create a citation
        citation_id = citation_service.create_citation(
            title="Original Title",
            authors=[{"name": "Original Author"}],
            publication_year=2019,
            tags=["original"]
        )
        
        # Update the citation
        citation_service.update_citation(
            citation_id=citation_id,
            title="Updated Title",
            authors=[
                {"name": "Updated Author", "affiliation": "New University"}
            ],
            publication_year=2020,
            tags=["updated"]
        )
        
        # Retrieve the updated citation
        citation = citation_service.get_citation(citation_id)
        
        # Verify the updates
        assert citation.title == "Updated Title"
        assert len(citation.authors) == 1
        assert citation.authors[0].name == "Updated Author"
        assert citation.authors[0].affiliation == "New University"
        assert citation.publication_year == 2020
        assert citation.tags == {"updated"}
    
    def test_add_reference(self, citation_service):
        """Test adding a reference to a citation."""
        # Create a citation
        citation_id = citation_service.create_citation(
            title="Citing Paper",
            authors=[{"name": "Author"}]
        )
        
        # Add a reference
        citation_service.add_reference(
            citation_id=citation_id,
            referenced_item_id="related123",
            item_type=KnowledgeItemType.NOTE
        )
        
        # Retrieve the citation
        citation = citation_service.get_citation(citation_id)
        
        # Verify the reference
        assert len(citation.references) == 1
        assert citation.references[0].item_id == "related123"
        assert citation.references[0].item_type == KnowledgeItemType.NOTE
    
    def test_add_citation_relationship(self, citation_service):
        """Test adding a citation relationship between papers."""
        # Create two citations
        citing_id = citation_service.create_citation(
            title="Citing Paper",
            authors=[{"name": "Author A"}],
            publication_year=2022
        )
        cited_id = citation_service.create_citation(
            title="Cited Paper",
            authors=[{"name": "Author B"}],
            publication_year=2020
        )
        
        # Add the citation relationship
        citation_service.add_citation_relationship(citing_id, cited_id)
        
        # Retrieve both citations
        citing_paper = citation_service.get_citation(citing_id)
        cited_paper = citation_service.get_citation(cited_id)
        
        # Verify the relationship in citing paper
        assert len(citing_paper.references) == 1
        assert citing_paper.references[0].item_id == cited_id
        assert citing_paper.references[0].item_type == KnowledgeItemType.CITATION
        
        # Verify the relationship in cited paper
        assert len(cited_paper.cited_by) == 1
        assert cited_paper.cited_by[0].item_id == citing_id
        assert cited_paper.cited_by[0].item_type == KnowledgeItemType.CITATION
    
    def test_create_collection(self, citation_service):
        """Test creating a citation collection."""
        # Create some citations
        citation_id1 = citation_service.create_citation(
            title="Paper 1",
            authors=[{"name": "Author 1"}]
        )
        citation_id2 = citation_service.create_citation(
            title="Paper 2",
            authors=[{"name": "Author 2"}]
        )
        
        # Create a collection
        collection_id = citation_service.create_collection(
            name="Test Collection",
            description="A collection for testing",
            citation_ids=[citation_id1, citation_id2],
            tags=["test", "collection"]
        )
        
        # Retrieve the collection
        collection = citation_service.get_collection(collection_id)
        
        # Verify the collection
        assert collection.name == "Test Collection"
        assert collection.description == "A collection for testing"
        assert collection.citation_ids == {citation_id1, citation_id2}
        assert collection.tags == {"test", "collection"}
    
    def test_add_citation_to_collection(self, citation_service):
        """Test adding a citation to a collection."""
        # Create a citation and a collection
        citation_id = citation_service.create_citation(
            title="Paper",
            authors=[{"name": "Author"}]
        )
        collection_id = citation_service.create_collection(name="Collection")
        
        # Add the citation to the collection
        citation_service.add_citation_to_collection(collection_id, citation_id)
        
        # Retrieve the collection
        collection = citation_service.get_collection(collection_id)
        
        # Verify the citation was added
        assert citation_id in collection.citation_ids
    
    def test_remove_citation_from_collection(self, citation_service):
        """Test removing a citation from a collection."""
        # Create a citation and a collection with the citation
        citation_id = citation_service.create_citation(
            title="Paper",
            authors=[{"name": "Author"}]
        )
        collection_id = citation_service.create_collection(
            name="Collection",
            citation_ids=[citation_id]
        )
        
        # Verify the citation is in the collection
        collection = citation_service.get_collection(collection_id)
        assert citation_id in collection.citation_ids
        
        # Remove the citation from the collection
        citation_service.remove_citation_from_collection(collection_id, citation_id)
        
        # Retrieve the updated collection
        collection = citation_service.get_collection(collection_id)
        
        # Verify the citation was removed
        assert citation_id not in collection.citation_ids
    
    def test_import_bibtex(self, citation_service):
        """Test importing citations from BibTeX content."""
        # BibTeX content
        bibtex_content = """
        @article{smith2020ml,
            author = {John Smith and Jane Doe},
            title = {Machine Learning Techniques},
            journal = {Journal of Machine Learning},
            year = {2020},
            volume = {42},
            number = {3},
            pages = {123--145},
            doi = {10.1234/jml.2020.42.3.123}
        }
        
        @inproceedings{jones2021dl,
            author = {Bob Jones},
            title = {Deep Learning Methods},
            booktitle = {Conference on AI},
            year = {2021},
            pages = {45--60}
        }
        """
        
        # Import the BibTeX
        citation_ids = citation_service.import_bibtex(bibtex_content)
        
        # Verify the import
        assert len(citation_ids) == 2
        
        # Retrieve and verify the citations
        citation1 = citation_service.get_citation(citation_ids[0])
        citation2 = citation_service.get_citation(citation_ids[1])
        
        # Check that the citations have the correct data
        smith_citation = None
        jones_citation = None
        
        if citation1.title == "Machine Learning Techniques":
            smith_citation = citation1
            jones_citation = citation2
        else:
            smith_citation = citation2
            jones_citation = citation1
        
        # Verify smith2020ml
        assert smith_citation.title == "Machine Learning Techniques"
        assert len(smith_citation.authors) == 2
        assert smith_citation.authors[0].name == "John Smith"
        assert smith_citation.authors[1].name == "Jane Doe"
        assert smith_citation.publication_year == 2020
        assert smith_citation.type == PublicationType.JOURNAL_ARTICLE
        assert smith_citation.journal_or_conference == "Journal of Machine Learning"
        assert smith_citation.volume == "42"
        assert smith_citation.issue == "3"
        assert smith_citation.doi == "10.1234/jml.2020.42.3.123"
        
        # Verify jones2021dl
        assert jones_citation.title == "Deep Learning Methods"
        assert len(jones_citation.authors) == 1
        assert jones_citation.authors[0].name == "Bob Jones"
        assert jones_citation.publication_year == 2021
        assert jones_citation.type == PublicationType.CONFERENCE_PAPER
        assert jones_citation.journal_or_conference == "Conference on AI"
        assert jones_citation.pages == "45--60"
    
    def test_search_citations(self, citation_service):
        """Test searching for citations based on various criteria."""
        # Create test citations
        citation_id1 = citation_service.create_citation(
            title="Machine Learning Survey",
            authors=[{"name": "John Smith"}, {"name": "Jane Doe"}],
            publication_year=2020,
            publication_type=PublicationType.JOURNAL_ARTICLE,
            journal_or_conference="Journal of AI",
            tags=["machine_learning", "survey"]
        )
        citation_id2 = citation_service.create_citation(
            title="Deep Learning Applications",
            authors=[{"name": "Jane Doe"}, {"name": "Bob Johnson"}],
            publication_year=2021,
            publication_type=PublicationType.CONFERENCE_PAPER,
            journal_or_conference="Conference on AI",
            tags=["deep_learning", "applications"]
        )
        citation_id3 = citation_service.create_citation(
            title="Statistical Methods",
            authors=[{"name": "Alice Williams"}],
            publication_year=2019,
            publication_type=PublicationType.JOURNAL_ARTICLE,
            journal_or_conference="Statistics Journal",
            tags=["statistics", "methods"]
        )
        
        # Search by text
        results = citation_service.search_citations(text="learning")
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id2 in results
        
        # Search by authors
        results = citation_service.search_citations(authors=["Jane Doe"])
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id2 in results
        
        # Search by year range
        results = citation_service.search_citations(year_range=(2020, 2021))
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id2 in results
        
        # Search by publication type
        results = citation_service.search_citations(publication_type=PublicationType.JOURNAL_ARTICLE)
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id3 in results
        
        # Search by journal
        results = citation_service.search_citations(journal="Journal")
        assert len(results) == 2
        assert citation_id1 in results
        assert citation_id3 in results
        
        # Search by tags
        results = citation_service.search_citations(tags=["survey"])
        assert len(results) == 1
        assert citation_id1 in results
        
        # Search with multiple criteria
        results = citation_service.search_citations(
            text="learning",
            authors=["Jane Doe"],
            publication_type=PublicationType.JOURNAL_ARTICLE
        )
        assert len(results) == 1
        assert citation_id1 in results
    
    def test_find_by_citation_key(self, citation_service):
        """Test finding a citation by its citation key."""
        # Create a citation with a specific citation key
        citation_id = citation_service.create_citation(
            title="Paper",
            authors=[{"name": "Author"}],
            citation_key="unique_key_2022"
        )
        
        # Find the citation by its key
        result = citation_service.find_by_citation_key("unique_key_2022")
        
        # Verify the result
        assert result == citation_id
        
        # Search for a nonexistent key
        result = citation_service.find_by_citation_key("nonexistent_key")
        assert result is None
    
    def test_export_bibtex(self, citation_service, tmpdir):
        """Test exporting citations to BibTeX format."""
        # Create test citations
        citation_id1 = citation_service.create_citation(
            title="Paper One",
            authors=[{"name": "John Smith"}],
            publication_year=2020,
            publication_type=PublicationType.JOURNAL_ARTICLE,
            journal_or_conference="Journal",
            volume="1",
            issue="2",
            pages="34-56",
            citation_key="smith2020paper"
        )
        citation_id2 = citation_service.create_citation(
            title="Paper Two",
            authors=[{"name": "Jane Doe"}],
            publication_year=2021,
            publication_type=PublicationType.CONFERENCE_PAPER,
            journal_or_conference="Conference",
            citation_key="doe2021paper"
        )
        
        # Export to BibTeX
        bibtex_content = citation_service.export_bibtex([citation_id1, citation_id2])
        
        # Verify the BibTeX content
        assert "@article{smith2020paper" in bibtex_content
        assert "title = {Paper One}" in bibtex_content
        assert "author = {John Smith}" in bibtex_content
        assert "year = {2020}" in bibtex_content
        
        assert "@inproceedings{doe2021paper" in bibtex_content
        assert "title = {Paper Two}" in bibtex_content
        assert "author = {Jane Doe}" in bibtex_content
        assert "year = {2021}" in bibtex_content
        
        # Test exporting to a file
        export_file = Path(tmpdir) / "export.bib"
        citation_service.export_bibtex_file([citation_id1, citation_id2], export_file)
        
        # Verify the file exists and contains the BibTeX
        assert export_file.exists()
        with open(export_file, 'r') as f:
            file_content = f.read()
            assert "@article{smith2020paper" in file_content
            assert "@inproceedings{doe2021paper" in file_content