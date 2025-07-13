"""Data models for the legal document archive system."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, ConfigDict


class DocumentType(str, Enum):
    """Legal document types."""

    BRIEF = "brief"
    MOTION = "motion"
    EXHIBIT = "exhibit"
    TRANSCRIPT = "transcript"
    DISCOVERY = "discovery"
    CORRESPONDENCE = "correspondence"
    COURT_ORDER = "court_order"
    PLEADING = "pleading"
    OTHER = "other"


class RedactionLevel(str, Enum):
    """Redaction privilege levels."""

    PUBLIC = "public"
    ATTORNEY_CLIENT = "attorney_client"
    WORK_PRODUCT = "work_product"
    CONFIDENTIAL = "confidential"
    SEALED = "sealed"


class OCRResult(BaseModel):
    """OCR processing result."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    document_id: str
    original_path: Path
    text_content: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    language: str = "en"
    page_count: int = Field(gt=0)
    processing_time: float
    error_message: Optional[str] = None


class DocumentMetadata(BaseModel):
    """Legal document metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    document_id: str
    file_name: str
    document_type: DocumentType
    case_number: Optional[str] = None
    party_name: Optional[str] = None
    filing_date: Optional[datetime] = None
    bates_number: Optional[str] = None
    exhibit_number: Optional[str] = None
    page_count: int = Field(gt=0)
    file_size: int = Field(gt=0)
    checksum: str
    created_date: datetime = Field(default_factory=datetime.now)
    modified_date: datetime = Field(default_factory=datetime.now)
    tags: Set[str] = Field(default_factory=set)
    metadata: Dict[str, str] = Field(default_factory=dict)


class HierarchyNode(BaseModel):
    """Node in the legal filing hierarchy."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_id: str
    name: str
    node_type: str  # case, party, document_type, date, etc.
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    sort_order: int = 0
    metadata: Dict[str, str] = Field(default_factory=dict)


class Redaction(BaseModel):
    """Redaction information."""

    redaction_id: str
    document_id: str
    page_number: int
    coordinates: List[int]  # [x1, y1, x2, y2]
    redaction_level: RedactionLevel
    reason: str
    applied_by: str
    applied_date: datetime = Field(default_factory=datetime.now)
    is_permanent: bool = True


class CrossReference(BaseModel):
    """Document cross-reference."""

    reference_id: str
    source_document_id: str
    target_document_id: str
    source_page: Optional[int] = None
    target_page: Optional[int] = None
    reference_type: str  # citation, exhibit, attachment, etc.
    reference_text: Optional[str] = None
    is_bidirectional: bool = False


class TOCEntry(BaseModel):
    """Table of contents entry."""

    entry_id: str
    document_id: str
    title: str
    page_number: Optional[int] = None
    level: int = 0
    parent_entry_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    hyperlink: Optional[str] = None
    summary: Optional[str] = None


class ArchiveManifest(BaseModel):
    """Archive manifest containing all metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    archive_id: str
    archive_name: str
    case_number: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.now)
    creator: str
    total_documents: int = Field(ge=0)
    total_size: int = Field(ge=0)
    compression_ratio: float = Field(ge=0.0)
    documents: List[DocumentMetadata] = Field(default_factory=list)
    hierarchy_root: Optional[str] = None
    toc_formats: List[str] = Field(default_factory=list)
    has_ocr: bool = False
    has_redactions: bool = False
    cross_references_count: int = Field(ge=0)