"""Transaction categorization engine shared across implementations."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from common.core.categorization.categorizer import BaseCategorizer, CategorizationResult
from common.core.categorization.rule import Rule, TransactionRule
from common.core.models.transaction import BaseTransaction, TransactionType


class MixedUseItem(BaseModel):
    """
    Model for tracking items that are partially business and partially personal.
    
    Used in expense categorization to handle items used for both business
    and personal purposes.
    """
    
    id: Union[str, UUID]
    name: str
    category: str
    business_use_percentage: float
    description: Optional[str] = None
    

class TransactionCategorizer(BaseCategorizer[BaseTransaction, CategorizationResult[BaseTransaction]]):
    """
    Categorizer for financial transactions.
    
    Handles categorization of transactions based on rules and mixed-use items.
    """
    
    def __init__(self):
        """Initialize the transaction categorizer."""
        super().__init__()
        self.mixed_use_items: List[MixedUseItem] = []
    
    def add_mixed_use_item(self, item: MixedUseItem) -> MixedUseItem:
        """
        Add a new mixed-use item.
        
        Args:
            item: The mixed-use item to add
            
        Returns:
            The added item
        """
        # Check for duplicate item ID
        if any(i.id == item.id for i in self.mixed_use_items):
            raise ValueError(f"Mixed-use item with ID {item.id} already exists")
        
        # Add the item
        self.mixed_use_items.append(item)
        
        # Clear cache
        self._categorization_cache = {}
        
        return item
    
    def categorize(
        self, transaction: BaseTransaction, recategorize: bool = False
    ) -> CategorizationResult[BaseTransaction]:
        """
        Categorize a transaction using the defined rules.
        
        Args:
            transaction: The transaction to categorize
            recategorize: Whether to recategorize even if already categorized
            
        Returns:
            CategorizationResult with the categorization details
        """
        # Start performance timer
        start_time = time.time()
        
        # Skip non-expense transactions if desired
        if hasattr(transaction, 'transaction_type'):
            if getattr(transaction, 'transaction_type') != TransactionType.EXPENSE:
                result = CategorizationResult(
                    item_id=transaction.id,
                    original_item=transaction,
                    confidence_score=0.0,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    notes="Non-expense transaction",
                )
                return result
        
        # Check cache unless forced to recategorize
        cache_key = str(transaction.id)
        if not recategorize and cache_key in self._categorization_cache:
            return self._categorization_cache[cache_key]
        
        # Skip if already categorized and not forced to recategorize
        if (
            not recategorize 
            and hasattr(transaction, 'category') 
            and getattr(transaction, 'category') is not None
        ):
            # For business transactions, check business use percentage
            business_use_percentage = None
            if hasattr(transaction, 'business_use_percentage'):
                business_use_percentage = getattr(transaction, 'business_use_percentage')
                
            result = CategorizationResult(
                item_id=transaction.id,
                original_item=transaction,
                assigned_category=transaction.category,
                business_use_percentage=business_use_percentage,
                confidence_score=1.0,  # Already categorized, so high confidence
                processing_time_ms=(time.time() - start_time) * 1000,
                notes="Transaction was already categorized",
            )
            
            self._categorization_cache[cache_key] = result
            return result
        
        # Check if this matches a known mixed-use item
        mixed_use_match = None
        for item in self.mixed_use_items:
            if (
                hasattr(transaction, 'description') 
                and item.name.lower() in getattr(transaction, 'description', '').lower()
            ):
                mixed_use_match = item
                break
        
        # Apply categorization rules
        matched_rule = None
        for rule in self.rules:
            if rule.matches(transaction):
                matched_rule = rule
                break
        
        # Determine category and business use percentage
        category = None
        business_percentage = None
        is_mixed_use = False
        confidence = 0.5
        notes = "No matching rules or mixed-use items"
        metadata = {}
        
        if mixed_use_match:
            category = mixed_use_match.category
            business_percentage = mixed_use_match.business_use_percentage
            is_mixed_use = True
            confidence = 0.9
            notes = f"Matched mixed-use item: {mixed_use_match.name}"
            metadata["mixed_use_item_id"] = str(mixed_use_match.id)
        elif matched_rule:
            # Extract category and business percentage from rule
            rule_result = matched_rule.apply(transaction)
            category = rule_result.get("category")
            
            if "business_use_percentage" in rule_result:
                business_percentage = rule_result.get("business_use_percentage")
                is_mixed_use = business_percentage < 100 and business_percentage > 0
                
            confidence = 0.8
            notes = f"Matched rule: {matched_rule.name}"
            metadata["rule_id"] = str(matched_rule.id)
            
        # Finalize processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Create result
        result = CategorizationResult(
            item_id=transaction.id,
            original_item=transaction,
            assigned_category=category,
            confidence_score=confidence,
            matched_rule=matched_rule,
            processing_time_ms=processing_time_ms,
            notes=notes,
            metadata={
                "is_mixed_use": is_mixed_use,
                "business_use_percentage": business_percentage,
                **metadata,
            },
        )
        
        # Record audit trail
        previous_state = {}
        if hasattr(transaction, 'category'):
            previous_state["category"] = getattr(transaction, 'category')
        if hasattr(transaction, 'business_use_percentage'):
            previous_state["business_use_percentage"] = getattr(transaction, 'business_use_percentage')
        
        new_state = {
            "category": category,
            "business_use_percentage": business_percentage,
        }
        
        self.record_audit(
            item_id=transaction.id,
            action="categorize",
            previous_state=previous_state,
            new_state=new_state,
        )
        
        # Update cache
        self._categorization_cache[cache_key] = result
        
        return result
    
    def apply_categorization(
        self, transaction: BaseTransaction, result: CategorizationResult
    ) -> BaseTransaction:
        """
        Apply a categorization result to a transaction.
        
        Args:
            transaction: The transaction to update
            result: The categorization result to apply
            
        Returns:
            The updated transaction
        """
        # Record previous state for audit
        previous_state = {}
        if hasattr(transaction, 'category'):
            previous_state["category"] = getattr(transaction, 'category')
        if hasattr(transaction, 'business_use_percentage'):
            previous_state["business_use_percentage"] = getattr(transaction, 'business_use_percentage')
        
        # Apply categorization if possible
        if hasattr(transaction, 'category') and result.assigned_category is not None:
            setattr(transaction, 'category', result.assigned_category)
            
        if (
            hasattr(transaction, 'business_use_percentage') 
            and result.metadata.get('business_use_percentage') is not None
        ):
            setattr(
                transaction, 
                'business_use_percentage', 
                result.metadata['business_use_percentage']
            )
        
        # Record audit trail
        new_state = {}
        if hasattr(transaction, 'category'):
            new_state["category"] = getattr(transaction, 'category')
        if hasattr(transaction, 'business_use_percentage'):
            new_state["business_use_percentage"] = getattr(transaction, 'business_use_percentage')
        
        self.record_audit(
            item_id=transaction.id,
            action="apply_categorization",
            previous_state=previous_state,
            new_state=new_state,
        )
        
        # Clear cache for this transaction
        cache_key = str(transaction.id)
        if cache_key in self._categorization_cache:
            del self._categorization_cache[cache_key]
        
        return transaction