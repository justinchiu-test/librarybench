"""Table of contents generation in multiple formats for legal archives."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, Template
from lxml import etree

from .models import DocumentMetadata, DocumentType, TOCEntry, HierarchyNode


logger = logging.getLogger(__name__)


class TOCGenerator:
    """Generates table of contents in multiple formats."""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize TOC generator.

        Args:
            template_dir: Directory containing custom templates
        """
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self._ensure_default_templates()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )
        self.entries: Dict[str, TOCEntry] = {}
        self._entry_counter = 0

    def add_entry(
        self,
        document: DocumentMetadata,
        title: Optional[str] = None,
        page_number: Optional[int] = None,
        level: int = 0,
        parent_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> str:
        """Add an entry to the table of contents.

        Args:
            document: Document metadata
            title: Entry title (defaults to file name)
            page_number: Page number in compiled document
            level: Hierarchy level (0 = top level)
            parent_id: Parent entry ID
            summary: Document summary

        Returns:
            Entry ID
        """
        entry_id = self._generate_entry_id()
        
        entry = TOCEntry(
            entry_id=entry_id,
            document_id=document.document_id,
            title=title or document.file_name,
            page_number=page_number,
            level=level,
            parent_entry_id=parent_id,
            summary=summary,
        )
        
        self.entries[entry_id] = entry
        
        # Update parent's children
        if parent_id and parent_id in self.entries:
            self.entries[parent_id].children.append(entry_id)
        
        return entry_id

    def generate_from_hierarchy(
        self,
        hierarchy: Dict[str, HierarchyNode],
        documents: Dict[str, DocumentMetadata],
        root_node_id: str,
    ) -> None:
        """Generate TOC from legal hierarchy.

        Args:
            hierarchy: Dictionary of hierarchy nodes
            documents: Dictionary of document metadata
            root_node_id: Root node to start from
        """
        self.entries.clear()
        self._entry_counter = 0
        
        # Traverse hierarchy and create entries
        self._traverse_hierarchy(
            hierarchy, documents, root_node_id, level=0, parent_entry_id=None
        )
        
        # Generate page numbers
        self._assign_page_numbers(documents)

    def generate_pdf(
        self,
        output_path: Path,
        case_info: Optional[Dict] = None,
        include_hyperlinks: bool = True,
    ) -> Path:
        """Generate PDF table of contents.

        Args:
            output_path: Output file path
            case_info: Case information for header
            include_hyperlinks: Whether to include document hyperlinks

        Returns:
            Path to generated PDF
        """
        # Get template
        template = self.jinja_env.get_template("toc_pdf.html")
        
        # Prepare data
        toc_data = self._prepare_toc_data()
        context = {
            "title": "Table of Contents",
            "case_info": case_info or {},
            "entries": toc_data,
            "include_hyperlinks": include_hyperlinks,
            "generated_date": datetime.now().strftime("%B %d, %Y"),
            "total_documents": len(self.entries),
        }
        
        # Render HTML
        html_content = template.render(**context)
        
        # In production, would use proper PDF generation library
        # For now, save as HTML that can be converted to PDF
        html_path = output_path.with_suffix(".html")
        with open(html_path, "w") as f:
            f.write(html_content)
        
        logger.info(f"Generated PDF TOC at {html_path}")
        return html_path

    def generate_html(
        self,
        output_path: Path,
        case_info: Optional[Dict] = None,
        include_summaries: bool = True,
        collapsible: bool = True,
    ) -> Path:
        """Generate HTML table of contents.

        Args:
            output_path: Output file path
            case_info: Case information for header
            include_summaries: Whether to include document summaries
            collapsible: Whether to make hierarchy collapsible

        Returns:
            Path to generated HTML
        """
        template = self.jinja_env.get_template("toc_html.html")
        
        toc_data = self._prepare_toc_data()
        context = {
            "title": "Legal Document Archive - Table of Contents",
            "case_info": case_info or {},
            "entries": toc_data,
            "include_summaries": include_summaries,
            "collapsible": collapsible,
            "generated_date": datetime.now().strftime("%B %d, %Y"),
            "total_documents": len(self.entries),
        }
        
        html_content = template.render(**context)
        
        with open(output_path, "w") as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML TOC at {output_path}")
        return output_path

    def generate_xml(
        self,
        output_path: Path,
        schema: Optional[str] = "legal_toc",
        include_metadata: bool = True,
    ) -> Path:
        """Generate XML table of contents.

        Args:
            output_path: Output file path
            schema: XML schema to use
            include_metadata: Whether to include document metadata

        Returns:
            Path to generated XML
        """
        # Create root element
        root = etree.Element(
            "TableOfContents",
            schema=schema,
            generated=datetime.now().isoformat(),
        )
        
        # Add metadata
        if include_metadata:
            metadata = etree.SubElement(root, "Metadata")
            etree.SubElement(metadata, "TotalEntries").text = str(len(self.entries))
            etree.SubElement(metadata, "GeneratedDate").text = datetime.now().isoformat()
        
        # Add entries
        entries_elem = etree.SubElement(root, "Entries")
        
        # Build hierarchical structure
        root_entries = [e for e in self.entries.values() if not e.parent_entry_id]
        for entry in sorted(root_entries, key=lambda e: e.page_number or 0):
            self._add_xml_entry(entries_elem, entry, include_metadata)
        
        # Write XML
        tree = etree.ElementTree(root)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        
        logger.info(f"Generated XML TOC at {output_path}")
        return output_path

    def generate_exhibit_list(
        self,
        output_path: Path,
        party_name: str,
        exhibit_numbers: Dict[str, str],
        format: str = "pdf",
    ) -> Path:
        """Generate exhibit list for court filing.

        Args:
            output_path: Output file path
            party_name: Party name for exhibit list
            exhibit_numbers: Mapping of document IDs to exhibit numbers
            format: Output format (pdf, html)

        Returns:
            Path to generated exhibit list
        """
        # Filter entries for exhibits
        exhibit_entries = []
        for entry in self.entries.values():
            if entry.document_id in exhibit_numbers:
                exhibit_data = {
                    "exhibit_number": exhibit_numbers[entry.document_id],
                    "description": entry.title,
                    "page_number": entry.page_number,
                    "document_id": entry.document_id,
                }
                exhibit_entries.append(exhibit_data)
        
        # Sort by exhibit number
        exhibit_entries.sort(key=lambda x: x["exhibit_number"])
        
        # Generate based on format
        if format == "html":
            template = self.jinja_env.get_template("exhibit_list.html")
        else:
            template = self.jinja_env.get_template("exhibit_list_pdf.html")
        
        context = {
            "party_name": party_name,
            "exhibits": exhibit_entries,
            "total_exhibits": len(exhibit_entries),
            "generated_date": datetime.now().strftime("%B %d, %Y"),
        }
        
        content = template.render(**context)
        
        with open(output_path, "w") as f:
            f.write(content)
        
        logger.info(f"Generated exhibit list at {output_path}")
        return output_path

    def generate_hyperlinks(
        self, base_url: str, use_document_ids: bool = True
    ) -> Dict[str, str]:
        """Generate hyperlinks for all TOC entries.

        Args:
            base_url: Base URL for documents
            use_document_ids: Use document IDs vs file names

        Returns:
            Mapping of entry IDs to hyperlinks
        """
        hyperlinks = {}
        
        for entry in self.entries.values():
            if use_document_ids:
                url = f"{base_url}/document/{entry.document_id}"
            else:
                # Would need document metadata for file names
                url = f"{base_url}/file/{entry.document_id}"
            
            if entry.page_number:
                url += f"#page={entry.page_number}"
            
            hyperlinks[entry.entry_id] = url
            entry.hyperlink = url
        
        return hyperlinks

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID."""
        self._entry_counter += 1
        return f"toc_entry_{self._entry_counter:06d}"

    def _traverse_hierarchy(
        self,
        hierarchy: Dict[str, HierarchyNode],
        documents: Dict[str, DocumentMetadata],
        node_id: str,
        level: int,
        parent_entry_id: Optional[str],
    ) -> None:
        """Recursively traverse hierarchy to create TOC entries."""
        node = hierarchy.get(node_id)
        if not node:
            return
        
        # Create entry for node if it has documents
        node_entry_id = None
        if node.documents:
            # Create section entry
            node_entry_id = self.add_entry(
                document=DocumentMetadata(
                    document_id=f"section_{node_id}",
                    file_name=node.name,
                    document_type=DocumentType.OTHER,
                    page_count=1,
                    file_size=1,
                    checksum="section",
                ),
                title=node.name,
                level=level,
                parent_id=parent_entry_id,
            )
            
            # Add documents in node
            for doc_id in node.documents:
                if doc_id in documents:
                    self.add_entry(
                        document=documents[doc_id],
                        level=level + 1,
                        parent_id=node_entry_id,
                    )
        
        # Traverse children
        for child_id in node.children:
            self._traverse_hierarchy(
                hierarchy,
                documents,
                child_id,
                level + 1 if node_entry_id else level,
                node_entry_id or parent_entry_id,
            )

    def _assign_page_numbers(self, documents: Dict[str, DocumentMetadata]) -> None:
        """Assign page numbers based on document order."""
        current_page = 1
        
        # Process entries in order
        def process_entry(entry_id: str) -> int:
            nonlocal current_page
            entry = self.entries[entry_id]
            
            if not entry.document_id.startswith("section_"):
                # Actual document
                if entry.document_id in documents:
                    doc = documents[entry.document_id]
                    entry.page_number = current_page
                    current_page += doc.page_count
            
            # Process children
            for child_id in entry.children:
                process_entry(child_id)
            
            return current_page
        
        # Process root entries
        root_entries = [e for e in self.entries.values() if not e.parent_entry_id]
        for entry in root_entries:
            process_entry(entry.entry_id)

    def _prepare_toc_data(self) -> List[Dict]:
        """Prepare TOC data for templates."""
        def build_entry_data(entry: TOCEntry) -> Dict:
            data = {
                "id": entry.entry_id,
                "title": entry.title,
                "page_number": entry.page_number,
                "level": entry.level,
                "summary": entry.summary,
                "hyperlink": entry.hyperlink,
                "children": [],
            }
            
            for child_id in entry.children:
                if child_id in self.entries:
                    data["children"].append(build_entry_data(self.entries[child_id]))
            
            return data
        
        # Build from root entries
        root_entries = [e for e in self.entries.values() if not e.parent_entry_id]
        return [build_entry_data(entry) for entry in sorted(
            root_entries, key=lambda e: e.page_number or 0
        )]

    def _add_xml_entry(
        self, parent_elem: etree.Element, entry: TOCEntry, include_metadata: bool
    ) -> None:
        """Add entry to XML recursively."""
        entry_elem = etree.SubElement(parent_elem, "Entry")
        entry_elem.set("id", entry.entry_id)
        entry_elem.set("level", str(entry.level))
        
        etree.SubElement(entry_elem, "Title").text = entry.title
        
        if entry.page_number:
            etree.SubElement(entry_elem, "PageNumber").text = str(entry.page_number)
        
        if entry.hyperlink:
            etree.SubElement(entry_elem, "Hyperlink").text = entry.hyperlink
        
        if include_metadata and entry.summary:
            etree.SubElement(entry_elem, "Summary").text = entry.summary
        
        # Add children
        if entry.children:
            children_elem = etree.SubElement(entry_elem, "Children")
            for child_id in entry.children:
                if child_id in self.entries:
                    self._add_xml_entry(
                        children_elem, self.entries[child_id], include_metadata
                    )

    def _ensure_default_templates(self) -> None:
        """Ensure default templates exist."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic templates if they don't exist
        templates = {
            "toc_pdf.html": self._get_default_pdf_template(),
            "toc_html.html": self._get_default_html_template(),
            "exhibit_list.html": self._get_default_exhibit_template(),
            "exhibit_list_pdf.html": self._get_default_exhibit_pdf_template(),
        }
        
        for filename, content in templates.items():
            template_path = self.template_dir / filename
            if not template_path.exists():
                template_path.write_text(content)

    def _get_default_pdf_template(self) -> str:
        """Get default PDF template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Times New Roman, serif; }
        .header { text-align: center; margin-bottom: 30px; }
        .entry { margin: 5px 0; }
        .level-0 { margin-left: 0px; }
        .level-1 { margin-left: 20px; }
        .level-2 { margin-left: 40px; }
        .level-3 { margin-left: 60px; }
        .level-4 { margin-left: 80px; }
        .level-5 { margin-left: 100px; }
        .page-number { float: right; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        {% if case_info.case_number %}
        <p>Case No. {{ case_info.case_number }}</p>
        {% endif %}
    </div>
    {%- macro render_entry(entry) -%}
    <div class="entry level-{{ entry.level }}">
        <span>{{ entry.title }}</span>
        <span class="page-number">{{ entry.page_number or '' }}</span>
    </div>
    {%- if entry.children %}
    {%- for child in entry.children %}
    {{ render_entry(child) }}
    {%- endfor %}
    {%- endif %}
    {%- endmacro -%}
    
    {%- for entry in entries %}
    {{ render_entry(entry) }}
    {%- endfor %}
</body>
</html>'''

    def _get_default_html_template(self) -> str:
        """Get default HTML template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .toc-entry { margin: 10px 0; }
        .level-0 { margin-left: 0px; }
        .level-1 { margin-left: 20px; }
        .level-2 { margin-left: 40px; }
        .level-3 { margin-left: 60px; }
        .level-4 { margin-left: 80px; }
        .level-5 { margin-left: 100px; }
        .summary { font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="toc-container">
        {%- macro render_entry(entry) -%}
        <div class="toc-entry level-{{ entry.level }}">
            <a href="{{ entry.hyperlink or '#' }}">{{ entry.title }}</a>
            {%- if include_summaries and entry.summary %}
            <div class="summary">{{ entry.summary }}</div>
            {%- endif %}
            {%- if entry.children %}
            {%- for child in entry.children %}
            {{ render_entry(child) }}
            {%- endfor %}
            {%- endif %}
        </div>
        {%- endmacro -%}
        
        {%- for entry in entries %}
        {{ render_entry(entry) }}
        {%- endfor %}
    </div>
</body>
</html>'''

    def _get_default_exhibit_template(self) -> str:
        """Get default exhibit list template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Exhibit List - {{ party_name }}</title>
</head>
<body>
    <h1>{{ party_name }} Exhibit List</h1>
    <table>
        <tr>
            <th>Exhibit No.</th>
            <th>Description</th>
            <th>Page</th>
        </tr>
        {% for exhibit in exhibits %}
        <tr>
            <td>{{ exhibit.exhibit_number }}</td>
            <td>{{ exhibit.description }}</td>
            <td>{{ exhibit.page_number }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>'''

    def _get_default_exhibit_pdf_template(self) -> str:
        """Get default exhibit PDF template."""
        return self._get_default_exhibit_template()