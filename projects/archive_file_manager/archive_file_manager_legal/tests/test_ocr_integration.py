"""Tests for OCR integration module."""

from pathlib import Path
import pytest
from unittest.mock import Mock, patch

from legal_archive.ocr_integration import OCRProcessor
from legal_archive.models import DocumentMetadata, DocumentType


class TestOCRProcessor:
    """Test OCR processor functionality."""

    def test_initialization(self):
        """Test OCR processor initialization."""
        processor = OCRProcessor(min_confidence=0.8, languages=["en", "es"], max_workers=2)
        
        assert processor.min_confidence == 0.8
        assert processor.languages == ["en", "es"]
        assert processor.max_workers == 2
        assert processor._ocr_cache == {}

    def test_process_pdf_document(self, temp_dir, create_test_pdf):
        """Test processing PDF documents."""
        processor = OCRProcessor()
        pdf_path = create_test_pdf("test.pdf", "Legal document content")
        
        result = processor.process_document(pdf_path, "doc_001")
        
        assert result.document_id == "doc_001"
        assert result.original_path == pdf_path
        assert result.text_content != ""
        assert result.confidence_score > 0
        assert result.page_count > 0
        assert result.error_message is None

    def test_process_image_document(self, temp_dir, create_test_image):
        """Test processing image documents."""
        processor = OCRProcessor()
        img_path = create_test_image("scan.png")
        
        result = processor.process_document(img_path, "doc_002")
        
        assert result.document_id == "doc_002"
        assert result.original_path == img_path
        assert result.text_content != ""
        assert result.confidence_score > 0
        assert result.page_count == 1
        assert result.error_message is None

    def test_process_unsupported_format(self, temp_dir):
        """Test processing unsupported file formats."""
        processor = OCRProcessor()
        unsupported_path = temp_dir / "test.xyz"
        unsupported_path.write_text("content")
        
        result = processor.process_document(unsupported_path, "doc_003")
        
        assert result.document_id == "doc_003"
        assert result.text_content == ""
        assert result.confidence_score == 0.0
        assert result.error_message is not None
        assert "Unsupported file type" in result.error_message

    def test_batch_processing(self, temp_dir, create_test_pdf, create_test_image):
        """Test batch processing of multiple documents."""
        processor = OCRProcessor(max_workers=2)
        
        documents = [
            (create_test_pdf("doc1.pdf"), "doc_001"),
            (create_test_pdf("doc2.pdf"), "doc_002"),
            (create_test_image("doc3.png"), "doc_003"),
        ]
        
        results = processor.batch_process(documents)
        
        assert len(results) == 3
        assert all(r.confidence_score > 0 for r in results)
        assert all(r.text_content != "" for r in results)

    def test_ocr_caching(self, temp_dir, create_test_pdf):
        """Test OCR result caching."""
        processor = OCRProcessor()
        pdf_path = create_test_pdf("cached.pdf")
        
        # First processing
        result1 = processor.process_document(pdf_path, "doc_001")
        
        # Second processing (should use cache)
        result2 = processor.process_document(pdf_path, "doc_001")
        
        assert result1.text_content == result2.text_content
        assert len(processor._ocr_cache) == 1

    def test_quality_metrics(self, temp_dir, create_test_pdf):
        """Test OCR quality metrics calculation."""
        processor = OCRProcessor(min_confidence=0.7)
        
        documents = [
            (create_test_pdf("high_quality.pdf"), "doc_001"),
            (create_test_pdf("medium_quality.pdf"), "doc_002"),
        ]
        
        results = processor.batch_process(documents)
        metrics = processor.get_quality_metrics(results)
        
        assert "average_confidence" in metrics
        assert "success_rate" in metrics
        assert "total_pages" in metrics
        assert "processing_rate" in metrics
        assert metrics["success_rate"] > 0

    def test_store_ocr_metadata(self, sample_documents):
        """Test storing OCR metadata with document."""
        processor = OCRProcessor(min_confidence=0.8)
        document = sample_documents[0]
        
        # High confidence result
        high_conf_result = Mock(
            confidence_score=0.9,
            error_message=None
        )
        processor.store_ocr_metadata(high_conf_result, document)
        
        assert "ocr_processed" in document.tags
        assert "ocr_high_confidence" in document.tags
        
        # Low confidence result
        document.tags.clear()
        low_conf_result = Mock(
            confidence_score=0.5,
            error_message=None
        )
        processor.store_ocr_metadata(low_conf_result, document)
        
        assert "ocr_processed" in document.tags
        assert "ocr_low_confidence" in document.tags
        
        # Error result
        document.tags.clear()
        error_result = Mock(
            confidence_score=0.0,
            error_message="OCR failed"
        )
        processor.store_ocr_metadata(error_result, document)
        
        assert "ocr_error" in document.tags

    def test_concurrent_processing_error_handling(self, temp_dir):
        """Test error handling in concurrent processing."""
        processor = OCRProcessor(max_workers=2)
        
        # Mix of valid and invalid documents
        documents = [
            (temp_dir / "valid.pdf", "doc_001"),  # Will fail - doesn't exist
            (temp_dir / "invalid.xyz", "doc_002"),  # Will fail - unsupported
        ]
        
        results = processor.batch_process(documents)
        
        assert len(results) == 2
        assert all(r.error_message is not None for r in results)
        assert all(r.confidence_score == 0.0 for r in results)

    def test_ocr_performance_benchmarks(self, temp_dir, create_test_pdf):
        """Test OCR processing meets performance requirements."""
        processor = OCRProcessor(max_workers=4)
        
        # Create multiple documents
        documents = [
            (create_test_pdf(f"doc_{i}.pdf"), f"doc_{i:03d}")
            for i in range(10)
        ]
        
        import time
        start_time = time.time()
        results = processor.batch_process(documents)
        processing_time = time.time() - start_time
        
        # Should process 10 documents quickly
        assert len(results) == 10
        assert processing_time < 5.0  # Should complete in under 5 seconds
        
        # Calculate pages per minute
        total_pages = sum(r.page_count for r in results)
        pages_per_minute = (total_pages / processing_time) * 60
        
        # Should meet performance requirement of 100+ pages per minute
        # (In mock mode it will be much faster)
        assert pages_per_minute > 100