"""Cross-reference preservation for linked legal documents."""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pypdf

from .models import CrossReference, DocumentMetadata


logger = logging.getLogger(__name__)


class CrossReferenceManager:
    """Manages cross-references between legal documents."""

    def __init__(self):
        """Initialize cross-reference manager."""
        self.references: Dict[str, CrossReference] = {}
        self.document_references: Dict[str, List[str]] = defaultdict(list)
        self.citation_patterns = self._load_citation_patterns()
        self._ref_counter = 0

    def extract_references(
        self,
        document_id: str,
        content: str,
        document_type: str = "general",
    ) -> List[CrossReference]:
        """Extract cross-references from document content.

        Args:
            document_id: Source document ID
            content: Document text content
            document_type: Type of document for pattern matching

        Returns:
            List of extracted cross-references
        """
        references = []
        
        # Extract various types of references
        references.extend(self._extract_legal_citations(document_id, content))
        references.extend(self._extract_exhibit_references(document_id, content))
        references.extend(self._extract_document_references(document_id, content))
        references.extend(self._extract_hyperlinks(document_id, content))
        
        # Store references
        for ref in references:
            self.add_reference(ref)
        
        logger.info(f"Extracted {len(references)} references from {document_id}")
        return references

    def add_reference(self, reference: CrossReference) -> None:
        """Add a cross-reference.

        Args:
            reference: Cross-reference to add
        """
        self.references[reference.reference_id] = reference
        self.document_references[reference.source_document_id].append(
            reference.reference_id
        )
        
        if reference.is_bidirectional:
            # Create reverse reference
            reverse_ref = CrossReference(
                reference_id=self._generate_reference_id(),
                source_document_id=reference.target_document_id,
                target_document_id=reference.source_document_id,
                source_page=reference.target_page,
                target_page=reference.source_page,
                reference_type=f"reverse_{reference.reference_type}",
                reference_text=reference.reference_text,
                is_bidirectional=False,
            )
            self.references[reverse_ref.reference_id] = reverse_ref
            self.document_references[reverse_ref.source_document_id].append(
                reverse_ref.reference_id
            )

    def preserve_references_in_archive(
        self,
        archive_path: Path,
        document_mapping: Dict[str, str],
    ) -> None:
        """Preserve references when creating archive.

        Args:
            archive_path: Path to archive being created
            document_mapping: Mapping of document IDs to archive paths
        """
        # Update references with archive paths
        preserved_refs = []
        
        for ref in self.references.values():
            if (ref.source_document_id in document_mapping and 
                ref.target_document_id in document_mapping):
                
                preserved_ref = {
                    "reference_id": ref.reference_id,
                    "source_path": document_mapping[ref.source_document_id],
                    "target_path": document_mapping[ref.target_document_id],
                    "source_page": ref.source_page,
                    "target_page": ref.target_page,
                    "reference_type": ref.reference_type,
                    "reference_text": ref.reference_text,
                }
                preserved_refs.append(preserved_ref)
        
        # Save reference manifest
        manifest_path = archive_path.parent / f"{archive_path.stem}_references.json"
        manifest = {
            "total_references": len(preserved_refs),
            "reference_types": self._count_reference_types(),
            "references": preserved_refs,
        }
        
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Preserved {len(preserved_refs)} references in {manifest_path}")

    def verify_reference_integrity(
        self, document_ids: Set[str]
    ) -> Tuple[bool, List[str]]:
        """Verify that all references point to valid documents.

        Args:
            document_ids: Set of valid document IDs

        Returns:
            Tuple of (is_valid, list_of_broken_references)
        """
        broken_references = []
        
        for ref in self.references.values():
            if ref.target_document_id not in document_ids:
                broken_references.append(
                    f"Reference {ref.reference_id}: "
                    f"{ref.source_document_id} -> {ref.target_document_id} (missing)"
                )
        
        is_valid = len(broken_references) == 0
        
        if not is_valid:
            logger.warning(f"Found {len(broken_references)} broken references")
        
        return is_valid, broken_references

    def get_document_references(
        self, document_id: str, include_incoming: bool = True
    ) -> Dict[str, List[CrossReference]]:
        """Get all references for a document.

        Args:
            document_id: Document ID
            include_incoming: Whether to include incoming references

        Returns:
            Dictionary with outgoing and optionally incoming references
        """
        result = {"outgoing": [], "incoming": []}
        
        # Get outgoing references
        for ref_id in self.document_references.get(document_id, []):
            if ref_id in self.references:
                result["outgoing"].append(self.references[ref_id])
        
        # Get incoming references if requested
        if include_incoming:
            for ref in self.references.values():
                if ref.target_document_id == document_id:
                    result["incoming"].append(ref)
        
        return result

    def build_citation_chain(
        self, document_id: str, max_depth: int = 5
    ) -> Dict[str, List[str]]:
        """Build citation chain for a document.

        Args:
            document_id: Starting document ID
            max_depth: Maximum depth to traverse

        Returns:
            Citation chain as adjacency list
        """
        chain = defaultdict(list)
        visited = set()
        
        def traverse(doc_id: str, depth: int):
            if depth >= max_depth or doc_id in visited:
                return
            
            visited.add(doc_id)
            
            # Get outgoing citations
            for ref_id in self.document_references.get(doc_id, []):
                if ref_id in self.references:
                    ref = self.references[ref_id]
                    if ref.reference_type in ["citation", "legal_citation"]:
                        chain[doc_id].append(ref.target_document_id)
                        traverse(ref.target_document_id, depth + 1)
        
        traverse(document_id, 0)
        return dict(chain)

    def generate_reference_graph(
        self, output_path: Path, format: str = "json"
    ) -> Path:
        """Generate visual representation of references.

        Args:
            output_path: Output file path
            format: Output format (json, dot, etc.)

        Returns:
            Path to generated graph
        """
        if format == "json":
            # Generate JSON representation
            nodes = []
            edges = []
            
            # Collect all document IDs
            doc_ids = set()
            for ref in self.references.values():
                doc_ids.add(ref.source_document_id)
                doc_ids.add(ref.target_document_id)
            
            # Create nodes
            for doc_id in doc_ids:
                nodes.append({"id": doc_id, "label": doc_id})
            
            # Create edges
            for ref in self.references.values():
                edges.append({
                    "source": ref.source_document_id,
                    "target": ref.target_document_id,
                    "type": ref.reference_type,
                    "label": ref.reference_text[:50] if ref.reference_text else "",
                })
            
            graph_data = {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_documents": len(nodes),
                    "total_references": len(edges),
                    "reference_types": self._count_reference_types(),
                }
            }
            
            with open(output_path, "w") as f:
                json.dump(graph_data, f, indent=2)
        
        elif format == "dot":
            # Generate Graphviz DOT format
            dot_content = ["digraph references {"]
            dot_content.append('  rankdir=LR;')
            dot_content.append('  node [shape=box];')
            
            # Add nodes
            doc_ids = set()
            for ref in self.references.values():
                doc_ids.add(ref.source_document_id)
                doc_ids.add(ref.target_document_id)
            
            for doc_id in doc_ids:
                dot_content.append(f'  "{doc_id}";')
            
            # Add edges
            for ref in self.references.values():
                label = ref.reference_type
                dot_content.append(
                    f'  "{ref.source_document_id}" -> "{ref.target_document_id}" '
                    f'[label="{label}"];'
                )
            
            dot_content.append("}")
            
            with open(output_path, "w") as f:
                f.write("\n".join(dot_content))
        
        logger.info(f"Generated reference graph at {output_path}")
        return output_path

    def update_references_after_modification(
        self,
        document_id: str,
        page_offset: int,
        operation: str = "insert",
    ) -> None:
        """Update references after document modification.

        Args:
            document_id: Modified document ID
            page_offset: Number of pages added/removed
            operation: Type of operation (insert, delete)
        """
        # Update references pointing to this document
        for ref in self.references.values():
            if ref.target_document_id == document_id and ref.target_page:
                if operation == "insert":
                    ref.target_page += page_offset
                elif operation == "delete" and ref.target_page > page_offset:
                    ref.target_page = max(1, ref.target_page - page_offset)
        
        logger.info(
            f"Updated references for {document_id} after {operation} "
            f"with offset {page_offset}"
        )

    def _generate_reference_id(self) -> str:
        """Generate unique reference ID."""
        self._ref_counter += 1
        return f"ref_{self._ref_counter:08d}"

    def _load_citation_patterns(self) -> Dict[str, re.Pattern]:
        """Load legal citation patterns."""
        return {
            # Matches both case names (Smith v. Jones) and reporter citations (123 F.3d 456)
            "case_citation": re.compile(
                r"(?:([A-Z][A-Za-z]+(?:\s+[A-Za-z.]+)*)\s+v\.\s+([A-Z][A-Za-z]+(?:\s+[A-Za-z.]+)*),?\s+)?(\d{1,4})\s+([A-Z][A-Za-z.]+(?:\s+\d+[a-z]+)?)\s+(\d{1,4})(?:\s*\((?:[\w\s.]+\s+)?\d{4}\))?"
            ),
            "statute_citation": re.compile(
                r"\b(\d{1,3})\s+U\.?\s?S\.?\s?C\.?\s*§+\s*(\d+(?:\([a-zA-Z0-9]+\))?)"
            ),
            "regulation_citation": re.compile(
                r"\b(\d{1,3})\s+C\.?\s?F\.?\s?R\.?\s*§?\s*(\d+(?:\.\d+)*(?:\([a-zA-Z0-9]+\))*)"
            ),
            "exhibit_reference": re.compile(
                r"\b(?:Exhibit|Ex\.|Exh\.)\s+([A-Z0-9][A-Z0-9\-]*)",
                re.IGNORECASE
            ),
            "document_reference": re.compile(
                r"\b(?:Document|Doc\.)\s+(\d+(?:-\d+)?)",
                re.IGNORECASE
            ),
            "page_reference": re.compile(
                r"\b(?:at|@)\s+(?:p\.|page|pp\.)\s*(\d+(?:-\d+)?)",
                re.IGNORECASE
            ),
        }

    def _extract_legal_citations(
        self, document_id: str, content: str
    ) -> List[CrossReference]:
        """Extract legal citations from content."""
        references = []
        
        # Extract case citations
        case_pattern = self.citation_patterns.get("case_citation")
        if case_pattern:
            for match in case_pattern.finditer(content):
                ref = CrossReference(
                    reference_id=self._generate_reference_id(),
                    source_document_id=document_id,
                    target_document_id=f"case_{match.group(0).replace(' ', '_').replace('.', '')}",
                    reference_type="legal_citation",
                    reference_text=match.group(0),
                )
                references.append(ref)
        
        # Extract statute citations
        statute_pattern = self.citation_patterns.get("statute_citation")
        if statute_pattern:
            for match in statute_pattern.finditer(content):
                ref = CrossReference(
                    reference_id=self._generate_reference_id(),
                    source_document_id=document_id,
                    target_document_id=f"statute_{match.group(0).replace(' ', '_').replace('.', '')}",
                    reference_type="statute_citation",
                    reference_text=match.group(0),
                )
                references.append(ref)
        
        # Extract regulation citations  
        reg_pattern = self.citation_patterns.get("regulation_citation")
        if reg_pattern:
            for match in reg_pattern.finditer(content):
                ref = CrossReference(
                    reference_id=self._generate_reference_id(),
                    source_document_id=document_id,
                    target_document_id=f"regulation_{match.group(0).replace(' ', '_').replace('.', '')}",
                    reference_type="regulation_citation",
                    reference_text=match.group(0),
                )
                references.append(ref)
        
        return references

    def _extract_exhibit_references(
        self, document_id: str, content: str
    ) -> List[CrossReference]:
        """Extract exhibit references from content."""
        references = []
        
        exhibit_pattern = self.citation_patterns.get("exhibit_reference")
        if exhibit_pattern:
            for match in exhibit_pattern.finditer(content):
                ref = CrossReference(
                    reference_id=self._generate_reference_id(),
                    source_document_id=document_id,
                    target_document_id=f"exhibit_{match.group(1)}",
                    reference_type="exhibit",
                    reference_text=match.group(0),
                )
                references.append(ref)
        
        return references

    def _extract_document_references(
        self, document_id: str, content: str
    ) -> List[CrossReference]:
        """Extract document references from content."""
        references = []
        
        doc_pattern = self.citation_patterns.get("document_reference")
        if doc_pattern:
            for match in doc_pattern.finditer(content):
                ref = CrossReference(
                    reference_id=self._generate_reference_id(),
                    source_document_id=document_id,
                    target_document_id=f"document_{match.group(1)}",
                    reference_type="document",
                    reference_text=match.group(0),
                )
                references.append(ref)
        
        return references

    def _extract_hyperlinks(
        self, document_id: str, content: str
    ) -> List[CrossReference]:
        """Extract hyperlinks from content."""
        references = []
        
        # Simple pattern for internal document links
        link_pattern = re.compile(r"#doc:([a-zA-Z0-9_\-]+)")
        
        for match in link_pattern.finditer(content):
            ref = CrossReference(
                reference_id=self._generate_reference_id(),
                source_document_id=document_id,
                target_document_id=match.group(1),
                reference_type="hyperlink",
                reference_text=match.group(0),
            )
            references.append(ref)
        
        return references

    def _count_reference_types(self) -> Dict[str, int]:
        """Count references by type."""
        type_counts = defaultdict(int)
        for ref in self.references.values():
            type_counts[ref.reference_type] += 1
        return dict(type_counts)