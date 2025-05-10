# Fixed Income Financial Management System

A personal finance tracker designed specifically for retirees living on fixed income, focusing on essential expense prioritization, medical cost tracking, benefit monitoring, and strategic resource allocation.

## Overview

This library provides a specialized financial management system for retirees living on fixed income sources such as Social Security and pensions. It focuses on essential expense prioritization, medical cost tracking, benefit payment monitoring, strategic withdrawal planning, and age-specific tax benefit management.

## Persona Description

Mrs. Johnson lives on Social Security and pension income with limited financial flexibility. She needs to carefully track essential expenses, manage medical costs, and ensure her fixed income stretches through each month while planning for occasional large expenses.

## Key Requirements

1. **Fixed income allocation with priority-based spending categories for essentials**
   - Income stream categorization and scheduling
   - Essential expense prioritization system
   - Automatic allocation of incoming funds to expense categories
   - This feature is critical for seniors on fixed incomes to ensure essential needs are met first and funds are properly allocated throughout the month

2. **Medical expense tracking categorized by insurance coverage and tax deductibility**
   - Medical cost categorization by type and coverage
   - Insurance reimbursement tracking
   - Tax deductible medical expense identification
   - This feature helps retirees manage often substantial medical costs, maximize insurance benefits, and properly document expenses for tax purposes

3. **Benefit payment monitoring ensuring regular deposits arrive as scheduled**
   - Expected payment scheduling and verification
   - Deposit confirmation and variance alerting
   - Payment history tracking and pattern recognition
   - This feature provides peace of mind by ensuring critical income sources are received as expected and alerting to any irregularities

4. **Strategic withdrawal planning from limited savings for major expenses**
   - Large expense forecasting and categorization
   - Withdrawal timing optimization
   - Impact analysis on monthly cash flow
   - This feature helps retirees plan for significant expenses by determining optimal timing and amounts for withdrawals from limited savings

5. **Age-specific tax benefit tracking including standard deduction adjustments and tax credits**
   - Age-based tax benefit identification
   - Required minimum distribution tracking
   - Medical expense deduction threshold monitoring
   - This feature helps retirees take advantage of age-specific tax benefits and comply with requirements like retirement account distributions

## Technical Requirements

### Testability Requirements
- All financial calculation algorithms must have unit tests with 95% code coverage
- Test data representing realistic fixed income scenarios and expense patterns
- Verification of tax calculations against current tax rules for seniors
- Time-dependent functions must support injectable time for deterministic testing

### Performance Expectations
- Support for 10+ years of transaction history with responsive performance
- Budget calculations and updates in real-time as transactions are entered
- Fast generation of tax benefit reports and medical expense summaries
- System should maintain performance on older computer hardware

### Integration Points
- Bank statement import capabilities
- Medical expense documentation storage
- Tax preparation export functionality
- Optional calendar integration for payment scheduling

### Key Constraints
- Interface design must consider accessibility for older users
- Calculations must be transparent and explainable
- No reliance on external financial services for core functionality
- Clear separation between actual data and projections/forecasts

## Core Functionality

The system must provide these core components:

1. **Fixed Income Management**:
   - Income stream tracking with payment schedules
   - Benefit amount change monitoring
   - Income allocation to expense categories
   - Monthly cash flow analysis

2. **Expense Prioritization System**:
   - Essential vs. discretionary expense categorization
   - Priority-based budget allocation
   - Expense timing optimization
   - Flexible category adjustment when income changes

3. **Medical Finance Tracking**:
   - Medical expense categorization and documentation
   - Insurance coverage and reimbursement tracking
   - Out-of-pocket cost analysis
   - Tax deduction qualification assessment

4. **Benefit Monitoring Tools**:
   - Payment schedule tracking and verification
   - Deposit confirmation and variance detection
   - History tracking and pattern analysis
   - Notification system for irregular payments

5. **Senior Financial Planning**:
   - Major expense preparation and timing
   - Limited savings optimization
   - Age-specific tax benefit identification
   - Required minimum distribution calculation

## Testing Requirements

### Key Functionalities to Verify
- Accurate allocation of fixed income to prioritized expense categories
- Correct categorization and tracking of medical expenses by insurance coverage
- Proper detection of missed or delayed benefit payments
- Optimal withdrawal planning for major expenses
- Accurate identification of applicable age-specific tax benefits

### Critical User Scenarios
- Setting up fixed income sources with payment schedules
- Allocating monthly income to prioritized expense categories
- Tracking medical expenses and insurance reimbursements
- Monitoring benefit payments and detecting irregularities
- Planning for a major expense requiring savings withdrawal

### Performance Benchmarks
- Process 5 years of fixed income and expense data in under 3 seconds
- Generate medical expense reports for tax purposes in under 2 seconds
- Calculate optimal withdrawal strategies for major expenses in under 3 seconds
- Maintain responsive performance with 10,000+ transactions

### Edge Cases and Error Conditions
- Handling of irregular or missed benefit payments
- Proper management of medical expenses spanning multiple tax years
- Recovery from incorrect expense categorization
- Dealing with benefit amount changes
- Handling one-time payments or adjustments (e.g., cost of living increases)

### Required Test Coverage Metrics
- 95% code coverage for all financial calculation algorithms
- Comprehensive tests for fixed income allocation methods
- Verification of medical expense tracking against reference examples
- Performance tests for operations on realistic senior financial datasets

## Success Criteria

The implementation will be considered successful when:

1. Fixed income sources are properly tracked and allocated to expenses by priority
2. Medical expenses are accurately categorized by insurance coverage and tax deductibility
3. Benefit payments are effectively monitored with alerts for missed or irregular deposits
4. Withdrawal strategies for major expenses are optimized to minimize impact on monthly finances
5. Age-specific tax benefits are properly identified and tracked
6. The system maintains performance with realistic retiree financial activity volume
7. All calculations are transparent and explainable
8. All tests pass with the required coverage and accuracy metrics

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

The implementation should focus on creating a reliable system that helps retirees on fixed incomes maximize their limited financial resources while ensuring essential needs are met and providing peace of mind through effective monitoring and planning tools.