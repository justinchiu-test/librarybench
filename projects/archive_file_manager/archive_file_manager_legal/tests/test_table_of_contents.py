"""Tests for table of contents generation module."""

import json
from pathlib import Path
from lxml import etree
import pytest

from legal_archive.table_of_contents import TOCGenerator
from legal_archive.hierarchical_structure import LegalHierarchy
from legal_archive.models import DocumentMetadata, DocumentType, HierarchyNode


class TestTOCGenerator:
    """Test table of contents generation functionality."""

    def test_initialization(self, temp_dir):
        """Test TOC generator initialization."""
        toc_gen = TOCGenerator(template_dir=temp_dir)
        
        assert toc_gen.template_dir == temp_dir
        assert toc_gen.entries == {}
        assert toc_gen._entry_counter == 0
        assert toc_gen.jinja_env is not None

    def test_add_entry(self, sample_documents):
        """Test adding entries to TOC."""
        toc_gen = TOCGenerator()
        doc = sample_documents[0]
        
        entry_id = toc_gen.add_entry(
            document=doc,
            title="Legal Complaint",
            page_number=1,
            level=0,
            summary="Initial complaint filed by plaintiff"
        )
        
        assert entry_id in toc_gen.entries
        entry = toc_gen.entries[entry_id]
        assert entry.document_id == doc.document_id
        assert entry.title == "Legal Complaint"
        assert entry.page_number == 1
        assert entry.level == 0
        assert entry.summary == "Initial complaint filed by plaintiff"

    def test_add_entry_with_hierarchy(self, sample_documents):
        """Test adding entries with parent-child relationships."""
        toc_gen = TOCGenerator()
        
        # Add parent entry
        parent_id = toc_gen.add_entry(
            document=sample_documents[0],
            title="Section 1: Pleadings",
            level=0
        )
        
        # Add child entry
        child_id = toc_gen.add_entry(
            document=sample_documents[1],
            title="Complaint",
            level=1,
            parent_id=parent_id
        )
        
        assert child_id in toc_gen.entries[parent_id].children
        assert toc_gen.entries[child_id].parent_entry_id == parent_id

    def test_generate_from_hierarchy(self, sample_documents):
        """Test generating TOC from legal hierarchy."""
        # Create hierarchy
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")
        
        # Add documents
        doc_dict = {}
        for doc in sample_documents:
            hierarchy.add_document(doc, auto_organize=True)
            doc_dict[doc.document_id] = doc
        
        # Generate TOC
        toc_gen = TOCGenerator()
        toc_gen.generate_from_hierarchy(hierarchy.nodes, doc_dict, root_id)
        
        assert len(toc_gen.entries) > 0
        # Check that page numbers were assigned
        doc_entries = [e for e in toc_gen.entries.values() 
                      if not e.document_id.startswith("section_")]
        assert any(e.page_number is not None for e in doc_entries)

    def test_generate_pdf(self, temp_dir, sample_documents):
        """Test PDF TOC generation."""
        toc_gen = TOCGenerator()
        
        # Add entries
        for i, doc in enumerate(sample_documents):
            toc_gen.add_entry(
                document=doc,
                title=f"Document {i+1}: {doc.file_name}",
                page_number=i * 10 + 1,
                level=0
            )
        
        # Generate PDF
        output_path = temp_dir / "toc.pdf"
        case_info = {
            "case_number": "2023-CV-12345",
            "case_title": "Smith v. Jones",
            "court": "Superior Court of California"
        }
        
        result_path = toc_gen.generate_pdf(
            output_path, case_info, include_hyperlinks=True
        )
        
        assert result_path.exists()
        # Since we generate HTML for PDF conversion
        assert result_path.suffix == ".html"
        
        # Check content
        content = result_path.read_text()
        assert "Table of Contents" in content
        assert "2023-CV-12345" in content
        assert "Document 1" in content

    def test_generate_html(self, temp_dir, sample_documents):
        """Test HTML TOC generation."""
        toc_gen = TOCGenerator()
        
        # Add hierarchical entries
        section_id = toc_gen.add_entry(
            document=DocumentMetadata(
                document_id="section_1",
                file_name="Pleadings",
                document_type=DocumentType.OTHER,
                page_count=1,
                file_size=1,
                checksum=""
            ),
            title="Section I: Pleadings",
            level=0
        )
        
        for i, doc in enumerate(sample_documents[:2]):
            toc_gen.add_entry(
                document=doc,
                title=doc.file_name,
                page_number=i * 10 + 1,
                level=1,
                parent_id=section_id,
                summary=f"Summary of {doc.file_name}"
            )
        
        # Generate HTML
        output_path = temp_dir / "toc.html"
        result_path = toc_gen.generate_html(
            output_path,
            case_info={"case_number": "2023-CV-12345"},
            include_summaries=True,
            collapsible=True
        )
        
        assert result_path.exists()
        content = result_path.read_text()
        assert "Legal Document Archive - Table of Contents" in content
        assert "Section I: Pleadings" in content
        assert "Summary of" in content

    def test_generate_xml(self, temp_dir, sample_documents):
        """Test XML TOC generation."""
        toc_gen = TOCGenerator()
        
        # Add entries
        for i, doc in enumerate(sample_documents):
            toc_gen.add_entry(
                document=doc,
                title=doc.file_name,
                page_number=i * 10 + 1,
                level=0
            )
        
        # Generate XML
        output_path = temp_dir / "toc.xml"
        result_path = toc_gen.generate_xml(
            output_path,
            schema="legal_toc",
            include_metadata=True
        )
        
        assert result_path.exists()
        
        # Parse and validate XML
        tree = etree.parse(str(result_path))
        root = tree.getroot()
        
        assert root.tag == "TableOfContents"
        assert root.get("schema") == "legal_toc"
        
        # Check metadata
        metadata = root.find("Metadata")
        assert metadata is not None
        assert metadata.find("TotalEntries").text == str(len(sample_documents))
        
        # Check entries
        entries = root.find("Entries")
        assert len(entries) == len(sample_documents)

    def test_generate_exhibit_list(self, temp_dir, sample_documents):
        """Test exhibit list generation."""
        toc_gen = TOCGenerator()
        
        # Add exhibit entries
        exhibit_numbers = {}
        for i, doc in enumerate(sample_documents):
            if doc.document_type == DocumentType.EXHIBIT:
                entry_id = toc_gen.add_entry(
                    document=doc,
                    title=f"Contract Agreement - {doc.file_name}",
                    page_number=i * 10 + 1
                )
                exhibit_numbers[doc.document_id] = f"A-{i+1}"
        
        # Generate exhibit list
        output_path = temp_dir / "exhibit_list.html"
        result_path = toc_gen.generate_exhibit_list(
            output_path,
            party_name="Smith",
            exhibit_numbers=exhibit_numbers,
            format="html"
        )
        
        assert result_path.exists()
        content = result_path.read_text()
        assert "Smith Exhibit List" in content
        assert "Exhibit No." in content

    def test_generate_hyperlinks(self, sample_documents):
        """Test hyperlink generation for entries."""
        toc_gen = TOCGenerator()
        
        # Add entries
        entry_ids = []
        for doc in sample_documents:
            entry_id = toc_gen.add_entry(document=doc, page_number=1)
            entry_ids.append(entry_id)
        
        # Generate hyperlinks
        base_url = "https://legal-archive.example.com"
        hyperlinks = toc_gen.generate_hyperlinks(base_url, use_document_ids=True)
        
        assert len(hyperlinks) == len(sample_documents)
        for entry_id in entry_ids:
            assert entry_id in hyperlinks
            assert hyperlinks[entry_id].startswith(base_url)
            assert "#page=" in hyperlinks[entry_id]

    def test_complex_hierarchy_toc(self, temp_dir):
        """Test TOC generation for complex hierarchical structures."""
        toc_gen = TOCGenerator()
        
        # Create complex structure
        root_doc = DocumentMetadata(
            document_id="root",
            file_name="Case File",
            document_type=DocumentType.OTHER,
            page_count=1,
            file_size=1,
            checksum=""
        )
        
        root_id = toc_gen.add_entry(
            document=root_doc,
            title="Smith v. Jones - Case File",
            level=0
        )
        
        # Add multiple levels
        for section in range(3):
            section_doc = DocumentMetadata(
                document_id=f"section_{section}",
                file_name=f"Section {section}",
                document_type=DocumentType.OTHER,
                page_count=1,
                file_size=1,
                checksum=""
            )
            
            section_id = toc_gen.add_entry(
                document=section_doc,
                title=f"Section {section + 1}",
                level=1,
                parent_id=root_id
            )
            
            # Add documents to section
            for doc_num in range(5):
                doc = DocumentMetadata(
                    document_id=f"doc_{section}_{doc_num}",
                    file_name=f"Document {doc_num}.pdf",
                    document_type=DocumentType.DISCOVERY,
                    page_count=10,
                    file_size=100000,
                    checksum=f"hash_{section}_{doc_num}"
                )
                
                toc_gen.add_entry(
                    document=doc,
                    title=f"Document {section}.{doc_num}",
                    level=2,
                    parent_id=section_id,
                    page_number=(section * 50) + (doc_num * 10) + 1
                )
        
        # Generate HTML with hierarchy
        output_path = temp_dir / "complex_toc.html"
        toc_gen.generate_html(output_path, collapsible=True)
        
        assert output_path.exists()
        content = output_path.read_text()
        assert "Smith v. Jones - Case File" in content
        assert "Section 1" in content
        assert "Document 0.0" in content

    def test_toc_page_number_assignment(self, sample_documents):
        """Test automatic page number assignment."""
        hierarchy = LegalHierarchy()
        root_id = hierarchy.create_hierarchy("2023-CV-12345")
        
        # Create documents with known page counts
        doc_dict = {}
        total_pages = 0
        for i, doc in enumerate(sample_documents):
            doc.page_count = (i + 1) * 10  # 10, 20, 30 pages
            hierarchy.add_document(doc)
            doc_dict[doc.document_id] = doc
            total_pages += doc.page_count
        
        # Generate TOC
        toc_gen = TOCGenerator()
        toc_gen.generate_from_hierarchy(hierarchy.nodes, doc_dict, root_id)
        
        # Check page numbers are sequential
        page_numbers = []
        for entry in toc_gen.entries.values():
            if entry.page_number and not entry.document_id.startswith("section_"):
                page_numbers.append(entry.page_number)
        
        # Page numbers should be assigned
        assert len(page_numbers) > 0
        # First document should start at page 1
        assert min(page_numbers) == 1

    def test_performance_large_toc(self, temp_dir):
        """Test performance with large TOC generation."""
        toc_gen = TOCGenerator()
        
        # Add many entries
        import time
        start_time = time.time()
        
        for i in range(1000):
            doc = DocumentMetadata(
                document_id=f"doc_{i:04d}",
                file_name=f"Document_{i:04d}.pdf",
                document_type="discovery",
                page_count=5,
                file_size=50000,
                checksum=f"hash_{i}"
            )
            
            toc_gen.add_entry(
                document=doc,
                title=f"Discovery Document {i:04d}",
                page_number=i * 5 + 1,
                level=0
            )
        
        # Generate TOC
        output_path = temp_dir / "large_toc.html"
        toc_gen.generate_html(output_path)
        
        elapsed_time = time.time() - start_time
        
        # Should handle 1000 entries quickly
        assert elapsed_time < 5.0  # Should complete in under 5 seconds
        assert output_path.exists()
        assert len(toc_gen.entries) == 1000

    def test_template_customization(self, temp_dir, sample_documents):
        """Test using custom templates."""
        # Create custom template
        custom_template = """
        <html>
        <head><title>Custom TOC</title></head>
        <body>
            <h1>{{ title }}</h1>
            <ul>
            {% for entry in entries %}
                <li>{{ entry.title }} - Page {{ entry.page_number }}</li>
            {% endfor %}
            </ul>
        </body>
        </html>
        """
        
        template_dir = temp_dir / "templates"
        template_dir.mkdir()
        (template_dir / "toc_html.html").write_text(custom_template)
        
        # Use custom template
        toc_gen = TOCGenerator(template_dir=template_dir)
        
        for doc in sample_documents:
            toc_gen.add_entry(document=doc, page_number=1)
        
        output_path = temp_dir / "custom_toc.html"
        toc_gen.generate_html(output_path)
        
        content = output_path.read_text()
        assert "<ul>" in content
        assert "Page 1" in content