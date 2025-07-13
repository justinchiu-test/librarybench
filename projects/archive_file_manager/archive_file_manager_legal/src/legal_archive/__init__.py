"""Legal Document Archive System

A specialized archive management system for legal document processors.
"""

__version__ = "1.0.0"

from .ocr_integration import OCRProcessor
from .hierarchical_structure import LegalHierarchy
from .redaction_compression import RedactionAwareCompressor
from .table_of_contents import TOCGenerator
from .cross_reference import CrossReferenceManager

__all__ = [
    "OCRProcessor",
    "LegalHierarchy",
    "RedactionAwareCompressor",
    "TOCGenerator",
    "CrossReferenceManager",
]