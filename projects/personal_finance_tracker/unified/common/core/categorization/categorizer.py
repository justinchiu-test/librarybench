"""Base categorization engine shared across implementations."""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from common.core.categorization.rule import Rule


# Type variable for categorizable items
T = TypeVar('T')
# Type variable for categorization results
R = TypeVar('R')


class CategorizationResult(BaseModel, Generic[T]):
    """
    Result of a categorization operation.
    
    Provides information about the categorization process and outcome.
    """
    
    item_id: Union[str, UUID]
    original_item: T
    assigned_category: Optional[str] = None
    confidence_score: float  # 0.0 to 1.0
    matched_rule: Optional[Rule] = None
    processing_time_ms: Optional[float] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class AuditRecord(BaseModel):
    """
    Record of a categorization action for audit purposes.
    
    Tracks changes for accountability and analysis.
    """
    
    id: Union[str, UUID] = Field(default_factory=uuid4)
    item_id: Union[str, UUID]
    action: str
    timestamp: datetime = Field(default_factory=datetime.now)
    previous_state: Dict[str, Any] = Field(default_factory=dict)
    new_state: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    notes: Optional[str] = None


class BaseCategorizer(Generic[T, R], ABC):
    """
    Abstract base class for categorization engines.
    
    Defines the core interface and functionality for all categorizers
    across different persona implementations.
    """
    
    def __init__(self):
        """Initialize the categorizer."""
        self.rules: List[Rule] = []
        self.audit_trail: List[AuditRecord] = []
        self._categorization_cache: Dict[str, R] = {}
        
    def add_rule(self, rule: Rule) -> Rule:
        """
        Add a new rule to the categorizer.
        
        Args:
            rule: The rule to add
            
        Returns:
            The added rule
        """
        # Check for duplicate rule ID
        if any(r.id == rule.id for r in self.rules):
            raise ValueError(f"Rule with ID {rule.id} already exists")
        
        # Add the rule
        self.rules.append(rule)
        
        # Sort rules by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Clear cache since rules have changed
        self._categorization_cache = {}
        
        return rule
    
    def update_rule(self, rule: Rule) -> Rule:
        """
        Update an existing rule.
        
        Args:
            rule: The rule to update
            
        Returns:
            The updated rule
        """
        # Find the rule to update
        for i, existing_rule in enumerate(self.rules):
            if existing_rule.id == rule.id:
                # Update the rule
                rule.updated_at = datetime.now()
                self.rules[i] = rule
                
                # Sort rules by priority (highest first)
                self.rules.sort(key=lambda r: r.priority, reverse=True)
                
                # Clear cache since rules have changed
                self._categorization_cache = {}
                
                return rule
        
        raise ValueError(f"Rule with ID {rule.id} not found")
    
    def remove_rule(self, rule_id: Union[str, UUID]) -> bool:
        """
        Remove a rule.
        
        Args:
            rule_id: ID of the rule to remove
            
        Returns:
            True if the rule was removed, False otherwise
        """
        # Find the rule to remove
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                # Remove the rule
                del self.rules[i]
                
                # Clear cache since rules have changed
                self._categorization_cache = {}
                
                return True
        
        return False
    
    def get_rules(self) -> List[Rule]:
        """
        Get all rules.
        
        Returns:
            List of all rules
        """
        return self.rules
    
    def get_audit_trail(
        self, item_id: Optional[Union[str, UUID]] = None, limit: int = 100
    ) -> List[AuditRecord]:
        """
        Get the audit trail for categorization actions.
        
        Args:
            item_id: Optional item ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of audit records
        """
        if item_id:
            # Filter to specific item
            filtered_trail = [
                record
                for record in self.audit_trail
                if record.item_id == item_id
            ]
        else:
            filtered_trail = self.audit_trail
        
        # Sort by timestamp (newest first) and limit
        sorted_trail = sorted(filtered_trail, key=lambda r: r.timestamp, reverse=True)
        
        return sorted_trail[:limit]
    
    def clear_cache(self) -> None:
        """Clear the categorization cache."""
        self._categorization_cache = {}
    
    @abstractmethod
    def categorize(self, item: T, recategorize: bool = False) -> R:
        """
        Categorize a single item.
        
        Args:
            item: The item to categorize
            recategorize: Whether to recategorize even if already categorized
            
        Returns:
            Categorization result
        """
        pass
    
    def categorize_batch(self, items: List[T], recategorize: bool = False) -> List[R]:
        """
        Categorize multiple items.
        
        Args:
            items: List of items to categorize
            recategorize: Whether to recategorize even if already categorized
            
        Returns:
            List of categorization results
        """
        # Start performance timer
        start_time = time.time()
        
        # Categorize each item
        results = []
        for item in items:
            result = self.categorize(item, recategorize)
            results.append(result)
        
        # Performance metrics
        elapsed_time = time.time() - start_time
        
        return results
    
    def record_audit(
        self,
        item_id: Union[str, UUID],
        action: str,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        notes: Optional[str] = None,
    ) -> AuditRecord:
        """
        Record an action in the audit trail.
        
        Args:
            item_id: ID of the item being modified
            action: Type of action performed
            previous_state: State before the action
            new_state: State after the action
            notes: Optional notes about the action
            
        Returns:
            The created audit record
        """
        audit_record = AuditRecord(
            item_id=item_id,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            notes=notes,
        )
        
        self.audit_trail.append(audit_record)
        
        return audit_record