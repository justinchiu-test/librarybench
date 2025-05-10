# Freelancer Financial Management System

A personal finance tracker optimized for professionals with irregular income patterns, focusing on cash flow management, project profitability, and tax planning.

## Overview

This library provides a financial management system specifically designed for freelancers and independent contractors with variable income streams. It focuses on income normalization, project-based financial analysis, tax planning, business/personal expense separation, and cash flow visualization.

## Persona Description

Jamal works as a freelance designer with irregular income patterns and project-based earnings. He needs to manage cash flow during lean periods, track business expenses for tax purposes, and ensure financial stability despite unpredictable revenue.

## Key Requirements

1. **Income smoothing calculations that normalize variable earnings for consistent budgeting**
   - Algorithms to calculate average monthly income based on irregular earnings history
   - Variance analysis showing deviation from baseline income
   - Seasonal pattern detection to account for predictable fluctuations in work volume
   - This feature is critical for freelancers to maintain stable monthly budgets despite highly variable income patterns

2. **Project profitability analysis comparing time invested against revenue generated**
   - Time tracking integration to record hours spent on client projects
   - Per-project revenue and expense tracking
   - Calculation of effective hourly rates across different clients and project types
   - This feature helps freelancers identify their most profitable work and optimize their project selection

3. **Tax obligation forecasting with quarterly estimated payment scheduling**
   - Self-employment tax calculation based on current and projected income
   - Quarterly tax payment scheduling and amount recommendations
   - Year-to-date income and tax tracking with projected year-end totals
   - This feature addresses the complex tax situation of freelancers who must manage their own tax withholding

4. **Business versus personal expense separation maintaining clear boundaries for deductions**
   - Dual-category system separating business and personal transactions
   - Tax deduction flagging for business expenses
   - Customizable expense categories aligned with tax schedule requirements
   - This feature ensures proper accounting for tax purposes while maintaining a complete picture of personal finances

5. **Cash runway visualization showing how long current funds will last at different spending levels**
   - Projection of account balances based on historical spending patterns
   - Scenario modeling with adjustable income and expense assumptions
   - Alert thresholds for low runway situations requiring spending adjustments
   - This feature helps freelancers manage the financial uncertainty of irregular income by visualizing their financial buffer

## Technical Requirements

### Testability Requirements
- All modules must have unit tests with ≥90% code coverage
- Time-based functions must support injectable time providers for deterministic testing
- Test data must represent realistic variable income patterns for proper algorithm verification
- Mocks for any external dependencies to ensure isolated testing

### Performance Expectations
- Income normalization algorithms must process 5+ years of transaction data in under 2 seconds
- Project profitability calculations should handle 50+ concurrent projects
- Tax forecasting should recalculate in real-time when transactions are added
- System should remain responsive with 10,000+ transactions

### Integration Points
- CSV/OFX import capabilities for bank and credit card transactions
- Export functionality for tax preparation software
- Time tracking integration for project profitability analysis
- Calendar integration for payment scheduling

### Key Constraints
- All calculations must be transparent and explainable
- No reliance on external services for core functionality
- Tax calculations must be configurable for different jurisdictions
- Personal financial data must remain private and secure

## Core Functionality

The system must provide these core components:

1. **Transaction Management**:
   - Multi-account transaction tracking
   - Business/personal categorization
   - Project and client tagging
   - Recurring transaction prediction

2. **Income Analysis and Smoothing**:
   - Variable income normalization algorithms
   - Seasonal adjustment capabilities
   - Historical pattern analysis
   - Income forecasting based on confirmed and prospective projects

3. **Project Financial Management**:
   - Per-project revenue and expense tracking
   - Time tracking and hourly rate calculation
   - Project profitability analysis
   - Client and project type performance comparison

4. **Tax Planning and Compliance**:
   - Self-employment tax calculation
   - Quarterly estimated payment scheduling
   - Deductible expense tracking
   - Tax category alignment with official schedules

5. **Cash Flow Management**:
   - Runway calculation and visualization
   - Scenario modeling with variable parameters
   - Buffer fund recommendations
   - Cash flow forecasting with confidence intervals

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of income smoothing algorithms with various income patterns
- Correct calculation of project profitability metrics
- Proper tax obligation estimates compared to reference calculations
- Accurate separation of business and personal expenses
- Cash runway projections under different scenarios

### Critical User Scenarios
- Setting up initial accounts and importing historical transaction data
- Recording and categorizing mixed business/personal transactions
- Analyzing the profitability of completed projects
- Estimating quarterly tax payments
- Evaluating financial stability during projected low-income periods

### Performance Benchmarks
- Process import of 1,000+ transactions in under 10 seconds
- Complete income normalization analysis in under 2 seconds for 5 years of data
- Recalculate tax obligations in under 1 second when transactions are modified
- Generate cash flow projections for 12 months in under 3 seconds

### Edge Cases and Error Conditions
- Handling extremely irregular income patterns with no clear seasonality
- Proper expense allocation for mixed-use items (partial business deductions)
- Graceful handling of retrospective project time tracking
- Recovery from incorrect business/personal categorization
- Handling of changed tax regulations affecting historical calculations

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of financial calculation algorithms
- Specific test cases for all supported tax jurisdictions
- Performance tests verifying speed with large datasets

## Success Criteria

The implementation will be considered successful when:

1. The income smoothing functionality accurately normalizes irregular earnings for reliable monthly budgeting
2. Project profitability analysis correctly calculates effective hourly rates and profit margins
3. Tax obligation forecasting provides estimates within 5% of actual tax obligations
4. Business and personal expenses are clearly separated with proper tax deduction categorization
5. Cash runway visualization accurately predicts financial buffer durations
6. All calculations are transparent and explainable to users
7. The system maintains responsiveness with 5+ years of freelance financial history
8. All tests pass with the required coverage and performance benchmarks

## Getting Started

To set up the development environment:

```bash
cd /path/to/project
uv init --lib
```

This will create a virtual environment and generate a `pyproject.toml` file. To install dependencies:

```bash
uv sync
```

To run individual Python scripts:

```bash
uv run python script.py
```

To run tests:

```bash
uv run pytest
```

The implementation should focus on creating a robust financial management system that addresses the unique challenges faced by freelancers with variable income.