"""Hierarchical archive structure matching legal filing systems."""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .models import DocumentMetadata, DocumentType, HierarchyNode


logger = logging.getLogger(__name__)


class LegalHierarchy:
    """Manages hierarchical structure for legal document archives."""

    def __init__(self):
        """Initialize legal hierarchy manager."""
        self.nodes: Dict[str, HierarchyNode] = {}
        self.document_locations: Dict[str, str] = {}  # doc_id -> node_id
        self.templates: Dict[str, Dict] = self._load_default_templates()
        self._id_counter = 0

    def create_hierarchy(
        self,
        case_number: str,
        template_name: Optional[str] = "federal_court",
    ) -> str:
        """Create a new hierarchy for a case.

        Args:
            case_number: Case number for the hierarchy
            template_name: Template to use for structure

        Returns:
            Root node ID
        """
        template = self.templates.get(template_name, self.templates["default"])
        root_id = self._generate_node_id()

        root_node = HierarchyNode(
            node_id=root_id,
            name=f"Case {case_number}",
            node_type="case",
            metadata={"case_number": case_number, "template": template_name},
        )
        self.nodes[root_id] = root_node

        # Build structure from template
        self._apply_template(root_node, template)

        logger.info(f"Created hierarchy for case {case_number} using {template_name}")
        return root_id

    def add_document(
        self,
        document: DocumentMetadata,
        parent_node_id: Optional[str] = None,
        auto_organize: bool = True,
    ) -> str:
        """Add a document to the hierarchy.

        Args:
            document: Document metadata
            parent_node_id: Specific node to add to (optional)
            auto_organize: Whether to automatically place based on metadata

        Returns:
            Node ID where document was placed
        """
        if auto_organize and not parent_node_id:
            parent_node_id = self._find_appropriate_node(document)

        if not parent_node_id or parent_node_id not in self.nodes:
            raise ValueError(f"Invalid parent node: {parent_node_id}")

        parent_node = self.nodes[parent_node_id]
        parent_node.documents.append(document.document_id)
        self.document_locations[document.document_id] = parent_node_id

        # Apply legal numbering
        self._apply_legal_numbering(document, parent_node)

        logger.info(
            f"Added document {document.document_id} to node {parent_node_id}"
        )
        return parent_node_id

    def create_node(
        self,
        name: str,
        node_type: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """Create a new node in the hierarchy.

        Args:
            name: Node name
            node_type: Type of node (party, document_type, etc.)
            parent_id: Parent node ID
            metadata: Additional metadata

        Returns:
            New node ID
        """
        node_id = self._generate_node_id()
        node = HierarchyNode(
            node_id=node_id,
            name=name,
            node_type=node_type,
            parent_id=parent_id,
            metadata=metadata or {},
        )

        self.nodes[node_id] = node

        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children.append(node_id)
            node.sort_order = len(self.nodes[parent_id].children)

        return node_id

    def get_path(self, node_id: str) -> List[str]:
        """Get the full path from root to a node.

        Args:
            node_id: Node ID

        Returns:
            List of node names from root to node
        """
        path = []
        current = self.nodes.get(node_id)

        while current:
            path.append(current.name)
            current = (
                self.nodes.get(current.parent_id) if current.parent_id else None
            )

        return list(reversed(path))

    def apply_bates_numbering(
        self, start_number: int = 1, prefix: str = ""
    ) -> Dict[str, str]:
        """Apply Bates numbering to all documents.

        Args:
            start_number: Starting Bates number
            prefix: Prefix for Bates numbers

        Returns:
            Mapping of document IDs to Bates numbers
        """
        bates_mapping = {}
        current_number = start_number

        # Traverse hierarchy in order
        for node_id in self._traverse_in_order():
            node = self.nodes[node_id]
            for doc_id in node.documents:
                bates_number = f"{prefix}{current_number:06d}"
                bates_mapping[doc_id] = bates_number
                current_number += 1

        return bates_mapping

    def apply_exhibit_numbering(
        self, party_name: str, start_number: int = 1
    ) -> Dict[str, str]:
        """Apply exhibit numbering for a party.

        Args:
            party_name: Party name for exhibit prefix
            start_number: Starting exhibit number

        Returns:
            Mapping of document IDs to exhibit numbers
        """
        exhibit_mapping = {}
        current_number = start_number
        prefix = "".join(word[0].upper() for word in party_name.split())

        # Find exhibit nodes
        exhibit_nodes = [
            n for n in self.nodes.values()
            if n.node_type == "document_type" and "exhibit" in n.name.lower()
        ]

        for node in sorted(exhibit_nodes, key=lambda n: n.sort_order):
            for doc_id in node.documents:
                exhibit_number = f"{prefix}-{current_number}"
                exhibit_mapping[doc_id] = exhibit_number
                current_number += 1

        return exhibit_mapping

    def get_filing_order(self) -> List[str]:
        """Get documents in proper legal filing order.

        Returns:
            Ordered list of document IDs
        """
        ordered_docs = []

        # Define filing priority
        type_priority = {
            "pleading": 1,
            "motion": 2,
            "brief": 3,
            "exhibit": 4,
            "transcript": 5,
            "discovery": 6,
            "correspondence": 7,
            "court_order": 8,
            "other": 9,
        }

        # Collect documents with their metadata
        doc_info = []
        for node_id in self._traverse_in_order():
            node = self.nodes[node_id]
            for doc_id in node.documents:
                doc_info.append((doc_id, node))

        # Sort by legal filing conventions
        doc_info.sort(
            key=lambda x: (
                type_priority.get(x[1].metadata.get("document_type", "other"), 9),
                x[1].metadata.get("filing_date", ""),
                x[1].sort_order,
            )
        )

        return [doc_id for doc_id, _ in doc_info]

    def export_structure(self, output_path: Path) -> None:
        """Export hierarchy structure to JSON.

        Args:
            output_path: Path to save structure
        """
        structure = {
            "nodes": {
                node_id: node.model_dump() for node_id, node in self.nodes.items()
            },
            "document_locations": self.document_locations,
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_nodes": len(self.nodes),
                "total_documents": len(self.document_locations),
            },
        }

        with open(output_path, "w") as f:
            json.dump(structure, f, indent=2)

    def import_structure(self, input_path: Path) -> None:
        """Import hierarchy structure from JSON.

        Args:
            input_path: Path to load structure from
        """
        with open(input_path, "r") as f:
            structure = json.load(f)

        self.nodes.clear()
        self.document_locations.clear()

        for node_id, node_data in structure["nodes"].items():
            self.nodes[node_id] = HierarchyNode(**node_data)

        self.document_locations = structure["document_locations"]

    def _generate_node_id(self) -> str:
        """Generate unique node ID."""
        self._id_counter += 1
        return f"node_{self._id_counter:06d}"

    def _load_default_templates(self) -> Dict[str, Dict]:
        """Load default hierarchy templates."""
        return {
            "federal_court": {
                "structure": [
                    {
                        "name": "Pleadings",
                        "type": "document_type",
                        "children": ["Complaint", "Answer", "Reply"],
                    },
                    {
                        "name": "Motions",
                        "type": "document_type",
                        "children": ["Plaintiff Motions", "Defendant Motions"],
                    },
                    {
                        "name": "Discovery",
                        "type": "document_type",
                        "children": [
                            "Interrogatories",
                            "Depositions",
                            "Document Requests",
                        ],
                    },
                    {
                        "name": "Exhibits",
                        "type": "document_type",
                        "children": ["Plaintiff Exhibits", "Defendant Exhibits"],
                    },
                    {"name": "Court Orders", "type": "document_type"},
                    {"name": "Correspondence", "type": "document_type"},
                ]
            },
            "state_court": {
                "structure": [
                    {"name": "Initial Filings", "type": "document_type"},
                    {"name": "Responsive Pleadings", "type": "document_type"},
                    {"name": "Discovery", "type": "document_type"},
                    {"name": "Pre-Trial Motions", "type": "document_type"},
                    {"name": "Trial Documents", "type": "document_type"},
                    {"name": "Post-Trial", "type": "document_type"},
                ]
            },
            "default": {
                "structure": [
                    {"name": "Documents", "type": "document_type"},
                ]
            },
        }

    def _apply_template(
        self, parent_node: HierarchyNode, template: Dict
    ) -> None:
        """Apply template structure to hierarchy."""
        for item in template.get("structure", []):
            node_id = self.create_node(
                name=item["name"],
                node_type=item["type"],
                parent_id=parent_node.node_id,
            )

            if "children" in item:
                child_node = self.nodes[node_id]
                for child_name in item["children"]:
                    self.create_node(
                        name=child_name,
                        node_type="subcategory",
                        parent_id=node_id,
                    )

    def _find_appropriate_node(self, document: DocumentMetadata) -> str:
        """Find the appropriate node for a document based on metadata."""
        # Map document types to node names
        type_mapping = {
            "pleading": ["pleading", "complaint", "answer", "reply"],
            "motion": ["motion"],
            "exhibit": ["exhibit"],
            "discovery": ["discovery", "interrogator", "deposition", "request"],
            "brief": ["brief", "motion"],
            "transcript": ["transcript", "deposition"],
            "court_order": ["court order", "order"],
            "correspondence": ["correspondence", "letter"],
        }
        
        # Get possible node names for this document type
        doc_type_lower = document.document_type.value.lower()
        possible_names = type_mapping.get(doc_type_lower, [doc_type_lower])
        
        # Search for matching nodes
        for node in self.nodes.values():
            if node.node_type == "document_type":
                node_name_lower = node.name.lower()
                for name in possible_names:
                    if name in node_name_lower:
                        return node.node_id

                # Check children
                for child_id in node.children:
                    child = self.nodes[child_id]
                    child_name_lower = child.name.lower()
                    for name in possible_names:
                        if name in child_name_lower:
                            return child_id

        # Default to first document node
        for node in self.nodes.values():
            if node.node_type == "document_type":
                return node.node_id

        raise ValueError("No appropriate node found for document")

    def _apply_legal_numbering(
        self, document: DocumentMetadata, node: HierarchyNode
    ) -> None:
        """Apply legal numbering conventions to document."""
        # Set sort order based on filing date if available
        if document.filing_date:
            # Find position among existing documents
            existing_dates = []
            for doc_id in node.documents:
                if doc_id != document.document_id:
                    # In production, would look up actual document metadata
                    existing_dates.append(datetime.now())

            # Sort position
            position = sum(
                1 for d in existing_dates if d < document.filing_date
            )
            document.metadata["sort_order"] = str(position)

    def _traverse_in_order(self) -> List[str]:
        """Traverse hierarchy in legal filing order."""
        result = []

        def traverse(node_id: str):
            result.append(node_id)
            node = self.nodes[node_id]
            # Sort children by sort_order
            sorted_children = sorted(
                node.children,
                key=lambda cid: self.nodes[cid].sort_order
            )
            for child_id in sorted_children:
                traverse(child_id)

        # Find root nodes
        root_nodes = [
            n for n in self.nodes.values() if n.parent_id is None
        ]
        for root in sorted(root_nodes, key=lambda n: n.sort_order):
            traverse(root.node_id)

        return result