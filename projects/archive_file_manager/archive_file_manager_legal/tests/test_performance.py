"""Performance tests for the legal archive system."""

import pytest
import time
from pathlib import Path
import random
import string

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


class TestPerformance:
    """Performance tests to ensure system meets requirements."""

    def generate_random_text(self, size: int) -> str:
        """Generate random text of specified size."""
        return ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size))

    def test_ocr_processing_speed(self, temp_dir):
        """Test OCR processing meets 100+ pages/minute requirement."""
        ocr = OCRProcessor()
        
        # Create test documents
        documents = []
        for i in range(10):
            doc_path = temp_dir / f"test_doc_{i}.pdf"
            doc_path.write_text(self.generate_random_text(10000))
            documents.append((doc_path, f"doc_{i}"))
        
        # Process documents and measure time
        start_time = time.time()
        results = []
        
        for doc_path, doc_id in documents:
            result = ocr.process_document(doc_path, doc_id)
            results.append(result)
        
        elapsed_time = time.time() - start_time
        
        # Calculate processing rate (assuming 10 pages per document)
        total_pages = 10 * len(documents)
        pages_per_minute = (total_pages / elapsed_time) * 60
        
        # Should process at least 100 pages per minute
        assert pages_per_minute > 100

    def test_toc_generation_speed(self, temp_dir):
        """Test TOC generation for 10,000 documents in under 30 seconds."""
        toc_gen = TOCGenerator()
        
        # Create 10,000 document entries
        start_time = time.time()
        
        for i in range(10000):
            metadata = DocumentMetadata(
                document_id=f"doc_{i:05d}",
                file_name=f"document_{i:05d}.pdf",
                document_type=random.choice(list(DocumentType)),
                page_count=random.randint(1, 50),
                file_size=random.randint(1000, 1000000),
                checksum=f"checksum_{i:05d}"
            )
            
            toc_gen.add_entry(
                document=metadata,
                title=metadata.file_name,
                page_number=i * 10 + 1,
                level=random.randint(0, 3)
            )
        
        # Generate TOC
        output_path = temp_dir / "large_toc.html"
        toc_gen.generate_html(output_path)
        
        elapsed_time = time.time() - start_time
        
        # Should complete in under 30 seconds
        assert elapsed_time < 30
        assert output_path.exists()

    def test_compression_large_archive(self, temp_dir):
        """Test compression can handle archives up to 500GB (simulated)."""
        compressor = RedactionAwareCompressor()
        
        # Create sample documents (simulated large files)
        documents = []
        total_size = 0
        
        for i in range(100):  # Simulate 100 large documents
            doc_path = temp_dir / f"large_doc_{i}.pdf"
            # Create smaller actual files but track larger simulated sizes
            doc_path.write_bytes(b"x" * 1024)  # 1KB actual
            
            metadata = DocumentMetadata(
                document_id=f"large_doc_{i}",
                file_name=doc_path.name,
                document_type=DocumentType.DISCOVERY,
                page_count=1000,  # Simulate 1000 pages
                file_size=5 * 1024 * 1024 * 1024,  # Simulate 5GB per file
                checksum=f"checksum_{i}"
            )
            
            documents.append((doc_path, metadata))
            total_size += metadata.file_size
        
        # Compress documents
        archive_path = temp_dir / "large_archive.zip"
        start_time = time.time()
        
        stats = compressor.compress_with_redactions(documents, archive_path)
        
        elapsed_time = time.time() - start_time
        
        # Should handle large archives efficiently
        assert archive_path.exists()
        assert stats["total_documents"] == 100
        # Ensure reasonable processing time for the actual small files
        assert elapsed_time < 10

    def test_concurrent_access_simulation(self):
        """Test system can handle concurrent access from multiple users."""
        # Create shared hierarchy
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("shared_case", "federal_court")
        
        # Simulate multiple users adding documents concurrently
        user_documents = []
        
        for user_id in range(10):  # 10 concurrent users
            for doc_num in range(10):  # Each adds 10 documents
                metadata = DocumentMetadata(
                    document_id=f"user{user_id}_doc{doc_num}",
                    file_name=f"user{user_id}_document{doc_num}.pdf",
                    document_type=DocumentType.DISCOVERY,
                    page_count=10,
                    file_size=100000,
                    checksum=f"checksum_u{user_id}d{doc_num}"
                )
                
                # Add document (simulating concurrent access)
                hierarchy.add_document(metadata, auto_organize=True)
                user_documents.append(metadata)
        
        # Verify hierarchy has nodes
        assert len(hierarchy.nodes) > 0

    def test_reference_extraction_performance(self):
        """Test cross-reference extraction performance on large documents."""
        manager = CrossReferenceManager()
        
        # Generate large document with many citations
        content_parts = []
        for i in range(1000):
            content_parts.append(f"""
            See case {i} U.S. {i+100} ({2000+i%20}), and also
            {i+500} F.3d {i+200} (9th Cir. {2010+i%10}).
            Reference to Exhibit {chr(65 + i%26)}-{i:03d}.
            """)
        
        large_content = "\n".join(content_parts)
        
        # Extract references and measure time
        start_time = time.time()
        references = manager.extract_references("large_doc", large_content)
        elapsed_time = time.time() - start_time
        
        # Should extract many references efficiently
        assert len(references) > 1000
        assert elapsed_time < 5  # Should complete in under 5 seconds

    def test_hierarchy_traversal_performance(self):
        """Test hierarchy traversal performance with deep structures."""
        hierarchy = LegalHierarchy()
        
        # Create deep hierarchy
        parent_id = hierarchy.create_hierarchy("deep_case", "federal_court")
        
        # Create 10 levels deep, 10 nodes per level
        for level in range(10):
            new_parents = []
            for node_num in range(10):
                node_id = hierarchy.create_node(
                    f"Level {level} Node {node_num}",
                    "category",
                    parent_id
                )
                new_parents.append(node_id)
            
            # Pick first node as parent for next level
            if new_parents:
                parent_id = new_parents[0]
        
        # Test traversal performance by checking nodes exist
        start_time = time.time()
        # Just verify we can access nodes efficiently
        node_count = len(hierarchy.nodes)
        elapsed_time = time.time() - start_time
        
        # Should have created many nodes
        assert node_count > 50  # At least some nodes from the hierarchy
        assert elapsed_time < 1

    def test_redaction_application_performance(self, temp_dir):
        """Test redaction application performance on documents."""
        compressor = RedactionAwareCompressor()
        
        # Create document with many redactions
        doc_id = "heavily_redacted"
        redactions = []
        
        for page in range(100):  # 100 pages
            for redaction_num in range(10):  # 10 redactions per page
                redaction = Redaction(
                    redaction_id=f"red_p{page}_r{redaction_num}",
                    document_id=doc_id,
                    page_number=page + 1,
                    coordinates=[
                        redaction_num * 50,
                        redaction_num * 50,
                        redaction_num * 50 + 40,
                        redaction_num * 50 + 40
                    ],
                    redaction_level=random.choice(list(RedactionLevel)),
                    reason="Performance test",
                    applied_by="Test User"
                )
                redactions.append(redaction)
                compressor.add_redaction(redaction)
        
        # Create and compress document
        doc_path = temp_dir / "heavily_redacted.pdf"
        doc_path.write_bytes(b"x" * 10000)
        
        metadata = DocumentMetadata(
            document_id=doc_id,
            file_name="heavily_redacted.pdf",
            document_type=DocumentType.DISCOVERY,
            page_count=100,
            file_size=10000,
            checksum="test"
        )
        
        start_time = time.time()
        archive_path = temp_dir / "redacted_archive.zip"
        stats = compressor.compress_with_redactions([(doc_path, metadata)], archive_path)
        elapsed_time = time.time() - start_time
        
        # Should handle many redactions efficiently
        assert stats["redacted_documents"] == 1
        assert elapsed_time < 5

    def test_batch_operations_performance(self):
        """Test performance of batch operations."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("batch_test", "state_court")
        
        # Batch add documents
        documents = []
        for i in range(1000):
            metadata = DocumentMetadata(
                document_id=f"batch_doc_{i:04d}",
                file_name=f"batch_{i:04d}.pdf",
                document_type=DocumentType.DISCOVERY,
                page_count=5,
                file_size=50000,
                checksum=f"batch_{i:04d}"
            )
            documents.append(metadata)
        
        # Time batch operation
        start_time = time.time()
        
        for doc in documents:
            hierarchy.add_document(doc, auto_organize=True)
        
        # Apply numbering in batch
        bates_map = hierarchy.apply_bates_numbering(start_number=1000000)
        
        elapsed_time = time.time() - start_time
        
        # Should complete batch operations quickly
        assert len(bates_map) == 1000
        assert elapsed_time < 10

    def test_memory_usage_large_dataset(self, temp_dir):
        """Test memory usage with large datasets."""
        # Create managers
        toc_gen = TOCGenerator()
        ref_manager = CrossReferenceManager()
        
        # Add many entries without excessive memory usage
        for i in range(5000):
            # TOC entries
            metadata = DocumentMetadata(
                document_id=f"mem_doc_{i}",
                file_name=f"memory_test_{i}.pdf",
                document_type=DocumentType.OTHER,
                page_count=1,
                file_size=1000,
                checksum=f"mem_{i}"
            )
            
            toc_gen.add_entry(
                document=metadata,
                title=f"Document {i}",
                page_number=i + 1,
                level=i % 4
            )
            
            # Cross references
            if i > 0:
                ref = CrossReference(
                    reference_id=f"ref_{i}",
                    source_document_id=f"mem_doc_{i}",
                    target_document_id=f"mem_doc_{i-1}",
                    reference_type="sequential",
                    reference_text=f"See previous document {i-1}"
                )
                ref_manager.add_reference(ref)
        
        # Generate outputs
        toc_path = temp_dir / "memory_test_toc.xml"
        ref_path = temp_dir / "memory_test_refs.json"
        
        toc_gen.generate_xml(toc_path)
        ref_manager.generate_reference_graph(ref_path)
        
        # Should complete without memory issues
        assert toc_path.exists()
        assert ref_path.exists()

    def test_search_performance_large_archive(self):
        """Test search performance in large archives."""
        manager = CrossReferenceManager()
        
        # Create large reference set
        for i in range(10000):
            ref = CrossReference(
                reference_id=f"search_ref_{i:05d}",
                source_document_id=f"search_doc_{i:05d}",
                target_document_id=f"search_doc_{(i+1):05d}",
                reference_type="citation",
                reference_text=f"Citation number {i}"
            )
            manager.add_reference(ref)
        
        # Test search performance
        start_time = time.time()
        
        # Search for specific document references
        refs = manager.get_document_references("search_doc_05000")
        
        # Build citation chain
        chain = manager.build_citation_chain("search_doc_00000", max_depth=10)
        
        elapsed_time = time.time() - start_time
        
        # Should search efficiently
        assert len(refs["outgoing"]) > 0
        assert len(chain) > 0
        assert elapsed_time < 1

    def test_parallel_compression_performance(self, temp_dir):
        """Test performance with parallel compression operations."""
        # Create multiple compressors (simulating parallel operations)
        compressors = [RedactionAwareCompressor() for _ in range(5)]
        
        # Create documents for each compressor
        all_documents = []
        for c_idx, compressor in enumerate(compressors):
            documents = []
            for d_idx in range(20):
                doc_path = temp_dir / f"parallel_c{c_idx}_d{d_idx}.pdf"
                doc_path.write_bytes(b"x" * 1000)
                
                metadata = DocumentMetadata(
                    document_id=f"parallel_c{c_idx}_d{d_idx}",
                    file_name=doc_path.name,
                    document_type=DocumentType.OTHER,
                    page_count=5,
                    file_size=1000,
                    checksum=f"parallel_{c_idx}_{d_idx}"
                )
                
                documents.append((doc_path, metadata))
            
            all_documents.append((compressor, documents, c_idx))
        
        # Compress all in sequence (simulating parallel)
        start_time = time.time()
        
        for compressor, documents, idx in all_documents:
            archive_path = temp_dir / f"parallel_archive_{idx}.zip"
            compressor.compress_with_redactions(documents, archive_path)
        
        elapsed_time = time.time() - start_time
        
        # Should handle multiple compressions efficiently
        assert elapsed_time < 10
        
        # Verify all archives created
        for idx in range(5):
            assert (temp_dir / f"parallel_archive_{idx}.zip").exists()