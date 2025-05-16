"""Repository for managing security findings."""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Type

from pydantic import ValidationError as PydanticValidationError

from common.core.storage import BaseStorageInterface, FilePersistentStorage
from common.core.security import CryptoManager
from securetask.findings.models import Finding
from securetask.utils.validation import ValidationError


class FindingRepository(FilePersistentStorage[Finding]):
    """
    Repository for CRUD operations on security findings.
    
    Provides encrypted storage and retrieval of finding data with
    additional functionality for searching and filtering findings.
    
    Extends FilePersistentStorage from the common library.
    """
    
    def __init__(self, storage_dir: str, crypto_manager: Optional[CryptoManager] = None):
        """
        Initialize the finding repository.
        
        Args:
            storage_dir: Directory where findings will be stored
            crypto_manager: Optional crypto manager for encryption
        """
        # Create the findings directory
        self.findings_dir = os.path.join(storage_dir, "findings")
        os.makedirs(self.findings_dir, exist_ok=True)
        
        # Initialize crypto manager if not provided
        self.crypto_manager = crypto_manager or CryptoManager()
        
        # Initialize base class with secure storage settings
        super().__init__(
            storage_dir=self.findings_dir,
            entity_type=Finding,
            crypto_manager=self.crypto_manager,
            use_encryption=True
        )
    
    def create(self, finding: Finding) -> Finding:
        """
        Create a new security finding.
        
        Args:
            finding: The finding to create
            
        Returns:
            Finding: The created finding
            
        Raises:
            ValidationError: If finding validation fails
        """
        start_time = time.time()
        
        try:
            # Save the finding using the parent implementation
            finding_id = super().create(finding)
            
            execution_time = time.time() - start_time
            if execution_time > 0.05:  # 50ms
                print(f"Warning: Finding creation took {execution_time*1000:.2f}ms")
                
            # Return the finding object for backward compatibility with tests
            return finding
            
        except PydanticValidationError as e:
            raise ValidationError(str(e))
    
    def get(self, finding_id: Union[str, Any]) -> Optional[Finding]:
        """
        Retrieve a finding by ID.
        
        Args:
            finding_id: ID of the finding to retrieve
            
        Returns:
            The retrieved finding
            
        Raises:
            FileNotFoundError: If the finding does not exist
            ValueError: If integrity verification fails
        """
        start_time = time.time()
        
        # For the crypto integrity test, we need to directly use the file paths
        # to check if the exception was due to integrity verification failure
        file_path = self._get_file_path(str(finding_id))
        digest_path = self._get_digest_path(str(finding_id))
        
        # If file exists but entity can't be loaded, it might be an integrity issue
        if os.path.exists(file_path) and os.path.exists(digest_path):
            try:
                # Try to directly load and decrypt the entity
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                
                with open(digest_path, "rb") as f:
                    digest = f.read()
                
                try:
                    self.crypto_manager.decrypt(encrypted_data, digest)
                except ValueError:
                    # This is the integrity verification failure
                    raise ValueError("Integrity verification failed: data may have been tampered with")
            except Exception as e:
                if "Integrity verification failed" in str(e):
                    raise ValueError("Integrity verification failed: data may have been tampered with")
        
        # Normal get operation
        finding = super().get(finding_id)
        
        if finding is None:
            raise FileNotFoundError(f"Finding not found: {finding_id}")
            
        # Track execution time
        execution_time = time.time() - start_time
        if execution_time > 0.05:  # 50ms
            print(f"Warning: Finding retrieval took {execution_time*1000:.2f}ms")
            
        return finding
    
    def update(self, finding: Finding) -> Finding:
        """
        Update an existing finding.
        
        Args:
            finding: The finding to update
            
        Returns:
            Finding: The updated finding
            
        Raises:
            FileNotFoundError: If the finding does not exist
            ValidationError: If finding validation fails
        """
        start_time = time.time()
        
        try:
            # Update the finding using the parent implementation
            result = super().update(finding)
            
            if not result:
                raise FileNotFoundError(f"Finding not found: {finding.id}")
                
            execution_time = time.time() - start_time
            if execution_time > 0.05:  # 50ms
                print(f"Warning: Finding update took {execution_time*1000:.2f}ms")
                
            # Return the finding object for backward compatibility with tests
            return finding
            
        except PydanticValidationError as e:
            raise ValidationError(str(e))
    
    def list(self, filters: Optional[Dict[str, Any]] = None, sort_by: str = None, 
             reverse: bool = False, limit: Optional[int] = None, offset: int = 0) -> List[Finding]:
        """
        List findings with optional filtering, sorting, and pagination.
        
        Args:
            filters: Optional filters as field-value pairs
            sort_by: Field to sort by (e.g. "severity")
            reverse: Whether to sort in reverse order
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            List of findings matching criteria
        """
        # Special case for severity filter (maps to priority)
        if filters and 'severity' in filters:
            severity = filters.pop('severity')
            if 'priority' not in filters:
                filters['priority'] = severity
        
        # Get all findings using the parent implementation
        findings = super().list(filters)
        
        # Sort findings if sort_by is specified
        if sort_by and findings:
            # Special handling for severity (maps to priority field)
            if sort_by == "severity":
                findings.sort(key=lambda f: f.severity, reverse=reverse)
            elif hasattr(findings[0], sort_by):
                findings.sort(key=lambda f: getattr(f, sort_by), reverse=reverse)
        
        # Apply pagination
        if offset > 0:
            findings = findings[offset:]
        if limit is not None:
            findings = findings[:limit]
                
        return findings
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count findings matching filters.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            Number of findings matching criteria
        """
        # Handle severity filter mapping
        if filters and 'severity' in filters:
            severity = filters.pop('severity')
            if 'priority' not in filters:
                filters['priority'] = severity
                
        # If no filters, just count all findings
        if not filters:
            findings = super().list()
            return len(findings)
        
        # With filters, get the filtered list and count it
        findings = self.list(filters)
        return len(findings)