"""Integration tests for year-over-year financial comparisons using mocks."""

from datetime import datetime
import uuid
from typing import Dict, List

import pytest
import pandas as pd
import numpy as np

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
)


class TestYearOverYearComparison:
    """Integration tests for year-over-year financial comparisons."""

    def test_income_growth_analysis(self):
        """Test analyzing income growth across multiple years."""
        # Create income data for three years
        yearly_income = {
            2021: [2000, 0, 3000, 1000, 2500, 500, 4000, 0, 2000, 2800, 1000, 3000],
            2022: [2500, 0, 4500, 1500, 3000, 500, 5000, 0, 2000, 3500, 1000, 4000],
            2023: [3000, 2000, 5000, 2500, 4000, 3000, 5500, 2500, 4000, 4500, 3500, 5000],
        }
        
        # Create transactions
        transactions = []
        for year, monthly_amounts in yearly_income.items():
            for month, amount in enumerate(monthly_amounts, 1):
                if amount > 0:
                    transaction = Transaction(
                        id=uuid.uuid4(),
                        date=datetime(year, month, 15),
                        amount=amount,
                        description=f"Income for {year}-{month:02d}",
                        transaction_type=TransactionType.INCOME,
                        account_id="checking123",
                    )
                    transactions.append(transaction)
        
        # Calculate yearly totals
        yearly_totals = {}
        for year in yearly_income:
            yearly_totals[year] = sum(yearly_income[year])
        
        # Calculate year-over-year growth
        growth_2021_to_2022 = (yearly_totals[2022] - yearly_totals[2021]) / yearly_totals[2021]
        growth_2022_to_2023 = (yearly_totals[2023] - yearly_totals[2022]) / yearly_totals[2022]
        
        # Verify positive growth
        assert growth_2021_to_2022 > 0
        assert growth_2022_to_2023 > 0
        
        # Calculate monthly income variability
        monthly_variability = {}
        for year, monthly_amounts in yearly_income.items():
            if any(monthly_amounts):
                std = np.std(monthly_amounts)
                mean = np.mean(monthly_amounts)
                if mean > 0:
                    monthly_variability[year] = std / mean  # Coefficient of variation
        
        # Verify decreasing variability (more stable income over time)
        assert monthly_variability[2023] < monthly_variability[2021]
    
    def test_expense_category_trends(self):
        """Test analyzing expense category trends across multiple years."""
        # Create expense data for three years with inflation
        base_expenses = {
            ExpenseCategory.BUSINESS_SUPPLIES: 1200,
            ExpenseCategory.SOFTWARE: 600,
            ExpenseCategory.MARKETING: 2400,
            ExpenseCategory.UTILITIES: 1800,
            ExpenseCategory.MEALS: 960,
            ExpenseCategory.EQUIPMENT: 6000,
            ExpenseCategory.PHONE: 1200,
            ExpenseCategory.INTERNET: 960,
            ExpenseCategory.PERSONAL: 12000,
        }
        
        # Apply yearly growth
        yearly_expenses = {
            2021: {k: v for k, v in base_expenses.items()},
            2022: {k: v * 1.05 for k, v in base_expenses.items()},  # 5% growth
            2023: {k: v * 1.12 for k, v in base_expenses.items()},  # 12% growth over 2021
        }
        
        # Create transactions
        transactions = []
        for year, expenses in yearly_expenses.items():
            for category, annual_amount in expenses.items():
                # Distribute expense over months (simplified)
                monthly_amount = annual_amount / 12
                
                for month in range(1, 13):
                    # Add random variation
                    amount = monthly_amount * (0.9 + 0.2 * np.random.random())
                    
                    # Determine business use percentage based on category
                    if category == ExpenseCategory.PERSONAL:
                        business_percentage = 0.0
                    elif category in [ExpenseCategory.UTILITIES, ExpenseCategory.PHONE]:
                        business_percentage = 50.0
                    else:
                        business_percentage = 100.0
                    
                    transaction = Transaction(
                        id=uuid.uuid4(),
                        date=datetime(year, month, 15),
                        amount=amount,
                        description=f"{category.value} expense for {year}-{month:02d}",
                        transaction_type=TransactionType.EXPENSE,
                        account_id="checking123",
                        category=category,
                        business_use_percentage=business_percentage,
                    )
                    transactions.append(transaction)
        
        # Calculate business vs personal expense ratio by year
        yearly_business_ratio = {}
        
        for year in yearly_expenses:
            year_transactions = [tx for tx in transactions 
                               if tx.date.year == year 
                               and tx.transaction_type == TransactionType.EXPENSE]
            
            business_expenses = sum(
                tx.amount * (tx.business_use_percentage / 100)
                for tx in year_transactions
                if tx.category != ExpenseCategory.PERSONAL 
                and tx.business_use_percentage > 0
            )
            
            personal_expenses = sum(
                tx.amount if tx.category == ExpenseCategory.PERSONAL
                else tx.amount * (1 - tx.business_use_percentage / 100)
                for tx in year_transactions
            )
            
            total_expenses = business_expenses + personal_expenses
            
            if total_expenses > 0:
                yearly_business_ratio[year] = business_expenses / total_expenses
        
        # Due to random variations and the constant ratio of business/personal expenses,
        # the business ratio should be approximately the same across years
        # The important part is that we can calculate and compare these metrics
        assert abs(yearly_business_ratio[2023] - yearly_business_ratio[2021]) < 0.05  # Within 5%
    
    def test_tax_liability_comparison(self):
        """Test comparing tax liabilities across multiple years."""
        # Define total income and business expenses for each year
        yearly_data = {
            2021: {"income": 21800, "business_expenses": 8500},
            2022: {"income": 27500, "business_expenses": 10000},
            2023: {"income": 44500, "business_expenses": 15000},
        }
        
        # Simplified tax calculation function - progressive tax brackets
        def calculate_tax(income, deductions=0):
            taxable_income = max(0, income - deductions)
            
            # Simplified 2022 US tax brackets for single filer
            brackets = [
                (0, 10275, 0.10),      # 10% for $0 - $10,275
                (10275, 41775, 0.12),  # 12% for $10,276 - $41,775
                (41775, 89075, 0.22),  # 22% for $41,776 - $89,075
                (89075, float('inf'), 0.24),  # 24% for $89,076+
            ]
            
            tax = 0
            for bracket_min, bracket_max, rate in brackets:
                if taxable_income <= bracket_min:
                    break
                
                bracket_amount = min(taxable_income, bracket_max) - bracket_min
                tax += max(0, bracket_amount) * rate
                
                if taxable_income <= bracket_max:
                    break
            
            return tax
        
        # Calculate tax liability for each year
        tax_liabilities = {}
        effective_tax_rates = {}
        
        for year, data in yearly_data.items():
            taxable_income = data["income"] - data["business_expenses"]
            tax = calculate_tax(taxable_income)
            
            tax_liabilities[year] = tax
            effective_tax_rates[year] = (tax / data["income"]) if data["income"] > 0 else 0
        
        # Verify tax increases with income
        assert tax_liabilities[2022] > tax_liabilities[2021]
        assert tax_liabilities[2023] > tax_liabilities[2022]
        
        # Verify effective tax rate increases with income due to progressive brackets
        assert effective_tax_rates[2023] > effective_tax_rates[2021]
    
    def test_project_profitability_trends(self):
        """Test analyzing project profitability trends across multiple years."""
        # Create project data for three years
        yearly_projects = {
            2021: [
                {"name": "Project A", "revenue": 3000, "expenses": 1200, "hours": 40},
                {"name": "Project B", "revenue": 5000, "expenses": 2000, "hours": 60},
                {"name": "Project C", "revenue": 2500, "expenses": 1000, "hours": 30},
            ],
            2022: [
                {"name": "Project D", "revenue": 4000, "expenses": 1500, "hours": 45},
                {"name": "Project E", "revenue": 6000, "expenses": 2200, "hours": 65},
                {"name": "Project F", "revenue": 3500, "expenses": 1100, "hours": 35},
            ],
            2023: [
                {"name": "Project G", "revenue": 5000, "expenses": 1700, "hours": 48},
                {"name": "Project H", "revenue": 7500, "expenses": 2500, "hours": 70},
                {"name": "Project I", "revenue": 4500, "expenses": 1300, "hours": 38},
            ],
        }
        
        # Calculate yearly metrics
        yearly_metrics = {}
        
        for year, projects in yearly_projects.items():
            total_revenue = sum(p["revenue"] for p in projects)
            total_expenses = sum(p["expenses"] for p in projects)
            total_profit = total_revenue - total_expenses
            total_hours = sum(p["hours"] for p in projects)
            
            # Calculate metrics
            if total_hours > 0:
                effective_hourly_rate = total_revenue / total_hours
                cost_per_hour = total_expenses / total_hours
                profit_per_hour = total_profit / total_hours
            else:
                effective_hourly_rate = 0
                cost_per_hour = 0
                profit_per_hour = 0
                
            if total_revenue > 0:
                profit_margin = (total_profit / total_revenue) * 100
            else:
                profit_margin = 0
                
            yearly_metrics[year] = {
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "total_profit": total_profit,
                "total_hours": total_hours,
                "effective_hourly_rate": effective_hourly_rate,
                "profit_margin": profit_margin,
                "profit_per_hour": profit_per_hour,
            }
        
        # Verify improving metrics over time
        assert yearly_metrics[2022]["effective_hourly_rate"] > yearly_metrics[2021]["effective_hourly_rate"]
        assert yearly_metrics[2023]["effective_hourly_rate"] > yearly_metrics[2022]["effective_hourly_rate"]
        
        assert yearly_metrics[2023]["profit_margin"] > yearly_metrics[2021]["profit_margin"]
        assert yearly_metrics[2023]["profit_per_hour"] > yearly_metrics[2021]["profit_per_hour"]