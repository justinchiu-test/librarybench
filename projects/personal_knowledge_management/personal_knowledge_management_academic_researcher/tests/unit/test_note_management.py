"""
Unit tests for the note management functionality.
"""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from academic_knowledge_vault.models.base import KnowledgeItemType, Reference
from academic_knowledge_vault.models.note import Note, NoteCollection, NoteType, NoteContent
from academic_knowledge_vault.storage.note_storage import NoteStorage, NoteCollectionStorage
from academic_knowledge_vault.services.note_management.note_service import NoteService, CitationExtractor


class TestCitationExtractor:
    """Tests for the CitationExtractor utility class."""
    
    def test_extract_citation_keys(self):
        """Test extracting citation keys from text."""
        # Test simple @citation format
        text = "This is a reference to @smith2020 and another to @jones2021."
        keys = CitationExtractor.extract_citation_keys(text)
        assert keys == {"smith2020", "jones2021"}
        
        # Test [@citation] format
        text = "This is a reference to [@brown2019] and multiple refs [@lee2020; @wang2018]."
        keys = CitationExtractor.extract_citation_keys(text)
        assert keys == {"brown2019", "lee2020", "wang2018"}
        
        # Test mixed formats
        text = "References include @miller2020 and [@chen2021]."
        keys = CitationExtractor.extract_citation_keys(text)
        assert keys == {"miller2020", "chen2021"}
        
        # Test empty text
        text = "This text has no citations."
        keys = CitationExtractor.extract_citation_keys(text)
        assert keys == set()
    
    def test_extract_dois(self):
        """Test extracting DOIs from text."""
        # Test simple DOI format
        text = "The DOI is 10.1234/abcd.5678."
        dois = CitationExtractor.extract_dois(text)
        assert dois == {"10.1234/abcd.5678"}
        
        # Test with URL format
        text = "The DOI link is https://doi.org/10.5678/efgh.9012."
        dois = CitationExtractor.extract_dois(text)
        assert dois == {"10.5678/efgh.9012"}
        
        # Test with prefix
        text = "DOI: 10.9876/ijkl.3456"
        dois = CitationExtractor.extract_dois(text)
        assert dois == {"10.9876/ijkl.3456"}
        
        # Test multiple DOIs
        text = "References: 10.1234/abcd.5678 and https://doi.org/10.5678/efgh.9012"
        dois = CitationExtractor.extract_dois(text)
        assert dois == {"10.1234/abcd.5678", "10.5678/efgh.9012"}
        
        # Test empty text
        text = "This text has no DOIs."
        dois = CitationExtractor.extract_dois(text)
        assert dois == set()


class TestNoteStorage:
    """Tests for the NoteStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def note_storage(self, storage_dir):
        """Create a NoteStorage instance."""
        return NoteStorage(storage_dir)
    
    def test_save_and_get_note(self, note_storage):
        """Test saving and retrieving a note."""
        # Create a test note
        note = Note(
            title="Test Note",
            content=NoteContent(content="This is a test note."),
            type=NoteType.CONCEPT,
            tags={"test", "example"}
        )
        
        # Save the note
        note_id = note_storage.save(note)
        
        # Retrieve the note
        retrieved_note = note_storage.get(note_id)
        
        # Verify the note
        assert retrieved_note.id == note_id
        assert retrieved_note.title == "Test Note"
        assert retrieved_note.content.content == "This is a test note."
        assert retrieved_note.type == NoteType.CONCEPT
        assert retrieved_note.tags == {"test", "example"}
    
    def test_list_ids(self, note_storage):
        """Test listing note IDs."""
        # Create test notes
        note1 = Note(title="Note 1", content=NoteContent(content="Content 1"))
        note2 = Note(title="Note 2", content=NoteContent(content="Content 2"))
        
        # Save the notes
        note_id1 = note_storage.save(note1)
        note_id2 = note_storage.save(note2)
        
        # List the IDs
        ids = note_storage.list_ids()
        
        # Verify the IDs
        assert len(ids) == 2
        assert note_id1 in ids
        assert note_id2 in ids
    
    def test_delete_note(self, note_storage):
        """Test deleting a note."""
        # Create a test note
        note = Note(title="Delete Me", content=NoteContent(content="This should be deleted."))
        
        # Save the note
        note_id = note_storage.save(note)
        
        # Verify the note exists
        assert note_storage.exists(note_id)
        
        # Delete the note
        result = note_storage.delete(note_id)
        
        # Verify the deletion
        assert result is True
        assert not note_storage.exists(note_id)
        
        # Try to delete a nonexistent note
        result = note_storage.delete("nonexistent-id")
        assert result is False
    
    def test_search_by_tags(self, note_storage):
        """Test searching notes by tags."""
        # Create test notes with different tags
        note1 = Note(title="Note 1", content=NoteContent(content="Content 1"), tags={"tag1", "tag2"})
        note2 = Note(title="Note 2", content=NoteContent(content="Content 2"), tags={"tag2", "tag3"})
        note3 = Note(title="Note 3", content=NoteContent(content="Content 3"), tags={"tag4"})
        
        # Save the notes
        note_id1 = note_storage.save(note1)
        note_id2 = note_storage.save(note2)
        note_id3 = note_storage.save(note3)
        
        # Search by tag with match_all=True
        results = note_storage.search_by_tags(["tag2"], match_all=True)
        assert len(results) == 2
        assert note_id1 in results
        assert note_id2 in results
        
        # Search by multiple tags with match_all=True
        results = note_storage.search_by_tags(["tag1", "tag2"], match_all=True)
        assert len(results) == 1
        assert note_id1 in results
        
        # Search by tag with match_all=False
        results = note_storage.search_by_tags(["tag1", "tag3"], match_all=False)
        assert len(results) == 2
        assert note_id1 in results
        assert note_id2 in results
    
    def test_search_by_content(self, note_storage):
        """Test searching notes by content."""
        # Create test notes with different content
        note1 = Note(title="Title 1", content=NoteContent(content="This note mentions keywords."))
        note2 = Note(title="Keywords", content=NoteContent(content="This is another note."))
        note3 = Note(title="Title 3", content=NoteContent(content="Unrelated content."))
        
        # Save the notes
        note_id1 = note_storage.save(note1)
        note_id2 = note_storage.save(note2)
        note_id3 = note_storage.save(note3)
        
        # Search by content
        results = note_storage.search_by_content("keywords")
        assert len(results) == 2
        assert note_id1 in results
        assert note_id2 in results
        
        # Search by content case insensitive
        results = note_storage.search_by_content("KEYWORDS")
        assert len(results) == 2
        assert note_id1 in results
        assert note_id2 in results
    
    def test_search_by_citation_key(self, note_storage):
        """Test searching notes by citation key."""
        # Create test notes with citation keys
        note1 = Note(
            title="Note with Citation", 
            content=NoteContent(content="This cites @smith2020."),
            citation_keys={"smith2020"}
        )
        note2 = Note(
            title="Another Note", 
            content=NoteContent(content="This cites @jones2021."),
            citation_keys={"jones2021"}
        )
        
        # Save the notes
        note_id1 = note_storage.save(note1)
        note_id2 = note_storage.save(note2)
        
        # Search by citation key
        results = note_storage.search_by_citation_key("smith2020")
        assert len(results) == 1
        assert note_id1 in results
        
        # Search by nonexistent citation key
        results = note_storage.search_by_citation_key("nonexistent")
        assert len(results) == 0


class TestNoteCollectionStorage:
    """Tests for the NoteCollectionStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def collection_storage(self, storage_dir):
        """Create a NoteCollectionStorage instance."""
        return NoteCollectionStorage(storage_dir)
    
    def test_save_and_get_collection(self, collection_storage):
        """Test saving and retrieving a collection."""
        # Create a test collection
        collection = NoteCollection(
            name="Test Collection",
            description="A collection for testing",
            note_ids={"note1", "note2"},
            tags={"test", "example"}
        )
        
        # Save the collection
        collection_id = collection_storage.save(collection)
        
        # Retrieve the collection
        retrieved_collection = collection_storage.get(collection_id)
        
        # Verify the collection
        assert retrieved_collection.id == collection_id
        assert retrieved_collection.name == "Test Collection"
        assert retrieved_collection.description == "A collection for testing"
        assert retrieved_collection.note_ids == {"note1", "note2"}
        assert retrieved_collection.tags == {"test", "example"}
    
    def test_get_collections_containing_note(self, collection_storage):
        """Test finding collections containing a specific note."""
        # Create test collections
        collection1 = NoteCollection(name="Collection 1", note_ids={"note1", "note2"})
        collection2 = NoteCollection(name="Collection 2", note_ids={"note2", "note3"})
        collection3 = NoteCollection(name="Collection 3", note_ids={"note4"})
        
        # Save the collections
        collection_id1 = collection_storage.save(collection1)
        collection_id2 = collection_storage.save(collection2)
        collection_id3 = collection_storage.save(collection3)
        
        # Find collections containing a specific note
        results = collection_storage.get_collections_containing_note("note2")
        assert len(results) == 2
        assert collection_id1 in results
        assert collection_id2 in results
        
        # Find collections containing a note that's only in one collection
        results = collection_storage.get_collections_containing_note("note4")
        assert len(results) == 1
        assert collection_id3 in results
        
        # Find collections containing a nonexistent note
        results = collection_storage.get_collections_containing_note("nonexistent")
        assert len(results) == 0


class TestNoteService:
    """Tests for the NoteService class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def note_service(self, storage_dir):
        """Create a NoteService instance."""
        note_storage = NoteStorage(Path(storage_dir) / "notes")
        collection_storage = NoteCollectionStorage(Path(storage_dir) / "collections")
        return NoteService(note_storage, collection_storage)
    
    def test_create_note(self, note_service):
        """Test creating a note."""
        # Create a note
        note_id = note_service.create_note(
            title="Test Note",
            content="This is a test note with a citation to @smith2020.",
            note_type=NoteType.CONCEPT,
            tags=["test", "example"]
        )
        
        # Retrieve the note
        note = note_service.get_note(note_id)
        
        # Verify the note
        assert note.title == "Test Note"
        assert note.content.content == "This is a test note with a citation to @smith2020."
        assert note.type == NoteType.CONCEPT
        assert note.tags == {"test", "example"}
        assert "smith2020" in note.citation_keys
    
    def test_update_note(self, note_service):
        """Test updating a note."""
        # Create a note
        note_id = note_service.create_note(
            title="Original Title",
            content="Original content.",
            tags=["original"]
        )
        
        # Update the note
        note_service.update_note(
            note_id=note_id,
            title="Updated Title",
            content="Updated content with citation to @jones2021.",
            tags=["updated"]
        )
        
        # Retrieve the updated note
        note = note_service.get_note(note_id)
        
        # Verify the updates
        assert note.title == "Updated Title"
        assert note.content.content == "Updated content with citation to @jones2021."
        assert note.tags == {"updated"}
        assert "jones2021" in note.citation_keys
    
    def test_add_reference(self, note_service):
        """Test adding a reference to a note."""
        # Create a note
        note_id = note_service.create_note(
            title="Note with References",
            content="Content."
        )
        
        # Add a reference
        note_service.add_reference(
            note_id=note_id,
            referenced_item_id="citation123",
            item_type=KnowledgeItemType.CITATION,
            context="Important citation"
        )
        
        # Retrieve the note
        note = note_service.get_note(note_id)
        
        # Verify the reference
        assert len(note.references) == 1
        assert note.references[0].item_id == "citation123"
        assert note.references[0].item_type == KnowledgeItemType.CITATION
        assert note.references[0].context == "Important citation"
    
    def test_add_link(self, note_service):
        """Test adding a bidirectional link between notes."""
        # Create two notes
        note_id1 = note_service.create_note(
            title="Note 1",
            content="Content 1."
        )
        note_id2 = note_service.create_note(
            title="Note 2",
            content="Content 2."
        )
        
        # Add a link between them
        note_service.add_link(
            source_id=note_id1,
            target_id=note_id2,
            relationship_type="related_to",
            strength=0.8,
            context="These notes are related"
        )
        
        # Retrieve both notes
        note1 = note_service.get_note(note_id1)
        note2 = note_service.get_note(note_id2)
        
        # Verify the link in note1
        assert len(note1.linked_items) == 1
        assert note1.linked_items[0].source_id == note_id1
        assert note1.linked_items[0].target_id == note_id2
        assert note1.linked_items[0].relationship_type == "related_to"
        assert note1.linked_items[0].strength == 0.8
        assert note1.linked_items[0].context == "These notes are related"
        
        # Verify the link in note2
        assert len(note2.linked_items) == 1
        assert note2.linked_items[0].source_id == note_id2
        assert note2.linked_items[0].target_id == note_id1
        assert note2.linked_items[0].relationship_type == "related_to"
        assert note2.linked_items[0].strength == 0.8
        assert note2.linked_items[0].context == "These notes are related"
    
    def test_create_collection(self, note_service):
        """Test creating a note collection."""
        # Create some notes
        note_id1 = note_service.create_note(title="Note 1", content="Content 1")
        note_id2 = note_service.create_note(title="Note 2", content="Content 2")
        
        # Create a collection
        collection_id = note_service.create_collection(
            name="Test Collection",
            description="A collection for testing",
            note_ids=[note_id1, note_id2],
            tags=["test", "collection"]
        )
        
        # Retrieve the collection
        collection = note_service.get_collection(collection_id)
        
        # Verify the collection
        assert collection.name == "Test Collection"
        assert collection.description == "A collection for testing"
        assert collection.note_ids == {note_id1, note_id2}
        assert collection.tags == {"test", "collection"}
    
    def test_add_note_to_collection(self, note_service):
        """Test adding a note to a collection."""
        # Create a note and a collection
        note_id = note_service.create_note(title="Note", content="Content")
        collection_id = note_service.create_collection(name="Collection")
        
        # Add the note to the collection
        note_service.add_note_to_collection(collection_id, note_id)
        
        # Retrieve the collection
        collection = note_service.get_collection(collection_id)
        
        # Verify the note was added
        assert note_id in collection.note_ids
    
    def test_remove_note_from_collection(self, note_service):
        """Test removing a note from a collection."""
        # Create a note and a collection with the note
        note_id = note_service.create_note(title="Note", content="Content")
        collection_id = note_service.create_collection(
            name="Collection",
            note_ids=[note_id]
        )
        
        # Verify the note is in the collection
        collection = note_service.get_collection(collection_id)
        assert note_id in collection.note_ids
        
        # Remove the note from the collection
        note_service.remove_note_from_collection(collection_id, note_id)
        
        # Retrieve the updated collection
        collection = note_service.get_collection(collection_id)
        
        # Verify the note was removed
        assert note_id not in collection.note_ids
    
    def test_search_notes(self, note_service):
        """Test searching for notes based on various criteria."""
        # Create test notes
        note_id1 = note_service.create_note(
            title="Research on Machine Learning",
            content="This note discusses ML techniques. Citation: @smith2020.",
            note_type=NoteType.LITERATURE,
            tags=["research", "machine_learning"],
            project="ML Project"
        )
        note_id2 = note_service.create_note(
            title="Meeting Notes",
            content="Notes from team meeting.",
            note_type=NoteType.MEETING,
            tags=["meeting", "team"],
            project="ML Project"
        )
        note_id3 = note_service.create_note(
            title="Ideas for Future Research",
            content="Some ideas for future work.",
            note_type=NoteType.IDEA,
            tags=["research", "ideas"],
            project="Next Gen"
        )
        
        # Search by text
        results = note_service.search_notes(text="machine learning")
        assert len(results) == 1
        assert note_id1 in results
        
        # Search by tags
        results = note_service.search_notes(tags=["research"])
        assert len(results) == 2
        assert note_id1 in results
        assert note_id3 in results
        
        # Search by note type
        results = note_service.search_notes(note_type=NoteType.MEETING)
        assert len(results) == 1
        assert note_id2 in results
        
        # Search by project
        results = note_service.search_notes(project="ML Project")
        assert len(results) == 2
        assert note_id1 in results
        assert note_id2 in results
        
        # Search by citation key
        results = note_service.search_notes(citation_key="smith2020")
        assert len(results) == 1
        assert note_id1 in results
        
        # Search with multiple criteria
        results = note_service.search_notes(
            text="research",
            tags=["research"],
            project="Next Gen"
        )
        assert len(results) == 1
        assert note_id3 in results
    
    def test_export_notes_to_markdown(self, note_service, tmpdir):
        """Test exporting notes to Markdown files."""
        # Create a test note
        note_id = note_service.create_note(
            title="Export Test",
            content="This note should be exported to Markdown.",
            tags=["export", "test"]
        )
        
        # Export the note
        export_dir = Path(tmpdir) / "exports"
        exported_files = note_service.export_notes_to_markdown([note_id], export_dir)
        
        # Verify the export
        assert len(exported_files) == 1
        assert exported_files[0].exists()
        
        # Check the content of the exported file
        with open(exported_files[0], 'r') as f:
            content = f.read()
            assert "# Export Test" in content
            assert "This note should be exported to Markdown." in content
            # Tags are stored in a set, so the order might differ
            assert "**Tags:**" in content
            assert "export" in content
            assert "test" in content