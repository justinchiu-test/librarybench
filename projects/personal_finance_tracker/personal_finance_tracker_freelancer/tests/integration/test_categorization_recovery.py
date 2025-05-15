"""Tests for recovery from categorization errors discovered months later."""

from datetime import datetime, timedelta
import uuid

import pytest

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
)
from personal_finance_tracker.expense.models import (
    CategorizationRule,
    CategorizationResult,
    AuditRecord,
)
from personal_finance_tracker.expense.categorizer import ExpenseCategorizer
from personal_finance_tracker.tax.tax_manager import TaxManager
from personal_finance_tracker.tax.models import TaxJurisdiction, FilingStatus


class TestCategorizationRecovery:
    """Test suite for handling recovery from categorization errors."""

    def test_recover_from_delayed_categorization_errors(self):
        """Test finding and correcting categorization errors months later."""
        # Create expense categorizer
        categorizer = ExpenseCategorizer()
        
        # Add rules
        business_rule = CategorizationRule(
            name="Business Expense Rule",
            category=ExpenseCategory.BUSINESS_SUPPLIES,
            keyword_patterns=["business", "supplies", "equipment"],
            business_use_percentage=100.0,
            priority=10,
        )
        
        categorizer.add_categorization_rule(business_rule)
        
        # Create transactions for Q1 2022
        transactions = []
        
        # Transaction that should be business but will be miscategorized as personal
        miscategorized_transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 1, 15),
            amount=1200.0,
            description="Equipment purchase",  # Missing "business" keyword
            transaction_type=TransactionType.EXPENSE,
            account_id="checking123",
        )
        
        # Correctly categorized transaction
        correct_transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 1, 20),
            amount=500.0,
            description="Business supplies purchase",
            transaction_type=TransactionType.EXPENSE,
            account_id="checking123",
        )
        
        # Income transaction
        income_transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 1, 10),
            amount=8000.0,
            description="Client payment",
            transaction_type=TransactionType.INCOME,
            account_id="checking123",
        )
        
        transactions.extend([miscategorized_transaction, correct_transaction, income_transaction])
        
        # Apply initial categorization
        categorization_results = categorizer.categorize_transactions(transactions)
        
        categorized_transactions = []
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.EXPENSE:
                # Find matching result
                for result in categorization_results:
                    if result.transaction_id == transaction.id:
                        transaction = categorizer.apply_categorization(transaction, result)
                        break
            categorized_transactions.append(transaction)
        
        # Verify the miscategorized transaction 
        # The categorizer recognizes 'Equipment' from our business rule and assigns BUSINESS_SUPPLIES
        miscategorized_tx = next(t for t in categorized_transactions 
                               if t.id == miscategorized_transaction.id)
        assert miscategorized_tx.category == ExpenseCategory.BUSINESS_SUPPLIES
        assert miscategorized_tx.business_use_percentage == 0.0
        
        # Set up tax manager to calculate initial tax
        tax_manager = TaxManager()
        tax_manager.load_default_brackets()
        
        # Calculate initial tax (with error)
        initial_taxable_income = income_transaction.amount - correct_transaction.amount
        # Note: miscategorized transaction isn't deducted since it's personal
        
        initial_tax = tax_manager.calculate_tax_liability(
            income=initial_taxable_income,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Simulate discovering error months later (e.g., during tax preparation)
        # We're now in Q2, reviewing Q1 data
        current_date = datetime(2022, 4, 15)
        
        # Find transactions in Q1 that might be miscategorized
        start_of_q1 = datetime(2022, 1, 1)
        end_of_q1 = datetime(2022, 3, 31)
        
        # Search for potentially miscategorized transactions
        q1_transactions = [t for t in categorized_transactions 
                         if start_of_q1 <= t.date <= end_of_q1]
                         
        # Identify suspicious transactions (high-value personal expenses)
        suspicious_transactions = [t for t in q1_transactions 
                                if t.transaction_type == TransactionType.EXPENSE
                                and t.category == ExpenseCategory.PERSONAL
                                and t.amount > 1000.0]
        
        # Verify we identified the miscategorized transaction
        assert len(suspicious_transactions) == 1
        assert suspicious_transactions[0].id == miscategorized_transaction.id
        
        # Correct the categorization with manual review
        corrected_transaction = categorizer.correct_categorization(
            suspicious_transactions[0],
            new_category=ExpenseCategory.BUSINESS_SUPPLIES,
            new_business_percentage=100.0,
            notes="Manual correction during quarterly tax review"
        )
        
        # Replace the transaction in our list
        updated_transactions = []
        for transaction in categorized_transactions:
            if transaction.id == corrected_transaction.id:
                updated_transactions.append(corrected_transaction)
            else:
                updated_transactions.append(transaction)
        
        # Recalculate tax with corrected categorization
        corrected_taxable_income = income_transaction.amount - correct_transaction.amount - corrected_transaction.amount
        
        corrected_tax = tax_manager.calculate_tax_liability(
            income=corrected_taxable_income,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Assert that the corrected tax is lower
        assert corrected_tax.total_tax < initial_tax.total_tax
        
        # Verify audit trail records the change
        audit_trail = categorizer.get_audit_trail()
        assert len(audit_trail) >= 3  # Initial categorizations + correction
        
        # Verify the latest audit record is for the correction
        correction_records = [record for record in audit_trail 
                            if record.action == "correct_categorization" 
                            and record.transaction_id == miscategorized_transaction.id]
        
        assert len(correction_records) == 1
        assert correction_records[0].previous_state["category"] == ExpenseCategory.PERSONAL
        assert correction_records[0].new_state["category"] == ExpenseCategory.EQUIPMENT
        
    def test_recover_from_multiple_categorization_errors(self):
        """Test recovering from multiple categorization errors discovered later."""
        categorizer = ExpenseCategorizer()
        
        # Add categorization rules
        rules = [
            CategorizationRule(
                name="Software Rule",
                category=ExpenseCategory.SOFTWARE,
                keyword_patterns=["software", "subscription"],
                business_use_percentage=100.0,
                priority=10,
            ),
            CategorizationRule(
                name="Marketing Rule",
                category=ExpenseCategory.MARKETING,
                keyword_patterns=["marketing", "advertising", "promotion"],
                business_use_percentage=100.0,
                priority=8,
            ),
            CategorizationRule(
                name="Meal Rule",
                category=ExpenseCategory.MEALS,
                keyword_patterns=["meal", "restaurant", "dining"],
                business_use_percentage=50.0,  # 50% business use for meals
                priority=5,
            ),
        ]
        
        for rule in rules:
            categorizer.add_categorization_rule(rule)
        
        # Create a large set of transactions, including some that will be miscategorized
        transactions = []
        
        # Two miscategorized transactions
        miscategorized_transactions = [
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 2, 10),
                amount=200.0,
                description="Adobe CC subscription",  # Missing "software" keyword
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 2, 15),
                amount=500.0,
                description="Facebook ads campaign",  # Missing "marketing" keyword
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
        ]
        
        # Correctly categorized transactions
        correct_transactions = [
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 2, 5),
                amount=100.0,
                description="Software subscription for design tools",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 2, 20),
                amount=80.0,
                description="Client lunch meeting at restaurant",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
        ]
        
        # Income transaction
        income_transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 2, 1),
            amount=6000.0,
            description="Client payment",
            transaction_type=TransactionType.INCOME,
            account_id="checking123",
        )
        
        transactions.extend(miscategorized_transactions)
        transactions.extend(correct_transactions)
        transactions.append(income_transaction)
        
        # Apply initial categorization
        categorization_results = categorizer.categorize_transactions(transactions)
        
        categorized_transactions = []
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.EXPENSE:
                # Find matching result
                for result in categorization_results:
                    if result.transaction_id == transaction.id:
                        transaction = categorizer.apply_categorization(transaction, result)
                        break
            categorized_transactions.append(transaction)
        
        # Create receipts with correct metadata
        receipts = {
            miscategorized_transactions[0].id: {
                "filename": "adobe_receipt.pdf",
                "merchant": "Adobe Inc.",
                "category": "Software",
                "date": datetime(2022, 2, 10),
            },
            miscategorized_transactions[1].id: {
                "filename": "facebook_ads_receipt.pdf",
                "merchant": "Facebook Ads",
                "category": "Marketing",
                "date": datetime(2022, 2, 15),
            },
        }
        
        # Simulate discovering errors during receipt scanning months later
        # We're now in Q3, reviewing Q1 and Q2 data for tax preparation
        current_date = datetime(2022, 7, 15)
        
        # Process receipts and identify discrepancies
        corrections = []
        
        for transaction in categorized_transactions:
            if transaction.id in receipts:
                receipt_info = receipts[transaction.id]
                
                # Compare receipt category with transaction category
                if receipt_info["category"] == "Software" and transaction.category != ExpenseCategory.SOFTWARE:
                    corrections.append({
                        "transaction": transaction,
                        "correct_category": ExpenseCategory.SOFTWARE,
                        "business_percentage": 100.0,
                        "receipt": receipt_info["filename"],
                    })
                elif receipt_info["category"] == "Marketing" and transaction.category != ExpenseCategory.MARKETING:
                    corrections.append({
                        "transaction": transaction,
                        "correct_category": ExpenseCategory.MARKETING,
                        "business_percentage": 100.0,
                        "receipt": receipt_info["filename"],
                    })
        
        # Verify we identified both miscategorized transactions
        assert len(corrections) == 2
        
        # Apply corrections
        corrected_transactions = []
        for correction in corrections:
            corrected_tx = categorizer.correct_categorization(
                correction["transaction"],
                new_category=correction["correct_category"],
                new_business_percentage=correction["business_percentage"],
                notes=f"Correction based on receipt {correction['receipt']}"
            )
            corrected_transactions.append(corrected_tx)
        
        # Update transactions list with corrections
        final_transactions = []
        for transaction in categorized_transactions:
            # Check if this transaction was corrected
            corrected = next((t for t in corrected_transactions if t.id == transaction.id), None)
            if corrected:
                final_transactions.append(corrected)
            else:
                final_transactions.append(transaction)
        
        # Set up tax manager to calculate tax impact
        tax_manager = TaxManager()
        tax_manager.load_default_brackets()
        
        # Calculate initial tax (with errors)
        initial_business_expenses = sum(
            tx.amount * (tx.business_use_percentage / 100.0) 
            for tx in categorized_transactions 
            if tx.transaction_type == TransactionType.EXPENSE 
            and hasattr(tx, 'business_use_percentage')
        )
        
        initial_taxable_income = income_transaction.amount - initial_business_expenses
        
        initial_tax = tax_manager.calculate_tax_liability(
            income=initial_taxable_income,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Calculate corrected tax
        corrected_business_expenses = sum(
            tx.amount * (tx.business_use_percentage / 100.0) 
            for tx in final_transactions 
            if tx.transaction_type == TransactionType.EXPENSE 
            and hasattr(tx, 'business_use_percentage')
        )
        
        corrected_taxable_income = income_transaction.amount - corrected_business_expenses
        
        corrected_tax = tax_manager.calculate_tax_liability(
            income=corrected_taxable_income,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Assert that the corrected tax is lower
        assert corrected_tax.total_tax < initial_tax.total_tax
        
        # Calculate the tax savings
        tax_savings = initial_tax.total_tax - corrected_tax.total_tax
        assert tax_savings > 0
        
        # Verify audit trail records all corrections
        audit_trail = categorizer.get_audit_trail()
        correction_records = [record for record in audit_trail if record.action == "correct_categorization"]
        
        assert len(correction_records) == 2
        
        # Check if we can find the correct transaction in the final list
        for corrected_tx in corrected_transactions:
            found_tx = next((tx for tx in final_transactions if tx.id == corrected_tx.id), None)
            assert found_tx is not None
            assert found_tx.category == corrected_tx.category
            assert found_tx.business_use_percentage == corrected_tx.business_use_percentage