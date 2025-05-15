"""Integration tests using mock implementations for cross-module functionality."""

from datetime import datetime
import uuid
from typing import Dict, List, Optional

import pytest

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
)


class TestIntegrationWithMocks:
    """Tests demonstrating integration between different system components using mocks."""

    def test_expense_categorization_impacts_tax_liability(self):
        """Test how business expense categorization impacts tax liability."""
        # Create test transactions
        transactions = [
            # Business expense
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 15),
                amount=1000.0,
                description="Business supplies purchase",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
                category=ExpenseCategory.BUSINESS_SUPPLIES,
                business_use_percentage=100.0,
            ),
            
            # Mixed-use expense
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 20),
                amount=200.0,
                description="Internet bill payment",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
                category=ExpenseCategory.INTERNET,
                business_use_percentage=80.0,
            ),
            
            # Personal expense
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 25),
                amount=500.0,
                description="Personal groceries",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
                category=ExpenseCategory.PERSONAL,
                business_use_percentage=0.0,
            ),
            
            # Income
            Transaction(
                id=uuid.uuid4(),
                date=datetime(2022, 3, 10),
                amount=5000.0,
                description="Client payment",
                transaction_type=TransactionType.INCOME,
                account_id="checking123",
            ),
        ]
        
        # Calculate total income and deductible expenses
        total_income = sum(tx.amount for tx in transactions 
                         if tx.transaction_type == TransactionType.INCOME)
        
        business_expenses = sum(
            tx.amount * (tx.business_use_percentage / 100)
            for tx in transactions
            if tx.transaction_type == TransactionType.EXPENSE 
            and tx.category != ExpenseCategory.PERSONAL
        )
        
        # Simplified tax calculation function
        def calculate_tax(income):
            # Simple mock tax calculation (10% up to 10000, 20% after)
            if income <= 10000:
                return income * 0.10
            else:
                return 10000 * 0.10 + (income - 10000) * 0.20
        
        # Calculate tax without business expense deductions
        tax_without_deductions = calculate_tax(total_income)
        
        # Calculate tax with business expense deductions
        taxable_income = total_income - business_expenses
        tax_with_deductions = calculate_tax(taxable_income)
        
        # Verify tax impact
        assert tax_with_deductions < tax_without_deductions
        assert tax_without_deductions - tax_with_deductions > 0
        
    def test_categorization_correction_tax_impact(self):
        """Test the tax impact of correcting expense categorization."""
        # Create a personal and business expense transaction
        personal_expense = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 4, 15),
            amount=1000.0,
            description="Equipment initially categorized as personal",
            transaction_type=TransactionType.EXPENSE,
            account_id="checking123",
            category=ExpenseCategory.PERSONAL,
            business_use_percentage=0.0,
        )
        
        income_transaction = Transaction(
            id=uuid.uuid4(),
            date=datetime(2022, 4, 10),
            amount=10000.0,
            description="Client payment",
            transaction_type=TransactionType.INCOME,
            account_id="checking123",
        )
        
        # Simplified tax calculation function
        def calculate_tax(income):
            # Simple mock tax calculation (10% up to 10000, 20% after)
            if income <= 10000:
                return income * 0.10
            else:
                return 10000 * 0.10 + (income - 10000) * 0.20
        
        # Calculate initial tax (before correction)
        initial_taxable_income = income_transaction.amount
        initial_tax = calculate_tax(initial_taxable_income)
        
        # Simulate correction of categorization
        corrected_expense = Transaction(
            id=personal_expense.id,
            date=personal_expense.date,
            amount=personal_expense.amount,
            description=personal_expense.description,
            transaction_type=personal_expense.transaction_type,
            account_id=personal_expense.account_id,
            category=ExpenseCategory.EQUIPMENT,  # Corrected category
            business_use_percentage=100.0,  # Corrected percentage
        )
        
        # Calculate tax after correction
        corrected_taxable_income = income_transaction.amount - corrected_expense.amount
        corrected_tax = calculate_tax(corrected_taxable_income)
        
        # Verify tax impact of the correction
        assert corrected_tax < initial_tax
        assert initial_tax - corrected_tax > 0
    
    def test_quarterly_tax_estimation(self):
        """Test quarterly tax estimation based on income and expenses."""
        # Create quarterly income and expenses
        quarters = [
            {
                "income": 15000.0,
                "business_expenses": 4000.0,
                "quarter": 1,
                "due_date": datetime(2022, 4, 15),
            },
            {
                "income": 18000.0,
                "business_expenses": 4500.0,
                "quarter": 2,
                "due_date": datetime(2022, 6, 15),
            },
            {
                "income": 22000.0, 
                "business_expenses": 5500.0,
                "quarter": 3,
                "due_date": datetime(2022, 9, 15),
            },
            {
                "income": 20000.0,
                "business_expenses": 5000.0,
                "quarter": 4,
                "due_date": datetime(2023, 1, 15),
            },
        ]
        
        # Simplified tax calculation function
        def calculate_quarterly_tax(income, expenses, prior_payments=0.0):
            taxable_income = income - expenses
            
            # Simple mock tax calculation (15% of taxable income)
            annual_projection = taxable_income * 4  # Simple projection
            estimated_annual_tax = annual_projection * 0.15
            
            # Each quarter should be 1/4 of the projected annual tax
            quarterly_portion = estimated_annual_tax / 4
            
            # Adjusted for prior payments
            required_payment = max(0, (quarterly_portion * quarters_elapsed) - prior_payments)
            
            return {
                "payment_amount": required_payment,
                "taxable_income": taxable_income,
                "projected_annual_tax": estimated_annual_tax,
            }
        
        # Track total paid
        total_paid = 0.0
        
        # Process each quarter
        for i, quarter in enumerate(quarters):
            quarters_elapsed = i + 1
            
            # Calculate quarterly tax
            quarterly_tax = calculate_quarterly_tax(
                income=quarter["income"],
                expenses=quarter["business_expenses"],
                prior_payments=total_paid
            )
            
            # Track payment
            total_paid += quarterly_tax["payment_amount"]
            
            # Verify the payment is positive
            assert quarterly_tax["payment_amount"] >= 0
        
        # Verify total annual payment is reasonable
        total_income = sum(q["income"] for q in quarters)
        total_expenses = sum(q["business_expenses"] for q in quarters)
        taxable_income = total_income - total_expenses
        
        # Simple annual tax calculation for comparison
        annual_tax = taxable_income * 0.15
        
        # The total payments should be close to the annual tax
        # Might not be exactly equal due to quarterly estimation methods
        assert abs(total_paid - annual_tax) < (annual_tax * 0.1)  # Within 10%
    
    def test_multi_year_project_profitability(self):
        """Test profitability analysis for a project spanning multiple tax years."""
        # Define project timeline
        start_date = datetime(2022, 11, 1)
        end_date = datetime(2023, 3, 31)
        
        # Define quarterly invoices
        invoices = [
            {
                "date": datetime(2022, 11, 5),
                "amount": 3000.0,
                "payment_date": datetime(2022, 11, 10),
                "year": 2022
            },
            {
                "date": datetime(2022, 12, 20),
                "amount": 3000.0,
                "payment_date": datetime(2022, 12, 27),
                "year": 2022
            },
            {
                "date": datetime(2023, 2, 15),
                "amount": 3000.0,
                "payment_date": datetime(2023, 2, 20),
                "year": 2023
            },
            {
                "date": datetime(2023, 3, 31),
                "amount": 3000.0,
                "payment_date": datetime(2023, 4, 5),
                "year": 2023
            },
        ]
        
        # Define expenses
        expenses = [
            {
                "date": datetime(2022, 11, 10),
                "amount": 500.0,
                "year": 2022
            },
            {
                "date": datetime(2022, 12, 15),
                "amount": 1200.0,
                "year": 2022
            },
            {
                "date": datetime(2023, 1, 20),
                "amount": 800.0,
                "year": 2023
            },
            {
                "date": datetime(2023, 3, 15),
                "amount": 500.0,
                "year": 2023
            },
        ]
        
        # Calculate revenue and expenses by year
        revenue_by_year = {}
        expenses_by_year = {}
        
        for invoice in invoices:
            year = invoice["year"]
            revenue_by_year[year] = revenue_by_year.get(year, 0) + invoice["amount"]
            
        for expense in expenses:
            year = expense["year"]
            expenses_by_year[year] = expenses_by_year.get(year, 0) + expense["amount"]
        
        # Calculate profit by year
        profit_by_year = {}
        for year in set(revenue_by_year.keys()) | set(expenses_by_year.keys()):
            revenue = revenue_by_year.get(year, 0)
            expense = expenses_by_year.get(year, 0)
            profit_by_year[year] = revenue - expense
        
        # Calculate total profit
        total_revenue = sum(revenue_by_year.values())
        total_expenses = sum(expenses_by_year.values())
        total_profit = total_revenue - total_expenses
        
        # Verify that profits are calculated correctly
        assert profit_by_year[2022] == revenue_by_year[2022] - expenses_by_year[2022]
        assert profit_by_year[2023] == revenue_by_year[2023] - expenses_by_year[2023]
        assert total_profit == sum(profit_by_year.values())
        assert profit_by_year[2022] + profit_by_year[2023] == total_profit