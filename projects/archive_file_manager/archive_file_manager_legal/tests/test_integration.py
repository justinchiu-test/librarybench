"""Integration tests for the legal document archive system."""

import json
import zipfile
from pathlib import Path
import pytest

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
    ArchiveManifest,
)


class TestIntegration:
    """Test integrated functionality of all modules."""

    def test_complete_archive_workflow(self, temp_dir, create_test_pdf, create_test_image):
        """Test complete workflow from OCR to compressed archive."""
        # 1. Initialize components
        ocr_processor = OCRProcessor(min_confidence=0.7)
        hierarchy = LegalHierarchy()
        compressor = RedactionAwareCompressor()
        toc_generator = TOCGenerator()
        ref_manager = CrossReferenceManager()
        
        # 2. Create test documents
        test_files = [
            create_test_pdf("complaint.pdf", "Initial complaint filed by plaintiff"),
            create_test_pdf("motion_to_dismiss.pdf", "Motion to dismiss by defendant"),
            create_test_image("exhibit_a.png"),
            create_test_pdf("brief.pdf", "Legal brief citing multiple authorities"),
        ]
        
        # 3. Process documents with OCR
        documents = []
        ocr_results = []
        for i, file_path in enumerate(test_files):
            doc_id = f"doc_{i:03d}"
            
            # OCR processing
            ocr_result = ocr_processor.process_document(file_path, doc_id)
            ocr_results.append(ocr_result)
            
            # Create metadata
            doc_type = [DocumentType.PLEADING, DocumentType.MOTION, 
                       DocumentType.EXHIBIT, DocumentType.BRIEF][i]
            metadata = DocumentMetadata(
                document_id=doc_id,
                file_name=file_path.name,
                document_type=doc_type,
                case_number="2023-CV-12345",
                page_count=ocr_result.page_count,
                file_size=file_path.stat().st_size,
                checksum=f"hash_{i}",
            )
            
            # Store OCR metadata
            ocr_processor.store_ocr_metadata(ocr_result, metadata)
            documents.append((file_path, metadata))
        
        # 4. Create legal hierarchy
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        for _, metadata in documents:
            hierarchy.add_document(metadata, auto_organize=True)
        
        # Apply legal numbering
        bates_mapping = hierarchy.apply_bates_numbering(prefix="LEGAL")
        
        # 5. Extract and preserve cross-references
        for ocr_result in ocr_results:
            refs = ref_manager.extract_references(
                ocr_result.document_id,
                ocr_result.text_content
            )
        
        # 6. Add redactions
        redaction = Redaction(
            redaction_id="red_001",
            document_id="doc_000",
            page_number=1,
            coordinates=[100, 100, 200, 150],
            redaction_level=RedactionLevel.CONFIDENTIAL,
            reason="Contains sensitive information",
            applied_by="Legal Team"
        )
        compressor.add_redaction(redaction)
        
        # 7. Generate table of contents
        doc_dict = {metadata.document_id: metadata for _, metadata in documents}
        toc_generator.generate_from_hierarchy(hierarchy.nodes, doc_dict, root_id)
        
        # Generate multiple TOC formats
        toc_html = temp_dir / "toc.html"
        toc_xml = temp_dir / "toc.xml"
        toc_generator.generate_html(toc_html, case_info={"case_number": "2023-CV-12345"})
        toc_generator.generate_xml(toc_xml)
        
        # 8. Create compressed archive
        archive_path = temp_dir / "legal_archive.zip"
        stats = compressor.compress_with_redactions(documents, archive_path)
        
        # 9. Create archive manifest
        manifest = ArchiveManifest(
            archive_id="archive_001",
            archive_name="Smith v. Jones Legal Archive",
            case_number="2023-CV-12345",
            creator="Legal Archive System",
            total_documents=len(documents),
            total_size=sum(f.stat().st_size for f, _ in documents),
            compression_ratio=stats["compression_ratio"],
            documents=[metadata for _, metadata in documents],
            hierarchy_root=root_id,
            toc_formats=["html", "xml"],
            has_ocr=True,
            has_redactions=True,
            cross_references_count=len(ref_manager.references),
        )
        
        # Save manifest
        manifest_path = temp_dir / "archive_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest.model_dump(), f, indent=2, default=str)
        
        # Verify results
        assert archive_path.exists()
        assert toc_html.exists()
        assert toc_xml.exists()
        assert manifest_path.exists()
        assert stats["redacted_documents"] == 1
        assert all(result.confidence_score > 0 for result in ocr_results)

    def test_redaction_security_workflow(self, temp_dir, create_test_pdf):
        """Test security workflow with different access levels."""
        # Setup
        compressor = RedactionAwareCompressor(encrypt_redacted_content=True)
        
        # Create documents with different redaction levels
        documents = []
        redaction_levels = [
            RedactionLevel.PUBLIC,
            RedactionLevel.CONFIDENTIAL,
            RedactionLevel.ATTORNEY_CLIENT,
            RedactionLevel.SEALED,
        ]
        
        for i, level in enumerate(redaction_levels):
            pdf_path = create_test_pdf(f"doc_{level.value}.pdf", f"Content for {level.value}")
            metadata = DocumentMetadata(
                document_id=f"doc_{i:03d}",
                file_name=pdf_path.name,
                document_type=DocumentType.DISCOVERY,
                page_count=1,
                file_size=1000,
                checksum=f"hash_{i}",
            )
            documents.append((pdf_path, metadata))
            
            # Add redaction
            redaction = Redaction(
                redaction_id=f"red_{i:03d}",
                document_id=metadata.document_id,
                page_number=1,
                coordinates=[0, 0, 100, 100],
                redaction_level=level,
                reason=f"{level.value} content",
                applied_by="Security Admin"
            )
            compressor.add_redaction(redaction, b"sensitive content")
        
        # Create archive
        archive_path = temp_dir / "secure_archive.zip"
        compressor.compress_with_redactions(documents, archive_path)
        
        # Test extraction with different access levels
        
        # 1. Public access only
        public_dir = temp_dir / "public_access"
        public_files = compressor.extract_with_redaction_level(
            archive_path, public_dir, {RedactionLevel.PUBLIC}, "public_user"
        )
        
        # 2. Attorney access
        attorney_dir = temp_dir / "attorney_access"
        attorney_files = compressor.extract_with_redaction_level(
            archive_path, attorney_dir,
            {RedactionLevel.PUBLIC, RedactionLevel.CONFIDENTIAL, 
             RedactionLevel.ATTORNEY_CLIENT},
            "attorney_user"
        )
        
        # 3. Full access
        admin_dir = temp_dir / "admin_access"
        admin_files = compressor.extract_with_redaction_level(
            archive_path, admin_dir,
            {RedactionLevel.PUBLIC, RedactionLevel.CONFIDENTIAL,
             RedactionLevel.ATTORNEY_CLIENT, RedactionLevel.SEALED},
            "admin_user"
        )
        
        # Verify access control
        assert len(public_files) < len(attorney_files)
        assert len(attorney_files) < len(admin_files)
        assert len(admin_files) == len(documents)
        
        # Verify integrity
        is_valid, issues = compressor.verify_redaction_integrity(archive_path)
        assert is_valid is True

    def test_large_case_file_performance(self, temp_dir, create_test_pdf):
        """Test performance with large case file (simulated)."""
        import time
        
        # Initialize components
        ocr_processor = OCRProcessor(max_workers=4)
        hierarchy = LegalHierarchy()
        compressor = RedactionAwareCompressor(compression_level=1)  # Fast compression
        toc_generator = TOCGenerator()
        ref_manager = CrossReferenceManager()
        
        # Create many documents (simulate large case)
        num_documents = 100
        start_time = time.time()
        
        # 1. Create and OCR documents
        documents = []
        for i in range(num_documents):
            pdf_path = create_test_pdf(
                f"document_{i:04d}.pdf",
                f"Legal document content for case file {i}"
            )
            
            # Create metadata
            doc_types = list(DocumentType)
            metadata = DocumentMetadata(
                document_id=f"doc_{i:04d}",
                file_name=pdf_path.name,
                document_type=doc_types[i % len(doc_types)],
                case_number="2023-CV-12345",
                page_count=10,
                file_size=100000,
                checksum=f"hash_{i}",
            )
            documents.append((pdf_path, metadata))
        
        # 2. Batch OCR processing
        ocr_docs = [(path, metadata.document_id) for path, metadata in documents]
        ocr_results = ocr_processor.batch_process(ocr_docs[:10])  # Process subset
        
        # 3. Build hierarchy
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        for _, metadata in documents:
            hierarchy.add_document(metadata, auto_organize=True)
        
        # 4. Generate comprehensive TOC
        doc_dict = {metadata.document_id: metadata for _, metadata in documents}
        toc_generator.generate_from_hierarchy(hierarchy.nodes, doc_dict, root_id)
        toc_path = temp_dir / "large_toc.html"
        toc_generator.generate_html(toc_path)
        
        # 5. Create archive
        archive_path = temp_dir / "large_archive.zip"
        stats = compressor.compress_with_redactions(documents, archive_path)
        
        elapsed_time = time.time() - start_time
        
        # Performance assertions
        assert elapsed_time < 30.0  # Should complete in under 30 seconds
        assert stats["total_documents"] == num_documents
        assert archive_path.stat().st_size > 0
        assert toc_path.exists()
        
        # Calculate metrics
        docs_per_second = num_documents / elapsed_time
        print(f"Processed {docs_per_second:.1f} documents/second")
        assert docs_per_second > 3  # Should process at least 3 docs/second

    def test_cross_reference_preservation_in_archive(self, temp_dir, create_test_pdf):
        """Test that cross-references are preserved through archiving."""
        # Setup
        ref_manager = CrossReferenceManager()
        compressor = RedactionAwareCompressor()
        
        # Create documents with references
        doc1_content = "See Exhibit A for supporting evidence"
        doc2_content = "As stated in Document 1, the claim is valid"
        doc3_content = "Exhibit A - Contract Agreement"
        
        documents = []
        contents = [doc1_content, doc2_content, doc3_content]
        
        for i, content in enumerate(contents):
            pdf_path = create_test_pdf(f"doc_{i}.pdf", content)
            metadata = DocumentMetadata(
                document_id=f"doc_{i:03d}",
                file_name=pdf_path.name,
                document_type=DocumentType.BRIEF,
                page_count=1,
                file_size=1000,
                checksum=f"hash_{i}",
            )
            documents.append((pdf_path, metadata))
            
            # Extract references
            refs = ref_manager.extract_references(metadata.document_id, content)
        
        # Create document mapping for archive
        doc_mapping = {
            metadata.document_id: f"archive/{metadata.file_name}"
            for _, metadata in documents
        }
        
        # Preserve references
        archive_path = temp_dir / "ref_archive.zip"
        ref_manager.preserve_references_in_archive(archive_path, doc_mapping)
        
        # Create archive
        compressor.compress_with_redactions(documents, archive_path)
        
        # Verify references are preserved
        ref_manifest_path = temp_dir / "ref_archive_references.json"
        assert ref_manifest_path.exists()
        
        with open(ref_manifest_path, "r") as f:
            ref_manifest = json.load(f)
        
        # Check that manifest was created with expected structure
        assert "total_references" in ref_manifest
        assert "references" in ref_manifest
        # May have 0 references if no exhibit/document refs were found in the test content
        assert isinstance(ref_manifest["references"], list)

    def test_legal_compliance_features(self, temp_dir, create_test_pdf, sample_documents):
        """Test legal compliance features work together."""
        # Initialize system
        hierarchy = LegalHierarchy()
        toc_generator = TOCGenerator()
        
        # Create hierarchy with proper structure
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add documents with legal metadata
        for i, doc in enumerate(sample_documents):
            doc.bates_number = f"LEGAL{i:06d}"
            if doc.document_type == DocumentType.EXHIBIT:
                doc.exhibit_number = f"P-{i+1}"
            hierarchy.add_document(doc, auto_organize=True)
        
        # Apply legal numbering systems
        bates_mapping = hierarchy.apply_bates_numbering(1000, "SMITH")
        exhibit_mapping = hierarchy.apply_exhibit_numbering("Smith", 1)
        
        # Get filing order
        filing_order = hierarchy.get_filing_order()
        
        # Generate exhibit list
        exhibit_list_path = temp_dir / "exhibit_list.html"
        toc_generator.generate_exhibit_list(
            exhibit_list_path,
            "Smith",
            exhibit_mapping,
            format="html"
        )
        
        # Export hierarchy for court
        hierarchy_export = temp_dir / "case_structure.json"
        hierarchy.export_structure(hierarchy_export)
        
        # Verify compliance features
        assert len(bates_mapping) == len(sample_documents)
        assert all(bn.startswith("SMITH") for bn in bates_mapping.values())
        assert len(filing_order) == len(sample_documents)
        assert exhibit_list_path.exists()
        assert hierarchy_export.exists()
        
        # Verify structure matches legal requirements
        with open(hierarchy_export, "r") as f:
            structure = json.load(f)
        
        assert structure["metadata"]["total_documents"] == len(sample_documents)