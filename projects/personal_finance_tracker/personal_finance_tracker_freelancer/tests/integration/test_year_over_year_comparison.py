"""Integration tests for year-over-year financial comparison."""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List

import pytest
import pandas as pd
import numpy as np

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
    Client,
    Project,
)
from personal_finance_tracker.expense.models import ExpenseSummary
from personal_finance_tracker.expense.categorizer import ExpenseCategorizer
from personal_finance_tracker.income.income_manager import IncomeManager
from personal_finance_tracker.tax.tax_manager import TaxManager
from personal_finance_tracker.tax.models import (
    FilingStatus,
    TaxJurisdiction,
    TaxYearSummary,
    TaxBracket,
)
from personal_finance_tracker.project.profitability_analyzer import ProjectProfiler


class TestYearOverYearComparison:
    """Integration tests for year-over-year financial comparison."""

    @pytest.fixture
    def multi_year_transactions(self):
        """Create transactions spanning multiple years for testing."""
        transactions = []
        
        # Create data for 2021-2023 (3 years)
        for year in range(2021, 2024):
            # Income transactions - variable pattern typical for freelancer
            # Different patterns each year to show growth/changes
            if year == 2021:
                # First year - lower income, more variable
                income_amounts = [2000, 0, 3000, 1000, 2500, 500, 4000, 0, 2000, 2800, 1000, 3000]
            elif year == 2022:
                # Second year - higher income, still variable
                income_amounts = [2500, 0, 4500, 1500, 3000, 500, 5000, 0, 2000, 3500, 1000, 4000]
            else:  # 2023
                # Third year - even higher income, more stability
                income_amounts = [3000, 2000, 5000, 2500, 4000, 3000, 5500, 2500, 4000, 4500, 3500, 5000]
            
            # Create income transactions
            for i, amount in enumerate(income_amounts):
                month = i + 1  # 1-12
                
                date = datetime(year, month, 15)
                
                if amount > 0:
                    transaction = Transaction(
                        id=uuid.uuid4(),
                        date=date,
                        amount=amount,
                        description=f"Client payment for Project {i}",
                        transaction_type=TransactionType.INCOME,
                        account_id="checking123",
                        client_id=f"client{i % 3 + 1}",
                        project_id=f"project{i % 5 + 1}",
                    )
                    transactions.append(transaction)
            
            # Expense transactions - categories with different business percentages
            expense_categories = [
                (ExpenseCategory.BUSINESS_SUPPLIES, 100, 100),
                (ExpenseCategory.SOFTWARE, 50, 100),
                (ExpenseCategory.MARKETING, 200, 100),
                (ExpenseCategory.UTILITIES, 150, 30),
                (ExpenseCategory.MEALS, 80, 50),
                (ExpenseCategory.EQUIPMENT, 500, 80),
                (ExpenseCategory.PHONE, 100, 70),
                (ExpenseCategory.INTERNET, 80, 80),
                (ExpenseCategory.CAR, 200, 60),
                (ExpenseCategory.HOME_OFFICE, 300, 40),
                (ExpenseCategory.PERSONAL, 1000, 0),
            ]
            
            # Add yearly inflation factor for expenses
            inflation_factor = 1.0
            if year == 2022:
                inflation_factor = 1.05  # 5% inflation
            elif year == 2023:
                inflation_factor = 1.10  # 10% inflation over 2021
            
            # Create monthly expenses for each year
            for month in range(1, 13):
                date = datetime(year, month, 20)
                
                for category, base_amount, business_pct in expense_categories:
                    # Apply some variation and inflation
                    amount = base_amount * inflation_factor * (0.9 + 0.2 * np.random.random())
                    
                    transaction = Transaction(
                        id=uuid.uuid4(),
                        date=date,
                        amount=amount,
                        description=f"{category.value} expense",
                        transaction_type=TransactionType.EXPENSE,
                        account_id="checking123",
                        category=category,
                        business_use_percentage=business_pct,
                    )
                    transactions.append(transaction)
            
            # Tax payment transactions (quarterly)
            for quarter in range(1, 5):
                # Determine payment date based on quarter
                if quarter == 1:
                    date = datetime(year, 4, 15)
                elif quarter == 2:
                    date = datetime(year, 6, 15)
                elif quarter == 3:
                    date = datetime(year, 9, 15)
                else:
                    date = datetime(year + 1, 1, 15)
                
                # Tax amount increases each year
                tax_amount = 1800
                if year == 2022:
                    tax_amount = 2200
                elif year == 2023:
                    tax_amount = 2600
                
                transaction = Transaction(
                    id=uuid.uuid4(),
                    date=date,
                    amount=tax_amount,
                    description=f"Q{quarter} {year} Estimated Tax Payment",
                    transaction_type=TransactionType.TAX_PAYMENT,
                    account_id="checking123",
                )
                transactions.append(transaction)
        
        return transactions

    @pytest.fixture
    def multi_year_projects(self):
        """Create projects spanning multiple years for testing."""
        projects = []
        
        # Create projects that span different years
        # Year 1 (2021) Projects
        projects.extend([
            Project(
                id="project2021_1",
                name="Website Redesign 2021",
                client_id="client1",
                start_date=datetime(2021, 1, 15),
                end_date=datetime(2021, 3, 1),
                status="completed",
                hourly_rate=75.0,
                estimated_hours=40.0,
            ),
            Project(
                id="project2021_2",
                name="Mobile App Development 2021",
                client_id="client2",
                start_date=datetime(2021, 4, 1),
                end_date=datetime(2021, 7, 15),
                status="completed",
                hourly_rate=85.0,
                estimated_hours=100.0,
            ),
            Project(
                id="project2021_3",
                name="Brand Identity 2021",
                client_id="client3",
                start_date=datetime(2021, 8, 1),
                end_date=datetime(2021, 10, 30),
                status="completed",
                fixed_price=3000.0,
                estimated_hours=35.0,
            ),
        ])
        
        # Year 2 (2022) Projects
        projects.extend([
            Project(
                id="project2022_1",
                name="Website Redesign 2022",
                client_id="client1",
                start_date=datetime(2022, 2, 1),
                end_date=datetime(2022, 4, 15),
                status="completed",
                hourly_rate=80.0,
                estimated_hours=45.0,
            ),
            Project(
                id="project2022_2",
                name="Mobile App Development 2022",
                client_id="client2",
                start_date=datetime(2022, 5, 1),
                end_date=datetime(2022, 8, 30),
                status="completed",
                hourly_rate=90.0,
                estimated_hours=120.0,
            ),
            Project(
                id="project2022_3",
                name="Brand Identity 2022",
                client_id="client3",
                start_date=datetime(2022, 9, 1),
                end_date=datetime(2022, 11, 30),
                status="completed",
                fixed_price=3500.0,
                estimated_hours=40.0,
            ),
        ])
        
        # Year 3 (2023) Projects
        projects.extend([
            Project(
                id="project2023_1",
                name="Website Redesign 2023",
                client_id="client1",
                start_date=datetime(2023, 1, 15),
                end_date=datetime(2023, 3, 30),
                status="completed",
                hourly_rate=85.0,
                estimated_hours=50.0,
            ),
            Project(
                id="project2023_2",
                name="Mobile App Development 2023",
                client_id="client2",
                start_date=datetime(2023, 4, 1),
                end_date=datetime(2023, 7, 31),
                status="completed",
                hourly_rate=95.0,
                estimated_hours=130.0,
            ),
            Project(
                id="project2023_3",
                name="Brand Identity 2023",
                client_id="client3",
                start_date=datetime(2023, 8, 15),
                end_date=datetime(2023, 11, 15),
                status="completed",
                fixed_price=4000.0,
                estimated_hours=45.0,
            ),
        ])
        
        # Cross-year project (spanning 2022-2023)
        projects.append(
            Project(
                id="project_cross_year",
                name="Long Term Strategy Project",
                client_id="client1",
                start_date=datetime(2022, 11, 1),
                end_date=datetime(2023, 2, 28),
                status="completed",
                fixed_price=6000.0,
                estimated_hours=70.0,
            )
        )
        
        return projects

    @pytest.fixture
    def time_entries_for_projects(self, multi_year_projects):
        """Create time entries for the multi-year projects."""
        time_entries = []
        
        for project in multi_year_projects:
            # Skip if no start or end date
            if not project.start_date or not project.end_date:
                continue
                
            # Calculate project duration in days
            project_days = (project.end_date - project.start_date).days
            
            # For each project, create time entries
            # Distribute hours across the project duration
            total_hours = project.estimated_hours or 40
            work_days = max(1, project_days // 3)  # Work every third day on average
            hours_per_day = total_hours / work_days
            
            current_day = 0
            hours_logged = 0
            
            while hours_logged < total_hours and current_day < project_days:
                # Create a time entry every 2-4 days
                skip_days = np.random.randint(2, 5)
                current_day += skip_days
                
                if current_day >= project_days:
                    break
                
                # Determine hours to log for this day
                day_hours = min(hours_per_day * 1.5, total_hours - hours_logged)
                if day_hours <= 0:
                    break
                    
                hours_logged += day_hours
                
                # Create time entry
                entry_date = project.start_date + timedelta(days=current_day)
                start_time = datetime.combine(entry_date.date(), datetime.min.time()) + timedelta(hours=9)
                end_time = start_time + timedelta(hours=day_hours)
                
                time_entry = {
                    "id": str(uuid.uuid4()),
                    "project_id": project.id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": f"Work on {project.name}",
                    "billable": True,
                    "duration_minutes": int(day_hours * 60),
                }
                
                time_entries.append(time_entry)
        
        return time_entries

    def test_income_comparison_across_years(self, multi_year_transactions):
        """Test comparing income patterns across multiple years."""
        income_manager = IncomeManager()
        
        # Process transactions by year
        year_data = {}
        
        for year in range(2021, 2024):
            # Filter income transactions for this year
            year_transactions = [
                tx for tx in multi_year_transactions 
                if tx.date.year == year and tx.transaction_type == TransactionType.INCOME
            ]
            
            # Define start and end dates for the year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            # Calculate monthly income for the year
            monthly_income_dict = income_manager.calculate_monthly_income(year_transactions, start_date, end_date)
            
            # Convert to list format for compatibility with existing code
            monthly_income = [{"month": month, "amount": amount} for month, amount in monthly_income_dict.items()]
            
            # Store year data
            year_data[year] = {
                "transactions": year_transactions,
                "monthly_income": monthly_income,
                "total_income": sum(month["amount"] for month in monthly_income),
                "month_count": len(monthly_income),
                "average_monthly": sum(month["amount"] for month in monthly_income) / max(1, len(monthly_income)),
            }
        
        # Compare total income year-over-year
        assert year_data[2022]["total_income"] > year_data[2021]["total_income"]
        assert year_data[2023]["total_income"] > year_data[2022]["total_income"]
        
        # Calculate growth rates
        growth_2021_to_2022 = (year_data[2022]["total_income"] - year_data[2021]["total_income"]) / year_data[2021]["total_income"]
        growth_2022_to_2023 = (year_data[2023]["total_income"] - year_data[2022]["total_income"]) / year_data[2022]["total_income"]
        
        # Verify positive growth
        assert growth_2021_to_2022 > 0
        assert growth_2022_to_2023 > 0
        
        # Compare monthly patterns
        # Convert to DataFrame for easier comparison
        monthly_data = {}
        for year, data in year_data.items():
            monthly_amounts = [month["amount"] for month in data["monthly_income"]]
            # Pad with zeros if less than 12 months
            if len(monthly_amounts) < 12:
                monthly_amounts.extend([0] * (12 - len(monthly_amounts)))
            monthly_data[year] = monthly_amounts
        
        df = pd.DataFrame(monthly_data)
        
        # Calculate month-to-month variability for each year
        variability = {}
        for year in range(2021, 2024):
            if year in df.columns:
                # Calculate coefficient of variation (std/mean)
                std = df[year].std()
                mean = df[year].mean()
                if mean > 0:
                    variability[year] = std / mean
                else:
                    variability[year] = float('inf')
        
        # Verify that income becomes more stable over time (lower variability)
        if 2021 in variability and 2023 in variability:
            assert variability[2023] < variability[2021]
    
    def test_expense_comparison_across_years(self, multi_year_transactions):
        """Test comparing expense patterns across multiple years."""
        categorizer = ExpenseCategorizer()
        
        # Process expenses by year and category
        year_data = {}
        
        for year in range(2021, 2024):
            # Filter expense transactions for this year
            year_transactions = [
                tx for tx in multi_year_transactions 
                if tx.date.year == year and tx.transaction_type == TransactionType.EXPENSE
            ]
            
            # Generate expense summary for the year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            expense_summary = categorizer.generate_expense_summary(
                year_transactions, start_date, end_date
            )
            
            # Store data for analysis
            year_data[year] = {
                "transactions": year_transactions,
                "summary": expense_summary,
                "total_expenses": expense_summary.total_expenses,
                "business_expenses": expense_summary.business_expenses,
                "personal_expenses": expense_summary.personal_expenses,
                "by_category": expense_summary.by_category,
            }
        
        # Compare total expenses year-over-year
        # Should increase due to inflation and business growth
        assert year_data[2022]["total_expenses"] > year_data[2021]["total_expenses"]
        assert year_data[2023]["total_expenses"] > year_data[2022]["total_expenses"]
        
        # Calculate expense growth rates
        expense_growth_2021_to_2022 = (
            year_data[2022]["total_expenses"] - year_data[2021]["total_expenses"]
        ) / year_data[2021]["total_expenses"]
        
        expense_growth_2022_to_2023 = (
            year_data[2023]["total_expenses"] - year_data[2022]["total_expenses"]
        ) / year_data[2022]["total_expenses"]
        
        # Inflation was higher in 2023, so expense growth should be higher
        assert expense_growth_2022_to_2023 > expense_growth_2021_to_2022
        
        # Compare business vs personal expense ratio over time
        business_ratio = {}
        for year, data in year_data.items():
            if data["total_expenses"] > 0:
                business_ratio[year] = data["business_expenses"] / data["total_expenses"]
            else:
                business_ratio[year] = 0
        
        # Assuming business expenses should increase as a proportion over time
        # as the freelancer becomes more established
        # This will depend on the test data pattern
        assert business_ratio[2023] >= business_ratio[2021]
        
        # Compare expense categories across years
        # Convert to DataFrame for easier comparison
        categories = set()
        for data in year_data.values():
            categories.update(data["by_category"].keys())
        
        category_data = {}
        for year, data in year_data.items():
            year_categories = {}
            for category in categories:
                year_categories[category.value] = data["by_category"].get(category, 0)
            category_data[year] = year_categories
        
        df_categories = pd.DataFrame(category_data).T  # Transpose to get years as rows
        
        # Verify changes in specific categories
        # Example: Software expenses should increase year over year as the business grows
        if ExpenseCategory.SOFTWARE in categories:
            software_col = ExpenseCategory.SOFTWARE.value
            if software_col in df_categories.columns:
                software_expenses = df_categories[software_col]
                if 2021 in software_expenses.index and 2023 in software_expenses.index:
                    assert software_expenses[2023] > software_expenses[2021]
    
    def test_tax_comparison_across_years(self, multi_year_transactions):
        """Test comparing tax liabilities across multiple years."""
        tax_manager = TaxManager(FilingStatus.SINGLE)
        tax_manager.load_default_brackets()
        
        # Add tax brackets for other years (2021, 2023)
        # 2021 federal tax brackets (simplified)
        tax_brackets_2021 = TaxBracket(
            jurisdiction=TaxJurisdiction.FEDERAL,
            filing_status=FilingStatus.SINGLE,
            tax_year=2021,
            income_thresholds=[0, 9950, 40525, 86375, 164925, 209425, 523600],
            rates=[10, 12, 22, 24, 32, 35, 37],
        )
        
        # 2023 federal tax brackets (simplified)
        tax_brackets_2023 = TaxBracket(
            jurisdiction=TaxJurisdiction.FEDERAL,
            filing_status=FilingStatus.SINGLE,
            tax_year=2023,
            income_thresholds=[0, 11000, 44725, 95375, 182100, 231250, 578125],
            rates=[10, 12, 22, 24, 32, 35, 37],
        )
        
        # Set the tax brackets
        tax_manager.set_tax_brackets([tax_brackets_2021, tax_brackets_2023])
        
        categorizer = ExpenseCategorizer()
        
        # Process taxes by year
        year_data = {}
        
        for year in range(2021, 2024):
            # Filter transactions for this year
            year_transactions = [tx for tx in multi_year_transactions if tx.date.year == year]
            
            # Split into income and expenses
            income_transactions = [
                tx for tx in year_transactions 
                if tx.transaction_type == TransactionType.INCOME
            ]
            
            expense_transactions = [
                tx for tx in year_transactions 
                if tx.transaction_type == TransactionType.EXPENSE
            ]
            
            tax_transactions = [
                tx for tx in year_transactions 
                if tx.transaction_type == TransactionType.TAX_PAYMENT
            ]
            
            # Calculate total income
            total_income = sum(tx.amount for tx in income_transactions)
            
            # Generate expense summary
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            expense_summary = categorizer.generate_expense_summary(
                expense_transactions, start_date, end_date
            )
            
            # Calculate taxable income
            taxable_income = total_income - expense_summary.business_expenses
            
            # Calculate tax liability
            tax_calculation = tax_manager.calculate_tax_liability(
                income=taxable_income,
                tax_year=year,
                jurisdiction=TaxJurisdiction.FEDERAL
            )
            
            # Calculate total tax payments
            tax_payments = sum(tx.amount for tx in tax_transactions)
            
            # Store year data
            year_data[year] = {
                "total_income": total_income,
                "business_expenses": expense_summary.business_expenses,
                "taxable_income": taxable_income,
                "tax_liability": tax_calculation.total_tax,
                "tax_payments": tax_payments,
                "effective_tax_rate": tax_calculation.effective_rate,
                "marginal_tax_rate": tax_calculation.marginal_rate,
            }
        
        # Compare tax liabilities year-over-year
        assert year_data[2022]["tax_liability"] > year_data[2021]["tax_liability"]
        assert year_data[2023]["tax_liability"] > year_data[2022]["tax_liability"]
        
        # Verify effective tax rates
        # As income increases, effective tax rate should increase in a progressive system
        assert year_data[2023]["effective_tax_rate"] >= year_data[2021]["effective_tax_rate"]
        
        # Verify marginal tax rates
        # The highest marginal tax rate should increase or stay the same as income increases
        assert year_data[2023]["marginal_tax_rate"] >= year_data[2021]["marginal_tax_rate"]
        
        # Calculate tax efficiency (tax / income)
        tax_efficiency = {}
        for year, data in year_data.items():
            if data["total_income"] > 0:
                tax_efficiency[year] = data["tax_liability"] / data["total_income"]
            else:
                tax_efficiency[year] = 0
        
        # Calculate business expense deduction effectiveness
        # (tax saved per dollar of business expense)
        deduction_effectiveness = {}
        for year, data in year_data.items():
            if data["business_expenses"] > 0:
                # Calculate tax without deductions
                tax_without_deductions = tax_manager.calculate_tax_liability(
                    income=data["total_income"],
                    tax_year=year,
                    jurisdiction=TaxJurisdiction.FEDERAL
                ).total_tax
                
                # Tax saved
                tax_saved = tax_without_deductions - data["tax_liability"]
                
                # Effectiveness is tax saved per dollar of business expense
                deduction_effectiveness[year] = tax_saved / data["business_expenses"]
            else:
                deduction_effectiveness[year] = 0
        
        # As income increases and moves into higher tax brackets,
        # the effectiveness of deductions should increase
        if 2021 in deduction_effectiveness and 2023 in deduction_effectiveness:
            assert deduction_effectiveness[2023] >= deduction_effectiveness[2021]
    
    def test_project_profitability_across_years(self, multi_year_projects, time_entries_for_projects):
        """Test comparing project profitability across multiple years."""
        profiler = ProjectProfiler()
        
        # Add time entries
        for entry in time_entries_for_projects:
            # Create a TimeEntry object
            time_entry = TimeEntry(
                id=entry["id"],
                project_id=entry["project_id"],
                start_time=entry["start_time"],
                end_time=entry["end_time"],
                description=entry["description"],
                billable=entry["billable"],
                duration_minutes=entry["duration_minutes"]
            )
            profiler.record_time_entry(time_entry)
        
        # Analyze projects by year
        year_data = {}
        
        for year in range(2021, 2024):
            # Filter projects that were active in this year
            year_projects = [
                p for p in multi_year_projects
                if (p.start_date and p.start_date.year <= year) and
                   (not p.end_date or p.end_date.year >= year)
            ]
            
            # Skip if no projects
            if not year_projects:
                continue
                
            # Analyze each project
            project_results = []
            for project in year_projects:
                # Pass empty lists for time_entries, transactions, and invoices 
                # since we've already recorded the time entries with profiler.record_time_entry
                # In a real scenario, we'd pass actual time entries, transactions, and invoices here
                result = profiler.analyze_project_profitability(
                    project=project,
                    time_entries=[],  # Already recorded via record_time_entry
                    transactions=[],  # Not used in this test
                    invoices=[]       # Not used in this test
                )
                if result:
                    project_results.append(result)
            
            # Calculate year metrics
            if project_results:
                total_hours = sum(result.total_hours for result in project_results)
                total_revenue = sum(result.revenue for result in project_results)
                total_cost = sum(result.cost for result in project_results)
                total_profit = sum(result.profit for result in project_results)
                
                # Calculate overall effective hourly rate and profit margin
                if total_hours > 0:
                    effective_hourly_rate = total_revenue / total_hours
                else:
                    effective_hourly_rate = 0
                    
                if total_revenue > 0:
                    profit_margin = total_profit / total_revenue
                else:
                    profit_margin = 0
                
                # Store year data
                year_data[year] = {
                    "projects": project_results,
                    "project_count": len(project_results),
                    "total_hours": total_hours,
                    "total_revenue": total_revenue,
                    "total_cost": total_cost,
                    "total_profit": total_profit,
                    "effective_hourly_rate": effective_hourly_rate,
                    "profit_margin": profit_margin,
                }
        
        # Compare key metrics across years
        years_to_compare = [y for y in range(2021, 2024) if y in year_data]
        if len(years_to_compare) >= 2:
            first_year = min(years_to_compare)
            last_year = max(years_to_compare)
            
            # Compare hourly rates (should increase over time)
            assert year_data[last_year]["effective_hourly_rate"] > year_data[first_year]["effective_hourly_rate"]
            
            # Calculate hourly rate growth
            hourly_rate_growth = (
                year_data[last_year]["effective_hourly_rate"] - 
                year_data[first_year]["effective_hourly_rate"]
            ) / max(0.1, year_data[first_year]["effective_hourly_rate"])
            
            # Verify positive growth in hourly rate
            assert hourly_rate_growth > 0
            
            # Compare project types and profitability
            # Group projects by client to see client profitability trends
            client_profitability = {}
            
            for year in years_to_compare:
                for project_result in year_data[year]["projects"]:
                    client_id = project_result.client_id
                    
                    if client_id not in client_profitability:
                        client_profitability[client_id] = {}
                    
                    if year not in client_profitability[client_id]:
                        client_profitability[client_id][year] = []
                    
                    client_profitability[client_id][year].append(project_result)
            
            # Check if clients became more profitable over time
            for client_id, client_years in client_profitability.items():
                if first_year in client_years and last_year in client_years:
                    # Calculate average profit margin for first and last year
                    first_year_margins = [
                        p.profit_margin for p in client_years[first_year]
                    ]
                    
                    last_year_margins = [
                        p.profit_margin for p in client_years[last_year]
                    ]
                    
                    # Calculate average margins
                    if first_year_margins and last_year_margins:
                        first_year_avg = sum(first_year_margins) / len(first_year_margins)
                        last_year_avg = sum(last_year_margins) / len(last_year_margins)
                        
                        # Most clients should become more profitable over time
                        # But we don't assert this because it depends on specific scenarios
                        client_profit_improved = last_year_avg > first_year_avg