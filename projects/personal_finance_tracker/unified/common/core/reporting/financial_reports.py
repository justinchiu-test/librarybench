"""Financial report generators shared across implementations."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union, Tuple

from common.core.reporting.report import (
    ReportGenerator,
    ReportParameters,
    ReportFormat,
    ReportPeriod,
    ReportSection,
    Report,
)
from common.core.analysis.time_series import TimeSeriesData
from common.core.analysis.portfolio import (
    PortfolioAnalysisResult,
    PortfolioPerformance,
    PortfolioESGMetrics,
)
from common.core.analysis.financial_projector import ProjectionResult, Projection


class TransactionSummaryGenerator(ReportGenerator):
    """
    Report generator for transaction summaries.
    
    Used for generating reports about financial transactions.
    """
    
    def generate(
        self, data: Dict[str, Any], parameters: ReportParameters
    ) -> Report:
        """
        Generate a transaction summary report.
        
        Args:
            data: Transaction data to include in the report
            parameters: Parameters to configure the report
            
        Returns:
            Transaction summary report
        """
        # Extract transactions and metadata
        transactions = data.get("transactions", [])
        categories = data.get("categories", {})
        date_range = (
            parameters.start_date or date.today(),
            parameters.end_date or date.today(),
        )
        
        # Create the report
        report = Report(
            title="Transaction Summary Report",
            description=f"Summary of transactions for the selected period",
            period=parameters.period,
            start_date=date_range[0],
            end_date=date_range[1],
            format=parameters.format,
            metadata={
                "transaction_count": len(transactions),
                "filters_applied": parameters.filters,
            },
        )
        
        # Generate overview section
        overview_section = self._generate_overview_section(transactions)
        report.sections.append(overview_section)
        
        # Generate category breakdown section
        if categories:
            category_section = self._generate_category_section(transactions, categories)
            report.sections.append(category_section)
        
        # Generate time analysis section
        time_section = self._generate_time_section(transactions, parameters.period)
        report.sections.append(time_section)
        
        return report
    
    def _generate_overview_section(self, transactions: List[Dict[str, Any]]) -> ReportSection:
        """
        Generate the overview section of the report.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Overview report section
        """
        # Calculate key metrics
        total_income = sum(
            t["amount"] for t in transactions if t.get("transaction_type") == "income"
        )
        total_expenses = sum(
            t["amount"] for t in transactions if t.get("transaction_type") == "expense"
        )
        net_cash_flow = total_income - total_expenses
        largest_transaction = max(transactions, key=lambda t: t["amount"], default={})
        
        # Create the section
        return ReportSection(
            title="Financial Overview",
            summary="Summary of key financial metrics for the period",
            data={
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_cash_flow": net_cash_flow,
                "transaction_count": len(transactions),
                "average_transaction": sum(t["amount"] for t in transactions) / len(transactions) if transactions else 0,
                "largest_transaction_amount": largest_transaction.get("amount", 0),
                "largest_transaction_description": largest_transaction.get("description", "N/A"),
            },
            charts=[
                {
                    "type": "pie",
                    "title": "Income vs Expenses",
                    "data": {
                        "Income": total_income,
                        "Expenses": total_expenses,
                    },
                },
            ],
        )
    
    def _generate_category_section(
        self, transactions: List[Dict[str, Any]], categories: Dict[str, Any]
    ) -> ReportSection:
        """
        Generate the category breakdown section of the report.
        
        Args:
            transactions: List of transactions
            categories: Category information
            
        Returns:
            Category breakdown report section
        """
        # Calculate spending by category
        spending_by_category = {}
        for transaction in transactions:
            if transaction.get("transaction_type") == "expense":
                category = transaction.get("category", "Uncategorized")
                if category not in spending_by_category:
                    spending_by_category[category] = 0
                spending_by_category[category] += transaction["amount"]
        
        # Sort categories by amount (descending)
        sorted_categories = sorted(
            spending_by_category.items(), key=lambda x: x[1], reverse=True
        )
        
        # Create subsections for top categories
        category_subsections = []
        for category, amount in sorted_categories[:5]:  # Top 5 categories
            category_data = categories.get(category, {})
            
            # Get transactions for this category
            category_transactions = [
                t for t in transactions
                if t.get("category") == category and t.get("transaction_type") == "expense"
            ]
            
            # Calculate metrics
            transaction_count = len(category_transactions)
            average_amount = amount / transaction_count if transaction_count > 0 else 0
            
            category_subsections.append(
                ReportSection(
                    title=f"{category}",
                    data={
                        "total_amount": amount,
                        "transaction_count": transaction_count,
                        "average_transaction": average_amount,
                        "percentage_of_expenses": amount / sum(spending_by_category.values()) if spending_by_category else 0,
                        "is_business": category_data.get("is_business", False),
                    },
                )
            )
        
        # Create the main category section
        return ReportSection(
            title="Expense Categories",
            summary="Breakdown of expenses by category",
            data={
                "top_category": sorted_categories[0][0] if sorted_categories else "None",
                "top_category_amount": sorted_categories[0][1] if sorted_categories else 0,
                "category_count": len(spending_by_category),
            },
            charts=[
                {
                    "type": "bar",
                    "title": "Expenses by Category",
                    "data": dict(sorted_categories),
                },
            ],
            subsections=category_subsections,
        )
    
    def _generate_time_section(
        self, transactions: List[Dict[str, Any]], period: ReportPeriod
    ) -> ReportSection:
        """
        Generate the time analysis section of the report.
        
        Args:
            transactions: List of transactions
            period: The report period
            
        Returns:
            Time analysis report section
        """
        # Group transactions by time period
        time_groups = {}
        for transaction in transactions:
            # Extract the date
            transaction_date = transaction.get("date")
            if not transaction_date:
                continue
                
            if isinstance(transaction_date, str):
                # Parse date string if needed
                try:
                    transaction_date = datetime.fromisoformat(transaction_date)
                except:
                    continue
            
            # Determine the time period key
            if period == ReportPeriod.DAILY:
                key = transaction_date.strftime("%Y-%m-%d")
            elif period == ReportPeriod.WEEKLY:
                # Use ISO week number
                key = f"{transaction_date.year}-W{transaction_date.isocalendar()[1]}"
            elif period == ReportPeriod.MONTHLY:
                key = transaction_date.strftime("%Y-%m")
            elif period == ReportPeriod.QUARTERLY:
                quarter = (transaction_date.month - 1) // 3 + 1
                key = f"{transaction_date.year}-Q{quarter}"
            elif period == ReportPeriod.YEARLY:
                key = str(transaction_date.year)
            else:
                # Default to daily
                key = transaction_date.strftime("%Y-%m-%d")
            
            # Add to the group
            if key not in time_groups:
                time_groups[key] = {
                    "income": 0,
                    "expenses": 0,
                    "count": 0,
                }
            
            # Update group metrics
            group = time_groups[key]
            group["count"] += 1
            
            if transaction.get("transaction_type") == "income":
                group["income"] += transaction["amount"]
            elif transaction.get("transaction_type") == "expense":
                group["expenses"] += transaction["amount"]
        
        # Calculate net cash flow for each period
        for key, group in time_groups.items():
            group["net_cash_flow"] = group["income"] - group["expenses"]
        
        # Sort groups by time period
        sorted_groups = sorted(time_groups.items())
        
        # Create chart data
        income_data = [(key, group["income"]) for key, group in sorted_groups]
        expense_data = [(key, group["expenses"]) for key, group in sorted_groups]
        net_data = [(key, group["net_cash_flow"]) for key, group in sorted_groups]
        
        # Create the section
        return ReportSection(
            title="Time Analysis",
            summary=f"Financial trends over {period.value} periods",
            data={
                "period_count": len(time_groups),
                "highest_income_period": max(sorted_groups, key=lambda x: x[1]["income"])[0] if sorted_groups else "None",
                "highest_expense_period": max(sorted_groups, key=lambda x: x[1]["expenses"])[0] if sorted_groups else "None",
                "average_period_income": sum(group["income"] for _, group in sorted_groups) / len(sorted_groups) if sorted_groups else 0,
                "average_period_expenses": sum(group["expenses"] for _, group in sorted_groups) / len(sorted_groups) if sorted_groups else 0,
            },
            charts=[
                {
                    "type": "line",
                    "title": "Income and Expenses Over Time",
                    "data": {
                        "Income": dict(income_data),
                        "Expenses": dict(expense_data),
                        "Net": dict(net_data),
                    },
                },
            ],
        )


class PortfolioReportGenerator(ReportGenerator):
    """
    Report generator for investment portfolios.
    
    Used for generating reports about portfolio composition and performance.
    """
    
    def generate(
        self, data: PortfolioAnalysisResult, parameters: ReportParameters
    ) -> Report:
        """
        Generate a portfolio analysis report.
        
        Args:
            data: Portfolio analysis data to include in the report
            parameters: Parameters to configure the report
            
        Returns:
            Portfolio analysis report
        """
        # Create the report
        report = Report(
            title="Portfolio Analysis Report",
            description="Analysis of investment portfolio composition, performance, and characteristics",
            period=parameters.period,
            start_date=parameters.start_date,
            end_date=parameters.end_date,
            format=parameters.format,
            metadata={
                "portfolio_id": data.subject_id,
                "analysis_date": data.analysis_date,
            },
        )
        
        # Generate composition section
        composition_section = self._generate_composition_section(data)
        report.sections.append(composition_section)
        
        # Generate performance section if available
        if data.performance:
            performance_section = self._generate_performance_section(data.performance)
            report.sections.append(performance_section)
        
        # Generate ESG metrics section if available
        if data.esg_metrics:
            esg_section = self._generate_esg_section(data.esg_metrics)
            report.sections.append(esg_section)
        
        # Generate recommendations section
        if data.recommendations:
            recommendation_section = ReportSection(
                title="Recommendations",
                summary="Suggested actions based on portfolio analysis",
                data={
                    "recommendation_count": len(data.recommendations),
                },
            )
            
            for i, recommendation in enumerate(data.recommendations, 1):
                recommendation_section.data[f"recommendation_{i}"] = recommendation
            
            report.sections.append(recommendation_section)
        
        return report
    
    def _generate_composition_section(
        self, data: PortfolioAnalysisResult
    ) -> ReportSection:
        """
        Generate the portfolio composition section of the report.
        
        Args:
            data: Portfolio analysis result
            
        Returns:
            Portfolio composition report section
        """
        # Extract breakdown data
        breakdown = data.breakdown
        
        # Create sector subsection
        sector_subsection = ReportSection(
            title="Sector Allocation",
            data=breakdown.by_sector,
            charts=[
                {
                    "type": "pie",
                    "title": "Allocation by Sector",
                    "data": breakdown.by_sector,
                },
            ],
        )
        
        # Create industry subsection
        industry_subsection = ReportSection(
            title="Industry Allocation",
            data=dict(
                sorted(breakdown.by_industry.items(), key=lambda x: x[1], reverse=True)[:10]
            ),  # Top 10 industries
            charts=[
                {
                    "type": "bar",
                    "title": "Top 10 Industries",
                    "data": dict(
                        sorted(breakdown.by_industry.items(), key=lambda x: x[1], reverse=True)[:10]
                    ),
                },
            ],
        )
        
        # Create market cap subsection
        market_cap_subsection = ReportSection(
            title="Market Cap Distribution",
            data=breakdown.by_market_cap,
            charts=[
                {
                    "type": "pie",
                    "title": "Allocation by Market Cap",
                    "data": breakdown.by_market_cap,
                },
            ],
        )
        
        # Create the main section
        return ReportSection(
            title="Portfolio Composition",
            summary="Analysis of portfolio allocations and diversification",
            data={
                "diversification_score": data.diversification_score,
                "top_sector": max(breakdown.by_sector.items(), key=lambda x: x[1])[0] if breakdown.by_sector else "None",
                "top_sector_allocation": max(breakdown.by_sector.items(), key=lambda x: x[1])[1] if breakdown.by_sector else 0,
                "sector_count": len(breakdown.by_sector),
                "industry_count": len(breakdown.by_industry),
                "concentration_index": breakdown.concentration_metrics.get("herfindahl_index", 0),
            },
            subsections=[
                sector_subsection,
                industry_subsection,
                market_cap_subsection,
            ],
        )
    
    def _generate_performance_section(
        self, performance: PortfolioPerformance
    ) -> ReportSection:
        """
        Generate the portfolio performance section of the report.
        
        Args:
            performance: Portfolio performance data
            
        Returns:
            Portfolio performance report section
        """
        return ReportSection(
            title="Performance Metrics",
            summary="Analysis of portfolio returns and risk-adjusted performance",
            data={
                "total_return": performance.total_return,
                "annualized_return": performance.annualized_return,
                "volatility": performance.volatility,
                "sharpe_ratio": performance.sharpe_ratio,
                "max_drawdown": performance.max_drawdown,
                "alpha": performance.alpha,
                "beta": performance.beta,
            },
            charts=[
                {
                    "type": "bar",
                    "title": "Performance Metrics",
                    "data": {
                        "Total Return": performance.total_return * 100,
                        "Volatility": performance.volatility * 100,
                        "Max Drawdown": performance.max_drawdown * 100,
                    },
                },
            ],
        )
    
    def _generate_esg_section(
        self, esg_metrics: PortfolioESGMetrics
    ) -> ReportSection:
        """
        Generate the ESG metrics section of the report.
        
        Args:
            esg_metrics: Portfolio ESG metrics data
            
        Returns:
            ESG metrics report section
        """
        # Create subsections for E, S, G components
        environmental_subsection = ReportSection(
            title="Environmental Metrics",
            data={
                "score": esg_metrics.environmental_score,
                "carbon_footprint": esg_metrics.carbon_footprint,
                "renewable_energy_exposure": esg_metrics.renewable_energy_exposure,
            },
        )
        
        social_subsection = ReportSection(
            title="Social Metrics",
            data={
                "score": esg_metrics.social_score,
                "diversity_score": esg_metrics.diversity_score,
            },
        )
        
        governance_subsection = ReportSection(
            title="Governance Metrics",
            data={
                "score": esg_metrics.governance_score,
            },
        )
        
        # Create the main section
        return ReportSection(
            title="ESG Profile",
            summary="Environmental, Social, and Governance characteristics of the portfolio",
            data={
                "overall_esg_score": esg_metrics.overall_esg_score,
                "controversy_exposure": esg_metrics.controversy_exposure,
            },
            charts=[
                {
                    "type": "radar",
                    "title": "ESG Component Scores",
                    "data": {
                        "Environmental": esg_metrics.environmental_score,
                        "Social": esg_metrics.social_score,
                        "Governance": esg_metrics.governance_score,
                    },
                },
            ],
            subsections=[
                environmental_subsection,
                social_subsection,
                governance_subsection,
            ],
        )


class ProjectionReportGenerator(ReportGenerator):
    """
    Report generator for financial projections.
    
    Used for generating reports about projected financial states.
    """
    
    def generate(
        self, data: ProjectionResult, parameters: ReportParameters
    ) -> Report:
        """
        Generate a financial projection report.
        
        Args:
            data: Projection data to include in the report
            parameters: Parameters to configure the report
            
        Returns:
            Financial projection report
        """
        # Create the report
        report = Report(
            title="Financial Projection Report",
            description="Projected financial states across different scenarios",
            period=parameters.period,
            start_date=data.baseline.start_date,
            end_date=data.baseline.end_date,
            format=parameters.format,
            metadata={
                "analysis_date": data.analysis_date,
                "projection_length": len(data.baseline.cash_flows),
            },
        )
        
        # Generate summary section
        summary_section = self._generate_summary_section(data)
        report.sections.append(summary_section)
        
        # Generate scenario sections
        baseline_section = self._generate_scenario_section(
            data.baseline, "Baseline Scenario"
        )
        report.sections.append(baseline_section)
        
        if data.optimistic:
            optimistic_section = self._generate_scenario_section(
                data.optimistic, "Optimistic Scenario"
            )
            report.sections.append(optimistic_section)
        
        if data.conservative:
            conservative_section = self._generate_scenario_section(
                data.conservative, "Conservative Scenario"
            )
            report.sections.append(conservative_section)
        
        if data.stress_test:
            stress_section = self._generate_scenario_section(
                data.stress_test, "Stress Test Scenario"
            )
            report.sections.append(stress_section)
        
        # Generate recommendations section
        if data.recommended_actions:
            recommendation_section = ReportSection(
                title="Recommended Actions",
                summary="Suggested financial actions based on projections",
                data={
                    "recommendation_count": len(data.recommended_actions),
                },
            )
            
            for i, recommendation in enumerate(data.recommended_actions, 1):
                recommendation_section.data[f"recommendation_{i}"] = recommendation
            
            report.sections.append(recommendation_section)
        
        return report
    
    def _generate_summary_section(self, data: ProjectionResult) -> ReportSection:
        """
        Generate the summary section of the report.
        
        Args:
            data: Projection result data
            
        Returns:
            Summary report section
        """
        # Compare scenarios
        scenarios = {
            "Baseline": data.baseline,
            "Optimistic": data.optimistic,
            "Conservative": data.conservative,
            "Stress Test": data.stress_test,
        }
        
        # Filter out None scenarios
        scenarios = {k: v for k, v in scenarios.items() if v is not None}
        
        # Calculate scenario comparison data
        comparison_data = {}
        for name, scenario in scenarios.items():
            comparison_data[f"{name}_final_balance"] = scenario.final_balance
            comparison_data[f"{name}_lowest_balance"] = scenario.lowest_balance
            
            if scenario.runway_months is not None:
                comparison_data[f"{name}_runway"] = (
                    f"{scenario.runway_months:.1f} months"
                    if scenario.runway_months < float('inf')
                    else "Sustainable"
                )
            else:
                comparison_data[f"{name}_runway"] = "N/A"
        
        # Create chart data for final balances
        final_balances = {
            name: scenario.final_balance
            for name, scenario in scenarios.items()
        }
        
        return ReportSection(
            title="Projection Summary",
            summary="Comparison of different financial scenarios",
            data={
                "starting_balance": data.baseline.starting_balance,
                "projection_period": f"{len(data.baseline.cash_flows)} months",
                "baseline_final_balance": data.baseline.final_balance,
                "baseline_runway": (
                    f"{data.baseline.runway_months:.1f} months"
                    if data.baseline.runway_months and data.baseline.runway_months < float('inf')
                    else "Sustainable"
                ),
                "emergency_fund_status": data.baseline.emergency_fund_status,
                **comparison_data,
            },
            charts=[
                {
                    "type": "bar",
                    "title": "Final Balance by Scenario",
                    "data": final_balances,
                },
            ],
        )
    
    def _generate_scenario_section(
        self, projection: Projection, title: str
    ) -> ReportSection:
        """
        Generate a section for a specific projection scenario.
        
        Args:
            projection: Projection data for the scenario
            title: Section title
            
        Returns:
            Scenario report section
        """
        # Create cash flow subsection
        cash_flow_data = {}
        for i, cf in enumerate(projection.cash_flows[:12]):  # Limit to first 12 periods
            month_name = cf.date.strftime("%b %Y")
            cash_flow_data[f"{month_name}_income"] = cf.income
            cash_flow_data[f"{month_name}_expenses"] = cf.expenses
            cash_flow_data[f"{month_name}_net"] = cf.net
            cash_flow_data[f"{month_name}_balance"] = cf.cumulative
        
        cash_flow_section = ReportSection(
            title="Cash Flow Projection",
            data=cash_flow_data,
            charts=[
                {
                    "type": "line",
                    "title": "Projected Cash Flow",
                    "data": {
                        "Income": {cf.date.strftime("%b %Y"): cf.income for cf in projection.cash_flows[:12]},
                        "Expenses": {cf.date.strftime("%b %Y"): cf.expenses for cf in projection.cash_flows[:12]},
                        "Net": {cf.date.strftime("%b %Y"): cf.net for cf in projection.cash_flows[:12]},
                    },
                },
                {
                    "type": "line",
                    "title": "Projected Balance",
                    "data": {
                        "Balance": {cf.date.strftime("%b %Y"): cf.cumulative for cf in projection.cash_flows[:12]},
                    },
                },
            ],
        )
        
        # Create tax subsection if available
        tax_section = None
        if projection.tax_liability:
            tax_data = {}
            for year, amount in projection.tax_liability.get("yearly", {}).items():
                tax_data[f"year_{year}"] = amount
            
            tax_section = ReportSection(
                title="Tax Projection",
                data={
                    "total_tax_liability": projection.tax_liability.get("total", 0),
                    "average_monthly_tax": projection.tax_liability.get("avg_monthly", 0),
                    "effective_tax_rate": projection.tax_liability.get("effective_rate", 0),
                    **tax_data,
                },
            )
        
        # Create the main section
        subsections = [cash_flow_section]
        if tax_section:
            subsections.append(tax_section)
        
        return ReportSection(
            title=title,
            summary=f"Financial projection under {projection.scenario.value} conditions",
            data={
                "starting_balance": projection.starting_balance,
                "final_balance": projection.final_balance,
                "lowest_balance": projection.lowest_balance,
                "highest_balance": projection.highest_balance,
                "runway_months": (
                    f"{projection.runway_months:.1f}"
                    if projection.runway_months and projection.runway_months < float('inf')
                    else "Sustainable"
                ),
                "emergency_fund_status": projection.emergency_fund_status,
                "confidence_level": projection.confidence_level,
            },
            subsections=subsections,
        )