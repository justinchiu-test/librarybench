# Legal Document Archive System

A specialized archive management system designed for legal document processors to manage case files containing millions of documents while maintaining document relationships, enabling efficient court submissions, and supporting document search capabilities.

## Features

- **OCR Integration**: Convert scanned documents into searchable text within archives
- **Hierarchical Structure**: Organize documents according to federal and state court filing requirements
- **Redaction-Aware Compression**: Preserve document modifications and redaction layers securely
- **Multi-Format TOC Generation**: Create table of contents in PDF, HTML, and XML formats
- **Cross-Reference Preservation**: Maintain document relationships and citation chains

## Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install the package
uv pip install -e .
```

## Usage Examples

### Basic Archive Creation

```python
from legal_archive import (
    OCRProcessor,
    LegalHierarchy,
    RedactionAwareCompressor,
    TOCGenerator,
    CrossReferenceManager,
)
from legal_archive.models import DocumentMetadata, DocumentType, Redaction, RedactionLevel

# Initialize components
ocr = OCRProcessor(min_confidence=0.7)
hierarchy = LegalHierarchy()
compressor = RedactionAwareCompressor()
toc_gen = TOCGenerator()
ref_manager = CrossReferenceManager()

# Create hierarchy for a case
root_id = hierarchy.create_hierarchy("2023-CV-12345", "federal_court")

# Process documents with OCR
ocr_result = ocr.process_document(Path("scanned_doc.pdf"), "doc_001")

# Add document to hierarchy
metadata = DocumentMetadata(
    document_id="doc_001",
    file_name="complaint.pdf",
    document_type=DocumentType.PLEADING,
    case_number="2023-CV-12345",
    page_count=25,
    file_size=1024000,
    checksum="abc123",
)
hierarchy.add_document(metadata, auto_organize=True)

# Apply redaction
redaction = Redaction(
    redaction_id="red_001",
    document_id="doc_001",
    page_number=3,
    coordinates=[100, 200, 300, 250],
    redaction_level=RedactionLevel.CONFIDENTIAL,
    reason="Contains personal information",
    applied_by="Attorney Smith",
)
compressor.add_redaction(redaction)

# Create archive
documents = [(Path("complaint.pdf"), metadata)]
archive_path = Path("case_archive.zip")
stats = compressor.compress_with_redactions(documents, archive_path)

# Generate table of contents
toc_gen.generate_from_hierarchy(hierarchy.nodes, {"doc_001": metadata}, root_id)
toc_gen.generate_html(Path("toc.html"), case_info={"case_number": "2023-CV-12345"})
```

### Extract Documents with Access Control

```python
# Extract documents based on user's access level
allowed_levels = {RedactionLevel.PUBLIC, RedactionLevel.CONFIDENTIAL}
extracted_files = compressor.extract_with_redaction_level(
    archive_path,
    Path("extracted_docs"),
    allowed_levels,
    "attorney_user"
)
```

### Legal Numbering Systems

```python
# Apply Bates numbering
bates_mapping = hierarchy.apply_bates_numbering(start_number=1000, prefix="SMITH")

# Apply exhibit numbering
exhibit_mapping = hierarchy.apply_exhibit_numbering("Smith", start_number=1)

# Get documents in proper filing order
filing_order = hierarchy.get_filing_order()
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=legal_archive

# Generate JSON report (required for verification)
pytest --json-report --json-report-file=pytest_results.json
```

## Architecture

The system consists of five main modules:

1. **OCR Integration** (`ocr_integration.py`): Handles text extraction from scanned documents
2. **Hierarchical Structure** (`hierarchical_structure.py`): Manages legal filing organization
3. **Redaction Compression** (`redaction_compression.py`): Secure compression with redaction preservation
4. **Table of Contents** (`table_of_contents.py`): Multi-format TOC generation
5. **Cross Reference** (`cross_reference.py`): Document relationship management

## Performance

- OCR processing: 100+ pages per minute
- TOC generation: 10,000 documents in under 30 seconds
- Archive compression: Handles archives up to 500GB
- Supports concurrent access from multiple users

## Security Features

- Encrypted storage of redacted content
- Multi-level access control based on redaction levels
- Comprehensive audit trails for all redactions
- Integrity verification for archived documents

## Legal Compliance

- Supports federal and state court filing structures
- Maintains Bates numbering for discovery
- Preserves document authenticity for admissibility
- Compatible with standard e-filing systems

## License

This project is designed for legal document management and should be used in accordance with applicable laws and regulations regarding document handling and privacy.