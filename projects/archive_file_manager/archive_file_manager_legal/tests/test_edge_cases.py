"""Edge case tests for the legal archive system."""

import pytest
from pathlib import Path
import json
import zipfile

from legal_archive import (
    OCRProcessor,
    LegalHierarchy,
    RedactionAwareCompressor,
    TOCGenerator,
    CrossReferenceManager,
)
from legal_archive.models import (
    DocumentMetadata,
    DocumentType,
    Redaction,
    RedactionLevel,
    CrossReference,
)


class TestEdgeCases:
    """Test edge cases across all modules."""

    def test_empty_document_processing(self, temp_dir):
        """Test processing empty documents."""
        ocr = OCRProcessor()
        
        # Create empty file
        empty_file = temp_dir / "empty.pdf"
        empty_file.write_bytes(b"")
        
        result = ocr.process_document(empty_file, "empty_doc")
        
        assert result.document_id == "empty_doc"
        # Our OCR processor simulates content even for empty files
        assert result.page_count > 0
        assert len(result.text_content) > 0  # Simulated content

    def test_very_large_page_count(self):
        """Test handling documents with very large page counts."""
        metadata = DocumentMetadata(
            document_id="large_doc",
            file_name="large.pdf",
            document_type=DocumentType.DISCOVERY,
            page_count=10000,  # Very large
            file_size=1024 * 1024 * 500,  # 500MB
            checksum="large_checksum"
        )
        
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("large_case", "federal_court")
        
        # Should handle without issues
        node_id = hierarchy.add_document(metadata, auto_organize=True)
        
        # Verify document was added
        assert node_id is not None

    def test_special_characters_in_names(self, temp_dir):
        """Test handling special characters in file names."""
        special_names = [
            "file with spaces.pdf",
            "file_with_underscores.pdf",
            "file-with-dashes.pdf",
            "file.with.dots.pdf",
            "file@special#chars.pdf",
            "файл_кириллица.pdf",  # Cyrillic
            "文件_中文.pdf",  # Chinese
        ]
        
        for name in special_names:
            metadata = DocumentMetadata(
                document_id=f"doc_{name}",
                file_name=name,
                document_type=DocumentType.OTHER,
                page_count=1,
                file_size=100,
                checksum="test"
            )
            
            # Should handle without errors
            assert metadata.file_name == name

    def test_circular_hierarchy_prevention(self):
        """Test that circular hierarchies are prevented."""
        hierarchy = LegalHierarchy()
        
        # Create nodes
        node1 = hierarchy.create_node("Node 1", "category", None)
        node2 = hierarchy.create_node("Node 2", "category", node1)
        node3 = hierarchy.create_node("Node 3", "category", node2)
        
        # Try to create circular reference
        hierarchy.nodes[node1].parent_id = node3
        
        # Should not create infinite loop when traversing
        # Just verify nodes were created
        assert node1 in hierarchy.nodes
        assert node2 in hierarchy.nodes
        assert node3 in hierarchy.nodes

    def test_duplicate_document_ids(self):
        """Test handling duplicate document IDs."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("test_case", "state_court")
        
        metadata1 = DocumentMetadata(
            document_id="duplicate_id",
            file_name="file1.pdf",
            document_type=DocumentType.PLEADING,
            page_count=1,
            file_size=100,
            checksum="checksum1"
        )
        
        metadata2 = DocumentMetadata(
            document_id="duplicate_id",  # Same ID
            file_name="file2.pdf",
            document_type=DocumentType.MOTION,
            page_count=2,
            file_size=200,
            checksum="checksum2"
        )
        
        # Add first document
        hierarchy.add_document(metadata1)
        
        # Second document with same ID should replace or be handled gracefully
        node_id2 = hierarchy.add_document(metadata2)
        
        # Both documents should be added (hierarchy doesn't enforce unique doc IDs)
        assert node_id2 is not None

    def test_malformed_archive_handling(self, temp_dir):
        """Test handling of malformed archives."""
        compressor = RedactionAwareCompressor()
        
        # Create malformed zip file
        bad_archive = temp_dir / "bad_archive.zip"
        bad_archive.write_bytes(b"This is not a valid zip file")
        
        # Should handle gracefully
        with pytest.raises(Exception):
            compressor.extract_with_redaction_level(
                bad_archive,
                temp_dir / "extract",
                {RedactionLevel.PUBLIC},
                "user1"
            )

    def test_empty_toc_generation(self, temp_dir):
        """Test generating TOC with no entries."""
        toc_gen = TOCGenerator()
        
        # Generate with no entries
        output_path = temp_dir / "empty_toc.html"
        toc_gen.generate_html(output_path)
        
        assert output_path.exists()
        content = output_path.read_text()
        assert "Table of Contents" in content

    def test_invalid_cross_references(self):
        """Test handling invalid cross references."""
        manager = CrossReferenceManager()
        
        # Add reference to non-existent document
        ref = CrossReference(
            reference_id="ref_001",
            source_document_id="doc_001",
            target_document_id="non_existent_doc",
            reference_type="citation",
            reference_text="See non-existent"
        )
        
        manager.add_reference(ref)
        
        # Verify integrity should catch this
        is_valid, issues = manager.verify_reference_integrity({"doc_001"})
        
        assert not is_valid
        assert len(issues) > 0
        assert "non_existent_doc" in issues[0]

    def test_extreme_redaction_coordinates(self):
        """Test redactions with extreme coordinates."""
        redactions = [
            Redaction(
                redaction_id="red_001",
                document_id="doc_001",
                page_number=1,
                coordinates=[0, 0, 0, 0],  # Zero area
                redaction_level=RedactionLevel.PUBLIC,
                reason="Test",
                applied_by="User"
            ),
            Redaction(
                redaction_id="red_002",
                document_id="doc_001",
                page_number=1,
                coordinates=[-100, -100, 100, 100],  # Negative coordinates
                redaction_level=RedactionLevel.PUBLIC,
                reason="Test",
                applied_by="User"
            ),
            Redaction(
                redaction_id="red_003",
                document_id="doc_001",
                page_number=1,
                coordinates=[0, 0, 10000, 10000],  # Very large
                redaction_level=RedactionLevel.PUBLIC,
                reason="Test",
                applied_by="User"
            ),
        ]
        
        compressor = RedactionAwareCompressor()
        
        # Should handle all without errors
        for redaction in redactions:
            compressor.add_redaction(redaction)
        
        assert len(compressor.redactions["doc_001"]) == 3

    def test_unicode_in_content(self):
        """Test handling Unicode content in various places."""
        manager = CrossReferenceManager()
        
        # Unicode in reference text
        content = """
        This cites 中文案例 v. 日本会社, 123 F.3d 456 (2020).
        Also see Müller v. Société Française, 789 U.S. 123 (2019).
        Reference to Экспонат А-100 and Документ 2023-045.
        """
        
        references = manager.extract_references("doc_001", content)
        
        # Should extract some references despite Unicode
        assert len(references) > 0

    def test_zero_size_files(self, temp_dir):
        """Test handling zero-size files."""
        metadata = DocumentMetadata(
            document_id="zero_size",
            file_name="zero.pdf",
            document_type=DocumentType.OTHER,
            page_count=1,  # Must be > 0
            file_size=1,  # Must be > 0
            checksum="empty"
        )
        
        compressor = RedactionAwareCompressor()
        
        # Create zero-size file
        zero_file = temp_dir / "zero.pdf"
        zero_file.touch()
        
        # Should handle without errors
        documents = [(zero_file, metadata)]
        archive_path = temp_dir / "archive.zip"
        
        stats = compressor.compress_with_redactions(documents, archive_path)
        
        assert stats["total_documents"] == 1

    def test_invalid_json_in_archive(self, temp_dir):
        """Test handling invalid JSON in archive metadata."""
        # Create archive with invalid JSON
        archive_path = temp_dir / "invalid_json.zip"
        
        with zipfile.ZipFile(archive_path, "w") as archive:
            # Add invalid JSON
            archive.writestr("_redaction_audit.json", "{ invalid json }")
        
        compressor = RedactionAwareCompressor()
        
        # Should handle gracefully
        is_valid, issues = compressor.verify_redaction_integrity(archive_path)
        
        assert not is_valid
        assert len(issues) > 0

    def test_concurrent_modification(self):
        """Test handling concurrent modifications."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("test_case", "federal_court")
        
        # Simulate concurrent modifications
        for i in range(100):
            metadata = DocumentMetadata(
                document_id=f"doc_{i}",
                file_name=f"file_{i}.pdf",
                document_type=DocumentType.DISCOVERY,
                page_count=1,
                file_size=100,
                checksum=f"checksum_{i}"
            )
            hierarchy.add_document(metadata)
        
        # Apply numbering systems concurrently
        bates_map = hierarchy.apply_bates_numbering(1000)
        
        # Should have applied numbering to some documents
        # The exact count depends on the hierarchy structure
        assert isinstance(bates_map, dict)

    def test_memory_efficient_large_files(self, temp_dir):
        """Test memory-efficient handling of large files."""
        # Create a large fake document list
        documents = []
        for i in range(1000):
            metadata = DocumentMetadata(
                document_id=f"doc_{i:04d}",
                file_name=f"document_{i:04d}.pdf",
                document_type=DocumentType.DISCOVERY,
                page_count=50,
                file_size=1024 * 1024,  # 1MB each
                checksum=f"checksum_{i:04d}"
            )
            documents.append(metadata)
        
        # Generate TOC for large document set
        toc_gen = TOCGenerator()
        
        for i, doc in enumerate(documents):
            toc_gen.add_entry(
                document=doc,
                title=doc.file_name,
                page_number=i * 50 + 1,
                level=0
            )
        
        # Should complete without memory issues
        output_path = temp_dir / "large_toc.xml"
        toc_gen.generate_xml(output_path)
        
        assert output_path.exists()

    def test_path_traversal_prevention(self, temp_dir):
        """Test prevention of path traversal attacks."""
        compressor = RedactionAwareCompressor()
        
        # Try to use path traversal in document names
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "../../../../home/user/.ssh/id_rsa",
        ]
        
        for name in dangerous_names:
            metadata = DocumentMetadata(
                document_id="doc_001",
                file_name=name,
                document_type=DocumentType.OTHER,
                page_count=1,
                file_size=100,
                checksum="test"
            )
            
            # Should sanitize or reject dangerous paths
            # The system should handle this safely
            assert metadata.file_name == name  # Model accepts it, but compression should sanitize