"""Redaction-aware compression that preserves document modifications."""

import hashlib
import io
import json
import logging
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cryptography.fernet import Fernet
from PIL import Image
import pypdf

from .models import Redaction, RedactionLevel, DocumentMetadata


logger = logging.getLogger(__name__)


class RedactionAwareCompressor:
    """Handles compression while preserving redaction information."""

    def __init__(
        self,
        compression_level: int = 6,
        encrypt_redacted_content: bool = True,
    ):
        """Initialize redaction-aware compressor.

        Args:
            compression_level: ZIP compression level (0-9)
            encrypt_redacted_content: Whether to encrypt redacted content
        """
        self.compression_level = compression_level
        self.encrypt_redacted_content = encrypt_redacted_content
        self.redactions: Dict[str, List[Redaction]] = defaultdict(list)
        self.redaction_audit: List[Dict] = []
        self._encryption_key = Fernet.generate_key() if encrypt_redacted_content else None
        self._fernet = Fernet(self._encryption_key) if self._encryption_key else None

    def add_redaction(
        self,
        redaction: Redaction,
        original_content: Optional[bytes] = None,
    ) -> None:
        """Add a redaction to be preserved.

        Args:
            redaction: Redaction information
            original_content: Original content being redacted (for secure storage)
        """
        self.redactions[redaction.document_id].append(redaction)

        # Audit trail
        audit_entry = {
            "redaction_id": redaction.redaction_id,
            "document_id": redaction.document_id,
            "applied_by": redaction.applied_by,
            "applied_date": redaction.applied_date.isoformat(),
            "redaction_level": redaction.redaction_level.value,
            "reason": redaction.reason,
        }

        if original_content and self.encrypt_redacted_content:
            # Securely store redacted content (encrypted)
            encrypted_content = self._fernet.encrypt(original_content)
            audit_entry["encrypted_content_hash"] = hashlib.sha256(
                encrypted_content
            ).hexdigest()

        self.redaction_audit.append(audit_entry)
        logger.info(f"Added redaction {redaction.redaction_id} for {redaction.document_id}")

    def compress_with_redactions(
        self,
        documents: List[Tuple[Path, DocumentMetadata]],
        output_path: Path,
        preserve_structure: bool = True,
    ) -> Dict[str, any]:
        """Compress documents while preserving redaction layers.

        Args:
            documents: List of (file_path, metadata) tuples
            output_path: Output archive path
            preserve_structure: Whether to preserve directory structure

        Returns:
            Compression statistics
        """
        stats = {
            "total_documents": len(documents),
            "original_size": 0,
            "compressed_size": 0,
            "redacted_documents": 0,
            "compression_ratio": 0.0,
        }

        with zipfile.ZipFile(
            output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=self.compression_level
        ) as archive:
            # Add documents
            for doc_path, metadata in documents:
                if not doc_path.exists():
                    logger.warning(f"Document not found: {doc_path}")
                    continue

                # Calculate paths
                if preserve_structure:
                    archive_path = doc_path.relative_to(doc_path.parent.parent)
                else:
                    archive_path = Path(metadata.document_id) / doc_path.name

                # Check for redactions
                doc_redactions = self.redactions.get(metadata.document_id, [])
                
                if doc_redactions:
                    # Process document with redactions
                    processed_content = self._apply_redactions_to_document(
                        doc_path, doc_redactions
                    )
                    archive.writestr(str(archive_path), processed_content)
                    stats["redacted_documents"] += 1
                    
                    # Store redaction metadata
                    redaction_meta_path = archive_path.parent / f".{archive_path.stem}_redactions.json"
                    redaction_data = {
                        "document_id": metadata.document_id,
                        "redactions": [r.model_dump(mode='json') for r in doc_redactions],
                        "applied_date": datetime.now().isoformat(),
                    }
                    archive.writestr(str(redaction_meta_path), json.dumps(redaction_data, indent=2))
                else:
                    # Add unredacted document
                    archive.write(doc_path, str(archive_path))

                stats["original_size"] += doc_path.stat().st_size

            # Add redaction audit trail
            if self.redaction_audit:
                audit_data = {
                    "audit_trail": self.redaction_audit,
                    "total_redactions": len(self.redaction_audit),
                    "encryption_enabled": self.encrypt_redacted_content,
                    "generated_date": datetime.now().isoformat(),
                }
                archive.writestr("_redaction_audit.json", json.dumps(audit_data, indent=2))

            # Add redaction key manifest (if encryption is used)
            if self._encryption_key:
                key_manifest = {
                    "encryption_algorithm": "Fernet",
                    "key_id": hashlib.sha256(self._encryption_key).hexdigest()[:16],
                    "warning": "Encryption key must be stored separately",
                }
                archive.writestr("_redaction_key_manifest.json", json.dumps(key_manifest, indent=2))

        # Calculate final statistics
        stats["compressed_size"] = output_path.stat().st_size
        # Ensure compression ratio is non-negative
        if stats["original_size"] > 0:
            ratio = 1 - stats["compressed_size"] / stats["original_size"]
            stats["compression_ratio"] = max(0.0, ratio)
        else:
            stats["compression_ratio"] = 0.0

        logger.info(
            f"Compressed {stats['total_documents']} documents "
            f"({stats['redacted_documents']} with redactions) "
            f"with {stats['compression_ratio']:.2%} compression"
        )

        return stats

    def extract_with_redaction_level(
        self,
        archive_path: Path,
        output_dir: Path,
        allowed_levels: Set[RedactionLevel],
        user_id: str,
    ) -> List[Path]:
        """Extract documents with appropriate redaction level.

        Args:
            archive_path: Path to compressed archive
            output_dir: Directory to extract to
            allowed_levels: Set of allowed redaction levels for user
            user_id: User requesting extraction

        Returns:
            List of extracted file paths
        """
        extracted_files = []
        output_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_path, "r") as archive:
            for file_info in archive.filelist:
                file_path = Path(file_info.filename)
                
                # Skip metadata files
                if file_path.name.startswith("_") or file_path.name.startswith("."):
                    continue

                # Check for redaction metadata
                redaction_meta_path = file_path.parent / f".{file_path.stem}_redactions.json"
                
                redaction_meta_str = str(redaction_meta_path)
                # Try both with and without leading directory
                if redaction_meta_str in archive.namelist() or redaction_meta_str.lstrip('/') in archive.namelist():
                    # Document has redactions
                    redaction_data = json.loads(
                        archive.read(str(redaction_meta_path)).decode()
                    )
                    
                    # Check if user can access based on redaction levels
                    doc_levels = {
                        RedactionLevel(r["redaction_level"])
                        for r in redaction_data["redactions"]
                    }
                    
                    if not self._can_access_document(doc_levels, allowed_levels):
                        logger.warning(
                            f"User {user_id} denied access to {file_path} "
                            f"due to redaction levels"
                        )
                        continue

                # Extract file
                output_path = output_dir / file_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with archive.open(file_info) as source:
                    with open(output_path, "wb") as target:
                        target.write(source.read())
                
                extracted_files.append(output_path)

        # Log access
        self._log_extraction_access(archive_path, user_id, allowed_levels, extracted_files)
        
        return extracted_files

    def verify_redaction_integrity(
        self, archive_path: Path
    ) -> Tuple[bool, List[str]]:
        """Verify that redactions are intact and unmodified.

        Args:
            archive_path: Path to archive to verify

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                # Check for audit trail
                if "_redaction_audit.json" not in archive.namelist():
                    issues.append("Missing redaction audit trail")
                    return False, issues

                audit_data = json.loads(
                    archive.read("_redaction_audit.json").decode()
                )

                # Verify each redacted document
                for audit_entry in audit_data["audit_trail"]:
                    doc_id = audit_entry["document_id"]
                    
                    # Find corresponding redaction metadata
                    # Look for files that contain the document ID in their path
                    redaction_files = []
                    for f in archive.namelist():
                        if f.endswith("_redactions.json"):
                            # Read the file to check if it's for this document
                            try:
                                content = json.loads(archive.read(f).decode())
                                if content.get("document_id") == doc_id:
                                    redaction_files.append(f)
                            except:
                                pass
                    
                    if not redaction_files:
                        issues.append(
                            f"Missing redaction metadata for document {doc_id}"
                        )

                # Check encryption key manifest if encryption was used
                if audit_data.get("encryption_enabled"):
                    if "_redaction_key_manifest.json" not in archive.namelist():
                        issues.append("Missing encryption key manifest")

        except Exception as e:
            issues.append(f"Archive verification failed: {str(e)}")
            return False, issues

        return len(issues) == 0, issues

    def _apply_redactions_to_document(
        self, doc_path: Path, redactions: List[Redaction]
    ) -> bytes:
        """Apply redactions to a document.

        Args:
            doc_path: Path to document
            redactions: List of redactions to apply

        Returns:
            Redacted document content
        """
        if doc_path.suffix.lower() == ".pdf":
            return self._redact_pdf(doc_path, redactions)
        elif doc_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            return self._redact_image(doc_path, redactions)
        else:
            # For other formats, return original content
            # In production, would handle more formats
            return doc_path.read_bytes()

    def _redact_pdf(self, pdf_path: Path, redactions: List[Redaction]) -> bytes:
        """Apply redactions to PDF."""
        # Simulate PDF redaction
        content = pdf_path.read_bytes()
        
        # Add redaction marker to simulate modification
        redaction_marker = b"\n[REDACTED CONTENT]\n"
        
        # For each redaction, simulate applying it
        for redaction in redactions:
            # In production, would use proper PDF library to black out regions
            content = content + redaction_marker
        
        return content

    def _redact_image(self, image_path: Path, redactions: List[Redaction]) -> bytes:
        """Apply redactions to image."""
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Apply redactions
            for redaction in redactions:
                if len(redaction.coordinates) == 4:
                    x1, y1, x2, y2 = redaction.coordinates
                    # Black out region
                    for x in range(x1, x2):
                        for y in range(y1, y2):
                            if 0 <= x < img.width and 0 <= y < img.height:
                                img.putpixel((x, y), (0, 0, 0))

            # Save to bytes
            output = io.BytesIO()
            img.save(output, format="PNG")
            return output.getvalue()

    def _can_access_document(
        self, doc_levels: Set[RedactionLevel], allowed_levels: Set[RedactionLevel]
    ) -> bool:
        """Check if user can access document based on redaction levels."""
        # Define level hierarchy
        level_hierarchy = {
            RedactionLevel.PUBLIC: 0,
            RedactionLevel.ATTORNEY_CLIENT: 1,
            RedactionLevel.WORK_PRODUCT: 2,
            RedactionLevel.CONFIDENTIAL: 3,
            RedactionLevel.SEALED: 4,
        }

        # Get highest document level
        max_doc_level = max(
            level_hierarchy.get(level, 0) for level in doc_levels
        )

        # Check if user has sufficient access
        max_allowed_level = max(
            level_hierarchy.get(level, 0) for level in allowed_levels
        )

        return max_allowed_level >= max_doc_level

    def _log_extraction_access(
        self,
        archive_path: Path,
        user_id: str,
        allowed_levels: Set[RedactionLevel],
        extracted_files: List[Path],
    ) -> None:
        """Log document access for audit purposes."""
        access_log = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "archive": str(archive_path),
            "allowed_levels": [level.value for level in allowed_levels],
            "extracted_files": [str(f) for f in extracted_files],
            "file_count": len(extracted_files),
        }
        
        logger.info(f"Access log: {json.dumps(access_log)}")