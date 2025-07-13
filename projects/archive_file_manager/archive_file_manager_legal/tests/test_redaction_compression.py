"""Tests for redaction-aware compression module."""

import json
import zipfile
from pathlib import Path
import pytest

from legal_archive.redaction_compression import RedactionAwareCompressor
from legal_archive.models import Redaction, RedactionLevel, DocumentMetadata


class TestRedactionAwareCompressor:
    """Test redaction-aware compression functionality."""

    def test_initialization(self):
        """Test compressor initialization."""
        compressor = RedactionAwareCompressor(
            compression_level=9, encrypt_redacted_content=True
        )
        
        assert compressor.compression_level == 9
        assert compressor.encrypt_redacted_content is True
        assert compressor._encryption_key is not None
        assert compressor._fernet is not None
        assert compressor.redactions == {}
        assert compressor.redaction_audit == []

    def test_add_redaction(self, sample_redactions):
        """Test adding redactions."""
        compressor = RedactionAwareCompressor()
        redaction = sample_redactions[0]
        
        compressor.add_redaction(redaction, original_content=b"sensitive data")
        
        assert redaction.document_id in compressor.redactions
        assert redaction in compressor.redactions[redaction.document_id]
        assert len(compressor.redaction_audit) == 1
        
        audit_entry = compressor.redaction_audit[0]
        assert audit_entry["redaction_id"] == redaction.redaction_id
        assert audit_entry["applied_by"] == redaction.applied_by

    def test_compress_with_redactions(self, temp_dir, create_test_pdf, sample_documents, sample_redactions):
        """Test compression with redaction preservation."""
        compressor = RedactionAwareCompressor()
        
        # Add redactions
        for redaction in sample_redactions:
            compressor.add_redaction(redaction)
        
        # Create test documents
        documents = []
        for doc in sample_documents[:2]:
            pdf_path = create_test_pdf(doc.file_name)
            documents.append((pdf_path, doc))
        
        # Compress
        output_path = temp_dir / "archive.zip"
        stats = compressor.compress_with_redactions(
            documents, output_path, preserve_structure=True
        )
        
        assert output_path.exists()
        assert stats["total_documents"] == 2
        assert stats["redacted_documents"] > 0
        assert stats["compressed_size"] > 0
        assert 0 <= stats["compression_ratio"] <= 1
        
        # Verify archive contents
        with zipfile.ZipFile(output_path, "r") as archive:
            namelist = archive.namelist()
            assert "_redaction_audit.json" in namelist
            
            # Check for redaction metadata files
            redaction_files = [f for f in namelist if "_redactions.json" in f]
            assert len(redaction_files) > 0

    def test_extract_with_redaction_level(self, temp_dir, create_test_pdf, sample_documents, sample_redactions):
        """Test extraction with redaction level filtering."""
        compressor = RedactionAwareCompressor()
        
        # Add redactions
        for redaction in sample_redactions:
            compressor.add_redaction(redaction)
        
        # Create and compress documents
        documents = [(create_test_pdf(doc.file_name), doc) for doc in sample_documents[:2]]
        archive_path = temp_dir / "archive.zip"
        compressor.compress_with_redactions(documents, archive_path)
        
        # Extract with different access levels
        output_dir = temp_dir / "extracted"
        
        # User with high access
        high_access_files = compressor.extract_with_redaction_level(
            archive_path,
            output_dir / "high",
            {RedactionLevel.PUBLIC, RedactionLevel.CONFIDENTIAL, RedactionLevel.ATTORNEY_CLIENT},
            "user_high"
        )
        
        # User with limited access
        low_access_files = compressor.extract_with_redaction_level(
            archive_path,
            output_dir / "low",
            {RedactionLevel.PUBLIC},
            "user_low"
        )
        
        # High access user should get more files
        assert len(high_access_files) >= len(low_access_files)

    def test_verify_redaction_integrity(self, temp_dir, create_test_pdf, sample_documents, sample_redactions):
        """Test redaction integrity verification."""
        compressor = RedactionAwareCompressor()
        
        # Add redactions and compress
        for redaction in sample_redactions:
            compressor.add_redaction(redaction)
        
        documents = [(create_test_pdf(doc.file_name), doc) for doc in sample_documents[:2]]
        archive_path = temp_dir / "archive.zip"
        compressor.compress_with_redactions(documents, archive_path)
        
        # Verify integrity
        is_valid, issues = compressor.verify_redaction_integrity(archive_path)
        
        assert is_valid is True
        assert len(issues) == 0

    def test_verify_redaction_integrity_corrupted(self, temp_dir):
        """Test verification of corrupted archive."""
        compressor = RedactionAwareCompressor()
        
        # Create corrupted archive (missing audit trail)
        archive_path = temp_dir / "corrupted.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("document.pdf", b"content")
        
        is_valid, issues = compressor.verify_redaction_integrity(archive_path)
        
        assert is_valid is False
        assert len(issues) > 0
        assert any("audit trail" in issue for issue in issues)

    def test_encryption_key_management(self):
        """Test encryption key generation and management."""
        compressor1 = RedactionAwareCompressor(encrypt_redacted_content=True)
        compressor2 = RedactionAwareCompressor(encrypt_redacted_content=True)
        
        # Each instance should have unique key
        assert compressor1._encryption_key != compressor2._encryption_key
        
        # Without encryption
        compressor3 = RedactionAwareCompressor(encrypt_redacted_content=False)
        assert compressor3._encryption_key is None
        assert compressor3._fernet is None

    def test_redaction_audit_trail(self, sample_redactions):
        """Test comprehensive audit trail generation."""
        compressor = RedactionAwareCompressor()
        
        # Add multiple redactions
        for i, redaction in enumerate(sample_redactions):
            compressor.add_redaction(
                redaction,
                original_content=f"content_{i}".encode()
            )
        
        assert len(compressor.redaction_audit) == len(sample_redactions)
        
        # Check audit entries
        for audit_entry in compressor.redaction_audit:
            assert "redaction_id" in audit_entry
            assert "document_id" in audit_entry
            assert "applied_by" in audit_entry
            assert "applied_date" in audit_entry
            assert "redaction_level" in audit_entry
            assert "reason" in audit_entry

    def test_apply_redactions_to_pdf(self, temp_dir, create_test_pdf):
        """Test applying redactions to PDF documents."""
        compressor = RedactionAwareCompressor()
        pdf_path = create_test_pdf("test.pdf", "Sensitive information here")
        
        redaction = Redaction(
            redaction_id="red_001",
            document_id="doc_001",
            page_number=1,
            coordinates=[100, 100, 200, 150],
            redaction_level=RedactionLevel.CONFIDENTIAL,
            reason="Contains SSN",
            applied_by="Admin"
        )
        
        redacted_content = compressor._apply_redactions_to_document(
            pdf_path, [redaction]
        )
        
        assert redacted_content is not None
        assert len(redacted_content) > 0
        assert redacted_content.startswith(b"%PDF")

    def test_apply_redactions_to_image(self, temp_dir, create_test_image):
        """Test applying redactions to image documents."""
        compressor = RedactionAwareCompressor()
        img_path = create_test_image("scan.png")
        
        redaction = Redaction(
            redaction_id="red_002",
            document_id="doc_002",
            page_number=1,
            coordinates=[10, 10, 50, 50],
            redaction_level=RedactionLevel.CONFIDENTIAL,
            reason="Contains signature",
            applied_by="Admin"
        )
        
        redacted_content = compressor._apply_redactions_to_document(
            img_path, [redaction]
        )
        
        assert redacted_content is not None
        assert len(redacted_content) > 0

    def test_redaction_level_hierarchy(self):
        """Test redaction level access hierarchy."""
        compressor = RedactionAwareCompressor()
        
        # Test access hierarchy
        test_cases = [
            ({RedactionLevel.SEALED}, {RedactionLevel.SEALED}, True),
            ({RedactionLevel.SEALED}, {RedactionLevel.CONFIDENTIAL}, False),
            ({RedactionLevel.PUBLIC}, {RedactionLevel.SEALED}, True),
            ({RedactionLevel.ATTORNEY_CLIENT}, {RedactionLevel.ATTORNEY_CLIENT, RedactionLevel.PUBLIC}, True),
        ]
        
        for doc_levels, allowed_levels, expected in test_cases:
            result = compressor._can_access_document(doc_levels, allowed_levels)
            assert result == expected

    def test_compression_performance(self, temp_dir, create_test_pdf, sample_documents):
        """Test compression performance benchmarks."""
        compressor = RedactionAwareCompressor(compression_level=1)  # Fast compression
        
        # Create many documents
        documents = []
        for i in range(50):
            doc = DocumentMetadata(
                document_id=f"doc_{i:03d}",
                file_name=f"document_{i}.pdf",
                document_type="discovery",
                page_count=20,
                file_size=1000000,
                checksum=f"hash_{i}",
            )
            pdf_path = create_test_pdf(doc.file_name, f"Content for document {i}" * 100)
            documents.append((pdf_path, doc))
        
        # Add some redactions
        for i in range(10):
            redaction = Redaction(
                redaction_id=f"red_{i:03d}",
                document_id=f"doc_{i:03d}",
                page_number=1,
                coordinates=[0, 0, 100, 100],
                redaction_level=RedactionLevel.CONFIDENTIAL,
                reason="Test redaction",
                applied_by="Test"
            )
            compressor.add_redaction(redaction)
        
        # Compress
        import time
        output_path = temp_dir / "large_archive.zip"
        start_time = time.time()
        
        stats = compressor.compress_with_redactions(documents, output_path)
        
        elapsed_time = time.time() - start_time
        
        # Should compress 50 documents reasonably quickly
        assert elapsed_time < 10.0  # Should complete in under 10 seconds
        assert stats["total_documents"] == 50
        assert stats["redacted_documents"] == 10
        assert stats["compression_ratio"] > 0

    def test_preserve_redaction_modifications(self, sample_redactions):
        """Test that redacted content cannot be recovered."""
        compressor = RedactionAwareCompressor(encrypt_redacted_content=True)
        
        sensitive_content = b"This is sensitive information"
        redaction = sample_redactions[0]
        
        compressor.add_redaction(redaction, original_content=sensitive_content)
        
        # The sensitive content should be encrypted in audit trail
        audit_entry = compressor.redaction_audit[0]
        assert "encrypted_content_hash" in audit_entry
        
        # Original content should not appear in plain text
        audit_json = json.dumps(compressor.redaction_audit)
        assert sensitive_content.decode() not in audit_json