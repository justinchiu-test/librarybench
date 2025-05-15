"""Data models for security findings."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Set

from pydantic import Field, field_validator, model_validator

from common.core.models import BaseTask
from securetask.utils.validation import ValidationError


class Finding(BaseTask):
    """
    Model representing a security finding or vulnerability.
    
    Contains comprehensive metadata about security issues, including
    technical details, affected systems, and tracking information.
    """
    
    # Required fields with defaults for BaseTask compatibility
    status: str = "open"  # Default value to match the allowed statuses
    priority: str = "medium"  # Default to medium priority
    
    # Custom fields for security findings
    affected_systems: List[str] = Field(default_factory=list)
    discovered_by: str = ""  # Default value for backward compatibility
    cvss_vector: Optional[str] = None
    cvss_score: Optional[float] = None
    cvss_severity: Optional[str] = None
    remediation_plan: Optional[str] = None
    remediation_date: Optional[datetime] = None
    remediated_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    compliance_controls: List[str] = Field(default_factory=list)
    
    # Field aliases for backward compatibility
    discovered_date: datetime = Field(default_factory=datetime.now, alias="discovered_date")
    
    # Prioritize 'severity' over 'priority' if provided in the input
    def __init__(self, **data):
        if 'severity' in data and 'priority' not in data:
            data['priority'] = data['severity']
        super().__init__(**data)
    
    # Add 'severity' property for backward compatibility
    @property
    def severity(self) -> str:
        """Return the priority field as severity for backward compatibility."""
        return self.priority
    
    @severity.setter
    def severity(self, value: str) -> None:
        """Set the priority field using severity value."""
        self.priority = value
    
    @field_validator("status", check_fields=False)
    @classmethod
    def validate_status(cls, value: str) -> str:
        """Validate that the status is a known value."""
        allowed_statuses = {
            "open", "in_progress", "remediated", "verified", "closed", "false_positive"
        }
        if value not in allowed_statuses:
            raise ValidationError(
                f"Invalid status: {value}. Allowed values: {', '.join(allowed_statuses)}", 
                "status"
            )
        return value
    
    @field_validator("priority", mode="before", check_fields=False)
    @classmethod
    def validate_severity(cls, value: str) -> str:
        """Validate that the severity is a known value."""
        allowed_severities = {"critical", "high", "medium", "low", "info"}
        if value not in allowed_severities:
            raise ValidationError(
                f"Invalid severity: {value}. Allowed values: {', '.join(allowed_severities)}", 
                "severity"
            )
        return value
    
    @model_validator(mode='after')
    def status_field_validation(self) -> 'Finding':
        """Validate fields based on status."""
        if self.status == "remediated" and not self.remediation_date:
            self.remediation_date = datetime.now()
            
        if self.status == "verified" and not self.verification_date:
            self.verification_date = datetime.now()
            
        return self
        
    def validate(self, value=None) -> 'Finding':
        """
        Compatibility method for Pydantic v2 validation API.

        Args:
            value: Optional value to validate (for Pydantic v2 compatibility)

        Returns:
            The validated Finding instance

        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            # Validate current instance
            self.validate_status(self.status)
            self.validate_severity(self.priority)
            return self
        else:
            # For Pydantic v2 compatibility
            if isinstance(value, dict):
                return Finding(**value)
            return value
    
    def add_note(self, content: str, author: str) -> Dict[str, Any]:
        """
        Add a timestamped note to the finding.
        
        Args:
            content: The note content
            author: The author of the note
            
        Returns:
            The created note as a dictionary
        """
        note = {
            "id": str(uuid.uuid4()),
            "content": content,
            "author": author,
            "timestamp": datetime.now()
        }
        self.notes.append(note)
        self.updated_at = datetime.now()
        return note
    
    def add_evidence(self, evidence_id: str) -> None:
        """
        Link evidence to the finding.
        
        Args:
            evidence_id: ID of the evidence to link
        """
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)
            self.updated_at = datetime.now()
            
    def remove_evidence(self, evidence_id: str) -> bool:
        """
        Remove linked evidence from the finding.
        
        Args:
            evidence_id: ID of the evidence to remove
            
        Returns:
            True if evidence was removed, False if not found
        """
        if evidence_id in self.evidence_ids:
            self.evidence_ids.remove(evidence_id)
            self.updated_at = datetime.now()
            return True
        return False
            
    def add_compliance_control(self, control_id: str) -> None:
        """
        Link a compliance control to the finding.
        
        Args:
            control_id: ID of the compliance control to link
        """
        if control_id not in self.compliance_controls:
            self.compliance_controls.append(control_id)
            self.updated_at = datetime.now()
    
    def remove_compliance_control(self, control_id: str) -> bool:
        """
        Remove a linked compliance control from the finding.
        
        Args:
            control_id: ID of the compliance control to remove
            
        Returns:
            True if control was removed, False if not found
        """
        if control_id in self.compliance_controls:
            self.compliance_controls.remove(control_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_cvss(self, vector: str, score: float, severity: str) -> None:
        """
        Update the CVSS information for this finding.
        
        Args:
            vector: CVSS vector string
            score: Calculated CVSS score
            severity: CVSS severity rating
        """
        self.cvss_vector = vector
        self.cvss_score = score
        self.cvss_severity = severity
        self.updated_at = datetime.now()
        
    def update_status(self, new_status: str, user: str) -> None:
        """
        Update the status of the finding.
        
        Args:
            new_status: New status value
            user: User making the status change
            
        Raises:
            ValidationError: If the status is invalid
        """
        # Validate status first
        self.validate_status(new_status)
        
        # Update status and related fields
        self.status = new_status
        
        if new_status == "remediated":
            self.remediation_date = datetime.now()
            self.remediated_by = user
        elif new_status == "verified":
            self.verification_date = datetime.now()
            self.verified_by = user
            
        # Add a note about the status change
        self.add_note(f"Status changed to '{new_status}'", user)