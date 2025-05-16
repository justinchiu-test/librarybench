"""Expense categorization system for freelancers."""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from uuid import UUID

# Import from common library
from common.core.categorization.categorizer import BaseCategorizer, CategorizationResult as CommonResult, AuditRecord as CommonAuditRecord
from common.core.categorization.transaction_categorizer import TransactionCategorizer, MixedUseItem as CommonMixedUseItem
from common.core.utils.performance import Timer

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
)

from personal_finance_tracker.expense.models import (
    CategorizationRule,
    MixedUseItem,
    CategorizationResult,
    ExpenseSummary,
    AuditRecord,
)

from personal_finance_tracker.expense.rules import ExpenseRule


class ExpenseCategorizer:
    """
    Expense categorization system for freelancers.

    This class helps separate business and personal expenses, calculate
    business use percentages, and maintain audit-ready records.
    """

    def __init__(self):
        """Initialize the expense categorizer."""
        # Use the common TransactionCategorizer for the core functionality
        self._categorizer = TransactionCategorizer()
        self.mixed_use_items = []
        self.audit_trail = []
        self._categorization_cache = {}
        self.timer = Timer()
        
    @property
    def rules(self) -> List[ExpenseRule]:
        """Get all categorization rules."""
        # Convert the underlying rules to our ExpenseRule type for test compatibility
        return self._categorizer.rules

    def add_categorization_rule(self, rule: ExpenseRule) -> ExpenseRule:
        """
        Add a new categorization rule.

        Args:
            rule: The rule to add

        Returns:
            The added rule
        """
        # Check for duplicate rule ID
        if any(r.id == rule.id for r in self.rules):
            raise ValueError(f"Rule with ID {rule.id} already exists")
            
        # Add the rule to the underlying categorizer
        self._categorizer.add_rule(rule)
        
        # Clear our cache since rules have changed
        self._categorization_cache = {}
        
        # Sort rules by priority (for test compatibility)
        self._categorizer.rules.sort(key=lambda r: r.priority, reverse=True)
        
        return rule

    def update_categorization_rule(
        self, rule: ExpenseRule
    ) -> ExpenseRule:
        """
        Update an existing categorization rule.

        Args:
            rule: The rule to update

        Returns:
            The updated rule
        """
        # Find the rule to update
        rule_found = False
        for existing_rule in self.rules:
            if existing_rule.id == rule.id:
                rule_found = True
                break
                
        if not rule_found:
            raise ValueError(f"Rule with ID {rule.id} not found")
            
        # Set the updated_at timestamp
        rule.updated_at = datetime.now()
            
        # Update the rule in the underlying categorizer
        updated_rule = self._categorizer.update_rule(rule)
        
        # Clear our cache since rules have changed
        self._categorization_cache = {}
        
        return updated_rule

    def remove_categorization_rule(self, rule_id: UUID) -> bool:
        """
        Remove a categorization rule.

        Args:
            rule_id: ID of the rule to remove

        Returns:
            True if the rule was removed, False otherwise
        """
        # Remove the rule from the underlying categorizer
        result = self._categorizer.remove_rule(rule_id)
        
        # Clear our cache since rules have changed
        if result:
            self._categorization_cache = {}
            
        return result

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

        # Add to our list
        self.mixed_use_items.append(item)
        
        # Add to the underlying categorizer
        common_item = CommonMixedUseItem(
            id=item.id,
            name=item.name,
            category=item.category,
            business_use_percentage=item.business_use_percentage,
            description=item.description,
        )
        self._categorizer.add_mixed_use_item(common_item)
        
        # Clear cache
        self._categorization_cache = {}

        return item

    def categorize_transaction(
        self, transaction: Transaction, recategorize: bool = False
    ) -> CategorizationResult:
        """
        Categorize a transaction using the defined rules.

        Args:
            transaction: The transaction to categorize
            recategorize: Whether to recategorize even if already categorized

        Returns:
            CategorizationResult with the categorization details
        """
        # Start performance timer
        self.timer.start()

        # Skip non-expense transactions
        if transaction.transaction_type != TransactionType.EXPENSE:
            return CategorizationResult(
                transaction_id=transaction.id,
                original_transaction=transaction,
                confidence_score=0.0,
            )

        # Check cache unless forced to recategorize
        cache_key = str(transaction.id)
        if not recategorize and cache_key in self._categorization_cache:
            return self._categorization_cache[cache_key]

        # Skip if already categorized and not forced to recategorize
        if not recategorize and transaction.category is not None:
            result = CategorizationResult(
                transaction_id=transaction.id,
                original_transaction=transaction,
                assigned_category=transaction.category,
                business_use_percentage=transaction.business_use_percentage,
                confidence_score=1.0,  # Already categorized, so high confidence
                notes="Transaction was already categorized",
            )
            return result

        # Use the common TransactionCategorizer to do the actual categorization
        common_result = self._categorizer.categorize(transaction, recategorize)
        
        # Convert the common result to our specialized result
        result = CategorizationResult.from_common_result(common_result, transaction.id)
        
        # Ensure we have the matched rule for test compatibility
        if common_result.matched_rule:
            result.matched_rule = common_result.matched_rule
            
        # Record audit trail
        audit_record = AuditRecord(
            transaction_id=transaction.id,
            action="categorize",
            previous_state={"category": None, "business_use_percentage": None},
            new_state={
                "category": result.assigned_category,
                "business_use_percentage": result.business_use_percentage,
                "matched_rule_name": result.matched_rule.name if result.matched_rule else None,
            },
        )
        self.audit_trail.append(audit_record)
        
        # Update cache
        self._categorization_cache[cache_key] = result
        
        # Stop timer
        self.timer.stop()

        return result

    def categorize_transactions(
        self, transactions: List[Transaction], recategorize: bool = False
    ) -> List[CategorizationResult]:
        """
        Categorize multiple transactions using the defined rules.

        Args:
            transactions: List of transactions to categorize
            recategorize: Whether to recategorize even if already categorized

        Returns:
            List of CategorizationResult objects
        """
        # Start performance timer
        self.timer.start()

        # Use the batch categorization from the common library
        common_results = self._categorizer.categorize_batch(transactions, recategorize)
        
        # Convert common results to our specialized results
        results = []
        for i, common_result in enumerate(common_results):
            transaction = transactions[i]
            result = CategorizationResult.from_common_result(common_result, transaction.id)
            
            # Ensure we have the matched rule for test compatibility
            if common_result.matched_rule:
                result.matched_rule = common_result.matched_rule
                
            # Add to cache
            cache_key = str(transaction.id)
            self._categorization_cache[cache_key] = result
            
            # Add to results
            results.append(result)
            
            # Record audit trail
            audit_record = AuditRecord(
                transaction_id=transaction.id,
                action="categorize",
                previous_state={"category": None, "business_use_percentage": None},
                new_state={
                    "category": result.assigned_category,
                    "business_use_percentage": result.business_use_percentage,
                    "matched_rule_name": result.matched_rule.name if result.matched_rule else None,
                },
            )
            self.audit_trail.append(audit_record)
        
        # Stop timer
        self.timer.stop()

        return results

    def apply_categorization(
        self, transaction: Transaction, result: CategorizationResult
    ) -> Transaction:
        """
        Apply a categorization result to a transaction.

        Args:
            transaction: The transaction to update
            result: The categorization result to apply

        Returns:
            The updated transaction
        """
        # Record previous state for audit
        previous_state = {
            "category": transaction.category,
            "business_use_percentage": transaction.business_use_percentage,
        }

        # Apply categorization
        transaction.category = result.assigned_category
        transaction.business_use_percentage = result.business_use_percentage

        # Record audit trail
        audit_record = AuditRecord(
            transaction_id=transaction.id,
            action="apply_categorization",
            previous_state=previous_state,
            new_state={
                "category": transaction.category,
                "business_use_percentage": transaction.business_use_percentage,
            },
        )
        self.audit_trail.append(audit_record)

        return transaction

    def generate_expense_summary(
        self, transactions: List[Transaction], start_date: datetime, end_date: datetime
    ) -> ExpenseSummary:
        """
        Generate a summary of expenses by category.

        Args:
            transactions: List of transactions
            start_date: Start date for the summary period
            end_date: End date for the summary period

        Returns:
            ExpenseSummary object with expense totals by category
        """
        # Start timer
        self.timer.start()
        
        # Filter to expenses in the date range
        expenses = [
            t
            for t in transactions
            if (
                t.transaction_type == TransactionType.EXPENSE
                and start_date <= t.date <= end_date
            )
        ]

        # Categorize any uncategorized expenses
        for expense in expenses:
            if expense.category is None:
                result = self.categorize_transaction(expense)
                self.apply_categorization(expense, result)

        # Calculate totals
        total_expenses = sum(t.amount for t in expenses)
        business_expenses = sum(
            t.amount * (t.business_use_percentage / 100 if t.business_use_percentage is not None else 0)
            for t in expenses
            if t.category != ExpenseCategory.PERSONAL
        )
        personal_expenses = total_expenses - business_expenses

        # Calculate expenses by category
        by_category = {}
        for expense in expenses:
            category = expense.category or ExpenseCategory.OTHER
            amount = expense.amount

            # For business expenses, apply the business use percentage
            if (
                category != ExpenseCategory.PERSONAL
                and expense.business_use_percentage is not None
            ):
                amount_business = amount * (expense.business_use_percentage / 100)

                # Add to business category
                if category not in by_category:
                    by_category[category] = 0
                by_category[category] += amount_business

                # Add personal portion to personal category
                amount_personal = amount - amount_business
                if amount_personal > 0:
                    if ExpenseCategory.PERSONAL not in by_category:
                        by_category[ExpenseCategory.PERSONAL] = 0
                    by_category[ExpenseCategory.PERSONAL] += amount_personal
            else:
                # Personal expense
                if category not in by_category:
                    by_category[category] = 0
                by_category[category] += amount

        # Create summary
        summary = ExpenseSummary(
            period_start=start_date,
            period_end=end_date,
            total_expenses=total_expenses,
            business_expenses=business_expenses,
            personal_expenses=personal_expenses,
            by_category=by_category,
        )
        
        # Stop timer
        self.timer.stop()

        return summary

    def get_audit_trail(
        self, transaction_id: Optional[UUID] = None, limit: int = 100
    ) -> List[AuditRecord]:
        """
        Get the audit trail for transactions.

        Args:
            transaction_id: Optional transaction ID to filter by
            limit: Maximum number of records to return

        Returns:
            List of audit records
        """
        if transaction_id:
            # Filter to specific transaction
            filtered_trail = [
                record
                for record in self.audit_trail
                if record.transaction_id == transaction_id
            ]
        else:
            filtered_trail = self.audit_trail

        # Sort by timestamp (newest first) and limit
        sorted_trail = sorted(filtered_trail, key=lambda r: r.timestamp, reverse=True)

        return sorted_trail[:limit]

    def attach_receipt(
        self, transaction: Transaction, receipt_path: str
    ) -> Transaction:
        """
        Attach a receipt to a transaction.

        Args:
            transaction: The transaction to update
            receipt_path: Path to the receipt file

        Returns:
            The updated transaction
        """
        # Record previous state for audit
        previous_state = {"receipt_path": transaction.receipt_path}

        # Update receipt path
        transaction.receipt_path = receipt_path

        # Record audit trail
        audit_record = AuditRecord(
            transaction_id=transaction.id,
            action="attach_receipt",
            previous_state=previous_state,
            new_state={"receipt_path": receipt_path},
        )
        self.audit_trail.append(audit_record)

        return transaction

    def correct_categorization(
        self,
        transaction: Transaction,
        new_category: ExpenseCategory,
        new_business_percentage: float,
    ) -> Transaction:
        """
        Correct the categorization of a transaction.

        Args:
            transaction: The transaction to update
            new_category: The correct category
            new_business_percentage: The correct business use percentage

        Returns:
            The updated transaction
        """
        # Record previous state for audit
        previous_state = {
            "category": transaction.category,
            "business_use_percentage": transaction.business_use_percentage,
        }

        # Update transaction
        transaction.category = new_category
        transaction.business_use_percentage = new_business_percentage

        # Record audit trail
        audit_record = AuditRecord(
            transaction_id=transaction.id,
            action="correct_categorization",
            previous_state=previous_state,
            new_state={
                "category": new_category,
                "business_use_percentage": new_business_percentage,
            },
            notes="Manual correction of categorization",
        )
        self.audit_trail.append(audit_record)

        # Clear cache for this transaction
        cache_key = str(transaction.id)
        if cache_key in self._categorization_cache:
            del self._categorization_cache[cache_key]

        return transaction