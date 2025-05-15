"""Integration tests for end-to-end quarterly tax preparation."""

from datetime import datetime, timedelta
import uuid
from decimal import Decimal

import pytest

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
)
from personal_finance_tracker.expense.models import (
    CategorizationRule,
    ExpenseSummary,
)
from personal_finance_tracker.expense.categorizer import ExpenseCategorizer
from personal_finance_tracker.income.models import SmoothingMethod
from personal_finance_tracker.income.income_manager import IncomeManager
from personal_finance_tracker.tax.models import (
    FilingStatus,
    TaxJurisdiction,
    TaxBracket,
    QuarterInfo,
    EstimatedPayment,
)
from personal_finance_tracker.tax.tax_manager import TaxManager


class TestQuarterlyTaxPreparation:
    """Integration tests for quarterly tax preparation process."""

    def test_comprehensive_quarterly_tax_preparation(self, sample_transactions, sample_date):
        """Test a comprehensive end-to-end quarterly tax preparation process."""
        # Set up the required components
        expense_categorizer = ExpenseCategorizer()
        income_manager = IncomeManager()
        tax_manager = TaxManager(FilingStatus.SINGLE)
        
        # Load default tax brackets
        tax_manager.load_default_brackets()
        
        # Add expense categorization rules
        rules = [
            CategorizationRule(
                name="Software Rule",
                category=ExpenseCategory.SOFTWARE,
                keyword_patterns=["software", "subscription"],
                business_use_percentage=100.0,
                priority=10,
            ),
            CategorizationRule(
                name="Office Supplies Rule",
                category=ExpenseCategory.BUSINESS_SUPPLIES,
                keyword_patterns=["supplies", "office"],
                business_use_percentage=100.0,
                priority=5,
            ),
            CategorizationRule(
                name="Internet Rule",
                category=ExpenseCategory.INTERNET,
                keyword_patterns=["internet", "wifi"],
                business_use_percentage=80.0,
                priority=8,
            ),
            CategorizationRule(
                name="Phone Rule",
                category=ExpenseCategory.PHONE,
                keyword_patterns=["phone", "mobile"],
                business_use_percentage=70.0,
                priority=8,
            ),
            CategorizationRule(
                name="Meal Rule",
                category=ExpenseCategory.MEALS,
                keyword_patterns=["meal", "restaurant", "food"],
                business_use_percentage=50.0,  # 50% business use
                priority=3,
            ),
        ]
        
        for rule in rules:
            expense_categorizer.add_categorization_rule(rule)
        
        # Define the quarter to prepare taxes for (Q2 2022)
        tax_year = 2022
        quarter_number = 2
        
        # Calculate quarter dates
        quarters = tax_manager.calculate_tax_quarters(tax_year)
        current_quarter = next(q for q in quarters if q.quarter == quarter_number)
        
        # Filter transactions for the current quarter
        quarter_transactions = [
            tx for tx in sample_transactions 
            if current_quarter.start_date <= tx.date <= current_quarter.end_date
        ]
        
        # Step 1: Categorize all expenses for the quarter
        expense_transactions = [
            tx for tx in quarter_transactions 
            if tx.transaction_type == TransactionType.EXPENSE
        ]
        
        categorization_results = expense_categorizer.categorize_transactions(expense_transactions)
        
        # Apply categorizations
        categorized_expenses = []
        for transaction in expense_transactions:
            for result in categorization_results:
                if result.transaction_id == transaction.id:
                    categorized_tx = expense_categorizer.apply_categorization(transaction, result)
                    categorized_expenses.append(categorized_tx)
                    break
        
        # Step 2: Calculate income for the quarter
        income_transactions = [
            tx for tx in quarter_transactions 
            if tx.transaction_type == TransactionType.INCOME
        ]
        
        # Calculate total quarterly income
        quarterly_income = sum(tx.amount for tx in income_transactions)
        
        # Step 3: Generate an expense summary for the quarter
        expense_summary = expense_categorizer.generate_expense_summary(
            categorized_expenses,
            current_quarter.start_date,
            current_quarter.end_date
        )
        
        # Step 4: Calculate taxable income (income - business expenses)
        business_expenses = expense_summary.business_expenses
        taxable_income = quarterly_income - business_expenses
        
        # Calculate year-to-date values
        # For Q2, we need Q1 + Q2
        ytd_start_date = datetime(tax_year, 1, 1)
        ytd_end_date = current_quarter.end_date
        
        ytd_transactions = [
            tx for tx in sample_transactions 
            if ytd_start_date <= tx.date <= ytd_end_date
        ]
        
        ytd_income_transactions = [
            tx for tx in ytd_transactions 
            if tx.transaction_type == TransactionType.INCOME
        ]
        
        ytd_expense_transactions = [
            tx for tx in ytd_transactions 
            if tx.transaction_type == TransactionType.EXPENSE
        ]
        
        # Categorize YTD expenses
        ytd_categorization_results = expense_categorizer.categorize_transactions(ytd_expense_transactions)
        
        ytd_categorized_expenses = []
        for transaction in ytd_expense_transactions:
            for result in ytd_categorization_results:
                if result.transaction_id == transaction.id:
                    categorized_tx = expense_categorizer.apply_categorization(transaction, result)
                    ytd_categorized_expenses.append(categorized_tx)
                    break
        
        # Generate YTD expense summary
        ytd_expense_summary = expense_categorizer.generate_expense_summary(
            ytd_categorized_expenses,
            ytd_start_date,
            ytd_end_date
        )
        
        # Calculate YTD income
        ytd_income = sum(tx.amount for tx in ytd_income_transactions)
        
        # Calculate YTD taxable income
        ytd_business_expenses = ytd_expense_summary.business_expenses
        ytd_taxable_income = ytd_income - ytd_business_expenses
        
        # Step 5: Calculate estimated quarterly tax payment
        quarterly_tax_calculation: EstimatedPayment = tax_manager.calculate_quarterly_tax_payment(
            quarterly_taxable_income=taxable_income,
            ytd_taxable_income=ytd_taxable_income,
            tax_year=tax_year,
            quarter=quarter_number
        )
        
        # Step 6: Generate a tax payment transaction for the quarter
        tax_payment_transaction = Transaction(
            id=uuid.uuid4(),
            date=current_quarter.due_date,
            amount=quarterly_tax_calculation.payment_amount,
            description=f"Q{quarter_number} {tax_year} Estimated Tax Payment",
            transaction_type=TransactionType.TAX_PAYMENT,
            account_id="checking123",
        )
        
        # Verify the tax calculation
        assert quarterly_tax_calculation.quarter == quarter_number
        assert quarterly_tax_calculation.year == tax_year
        assert quarterly_tax_calculation.payment_amount > 0
        
        # Verify that the quarterly calculation includes appropriate tax components
        assert hasattr(quarterly_tax_calculation, 'federal_tax')
        assert quarterly_tax_calculation.federal_tax >= 0
        
        # Optional: Verify self-employment tax is included if applicable
        if hasattr(quarterly_tax_calculation, 'self_employment_tax'):
            assert quarterly_tax_calculation.self_employment_tax >= 0
        
        # Verify expense summary data
        assert expense_summary.period_start == current_quarter.start_date
        assert expense_summary.period_end == current_quarter.end_date
        assert expense_summary.total_expenses > 0
        assert expense_summary.business_expenses > 0
        
        # Verify that business expenses are affecting tax calculations
        # Create income-only transactions for control calculation
        income_transactions = [tx for tx in quarter_transactions 
                             if tx.transaction_type == TransactionType.INCOME]
        control_tax: TaxLiability = tax_manager.calculate_tax_liability(
            transactions=income_transactions,  # Without deducting business expenses
            tax_year=tax_year
        )
        
        actual_tax: TaxLiability = tax_manager.calculate_tax_liability(
            transactions=categorized_expenses + income_transactions,  # With business expenses
            tax_year=tax_year
        )
        
        # Tax should be lower when business expenses are deducted
        assert actual_tax.total_tax < control_tax.total_tax

    def test_quarterly_tax_with_prior_payments(self):
        """Test quarterly tax preparation with prior quarterly payments."""
        # Set up components
        tax_manager = TaxManager(FilingStatus.SINGLE)
        tax_manager.load_default_brackets()
        
        # Define tax year and quarters
        tax_year = 2022
        quarters = tax_manager.calculate_tax_quarters(tax_year)
        
        # Simulate income and expenses for each quarter
        quarterly_data = [
            # Q1
            {
                "income": 15000.0,
                "business_expenses": 4000.0,
                "taxable_income": 11000.0,
            },
            # Q2
            {
                "income": 18000.0,
                "business_expenses": 4500.0,
                "taxable_income": 13500.0,
            },
            # Q3
            {
                "income": 22000.0,
                "business_expenses": 5500.0,
                "taxable_income": 16500.0,
            },
            # Q4
            {
                "income": 20000.0,
                "business_expenses": 5000.0,
                "taxable_income": 15000.0,
            },
        ]
        
        # Track prior payments and YTD values
        prior_payments = 0.0
        ytd_taxable_income = 0.0
        
        for quarter_idx, quarter_info in enumerate(quarterly_data):
            quarter_number = quarter_idx + 1
            current_quarter = quarters[quarter_idx]
            
            # Add current quarter income to YTD
            ytd_taxable_income += quarter_info["taxable_income"]
            
            # Calculate quarterly tax
            quarterly_tax: EstimatedPayment = tax_manager.calculate_quarterly_tax_payment(
                quarterly_taxable_income=quarter_info["taxable_income"],
                ytd_taxable_income=ytd_taxable_income,
                tax_year=tax_year,
                quarter=quarter_number,
                prior_payments=prior_payments
            )
            
            # Create tax payment transaction
            tax_payment_transaction = Transaction(
                id=uuid.uuid4(),
                date=current_quarter.due_date,
                amount=quarterly_tax.payment_amount,
                description=f"Q{quarter_number} {tax_year} Estimated Tax Payment",
                transaction_type=TransactionType.TAX_PAYMENT,
                account_id="checking123",
            )
            
            # Update prior payments for next quarter
            prior_payments += quarterly_tax.payment_amount
            
            # Verify the tax calculation is reasonable
            assert quarterly_tax.payment_amount > 0
            
            # For later quarters, verify adjustment based on prior payments
            if quarter_number > 1:
                # Calculate what this quarter's payment would be without prior payments
                control_tax: EstimatedPayment = tax_manager.calculate_quarterly_tax_payment(
                    quarterly_taxable_income=quarter_info["taxable_income"],
                    ytd_taxable_income=ytd_taxable_income,
                    tax_year=tax_year,
                    quarter=quarter_number,
                    prior_payments=0.0  # No prior payments
                )
                
                # In a progressive tax system with prior payments,
                # the quarterly payment should reflect adjustments
                # Either the actual payment is less (accounting for prior payments)
                # or it's the same if we're significantly under-withheld
                difference = abs(control_tax.payment_amount - quarterly_tax.payment_amount)
                
                # Allow for small floating point differences
                if difference > 0.01:
                    # If significant difference, the actual payment should be less than
                    # what would be required without prior payments
                    assert quarterly_tax.payment_amount <= control_tax.payment_amount
        
        # Verify end-of-year calculations
        # The sum of quarterly payments should approximately equal the annual tax liability
        annual_taxable_income = sum(q["taxable_income"] for q in quarterly_data)
        
        # Create synthetic transactions for annual calculation
        annual_income_tx = Transaction(
            id=uuid.uuid4(),
            date=datetime(tax_year, 12, 31),
            amount=sum(q["income"] for q in quarterly_data),
            description="Annual income",
            transaction_type=TransactionType.INCOME,
            account_id="checking123",
        )
        
        annual_expense_tx = Transaction(
            id=uuid.uuid4(),
            date=datetime(tax_year, 12, 31),
            amount=sum(q["business_expenses"] for q in quarterly_data),
            description="Annual business expenses",
            transaction_type=TransactionType.EXPENSE,
            account_id="checking123",
            category=ExpenseCategory.BUSINESS_SUPPLIES,
            business_use_percentage=100.0,
        )
        
        annual_tax = tax_manager.calculate_tax_liability(
            transactions=[annual_income_tx, annual_expense_tx],
            tax_year=tax_year
        )
        
        # Total of quarterly payments should be close to annual tax
        # (may not match exactly due to quarterly estimation methods)
        assert abs(prior_payments - annual_tax.total_tax) < (annual_tax.total_tax * 0.1)  # Within 10%

    def test_quarterly_tax_with_income_smoothing(self):
        """Test quarterly tax preparation with income smoothing."""
        # Set up components
        income_manager = IncomeManager()
        tax_manager = TaxManager(FilingStatus.SINGLE)
        tax_manager.load_default_brackets()
        
        # Create fluctuating monthly income for the year
        monthly_income = [
            3000.0,   # Jan
            2000.0,   # Feb
            1500.0,   # Mar
            5000.0,   # Apr
            4500.0,   # May
            2000.0,   # Jun
            1000.0,   # Jul
            1500.0,   # Aug
            6000.0,   # Sep
            4000.0,   # Oct
            3500.0,   # Nov
            8000.0,   # Dec
        ]
        
        # Convert to monthly transaction data
        monthly_transactions = []
        
        for i, amount in enumerate(monthly_income):
            month = i + 1  # 1-12
            year = 2022
            
            # Create transaction for this month
            tx = Transaction(
                id=uuid.uuid4(),
                date=datetime(year, month, 15),
                amount=amount,
                description=f"Income for {datetime(year, month, 1).strftime('%B %Y')}",
                transaction_type=TransactionType.INCOME,
                account_id="checking123",
            )
            
            monthly_transactions.append(tx)
        
        # Define quarterly periods
        quarters = tax_manager.calculate_tax_quarters(2022)
        
        # Process each quarter
        for quarter_idx, quarter in enumerate(quarters):
            quarter_number = quarter_idx + 1
            
            # Get transactions for this quarter
            quarter_transactions = [
                tx for tx in monthly_transactions 
                if quarter.start_date <= tx.date <= quarter.end_date
            ]
            
            # Calculate actual quarterly income
            actual_quarterly_income = sum(tx.amount for tx in quarter_transactions)
            
            # Calculate smoothed income using moving average
            # First generate all monthly income up to current quarter
            month_end = 3 * quarter_number  # Last month of current quarter
            income_data = monthly_income[:month_end]
            
            # Apply income smoothing
            smoothed_monthly_income = income_manager.smooth_income(
                income_data, 
                method=SmoothingMethod.MOVING_AVERAGE,
                window_size=6  # 6-month moving average
            )
            
            # Get smoothed income for the current quarter (last 3 months)
            smoothed_quarterly_income = sum(smoothed_monthly_income[-3:])
            
            # Calculate tax using both actual and smoothed income
            actual_tax = tax_manager.calculate_quarterly_tax_payment(
                quarterly_taxable_income=actual_quarterly_income,
                ytd_taxable_income=sum(monthly_income[:month_end]),
                tax_year=2022,
                quarter=quarter_number
            )
            
            smoothed_tax = tax_manager.calculate_quarterly_tax_payment(
                quarterly_taxable_income=smoothed_quarterly_income,
                ytd_taxable_income=sum(smoothed_monthly_income),
                tax_year=2022,
                quarter=quarter_number
            )
            
            # Verify smoothing is working
            if quarter_number > 1:  # Smoothing most effective after some data
                # For highly variable income, the smoothed payment should be more stable
                actual_variance = actual_quarterly_income / sum(monthly_income[:month_end])
                smoothed_variance = smoothed_quarterly_income / sum(smoothed_monthly_income)
                
                # The smoothed income should have less variance from the average
                # This is the income stability we're trying to achieve
                assert abs(smoothed_variance - 0.25) <= abs(actual_variance - 0.25)
                
            # For tax planning, create a tax payment based on smoothed income
            tax_payment_transaction = Transaction(
                id=uuid.uuid4(),
                date=quarter.due_date,
                amount=smoothed_tax.payment_amount,
                description=f"Q{quarter_number} 2022 Estimated Tax Payment (smoothed)",
                transaction_type=TransactionType.TAX_PAYMENT,
                account_id="checking123",
            )
            
            # Verify we have a valid payment amount
            assert smoothed_tax.payment_amount > 0