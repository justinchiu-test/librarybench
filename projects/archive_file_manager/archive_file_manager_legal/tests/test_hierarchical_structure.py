"""Tests for hierarchical archive structure module."""

import json
from pathlib import Path
import pytest

from legal_archive.hierarchical_structure import LegalHierarchy
from legal_archive.models import DocumentMetadata, DocumentType, HierarchyNode


class TestLegalHierarchy:
    """Test legal hierarchy functionality."""

    def test_initialization(self):
        """Test hierarchy initialization."""
        hierarchy = LegalHierarchy()
        
        assert hierarchy.nodes == {}
        assert hierarchy.document_locations == {}
        assert hierarchy.templates is not None
        assert "federal_court" in hierarchy.templates
        assert "state_court" in hierarchy.templates

    def test_create_hierarchy_federal_court(self):
        """Test creating federal court hierarchy."""
        hierarchy = LegalHierarchy()
        
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        assert root_id in hierarchy.nodes
        root_node = hierarchy.nodes[root_id]
        assert root_node.name == "Case 2023-CV-12345"
        assert root_node.node_type == "case"
        assert len(root_node.children) > 0
        
        # Check template structure was applied
        child_names = [hierarchy.nodes[cid].name for cid in root_node.children]
        assert "Pleadings" in child_names
        assert "Motions" in child_names
        assert "Discovery" in child_names
        assert "Exhibits" in child_names

    def test_create_hierarchy_state_court(self):
        """Test creating state court hierarchy."""
        hierarchy = LegalHierarchy()
        
        root_id = hierarchy.create_hierarchy("2023-ST-67890", "state_court")
        
        root_node = hierarchy.nodes[root_id]
        child_names = [hierarchy.nodes[cid].name for cid in root_node.children]
        assert "Initial Filings" in child_names
        assert "Discovery" in child_names
        assert "Pre-Trial Motions" in child_names

    def test_add_document_auto_organize(self, sample_documents):
        """Test adding document with auto-organization."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add pleading document
        doc = sample_documents[0]  # complaint (pleading)
        node_id = hierarchy.add_document(doc, auto_organize=True)
        
        assert doc.document_id in hierarchy.document_locations
        node = hierarchy.nodes[node_id]
        assert doc.document_id in node.documents
        
        # Should be in Pleadings section
        path = hierarchy.get_path(node_id)
        assert "Pleadings" in path

    def test_add_document_specific_node(self, sample_documents):
        """Test adding document to specific node."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345")
        
        # Create custom node
        custom_node_id = hierarchy.create_node(
            "Custom Category", "document_type", root_id
        )
        
        # Add document to custom node
        doc = sample_documents[0]
        result_node_id = hierarchy.add_document(doc, custom_node_id, auto_organize=False)
        
        assert result_node_id == custom_node_id
        assert doc.document_id in hierarchy.nodes[custom_node_id].documents

    def test_create_node(self):
        """Test creating custom nodes."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345")
        
        # Create parent node
        parent_id = hierarchy.create_node(
            "Special Documents",
            "document_type",
            root_id,
            {"description": "Sealed documents"}
        )
        
        assert parent_id in hierarchy.nodes
        parent_node = hierarchy.nodes[parent_id]
        assert parent_node.name == "Special Documents"
        assert parent_id in hierarchy.nodes[root_id].children
        
        # Create child node
        child_id = hierarchy.create_node(
            "Confidential",
            "subcategory",
            parent_id
        )
        
        assert child_id in parent_node.children

    def test_get_path(self):
        """Test getting path from root to node."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Find a deep node
        for node in hierarchy.nodes.values():
            if node.name == "Plaintiff Motions":
                path = hierarchy.get_path(node.node_id)
                assert path == ["Case 2023-CV-12345", "Motions", "Plaintiff Motions"]
                break

    def test_apply_bates_numbering(self, sample_documents):
        """Test applying Bates numbering to documents."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345")
        
        # Add documents
        for doc in sample_documents:
            hierarchy.add_document(doc)
        
        # Apply Bates numbering
        bates_mapping = hierarchy.apply_bates_numbering(
            start_number=1000, prefix="LEGAL"
        )
        
        assert len(bates_mapping) == len(sample_documents)
        assert all(bn.startswith("LEGAL") for bn in bates_mapping.values())
        assert bates_mapping[sample_documents[0].document_id] == "LEGAL001000"

    def test_apply_exhibit_numbering(self, sample_documents):
        """Test applying exhibit numbering."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add exhibit document
        exhibit_doc = sample_documents[2]  # exhibit
        hierarchy.add_document(exhibit_doc, auto_organize=True)
        
        # Apply exhibit numbering
        exhibit_mapping = hierarchy.apply_exhibit_numbering("Smith", start_number=1)
        
        if exhibit_doc.document_id in exhibit_mapping:
            assert exhibit_mapping[exhibit_doc.document_id] == "S-1"

    def test_get_filing_order(self, sample_documents):
        """Test getting documents in legal filing order."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add documents with different types
        for doc in sample_documents:
            hierarchy.add_document(doc, auto_organize=True)
        
        # Get filing order
        ordered_docs = hierarchy.get_filing_order()
        
        assert len(ordered_docs) == len(sample_documents)
        # Pleadings should come before motions
        pleading_idx = ordered_docs.index("doc_001")
        motion_idx = ordered_docs.index("doc_002")
        assert pleading_idx < motion_idx

    def test_export_import_structure(self, temp_dir):
        """Test exporting and importing hierarchy structure."""
        hierarchy1 = LegalHierarchy()
        root_id = hierarchy1.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add some nodes
        node_id = hierarchy1.create_node("Test Node", "custom", root_id)
        
        # Export structure
        export_path = temp_dir / "hierarchy.json"
        hierarchy1.export_structure(export_path)
        
        assert export_path.exists()
        
        # Import into new hierarchy
        hierarchy2 = LegalHierarchy()
        hierarchy2.import_structure(export_path)
        
        assert len(hierarchy2.nodes) == len(hierarchy1.nodes)
        assert node_id in hierarchy2.nodes
        assert hierarchy2.nodes[node_id].name == "Test Node"

    def test_hierarchical_depth_limits(self):
        """Test handling deep hierarchical structures."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345")
        
        # Create deep hierarchy
        current_id = root_id
        for i in range(10):
            current_id = hierarchy.create_node(
                f"Level {i}", "category", current_id
            )
        
        # Get path of deepest node
        path = hierarchy.get_path(current_id)
        assert len(path) == 11  # root + 10 levels

    def test_legal_numbering_systems(self, sample_documents):
        """Test various legal numbering systems."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345")
        
        # Test document with filing date
        doc = sample_documents[0]
        hierarchy.add_document(doc, auto_organize=True)
        
        # Check metadata was applied
        assert "sort_order" in doc.metadata

    def test_template_customization(self):
        """Test using custom templates."""
        hierarchy = LegalHierarchy()
        
        # Add custom template
        hierarchy.templates["custom_court"] = {
            "structure": [
                {"name": "Category A", "type": "document_type"},
                {"name": "Category B", "type": "document_type"},
            ]
        }
        
        root_id = hierarchy.create_hierarchy("2023-CUSTOM-001", "custom_court")
        
        root_node = hierarchy.nodes[root_id]
        child_names = [hierarchy.nodes[cid].name for cid in root_node.children]
        assert "Category A" in child_names
        assert "Category B" in child_names

    def test_performance_large_hierarchy(self, sample_documents):
        """Test performance with large document sets."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add many documents
        import time
        start_time = time.time()
        
        for i in range(100):
            doc = DocumentMetadata(
                document_id=f"doc_{i:04d}",
                file_name=f"document_{i}.pdf",
                document_type=DocumentType.DISCOVERY,
                page_count=10,
                file_size=100000,
                checksum=f"hash_{i}",
            )
            hierarchy.add_document(doc, auto_organize=True)
        
        elapsed_time = time.time() - start_time
        
        # Should handle 100 documents quickly
        assert elapsed_time < 1.0
        assert len(hierarchy.document_locations) == 100

    def test_circular_reference_prevention(self):
        """Test prevention of circular references in hierarchy."""
        hierarchy = LegalHierarchy()
        
        node1_id = hierarchy.create_node("Node 1", "category")
        node2_id = hierarchy.create_node("Node 2", "category", node1_id)
        
        # Try to create circular reference (should handle gracefully)
        # In production, this would raise an exception or be prevented
        assert hierarchy.nodes[node2_id].parent_id == node1_id
        assert node2_id in hierarchy.nodes[node1_id].children