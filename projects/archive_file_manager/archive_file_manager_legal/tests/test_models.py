"""Tests for data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from pathlib import Path
from legal_archive.models import (
    DocumentMetadata,
    DocumentType,
    Redaction,
    RedactionLevel,
    CrossReference,
    TOCEntry,
    HierarchyNode,
    OCRResult,
    ArchiveManifest,
)


class TestDocumentMetadata:
    """Test DocumentMetadata model."""

    def test_valid_document_metadata(self):
        """Test creating valid document metadata."""
        metadata = DocumentMetadata(
            document_id="doc_001",
            file_name="test.pdf",
            document_type=DocumentType.PLEADING,
            page_count=10,
            file_size=1024,
            checksum="abc123"
        )
        
        assert metadata.document_id == "doc_001"
        assert metadata.file_name == "test.pdf"
        assert metadata.document_type == DocumentType.PLEADING
        assert metadata.page_count == 10
        assert metadata.file_size == 1024
        assert metadata.checksum == "abc123"
        assert isinstance(metadata.created_date, datetime)

    def test_optional_fields(self):
        """Test optional fields in DocumentMetadata."""
        metadata = DocumentMetadata(
            document_id="doc_002",
            file_name="test2.pdf",
            document_type=DocumentType.MOTION,
            page_count=5,
            file_size=512,
            checksum="def456",
            case_number="2023-CV-001",
            party_name="Smith Corp"
        )
        
        assert metadata.case_number == "2023-CV-001"
        assert metadata.party_name == "Smith Corp"

    def test_document_type_enum(self):
        """Test all document type enum values."""
        for doc_type in DocumentType:
            metadata = DocumentMetadata(
                document_id=f"doc_{doc_type.value}",
                file_name=f"test_{doc_type.value}.pdf",
                document_type=doc_type,
                page_count=1,
                file_size=100,
                checksum="test"
            )
            assert metadata.document_type == doc_type

    def test_invalid_document_metadata(self):
        """Test validation errors for invalid data."""
        with pytest.raises(ValidationError):
            DocumentMetadata(
                document_id="doc_001",
                file_name="test.pdf",
                document_type=DocumentType.PLEADING,
                page_count=0,  # Invalid: must be > 0
                file_size=1024,
                checksum="abc123"
            )

    def test_negative_values(self):
        """Test that negative values are rejected."""
        with pytest.raises(ValidationError):
            DocumentMetadata(
                document_id="doc_001",
                file_name="test.pdf",
                document_type=DocumentType.PLEADING,
                page_count=-1,  # Negative page count
                file_size=1024,
                checksum="abc123"
            )


class TestRedaction:
    """Test Redaction model."""

    def test_valid_redaction(self):
        """Test creating valid redaction."""
        redaction = Redaction(
            redaction_id="red_001",
            document_id="doc_001",
            page_number=1,
            coordinates=[100, 200, 300, 400],
            redaction_level=RedactionLevel.CONFIDENTIAL,
            reason="Contains PII",
            applied_by="Attorney"
        )
        
        assert redaction.redaction_id == "red_001"
        assert redaction.document_id == "doc_001"
        assert redaction.page_number == 1
        assert redaction.coordinates == [100, 200, 300, 400]
        assert redaction.redaction_level == RedactionLevel.CONFIDENTIAL
        assert redaction.reason == "Contains PII"
        assert redaction.applied_by == "Attorney"

    def test_redaction_levels(self):
        """Test all redaction level enum values."""
        for level in RedactionLevel:
            redaction = Redaction(
                redaction_id=f"red_{level.value}",
                document_id="doc_001",
                page_number=1,
                coordinates=[0, 0, 100, 100],
                redaction_level=level,
                reason="Test reason",
                applied_by="Test User"
            )
            assert redaction.redaction_level == level

    def test_redaction_defaults(self):
        """Test redaction default values."""
        redaction = Redaction(
            redaction_id="red_002",
            document_id="doc_001",
            page_number=1,
            coordinates=[100, 200, 300, 400],
            redaction_level=RedactionLevel.ATTORNEY_CLIENT,
            reason="Privileged communication",
            applied_by="Attorney"
        )
        
        assert redaction.is_permanent is True
        assert isinstance(redaction.applied_date, datetime)


class TestCrossReference:
    """Test CrossReference model."""

    def test_valid_cross_reference(self):
        """Test creating valid cross reference."""
        ref = CrossReference(
            reference_id="ref_001",
            source_document_id="doc_001",
            target_document_id="doc_002",
            reference_type="citation",
            reference_text="See Document 2"
        )
        
        assert ref.reference_id == "ref_001"
        assert ref.source_document_id == "doc_001"
        assert ref.target_document_id == "doc_002"
        assert ref.reference_type == "citation"
        assert ref.reference_text == "See Document 2"
        assert ref.is_bidirectional is False

    def test_bidirectional_reference(self):
        """Test bidirectional reference."""
        ref = CrossReference(
            reference_id="ref_002",
            source_document_id="doc_001",
            target_document_id="doc_002",
            reference_type="related",
            reference_text="Related to",
            is_bidirectional=True
        )
        
        assert ref.is_bidirectional is True

    def test_page_references(self):
        """Test page-specific references."""
        ref = CrossReference(
            reference_id="ref_003",
            source_document_id="doc_001",
            target_document_id="doc_002",
            source_page=5,
            target_page=10,
            reference_type="page_ref",
            reference_text="See page 10"
        )
        
        assert ref.source_page == 5
        assert ref.target_page == 10


class TestTOCEntry:
    """Test TOCEntry model."""

    def test_valid_toc_entry(self):
        """Test creating valid TOC entry."""
        entry = TOCEntry(
            entry_id="toc_001",
            document_id="doc_001",
            title="Chapter 1",
            page_number=1,
            level=0
        )
        
        assert entry.entry_id == "toc_001"
        assert entry.document_id == "doc_001"
        assert entry.title == "Chapter 1"
        assert entry.page_number == 1
        assert entry.level == 0
        assert entry.children == []

    def test_toc_with_children(self):
        """Test TOC entry with children."""
        entry = TOCEntry(
            entry_id="toc_001",
            document_id="doc_001",
            title="Chapter 1",
            page_number=1,
            level=0,
            children=["toc_002", "toc_003"]
        )
        
        assert len(entry.children) == 2
        assert "toc_002" in entry.children

    def test_toc_with_summary(self):
        """Test TOC entry with summary."""
        entry = TOCEntry(
            entry_id="toc_001",
            document_id="doc_001",
            title="Chapter 1",
            page_number=1,
            level=0,
            summary="This chapter covers the introduction"
        )
        
        assert entry.summary == "This chapter covers the introduction"


class TestHierarchyNode:
    """Test HierarchyNode model."""

    def test_valid_hierarchy_node(self):
        """Test creating valid hierarchy node."""
        node = HierarchyNode(
            node_id="node_001",
            name="Pleadings",
            node_type="category"
        )
        
        assert node.node_id == "node_001"
        assert node.name == "Pleadings"
        assert node.node_type == "category"
        assert node.children == []
        assert node.documents == []

    def test_hierarchy_with_relationships(self):
        """Test hierarchy node with parent and children."""
        node = HierarchyNode(
            node_id="node_002",
            name="Motions",
            node_type="category",
            parent_id="node_001",
            children=["node_003", "node_004"],
            documents=["doc_001", "doc_002"]
        )
        
        assert node.parent_id == "node_001"
        assert len(node.children) == 2
        assert len(node.documents) == 2

    def test_hierarchy_metadata(self):
        """Test hierarchy node with metadata."""
        node = HierarchyNode(
            node_id="node_003",
            name="Discovery",
            node_type="phase",
            metadata={"phase": "initial", "deadline": "2023-12-31"}
        )
        
        assert node.metadata["phase"] == "initial"
        assert node.metadata["deadline"] == "2023-12-31"


class TestOCRModels:
    """Test OCR-related models."""

    def test_ocr_result(self):
        """Test OCRResult model."""
        result = OCRResult(
            document_id="doc_001",
            original_path=Path("/tmp/doc.pdf"),
            text_content="This is the extracted text",
            confidence_score=0.95,
            language="en",
            page_count=2,
            processing_time=1.5
        )
        
        assert result.document_id == "doc_001"
        assert result.original_path == Path("/tmp/doc.pdf")
        assert result.text_content == "This is the extracted text"
        assert result.confidence_score == 0.95
        assert result.language == "en"
        assert result.page_count == 2
        assert result.processing_time == 1.5

    def test_ocr_with_error(self):
        """Test OCR result with error message."""
        result = OCRResult(
            document_id="doc_001",
            original_path=Path("/tmp/doc.pdf"),
            text_content="",
            confidence_score=0.0,
            page_count=1,
            processing_time=0.1,
            error_message="Failed to process PDF"
        )
        
        assert result.error_message == "Failed to process PDF"
        assert result.confidence_score == 0.0

    def test_archive_manifest(self):
        """Test ArchiveManifest model."""
        manifest = ArchiveManifest(
            archive_id="archive_001",
            archive_name="Case Archive 2023",
            case_number="2023-CV-001",
            creator="Legal Team",
            total_documents=50,
            total_size=1024*1024*100,  # 100MB
            compression_ratio=0.75,
            cross_references_count=25
        )
        
        assert manifest.archive_id == "archive_001"
        assert manifest.archive_name == "Case Archive 2023"
        assert manifest.case_number == "2023-CV-001"
        assert manifest.creator == "Legal Team"
        assert manifest.total_documents == 50
        assert manifest.compression_ratio == 0.75
        assert manifest.has_ocr is False
        assert manifest.has_redactions is False


class TestModelValidation:
    """Test model validation edge cases."""

    def test_empty_strings(self):
        """Test that empty strings are accepted where allowed."""
        # Empty checksum is actually allowed
        metadata = DocumentMetadata(
            document_id="doc_001",
            file_name="test.pdf",
            document_type=DocumentType.PLEADING,
            page_count=1,
            file_size=100,
            checksum=""  # Empty checksum is allowed
        )
        assert metadata.checksum == ""

    def test_type_coercion(self):
        """Test that types are properly coerced."""
        metadata = DocumentMetadata(
            document_id="doc_001",
            file_name="test.pdf",
            document_type=DocumentType.PLEADING,
            page_count="10",  # String that can be converted to int
            file_size="1024",  # String that can be converted to int
            checksum="test"
        )
        
        assert metadata.page_count == 10
        assert metadata.file_size == 1024

    def test_datetime_handling(self):
        """Test datetime field handling."""
        now = datetime.now()
        redaction = Redaction(
            redaction_id="red_001",
            document_id="doc_001",
            page_number=1,
            coordinates=[0, 0, 100, 100],
            redaction_level=RedactionLevel.PUBLIC,
            reason="Test",
            applied_by="User",
            applied_date=now
        )
        
        assert redaction.applied_date == now

    def test_set_field_handling(self):
        """Test set field handling."""
        metadata = DocumentMetadata(
            document_id="doc_001",
            file_name="test.pdf",
            document_type=DocumentType.PLEADING,
            page_count=1,
            file_size=100,
            checksum="test",
            tags={"urgent", "confidential"}
        )
        
        assert "urgent" in metadata.tags
        assert "confidential" in metadata.tags
        assert len(metadata.tags) == 2

    def test_dict_field_handling(self):
        """Test dictionary field handling."""
        metadata = DocumentMetadata(
            document_id="doc_001",
            file_name="test.pdf",
            document_type=DocumentType.PLEADING,
            page_count=1,
            file_size=100,
            checksum="test",
            metadata={"author": "John Doe", "version": "1.0"}
        )
        
        assert metadata.metadata["author"] == "John Doe"
        assert metadata.metadata["version"] == "1.0"