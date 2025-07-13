"""Tests for cross-reference preservation module."""

import json
from pathlib import Path
import pytest

from legal_archive.cross_reference import CrossReferenceManager
from legal_archive.models import CrossReference


class TestCrossReferenceManager:
    """Test cross-reference management functionality."""

    def test_initialization(self):
        """Test cross-reference manager initialization."""
        manager = CrossReferenceManager()
        
        assert manager.references == {}
        assert manager.document_references == {}
        assert manager.citation_patterns is not None
        assert len(manager.citation_patterns) > 0

    def test_add_reference(self, sample_cross_references):
        """Test adding cross-references."""
        manager = CrossReferenceManager()
        ref = sample_cross_references[0]
        
        manager.add_reference(ref)
        
        assert ref.reference_id in manager.references
        assert ref.reference_id in manager.document_references[ref.source_document_id]

    def test_add_bidirectional_reference(self):
        """Test adding bidirectional references."""
        manager = CrossReferenceManager()
        
        ref = CrossReference(
            reference_id="ref_001",
            source_document_id="doc_001",
            target_document_id="doc_002",
            reference_type="citation",
            is_bidirectional=True
        )
        
        manager.add_reference(ref)
        
        # Should create two references
        assert len(manager.references) == 2
        assert "ref_001" in manager.references
        
        # Find reverse reference
        reverse_refs = [r for r in manager.references.values() 
                       if r.source_document_id == "doc_002" 
                       and r.target_document_id == "doc_001"]
        assert len(reverse_refs) == 1
        assert reverse_refs[0].reference_type == "reverse_citation"

    def test_extract_legal_citations(self):
        """Test extracting legal citations from content."""
        manager = CrossReferenceManager()
        
        content = """
        This matter is governed by 42 U.S.C. § 1983 and the precedent set in 
        Brown v. Board of Education, 347 U.S. 483 (1954). See also 28 C.F.R. § 35.130.
        """
        
        references = manager.extract_references("doc_001", content, "brief")
        
        # Should find statute and case citations
        citation_types = [ref.reference_type for ref in references]
        assert "legal_citation" in citation_types
        assert "statute_citation" in citation_types
        
        # Check specific citations
        statute_refs = [r for r in references if r.reference_type == "statute_citation"]
        assert any("42" in r.target_document_id for r in statute_refs)

    def test_extract_exhibit_references(self):
        """Test extracting exhibit references."""
        manager = CrossReferenceManager()
        
        content = """
        As shown in Exhibit A, the contract clearly states the terms.
        See also Ex. B-2 for supporting documentation.
        """
        
        references = manager.extract_references("doc_001", content, "motion")
        
        exhibit_refs = [r for r in references if r.reference_type == "exhibit"]
        assert len(exhibit_refs) >= 2
        assert any("A" in r.target_document_id for r in exhibit_refs)
        assert any("B-2" in r.target_document_id for r in exhibit_refs)

    def test_extract_document_references(self):
        """Test extracting document references."""
        manager = CrossReferenceManager()
        
        content = """
        See Document 123 for the original complaint.
        As discussed in Doc. 456, the plaintiff claims...
        """
        
        references = manager.extract_references("doc_001", content)
        
        doc_refs = [r for r in references if r.reference_type == "document"]
        assert len(doc_refs) >= 2
        assert any("123" in r.target_document_id for r in doc_refs)
        assert any("456" in r.target_document_id for r in doc_refs)

    def test_preserve_references_in_archive(self, temp_dir, sample_cross_references):
        """Test preserving references when archiving."""
        manager = CrossReferenceManager()
        
        # Add references
        for ref in sample_cross_references:
            manager.add_reference(ref)
        
        # Create document mapping
        document_mapping = {
            "doc_001": "archive/pleadings/complaint.pdf",
            "doc_002": "archive/motions/motion_to_dismiss.pdf",
            "doc_003": "archive/exhibits/exhibit_a.pdf",
        }
        
        # Preserve references
        archive_path = temp_dir / "test_archive.zip"
        manager.preserve_references_in_archive(archive_path, document_mapping)
        
        # Check manifest was created
        manifest_path = temp_dir / "test_archive_references.json"
        assert manifest_path.exists()
        
        # Verify manifest content
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        assert manifest["total_references"] > 0
        assert "references" in manifest
        assert len(manifest["references"]) > 0
        
        # Check reference preservation
        ref = manifest["references"][0]
        assert "source_path" in ref
        assert "target_path" in ref

    def test_verify_reference_integrity(self, sample_cross_references):
        """Test reference integrity verification."""
        manager = CrossReferenceManager()
        
        # Add references
        for ref in sample_cross_references:
            manager.add_reference(ref)
        
        # All documents exist
        valid_docs = {"doc_001", "doc_002", "doc_003"}
        is_valid, issues = manager.verify_reference_integrity(valid_docs)
        assert is_valid is True
        assert len(issues) == 0
        
        # Missing document
        partial_docs = {"doc_001", "doc_002"}  # doc_003 missing
        is_valid, issues = manager.verify_reference_integrity(partial_docs)
        assert is_valid is False
        assert len(issues) > 0
        assert any("doc_003" in issue for issue in issues)

    def test_get_document_references(self, sample_cross_references):
        """Test getting references for a specific document."""
        manager = CrossReferenceManager()
        
        # Add references
        for ref in sample_cross_references:
            manager.add_reference(ref)
        
        # Get references for doc_001
        refs = manager.get_document_references("doc_001", include_incoming=True)
        
        assert "outgoing" in refs
        assert "incoming" in refs
        assert len(refs["outgoing"]) > 0
        
        # doc_001 references doc_002
        outgoing_targets = [r.target_document_id for r in refs["outgoing"]]
        assert "doc_002" in outgoing_targets

    def test_build_citation_chain(self):
        """Test building citation chains."""
        manager = CrossReferenceManager()
        
        # Create chain: doc1 -> doc2 -> doc3 -> doc4
        refs = [
            CrossReference(
                reference_id="ref_001",
                source_document_id="doc_001",
                target_document_id="doc_002",
                reference_type="citation"
            ),
            CrossReference(
                reference_id="ref_002",
                source_document_id="doc_002",
                target_document_id="doc_003",
                reference_type="citation"
            ),
            CrossReference(
                reference_id="ref_003",
                source_document_id="doc_003",
                target_document_id="doc_004",
                reference_type="citation"
            ),
        ]
        
        for ref in refs:
            manager.add_reference(ref)
        
        # Build chain from doc_001
        chain = manager.build_citation_chain("doc_001", max_depth=3)
        
        assert "doc_001" in chain
        assert "doc_002" in chain["doc_001"]
        assert "doc_002" in chain
        assert "doc_003" in chain["doc_002"]

    def test_generate_reference_graph_json(self, temp_dir, sample_cross_references):
        """Test generating reference graph in JSON format."""
        manager = CrossReferenceManager()
        
        # Add references
        for ref in sample_cross_references:
            manager.add_reference(ref)
        
        # Generate graph
        output_path = temp_dir / "ref_graph.json"
        result_path = manager.generate_reference_graph(output_path, format="json")
        
        assert result_path.exists()
        
        # Verify graph structure
        with open(result_path, "r") as f:
            graph_data = json.load(f)
        
        assert "nodes" in graph_data
        assert "edges" in graph_data
        assert "metadata" in graph_data
        
        # Check nodes exist for all documents
        node_ids = {node["id"] for node in graph_data["nodes"]}
        assert "doc_001" in node_ids
        assert "doc_002" in node_ids
        
        # Check edges
        assert len(graph_data["edges"]) == len(sample_cross_references)

    def test_generate_reference_graph_dot(self, temp_dir):
        """Test generating reference graph in DOT format."""
        manager = CrossReferenceManager()
        
        # Add simple references
        refs = [
            CrossReference(
                reference_id="ref_001",
                source_document_id="doc_A",
                target_document_id="doc_B",
                reference_type="citation"
            ),
            CrossReference(
                reference_id="ref_002",
                source_document_id="doc_B",
                target_document_id="doc_C",
                reference_type="exhibit"
            ),
        ]
        
        for ref in refs:
            manager.add_reference(ref)
        
        # Generate DOT graph
        output_path = temp_dir / "ref_graph.dot"
        result_path = manager.generate_reference_graph(output_path, format="dot")
        
        assert result_path.exists()
        
        content = result_path.read_text()
        assert "digraph references" in content
        assert '"doc_A"' in content
        assert '"doc_B"' in content
        assert '"doc_C"' in content
        assert "->" in content

    def test_update_references_after_modification(self):
        """Test updating references after document modification."""
        manager = CrossReferenceManager()
        
        # Add reference with page numbers
        ref = CrossReference(
            reference_id="ref_001",
            source_document_id="doc_001",
            target_document_id="doc_002",
            source_page=5,
            target_page=10,
            reference_type="citation"
        )
        manager.add_reference(ref)
        
        # Insert pages before target
        manager.update_references_after_modification("doc_002", 3, "insert")
        
        # Target page should be updated
        updated_ref = manager.references["ref_001"]
        assert updated_ref.target_page == 13  # 10 + 3
        
        # Delete pages
        manager.update_references_after_modification("doc_002", 5, "delete")
        assert updated_ref.target_page == 8  # 13 - 5

    def test_complex_citation_patterns(self):
        """Test extraction of complex legal citations."""
        manager = CrossReferenceManager()
        
        content = """
        The court relied on multiple authorities:
        1. 123 F.3d 456 (9th Cir. 2020)
        2. 456 U.S. 789, 792-93 (1985)
        3. 15 U.S.C. § 1681(a)(1)
        4. 12 C.F.R. § 1024.35(e)(1)(i)
        
        See also Exhibit Z-100 and Document 2023-045.
        """
        
        references = manager.extract_references("doc_001", content)
        
        # Should extract various citation types
        assert len(references) >= 5
        
        # Verify different types found
        types_found = {ref.reference_type for ref in references}
        expected_types = {"legal_citation", "statute_citation", "regulation_citation", "exhibit", "document"}
        assert len(types_found.intersection(expected_types)) >= 4

    def test_circular_reference_detection(self):
        """Test handling of circular references."""
        manager = CrossReferenceManager()
        
        # Create circular references: A -> B -> C -> A
        refs = [
            CrossReference(
                reference_id="ref_001",
                source_document_id="doc_A",
                target_document_id="doc_B",
                reference_type="citation"
            ),
            CrossReference(
                reference_id="ref_002",
                source_document_id="doc_B",
                target_document_id="doc_C",
                reference_type="citation"
            ),
            CrossReference(
                reference_id="ref_003",
                source_document_id="doc_C",
                target_document_id="doc_A",
                reference_type="citation"
            ),
        ]
        
        for ref in refs:
            manager.add_reference(ref)
        
        # Build chain with max depth to prevent infinite loop
        chain = manager.build_citation_chain("doc_A", max_depth=5)
        
        # Should handle circular reference gracefully
        assert len(chain) <= 3  # A, B, C
        assert "doc_A" in chain

    def test_performance_large_reference_set(self):
        """Test performance with large number of references."""
        manager = CrossReferenceManager()
        
        # Create many references
        import time
        start_time = time.time()
        
        for i in range(1000):
            ref = CrossReference(
                reference_id=f"ref_{i:04d}",
                source_document_id=f"doc_{i % 100:03d}",
                target_document_id=f"doc_{(i + 1) % 100:03d}",
                reference_type="citation",
                reference_text=f"See Document {(i + 1) % 100}"
            )
            manager.add_reference(ref)
        
        elapsed_time = time.time() - start_time
        
        # Should handle 1000 references quickly
        assert elapsed_time < 1.0
        assert len(manager.references) == 1000
        
        # Test retrieval performance
        start_time = time.time()
        refs = manager.get_document_references("doc_001")
        elapsed_time = time.time() - start_time
        
        # Should retrieve references quickly
        assert elapsed_time < 0.1
        assert len(refs["outgoing"]) > 0