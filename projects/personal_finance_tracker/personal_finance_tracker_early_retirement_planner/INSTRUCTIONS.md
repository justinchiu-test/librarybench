# Financial Independence Planning System

A personal finance tracker specialized for early retirement planning, with tools for analyzing savings rates, simulating withdrawal strategies, and optimizing for financial independence.

## Overview

This library provides a comprehensive financial planning system designed specifically for individuals pursuing financial independence and early retirement (FIRE). It focuses on savings rate analysis, withdrawal simulations, geographic cost optimization, tax-efficient withdrawal sequencing, and financial independence projections.

## Persona Description

Dr. Chen is pursuing financial independence and early retirement (FIRE) through aggressive saving and investing. He needs detailed projections of passive income, withdrawal strategies, and portfolio longevity to plan his transition from working life.

## Key Requirements

1. **Savings rate analysis showing percentage of income preserved and path to independence**
   - Calculation of savings rate as percentage of gross and net income
   - Projection of time to financial independence based on savings rate and investment returns
   - Historical tracking of savings rate over time with trend analysis
   - This feature is critical as savings rate is the primary determinant of time to financial independence in the FIRE community

2. **Safe withdrawal rate simulations based on different market performance scenarios**
   - Implementation of various withdrawal methodologies (fixed percentage, variable percentage, floor-ceiling)
   - Monte Carlo simulations of portfolio longevity under different market conditions
   - Sequence of returns risk analysis
   - This feature helps users determine sustainable withdrawal rates that balance maximizing income with minimizing portfolio failure risk

3. **Geographic arbitrage comparisons of living costs in different retirement locations**
   - Cost of living database for different locations
   - Comparative analysis of expenses across potential retirement destinations
   - Adjustment of withdrawal needs based on location choice
   - This feature enables optimization of retirement funds through strategic location selection, a common FIRE strategy

4. **Tax-optimized withdrawal sequencing across different account types (401k, IRA, taxable)**
   - Modeling of optimal withdrawal order from different account types
   - Tax-loss harvesting simulation for taxable accounts
   - Roth conversion strategy planning during early retirement years
   - This feature maximizes after-tax income by strategically determining which accounts to draw from at different stages

5. **Coast FIRE calculator showing when investments could grow to support retirement without additional contributions**
   - Calculation of "Coast FIRE" numbers based on current investments and target retirement age
   - Partial financial independence milestones
   - Work reduction scenario planning
   - This feature helps users understand when they've reached the point where investments alone, without additional contributions, can grow to support retirement

## Technical Requirements

### Testability Requirements
- All financial calculation algorithms must have 100% test coverage
- Monte Carlo simulations must be seedable for deterministic testing
- Time-based projections must support injectable time providers
- Sensitivity analysis must verify calculations across a range of input parameters

### Performance Expectations
- Monte Carlo simulations (1000+ runs) should complete in under 10 seconds
- Tax optimization calculations should evaluate 20+ withdrawal strategies in under 5 seconds
- Geographic comparison analysis should support 50+ locations
- System should remain responsive with 30+ year projection periods

### Integration Points
- Import capabilities for existing portfolio and account information
- Export functionality for retirement plans and projections
- Cost of living data integration for geographic comparisons
- Tax rate information for different jurisdictions

### Key Constraints
- All calculations must be transparent and explainable to users
- Projection assumptions must be configurable
- No dependency on proprietary financial data services
- Clear separation between actual data and projections

## Core Functionality

The system must provide these core components:

1. **Financial Independence Projection Engine**:
   - Savings rate calculation and tracking
   - Investment growth modeling
   - FI target determination based on expenses
   - Milestone tracking with progress indicators

2. **Withdrawal Strategy Simulator**:
   - Multiple withdrawal methodologies implementation
   - Monte Carlo simulation of portfolio outcomes
   - Sequence-of-returns risk analysis
   - Success probability calculation

3. **Geographic Optimization Tools**:
   - Cost of living comparisons across locations
   - Expense adjustment based on location
   - Purchasing power analysis
   - Location ranking based on financial metrics

4. **Tax Optimization System**:
   - Multi-account withdrawal sequencing
   - Tax bracket optimization
   - Roth conversion strategy planning
   - Required minimum distribution handling

5. **Partial Independence Calculator**:
   - Coast FIRE milestone determination
   - Barista FIRE scenario planning
   - Semi-retirement funding analysis
   - Work reduction timeline projection

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of financial independence projections across various savings rates
- Statistical validity of Monte Carlo simulations for withdrawal strategies
- Correct cost adjustments for geographic arbitrage calculations
- Optimal account withdrawal sequencing for tax efficiency
- Accurate calculation of Coast FIRE numbers for different target ages

### Critical User Scenarios
- Setting up a financial independence plan with current portfolio and savings data
- Running withdrawal strategy simulations to determine safe withdrawal rates
- Comparing potential retirement locations based on cost of living impact
- Developing a tax-efficient withdrawal plan across multiple account types
- Calculating Coast FIRE milestones and partial independence points

### Performance Benchmarks
- Run 1000 monte carlo simulations in under 10 seconds
- Generate 40-year withdrawal projections in under 3 seconds
- Compare 50+ geographic locations in under 2 seconds
- Optimize tax strategies across 5+ account types in under 5 seconds

### Edge Cases and Error Conditions
- Portfolio survival with extreme market conditions
- Handling of partial retirement transitions
- Tax calculation with changing future tax codes
- Adjustment for irregular expenses in retirement
- Handling of multi-currency scenarios for international retirement

### Required Test Coverage Metrics
- 100% code coverage for all financial calculation algorithms
- Comprehensive verification against established FIRE calculations
- Historical backtesting using actual market performance data
- Performance testing for all computationally intensive operations

## Success Criteria

The implementation will be considered successful when:

1. Savings rate analysis accurately projects the time to financial independence based on different savings and return assumptions
2. Safe withdrawal simulations provide statistically valid portfolio survival probabilities
3. Geographic arbitrage tools correctly adjust expenses based on cost of living differences
4. Tax optimization recommends withdrawal sequences that demonstrably minimize tax burden
5. Coast FIRE calculations accurately show when investments can grow to support retirement without additional contributions
6. All projections can be explained with transparent methodology and assumptions
7. The system handles 30+ year planning horizons with performance within specified benchmarks
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

The implementation should focus on creating robust financial algorithms that help users plan their path to financial independence with accurate projections and optimization tools.