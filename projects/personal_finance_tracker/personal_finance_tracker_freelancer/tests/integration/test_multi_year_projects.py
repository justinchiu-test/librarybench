"""Integration tests for projects spanning multiple tax years."""

from datetime import datetime, timedelta
import uuid
from decimal import Decimal
import random

import pytest
import pandas as pd
import numpy as np

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
    TransactionType,
    Client,
    Project,
    TimeEntry,
    Invoice,
)
from personal_finance_tracker.project.models import ProjectProfitability
from personal_finance_tracker.project.profitability_analyzer import ProjectProfiler
from personal_finance_tracker.tax.models import (
    FilingStatus,
    TaxJurisdiction,
    TaxYearSummary,
)
from personal_finance_tracker.tax.tax_manager import TaxManager


class TestMultiYearProjects:
    """Integration tests for projects spanning multiple tax years."""

    @pytest.fixture
    def cross_year_project(self):
        """Create a project that spans across tax years."""
        return Project(
            id="cross_year_project",
            name="Long-term Website Redesign",
            client_id="client1",
            start_date=datetime(2022, 11, 1),
            end_date=datetime(2023, 3, 31),
            status="completed",
            hourly_rate=90.0,
            estimated_hours=160.0,
        )

    @pytest.fixture
    def cross_year_time_entries(self, cross_year_project):
        """Create time entries for a project spanning multiple tax years."""
        time_entries = []
        
        # Create time entries spanning from November 2022 to March 2023
        project_start = cross_year_project.start_date
        project_end = cross_year_project.end_date
        
        # Define different phases of the project
        phases = [
            {"name": "Discovery", "days": 20, "hours_per_day": 4},
            {"name": "Design", "days": 35, "hours_per_day": 6},
            {"name": "Development", "days": 45, "hours_per_day": 8},
            {"name": "Testing", "days": 20, "hours_per_day": 5},
            {"name": "Launch", "days": 10, "hours_per_day": 7},
        ]
        
        current_date = project_start
        for phase in phases:
            for i in range(phase["days"]):
                # Skip weekends
                if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                    current_date += timedelta(days=1)
                    continue
                
                # Add some variation to hours
                hours = phase["hours_per_day"] * (0.8 + 0.4 * random.random())
                
                # Create time entry
                start_time = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=9)  # 9 AM
                end_time = start_time + timedelta(hours=hours)
                
                time_entry = TimeEntry(
                    id=uuid.uuid4(),
                    project_id=cross_year_project.id,
                    start_time=start_time,
                    end_time=end_time,
                    description=f"{phase['name']} phase work",
                    billable=True,
                )
                
                time_entries.append(time_entry)
                
                # Move to next day
                current_date += timedelta(days=1)
                
                # Stop if we've reached project end
                if current_date > project_end:
                    break
                    
            # Stop if we've reached project end
            if current_date > project_end:
                break
        
        return time_entries

    @pytest.fixture
    def cross_year_expenses(self, cross_year_project):
        """Create project-related expenses spanning multiple tax years."""
        expenses = []
        
        # Define expenses for the cross-year project
        project_expenses = [
            # 2022 expenses
            {
                "date": datetime(2022, 11, 10),
                "amount": 300.0,
                "description": "Software licenses for project",
                "category": ExpenseCategory.SOFTWARE,
            },
            {
                "date": datetime(2022, 11, 25),
                "amount": 450.0,
                "description": "Design assets purchase",
                "category": ExpenseCategory.BUSINESS_SUPPLIES,
            },
            {
                "date": datetime(2022, 12, 15),
                "amount": 1200.0,
                "description": "External developer assistance",
                "category": ExpenseCategory.EQUIPMENT,
            },
            # 2023 expenses
            {
                "date": datetime(2023, 1, 20),
                "amount": 600.0,
                "description": "Server costs for development",
                "category": ExpenseCategory.SOFTWARE,
            },
            {
                "date": datetime(2023, 2, 10),
                "amount": 350.0,
                "description": "Testing tools subscription",
                "category": ExpenseCategory.SOFTWARE,
            },
            {
                "date": datetime(2023, 3, 15),
                "amount": 500.0,
                "description": "Client presentation materials",
                "category": ExpenseCategory.BUSINESS_SUPPLIES,
            },
        ]
        
        for expense_data in project_expenses:
            expense = Transaction(
                id=uuid.uuid4(),
                date=expense_data["date"],
                amount=expense_data["amount"],
                description=expense_data["description"],
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
                category=expense_data["category"],
                business_use_percentage=100.0,
                project_id=cross_year_project.id,
            )
            
            expenses.append(expense)
        
        return expenses

    @pytest.fixture
    def cross_year_invoices(self, cross_year_project):
        """Create project invoices spanning multiple tax years."""
        invoices = []
        
        # Create phased invoices for the cross-year project
        invoice_data = [
            # Initial deposit (2022)
            {
                "date": datetime(2022, 11, 5),
                "amount": 3600.0,  # 25% upfront
                "description": "Initial deposit for website redesign project",
                "status": "paid",
                "payment_date": datetime(2022, 11, 10),
            },
            # Phase completion invoice (2022)
            {
                "date": datetime(2022, 12, 20),
                "amount": 3600.0,  # 25% at phase completion
                "description": "Design phase completion payment",
                "status": "paid",
                "payment_date": datetime(2022, 12, 27),
            },
            # Phase completion invoice (2023)
            {
                "date": datetime(2023, 2, 15),
                "amount": 3600.0,  # 25% at phase completion
                "description": "Development phase completion payment",
                "status": "paid",
                "payment_date": datetime(2023, 2, 20),
            },
            # Final invoice (2023)
            {
                "date": datetime(2023, 3, 31),
                "amount": 3600.0,  # 25% at project completion
                "description": "Final payment for website redesign project",
                "status": "paid",
                "payment_date": datetime(2023, 4, 5),
            },
        ]
        
        for i, data in enumerate(invoice_data):
            invoice = Invoice(
                id=f"inv-{cross_year_project.id}-{i+1}",
                client_id=cross_year_project.client_id,
                project_id=cross_year_project.id,
                issue_date=data["date"],
                due_date=data["date"] + timedelta(days=15),
                amount=data["amount"],
                status=data["status"],
                payment_date=data.get("payment_date"),
                description=data["description"],
                line_items=[{"description": data["description"], "amount": data["amount"]}],
            )
            
            invoices.append(invoice)
        
        return invoices

    def test_project_profitability_across_tax_years(
        self, cross_year_project, cross_year_time_entries, cross_year_expenses, cross_year_invoices
    ):
        """Test profitability analysis for a project spanning multiple tax years."""
        # Set up project profiler
        profiler = ProjectProfiler()
        
        # Analyze project profitability for the full period
        result = profiler.analyze_project_profitability(
            project=cross_year_project,
            time_entries=cross_year_time_entries,
            transactions=cross_year_expenses,
            invoices=cross_year_invoices
        )
        
        # Verify overall profitability
        assert result is not None
        assert result.total_hours > 0
        assert result.total_revenue > 0
        assert result.total_profit > 0
        assert result.profit_margin > 0
        
        # Now analyze by tax year
        year_2022_start = datetime(2022, 1, 1)
        year_2022_end = datetime(2022, 12, 31)
        year_2023_start = datetime(2023, 1, 1)
        year_2023_end = datetime(2023, 12, 31)
        
        # Filter time entries for 2022
        time_entries_2022 = [
            entry for entry in cross_year_time_entries
            if entry.start_time >= year_2022_start and entry.start_time <= year_2022_end
        ]
        
        # Filter expenses for 2022
        expenses_2022 = [
            expense for expense in cross_year_expenses
            if expense.date >= year_2022_start and expense.date <= year_2022_end
        ]
        
        # Filter invoices for 2022
        invoices_2022 = [
            invoice for invoice in cross_year_invoices
            if invoice.issue_date >= year_2022_start and invoice.issue_date <= year_2022_end
        ]
        
        # Filter time entries for 2023
        time_entries_2023 = [
            entry for entry in cross_year_time_entries
            if entry.start_time >= year_2023_start and entry.start_time <= year_2023_end
        ]
        
        # Filter expenses for 2023
        expenses_2023 = [
            expense for expense in cross_year_expenses
            if expense.date >= year_2023_start and expense.date <= year_2023_end
        ]
        
        # Filter invoices for 2023
        invoices_2023 = [
            invoice for invoice in cross_year_invoices
            if invoice.issue_date >= year_2023_start and invoice.issue_date <= year_2023_end
        ]
        
        # Analyze 2022 portion
        result_2022 = profiler.analyze_project_profitability(
            project=cross_year_project,
            time_entries=time_entries_2022,
            transactions=expenses_2022,
            invoices=invoices_2022
        )
        
        # Analyze 2023 portion
        result_2023 = profiler.analyze_project_profitability(
            project=cross_year_project,
            time_entries=time_entries_2023,
            transactions=expenses_2023,
            invoices=invoices_2023
        )
        
        # Verify results for each year
        assert result_2022 is not None
        assert result_2023 is not None
        
        # Verify hours are split across years
        assert result_2022.total_hours > 0
        assert result_2023.total_hours > 0
        assert abs(result.total_hours - (result_2022.total_hours + result_2023.total_hours)) < 0.01
        
        # Verify revenue is split across years based on invoices
        assert result_2022.total_revenue > 0
        assert result_2023.total_revenue > 0
        assert abs(result.total_revenue - (result_2022.total_revenue + result_2023.total_revenue)) < 0.01
        
        # Verify expenses are split across years
        assert result_2022.total_expenses > 0
        assert result_2023.total_expenses > 0
        assert abs(result.total_expenses - (result_2022.total_expenses + result_2023.total_expenses)) < 0.01
        
        # Verify the split makes sense based on timing
        # In our fixture, the project starts in November 2022 and ends in March 2023
        # So most of the work and billing should be in 2023
        assert result_2023.total_hours > result_2022.total_hours
        
        # Generate trend analysis
        trend = profiler.generate_trend_analysis(
            metric_type=ProjectMetricType.HOURLY_RATE,
            start_date=year_2022_start,
            end_date=year_2023_end,
            period="monthly",
            project_id=cross_year_project.id,
            projects=[cross_year_project],
            time_entries=cross_year_time_entries,
            transactions=cross_year_expenses,
            invoices=cross_year_invoices
        )
        
        # Verify trend data
        assert trend is not None
        assert len(trend.data_points) > 0
        
        # Verify months from both years are included
        months_in_trend = [point.date for point in trend.data_points]
        assert any(m.year == 2022 for m in months_in_trend)
        assert any(m.year == 2023 for m in months_in_trend)

    def test_tax_implications_of_cross_year_project(
        self, cross_year_project, cross_year_time_entries, cross_year_expenses, cross_year_invoices
    ):
        """Test tax implications of a project spanning multiple tax years."""
        # Set up tax manager
        tax_manager = TaxManager(FilingStatus.SINGLE)
        tax_manager.load_default_brackets()
        
        # Set up project profiler
        profiler = ProjectProfiler()
        
        # Now analyze by tax year
        year_2022_start = datetime(2022, 1, 1)
        year_2022_end = datetime(2022, 12, 31)
        year_2023_start = datetime(2023, 1, 1)
        year_2023_end = datetime(2023, 12, 31)
        
        # Filter time entries, expenses, and invoices for 2022
        time_entries_2022 = [
            entry for entry in cross_year_time_entries
            if entry.start_time >= year_2022_start and entry.start_time <= year_2022_end
        ]
        
        expenses_2022 = [
            expense for expense in cross_year_expenses
            if expense.date >= year_2022_start and expense.date <= year_2022_end
        ]
        
        invoices_2022 = [
            invoice for invoice in cross_year_invoices
            if invoice.issue_date >= year_2022_start and invoice.issue_date <= year_2022_end
        ]
        
        # Filter time entries, expenses, and invoices for 2023
        time_entries_2023 = [
            entry for entry in cross_year_time_entries
            if entry.start_time >= year_2023_start and entry.start_time <= year_2023_end
        ]
        
        expenses_2023 = [
            expense for expense in cross_year_expenses
            if expense.date >= year_2023_start and expense.date <= year_2023_end
        ]
        
        invoices_2023 = [
            invoice for invoice in cross_year_invoices
            if invoice.issue_date >= year_2023_start and invoice.issue_date <= year_2023_end
        ]
        
        # Analyze 2022 portion
        result_2022 = profiler.analyze_project_profitability(
            project=cross_year_project,
            time_entries=time_entries_2022,
            transactions=expenses_2022,
            invoices=invoices_2022
        )
        
        # Analyze 2023 portion
        result_2023 = profiler.analyze_project_profitability(
            project=cross_year_project,
            time_entries=time_entries_2023,
            transactions=expenses_2023,
            invoices=invoices_2023
        )
        
        # Create income transactions from invoices
        income_transactions = []
        for invoice in cross_year_invoices:
            if invoice.payment_date:
                income_tx = Transaction(
                    id=uuid.uuid4(),
                    date=invoice.payment_date,
                    amount=invoice.amount,
                    description=f"Payment for invoice {invoice.id}",
                    transaction_type=TransactionType.INCOME,
                    account_id="checking123",
                    client_id=invoice.client_id,
                    project_id=invoice.project_id,
                )
                income_transactions.append(income_tx)
        
        # Calculate tax implications for each year
        # For 2022
        income_2022 = sum(tx.amount for tx in income_transactions 
                         if tx.date.year == 2022)
        expenses_2022 = result_2022.total_expenses
        taxable_income_2022 = income_2022 - expenses_2022
        
        tax_2022 = tax_manager.calculate_tax_liability(
            income=taxable_income_2022,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # For 2023
        income_2023 = sum(tx.amount for tx in income_transactions 
                         if tx.date.year == 2023)
        expenses_2023 = result_2023.total_expenses
        taxable_income_2023 = income_2023 - expenses_2023
        
        tax_2023 = tax_manager.calculate_tax_liability(
            income=taxable_income_2023,
            tax_year=2023,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Verify tax calculations
        assert tax_2022.total_tax >= 0
        assert tax_2023.total_tax >= 0
        
        # Create tax planning scenarios
        # Scenario: What if all invoices were paid in 2022?
        all_income_2022 = sum(invoice.amount for invoice in cross_year_invoices)
        all_taxable_2022 = all_income_2022 - expenses_2022
        
        tax_scenario_1 = tax_manager.calculate_tax_liability(
            income=all_taxable_2022,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Scenario: What if all invoices were paid in 2023?
        all_income_2023 = sum(invoice.amount for invoice in cross_year_invoices)
        all_taxable_2023 = all_income_2023 - expenses_2023
        
        tax_scenario_2 = tax_manager.calculate_tax_liability(
            income=all_taxable_2023,
            tax_year=2023,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Scenario: What if expenses were evenly distributed?
        total_expenses = result_2022.total_expenses + result_2023.total_expenses
        even_expenses = total_expenses / 2
        
        even_taxable_2022 = income_2022 - even_expenses
        even_taxable_2023 = income_2023 - even_expenses
        
        tax_scenario_3_2022 = tax_manager.calculate_tax_liability(
            income=even_taxable_2022,
            tax_year=2022,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        tax_scenario_3_2023 = tax_manager.calculate_tax_liability(
            income=even_taxable_2023,
            tax_year=2023,
            jurisdiction=TaxJurisdiction.FEDERAL
        )
        
        # Compare tax implications of different scenarios
        actual_total_tax = tax_2022.total_tax + tax_2023.total_tax
        scenario_1_tax = tax_scenario_1.total_tax
        scenario_2_tax = tax_scenario_2.total_tax
        scenario_3_tax = tax_scenario_3_2022.total_tax + tax_scenario_3_2023.total_tax
        
        # Determine which scenario results in lowest tax
        tax_scenarios = {
            "Actual split": actual_total_tax,
            "All income in 2022": scenario_1_tax,
            "All income in 2023": scenario_2_tax,
            "Even expense distribution": scenario_3_tax,
        }
        
        min_tax_scenario = min(tax_scenarios.items(), key=lambda x: x[1])
        
        # Verify we can calculate the optimal tax strategy
        assert min_tax_scenario[0] in tax_scenarios
        assert min_tax_scenario[1] <= actual_total_tax

    def test_cross_year_project_cash_flow(
        self, cross_year_project, cross_year_time_entries, cross_year_expenses, cross_year_invoices
    ):
        """Test cash flow analysis for a project spanning multiple tax years."""
        # Calculate monthly cash flow
        monthly_cash_flow = {}
        
        # Process invoices (income)
        for invoice in cross_year_invoices:
            if invoice.payment_date:
                year_month = (invoice.payment_date.year, invoice.payment_date.month)
                if year_month not in monthly_cash_flow:
                    monthly_cash_flow[year_month] = {"income": 0, "expenses": 0, "net": 0}
                
                monthly_cash_flow[year_month]["income"] += invoice.amount
        
        # Process expenses
        for expense in cross_year_expenses:
            year_month = (expense.date.year, expense.date.month)
            if year_month not in monthly_cash_flow:
                monthly_cash_flow[year_month] = {"income": 0, "expenses": 0, "net": 0}
            
            monthly_cash_flow[year_month]["expenses"] += expense.amount
        
        # Calculate net cash flow
        for year_month in monthly_cash_flow:
            monthly_cash_flow[year_month]["net"] = (
                monthly_cash_flow[year_month]["income"] - 
                monthly_cash_flow[year_month]["expenses"]
            )
        
        # Verify cash flow for each month
        for year_month, flow in monthly_cash_flow.items():
            year, month = year_month
            # Net can be positive or negative depending on timing of income/expenses
            assert flow["income"] >= 0
            assert flow["expenses"] >= 0
        
        # Calculate cumulative cash flow
        sorted_months = sorted(monthly_cash_flow.keys())
        cumulative_cash_flow = {}
        
        running_total = 0
        for year_month in sorted_months:
            running_total += monthly_cash_flow[year_month]["net"]
            cumulative_cash_flow[year_month] = running_total
        
        # Verify the project is ultimately profitable
        last_month = sorted_months[-1]
        assert cumulative_cash_flow[last_month] > 0
        
        # Find months with negative cash flow
        negative_cash_flow_months = [
            year_month for year_month in sorted_months
            if monthly_cash_flow[year_month]["net"] < 0
        ]
        
        # Create cash flow analysis
        cash_flow_data = []
        for year_month in sorted_months:
            year, month = year_month
            date_str = f"{year}-{month:02d}"
            cash_flow_data.append({
                "date": date_str,
                "income": monthly_cash_flow[year_month]["income"],
                "expenses": monthly_cash_flow[year_month]["expenses"],
                "net": monthly_cash_flow[year_month]["net"],
                "cumulative": cumulative_cash_flow[year_month],
            })
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(cash_flow_data)
        
        # Verify total project profit matches expected
        total_income = df["income"].sum()
        total_expenses = df["expenses"].sum()
        total_profit = total_income - total_expenses
        
        expected_income = sum(invoice.amount for invoice in cross_year_invoices 
                             if invoice.payment_date)
        expected_expenses = sum(expense.amount for expense in cross_year_expenses)
        expected_profit = expected_income - expected_expenses
        
        assert abs(total_income - expected_income) < 0.01
        assert abs(total_expenses - expected_expenses) < 0.01
        assert abs(total_profit - expected_profit) < 0.01
        
        # Verify final cumulative cash flow matches profit
        assert abs(df["cumulative"].iloc[-1] - total_profit) < 0.01

    def test_project_spanning_three_tax_years(self):
        """Test handling of a project spanning three tax years."""
        # Create a three-year project
        long_project = Project(
            id="three_year_project",
            name="Enterprise System Overhaul",
            client_id="major_client",
            start_date=datetime(2021, 8, 1),
            end_date=datetime(2023, 7, 31),
            status="completed",
            hourly_rate=110.0,
            estimated_hours=1200.0,
        )
        
        # Create quarterly invoices over three years
        invoices = []
        expenses = []
        
        # Define quarterly schedule
        quarters = [
            # Year 1 (2021)
            {"year": 2021, "quarter": 3, "invoice_pct": 0.10, "expense_pct": 0.08},
            {"year": 2021, "quarter": 4, "invoice_pct": 0.10, "expense_pct": 0.12},
            # Year 2 (2022)
            {"year": 2022, "quarter": 1, "invoice_pct": 0.15, "expense_pct": 0.15},
            {"year": 2022, "quarter": 2, "invoice_pct": 0.15, "expense_pct": 0.15},
            {"year": 2022, "quarter": 3, "invoice_pct": 0.15, "expense_pct": 0.15},
            {"year": 2022, "quarter": 4, "invoice_pct": 0.15, "expense_pct": 0.15},
            # Year 3 (2023)
            {"year": 2023, "quarter": 1, "invoice_pct": 0.10, "expense_pct": 0.10},
            {"year": 2023, "quarter": 2, "invoice_pct": 0.10, "expense_pct": 0.10},
        ]
        
        # Total project value and expenses
        total_value = long_project.hourly_rate * long_project.estimated_hours
        total_expenses = total_value * 0.3  # 30% of project value is expenses
        
        # Create invoices and expenses for each quarter
        for i, quarter in enumerate(quarters):
            # Define dates for this quarter
            quarter_month = (quarter["quarter"] - 1) * 3 + 2  # Middle month of quarter
            invoice_date = datetime(quarter["year"], quarter_month, 15)
            payment_date = invoice_date + timedelta(days=15)
            
            # Create invoice
            invoice_amount = total_value * quarter["invoice_pct"]
            invoice = Invoice(
                id=f"inv-{long_project.id}-{i+1}",
                client_id=long_project.client_id,
                project_id=long_project.id,
                issue_date=invoice_date,
                due_date=invoice_date + timedelta(days=30),
                amount=invoice_amount,
                status="paid",
                payment_date=payment_date,
                description=f"Q{quarter['quarter']} {quarter['year']} progress payment",
                line_items=[{"description": f"Project milestone {i+1}", "amount": invoice_amount}],
            )
            invoices.append(invoice)
            
            # Create expense
            expense_amount = total_expenses * quarter["expense_pct"]
            expense = Transaction(
                id=uuid.uuid4(),
                date=invoice_date - timedelta(days=15),  # Expense before invoice
                amount=expense_amount,
                description=f"Q{quarter['quarter']} {quarter['year']} project expenses",
                transaction_type=TransactionType.EXPENSE,
                account_id="checking123",
                category=ExpenseCategory.BUSINESS_SUPPLIES,
                business_use_percentage=100.0,
                project_id=long_project.id,
            )
            expenses.append(expense)
        
        # Set up project profiler
        profiler = ProjectProfiler()
        tax_manager = TaxManager(FilingStatus.SINGLE)
        tax_manager.load_default_brackets()
        
        # Create simple time entries (minimal for test)
        time_entries = []
        
        # Analyze project by each tax year
        tax_years = [2021, 2022, 2023]
        year_results = {}
        
        for year in tax_years:
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            
            # Filter data for this year
            year_invoices = [inv for inv in invoices if year_start <= inv.issue_date <= year_end]
            year_expenses = [exp for exp in expenses if year_start <= exp.date <= year_end]
            
            # Analyze this year's portion
            result = profiler.analyze_project_profitability(
                project=long_project,
                time_entries=time_entries,  # Using empty time entries for simplicity
                transactions=year_expenses,
                invoices=year_invoices
            )
            
            if result:
                year_results[year] = {
                    "revenue": result.total_revenue,
                    "expenses": result.total_expenses,
                    "profit": result.total_profit,
                }
        
        # Calculate tax impact for each year
        year_tax_impact = {}
        for year in tax_years:
            if year in year_results:
                # Calculate tax for this year's project portion
                taxable_income = year_results[year]["revenue"] - year_results[year]["expenses"]
                
                tax_calculation = tax_manager.calculate_tax_liability(
                    income=taxable_income,
                    tax_year=year,
                    jurisdiction=TaxJurisdiction.FEDERAL
                )
                
                year_tax_impact[year] = {
                    "taxable_income": taxable_income,
                    "tax": tax_calculation.total_tax,
                    "effective_rate": tax_calculation.effective_rate,
                }
        
        # Verify we have results for each year
        for year in tax_years:
            if year in year_results:
                assert year_results[year]["revenue"] >= 0
                assert year_results[year]["expenses"] >= 0
                
                # Middle year (2022) should have most activity
                if year == 2022:
                    assert year_results[2022]["revenue"] > year_results[2021]["revenue"]
                    if 2023 in year_results:
                        assert year_results[2022]["revenue"] > year_results[2023]["revenue"]
        
        # Verify tax impact
        for year in tax_years:
            if year in year_tax_impact:
                assert year_tax_impact[year]["tax"] >= 0
                assert 0 <= year_tax_impact[year]["effective_rate"] <= 0.5  # Reasonable rate range
        
        # Verify total project financials match expectations
        total_reported_revenue = sum(yr["revenue"] for yr in year_results.values())
        total_reported_expenses = sum(yr["expenses"] for yr in year_results.values())
        total_reported_profit = sum(yr["profit"] for yr in year_results.values())
        
        expected_revenue = sum(invoice.amount for invoice in invoices if invoice.status == "paid")
        expected_expenses = sum(expense.amount for expense in expenses)
        expected_profit = expected_revenue - expected_expenses
        
        # Values should match within small rounding errors
        assert abs(total_reported_revenue - expected_revenue) < 0.01
        assert abs(total_reported_expenses - expected_expenses) < 0.01
        assert abs(total_reported_profit - expected_profit) < 0.01