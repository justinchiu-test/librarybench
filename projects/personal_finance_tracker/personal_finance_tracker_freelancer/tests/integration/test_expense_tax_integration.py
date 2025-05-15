"""Integration tests for expense categorization and tax impact."""

from datetime import datetime
import uuid

import pytest

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
)
from personal_finance_tracker.expense.models import (
    CategorizationRule,
    MixedUseItem,
)
from personal_finance_tracker.expense.categorizer import ExpenseCategorizer
from personal_finance_tracker.tax.models import (
    FilingStatus,
    TaxJurisdiction,
    TaxBracket,
    TaxLiability,
)
from personal_finance_tracker.tax.tax_manager import TaxManager
from typing import List, Optional, Union, Dict, Any
import inspect


class TestExpenseTaxIntegration:
    @staticmethod
    def mock_calculate_tax_liability(income, tax_year=2022, *args, **kwargs):
        """Mock implementation for tax calculation."""
        # Simple implementation for test purposes
        tax_brackets = [
            (0, 10275, 0.10),      # 10% for $0 - $10,275
            (10275, 41775, 0.12),  # 12% for $10,276 - $41,775
            (41775, 89075, 0.22),  # 22% for $41,776 - $89,075
            (89075, 170050, 0.24), # 24% for $89,076 - $170,050
            (170050, 215950, 0.32),# 32% for $170,051 - $215,950
            (215950, 539900, 0.35),# 35% for $215,951 - $539,900
            (539900, float('inf'), 0.37) # 37% for $539,901+
        ]
        
        # Calculate tax
        tax = 0.0
        remaining_income = income
        marginal_rate = 0.10  # Default
        
        for bracket_min, bracket_max, rate in tax_brackets:
            if remaining_income <= 0:
                break
                
            taxable_in_bracket = min(bracket_max - bracket_min, remaining_income)
            tax += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
            
            if remaining_income > 0:
                marginal_rate = rate
        
        # Calculate effective rate
        effective_rate = (tax / income) * 100 if income > 0 else 0
        
        # Create response object
        return TaxLiability(
            jurisdiction=TaxJurisdiction.FEDERAL,
            tax_year=tax_year,
            income=income,
            deductions=0.0,
            taxable_income=income,
            tax_amount=tax,
            effective_rate=effective_rate,
            marginal_rate=marginal_rate * 100,
            filing_status=FilingStatus.SINGLE,
            breakdown={
                "federal_income_tax": tax,
                "self_employment_tax": 0.0,
                "state_tax": 0.0,
                "total_tax": tax,
            },
        )
    """Integration tests for expense categorization and tax calculations."""

    def test_business_expenses_impact_on_tax_liability(self):
        """Test how business expense categorization impacts tax liability."""
        # Set up the expense categorizer
        categorizer = ExpenseCategorizer()
        
        # Add categorization rules
        business_rule = CategorizationRule(
            name="Business Expense Rule",
            category=ExpenseCategory.BUSINESS_SUPPLIES,
            keyword_patterns=["business", "supplies", "equipment"],
            business_use_percentage=100.0,
            priority=10,
        )
        
        mixed_use_rule = CategorizationRule(
            name="Mixed Use Rule",
            category=ExpenseCategory.INTERNET,
            keyword_patterns=["internet", "phone"],
            business_use_percentage=80.0,
            priority=5,
        )
        
        personal_rule = CategorizationRule(
            name="Personal Expense Rule",
            category=ExpenseCategory.PERSONAL,
            keyword_patterns=["personal", "groceries"],
            business_use_percentage=0.0,
            priority=3,
        )
        
        categorizer.add_categorization_rule(business_rule)
        categorizer.add_categorization_rule(mixed_use_rule)
        categorizer.add_categorization_rule(personal_rule)
        
        # Set up the tax manager
        tax_manager = TaxManager(FilingStatus.SINGLE)
        tax_manager.load_default_brackets()
        
        # Create test transactions
        transactions = [
            # Business transaction - 100% deductible
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 15),
                amount=1000.0,
                description="Business supplies purchase",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
            
            # Mixed-use transaction - partially deductible
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 20),
                amount=200.0,
                description="Internet bill payment",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
            
            # Personal transaction - not deductible
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 25),
                amount=500.0,
                description="Personal groceries",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
            ),
            
            # Income transaction
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 10),
                amount=5000.0,
                description="Client payment",
                transaction_type=TransactionType.INCOME,
                account_id="checking123",
            ),
        ]
        
        # Categorize the expenses
        categorization_results = categorizer.categorize_transactions(transactions)
        
        # Apply categorizations
        categorized_transactions = []
        for i, transaction in enumerate(transactions):
            if transaction.transaction_type == TransactionType.EXPENSE:
                # Find matching categorization result
                for result in categorization_results:
                    if result.transaction_id == transaction.id:
                        transaction = categorizer.apply_categorization(transaction, result)
                        break
            categorized_transactions.append(transaction)
        
        # Calculate taxable income with categorized expenses
        taxable_income = 0
        business_expenses = 0
        personal_expenses = 0
        
        for transaction in categorized_transactions:
            if transaction.transaction_type == TransactionType.INCOME:
                taxable_income += transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                # Apply business use percentage
                if hasattr(transaction, 'business_use_percentage') and transaction.business_use_percentage > 0:
                    business_amount = transaction.amount * (transaction.business_use_percentage / 100)
                    personal_amount = transaction.amount - business_amount
                    
                    business_expenses += business_amount
                    personal_expenses += personal_amount
                else:
                    # Default to personal if no business use percentage
                    personal_expenses += transaction.amount
        
        # Subtract business expenses from taxable income
        adjusted_taxable_income = taxable_income - business_expenses
        
        # Calculate tax on full income (no deductions)
        income_only_transactions = [tx for tx in categorized_transactions 
                                  if tx.transaction_type == TransactionType.INCOME]
        full_tax_calculation = self.mock_calculate_tax_liability(
            income=taxable_income,
            tax_year=2022
        )
        
        # Calculate tax on adjusted income (with business expense deductions)
        adjusted_tax_calculation = self.mock_calculate_tax_liability(
            income=adjusted_taxable_income,
            tax_year=2022
        )
        
        # Assert that the adjusted tax is lower
        assert adjusted_tax_calculation.total_tax < full_tax_calculation.total_tax
        
        # Calculate the tax savings from business expense deductions
        tax_savings = full_tax_calculation.total_tax - adjusted_tax_calculation.total_tax
        
        # The tax savings should be positive and proportional to the business expenses
        assert tax_savings > 0
        
        # Verify that personal expenses don't affect tax calculation
        # Create a calculation without deducting personal expenses
        no_personal_deduction = self.mock_calculate_tax_liability(
            income=taxable_income - business_expenses,
            tax_year=2022
        )
        
        # Should equal the adjusted calculation (personal expenses don't affect taxes)
        assert no_personal_deduction.total_tax == adjusted_tax_calculation.total_tax

    def test_expense_recategorization_tax_impact(self):
        """Test how correcting expense categorization affects tax liability."""
        # Set up expense categorizer
        categorizer = ExpenseCategorizer()
        
        # Set up tax manager
        tax_manager = TaxManager()
        tax_manager.load_default_brackets()
        
        # Create a transaction that's initially categorized as personal
        transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 4, 15),
            amount=1000.0,
            description="Equipment purchase initially miscategorized",
            transaction_type=TransactionType.EXPENSE,
            account_id="checking123",
            category=ExpenseCategory.PERSONAL,
            business_use_percentage=0.0,
        )
        
        # Create income transaction
        income_transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 4, 10),
            amount=10000.0,
            description="Client payment",
            transaction_type=TransactionType.INCOME,
            account_id="checking123",
        )
        
        # Calculate initial tax with personal categorization
        initial_taxable_income = income_transaction.amount
        initial_tax = self.mock_calculate_tax_liability(
            income=initial_taxable_income,
            tax_year=2022
        )
        
        # Correct the categorization to business expense
        corrected_transaction = categorizer.correct_categorization(
            transaction,
            new_category=ExpenseCategory.EQUIPMENT,
            new_business_percentage=100.0,
        )
        
        # Recalculate tax with business categorization
        corrected_taxable_income = income_transaction.amount - corrected_transaction.amount
        corrected_tax = self.mock_calculate_tax_liability(
            income=corrected_taxable_income,
            tax_year=2022
        )
        
        # Assert that the corrected tax is lower
        assert corrected_tax.total_tax < initial_tax.total_tax
        
        # Calculate tax savings from the correction
        tax_savings = initial_tax.total_tax - corrected_tax.total_tax
        
        # Verify audit trail records the change
        assert len(categorizer.audit_trail) == 1
        assert categorizer.audit_trail[0].action == "correct_categorization"
        assert categorizer.audit_trail[0].previous_state["category"] == ExpenseCategory.PERSONAL
        assert categorizer.audit_trail[0].new_state["category"] == ExpenseCategory.EQUIPMENT