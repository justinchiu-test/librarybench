"""Pytest configuration and fixtures."""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import List
import pytest

from legal_archive.models import (
    DocumentMetadata,
    DocumentType,
    Redaction,
    RedactionLevel,
    CrossReference,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_documents() -> List[DocumentMetadata]:
    """Create sample document metadata."""
    return [
        DocumentMetadata(
            document_id="doc_001",
            file_name="complaint.pdf",
            document_type=DocumentType.PLEADING,
            case_number="2023-CV-12345",
            party_name="Smith",
            filing_date=datetime(2023, 1, 15),
            bates_number="SMITH000001",
            page_count=25,
            file_size=1024000,
            checksum="abc123",
        ),
        DocumentMetadata(
            document_id="doc_002",
            file_name="motion_to_dismiss.pdf",
            document_type=DocumentType.MOTION,
            case_number="2023-CV-12345",
            party_name="Jones",
            filing_date=datetime(2023, 2, 1),
            bates_number="JONES000001",
            page_count=15,
            file_size=768000,
            checksum="def456",
        ),
        DocumentMetadata(
            document_id="doc_003",
            file_name="exhibit_a.pdf",
            document_type=DocumentType.EXHIBIT,
            case_number="2023-CV-12345",
            party_name="Smith",
            filing_date=datetime(2023, 3, 1),
            exhibit_number="A",
            page_count=5,
            file_size=256000,
            checksum="ghi789",
        ),
    ]


@pytest.fixture
def sample_redactions() -> List[Redaction]:
    """Create sample redactions."""
    return [
        Redaction(
            redaction_id="red_001",
            document_id="doc_001",
            page_number=3,
            coordinates=[100, 200, 300, 250],
            redaction_level=RedactionLevel.CONFIDENTIAL,
            reason="Contains personal information",
            applied_by="Attorney Smith",
        ),
        Redaction(
            redaction_id="red_002",
            document_id="doc_002",
            page_number=7,
            coordinates=[150, 300, 400, 350],
            redaction_level=RedactionLevel.ATTORNEY_CLIENT,
            reason="Privileged communication",
            applied_by="Attorney Jones",
        ),
    ]


@pytest.fixture
def sample_cross_references() -> List[CrossReference]:
    """Create sample cross-references."""
    return [
        CrossReference(
            reference_id="ref_001",
            source_document_id="doc_001",
            target_document_id="doc_002",
            source_page=10,
            target_page=1,
            reference_type="citation",
            reference_text="See Motion to Dismiss",
        ),
        CrossReference(
            reference_id="ref_002",
            source_document_id="doc_002",
            target_document_id="doc_003",
            source_page=5,
            target_page=1,
            reference_type="exhibit",
            reference_text="Exhibit A",
        ),
    ]


@pytest.fixture
def create_test_pdf(temp_dir):
    """Create a test PDF file."""
    def _create_pdf(filename: str, content: str = "Test content") -> Path:
        pdf_path = temp_dir / filename
        # Create a simple PDF-like file (mock)
        pdf_path.write_bytes(b"%PDF-1.4\n" + content.encode() + b"\n%%EOF")
        return pdf_path
    return _create_pdf


@pytest.fixture
def create_test_image(temp_dir):
    """Create a test image file."""
    def _create_image(filename: str) -> Path:
        from PIL import Image
        
        img_path = temp_dir / filename
        img = Image.new("RGB", (100, 100), color="white")
        img.save(img_path, "PNG")
        return img_path
    return _create_image