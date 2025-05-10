# Multi-Currency International Finance Manager

A personal finance tracker designed for professionals who work across international borders, handling multiple currencies, tax jurisdictions, and international financial complexities.

## Overview

This library provides a specialized financial management system for individuals who work internationally and need to track financial activities across multiple countries and currencies. It focuses on currency management, international tax compliance, foreign account reporting, cost-of-living adjustments, and optimizing international money transfers.

## Persona Description

Priya works internationally and deals with multiple currencies, international tax obligations, and financial accounts in different countries. She needs to track assets and liabilities across national boundaries while optimizing for complex international tax situations.

## Key Requirements

1. **Multi-currency support with historical exchange rate tracking and conversion**
   - Storage and management of transactions in their original currencies
   - Historical exchange rate data for accurate point-in-time conversions
   - Base currency reporting with appropriate conversion methodology
   - This feature is essential for maintaining accurate financial records when regularly dealing with multiple currencies, ensuring transactions retain their original value and context

2. **Country-specific tax rule application for different income streams**
   - Tax residency tracking across multiple jurisdictions
   - Income source categorization by country
   - Application of relevant tax treaties and agreements
   - This feature helps international professionals properly categorize income for tax purposes in multiple countries, reducing the risk of non-compliance or double taxation

3. **Foreign account reporting compliance for tax requirements like FBAR or FATCA**
   - Tracking of foreign financial accounts and maximum balances
   - Automated identification of reportable accounts
   - Documentation generation for compliance requirements
   - This feature addresses the significant compliance burden faced by international professionals who must report foreign accounts to tax authorities

4. **International cost-of-living adjustments when moving between assignments**
   - Location-based expense categorization and benchmarking
   - Purchasing power comparison across regions
   - Budget adjustment recommendations during transitions
   - This feature helps users maintain appropriate budgets as they move between locations with vastly different costs for essential expenses

5. **Remittance optimization identifying the most cost-effective ways to move money internationally**
   - Transfer method comparison (bank transfers, specialized services)
   - Fee and exchange rate margin analysis
   - Timing recommendations based on currency trends
   - This feature helps minimize the often substantial costs associated with moving money across international borders

## Technical Requirements

### Testability Requirements
- All currency conversion algorithms must have unit tests with 100% code coverage
- Tax calculation tests must cover multiple jurisdictions and scenarios
- Mock exchange rate services for deterministic testing
- Test data representing diverse international financial situations

### Performance Expectations
- Support for transactions in 20+ currencies simultaneously
- Currency conversions for 1000+ transactions in under 2 seconds
- Tax calculations across 5+ jurisdictions in reasonable time
- System should remain responsive with 10+ years of international transaction history

### Integration Points
- Historical exchange rate data source
- Country-specific tax rule database
- Banking and financial institution data import
- Optional integration with international transfer services

### Key Constraints
- Precise currency handling with appropriate decimal precision
- Clear audit trail for all currency conversions
- Proper handling of exchange rate fluctuations in reports
- Compliance with relevant financial regulations in multiple jurisdictions

## Core Functionality

The system must provide these core components:

1. **Multi-Currency Transaction Management**:
   - Original currency transaction recording
   - Configurable base currency for reporting
   - Historical exchange rate tracking
   - Currency gain/loss calculation

2. **International Tax Management**:
   - Tax residency period tracking
   - Income source categorization by country
   - Tax treaty application
   - Foreign tax credit calculation

3. **Compliance Reporting Tools**:
   - Foreign account balance tracking
   - Reportable account identification
   - FBAR/FATCA threshold monitoring
   - Documentation generation

4. **Location Transition Management**:
   - Cost-of-living database by location
   - Expense category benchmarking
   - Purchasing power analysis
   - Budget recalibration tools

5. **International Money Movement**:
   - Transfer method comparison
   - Fee structure analysis
   - Exchange rate tracking
   - Optimization recommendations

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of currency conversions using historical exchange rates
- Correct application of country-specific tax rules to different income streams
- Proper identification of accounts requiring specific reporting
- Accurate cost-of-living adjustments between different locations
- Correct fee and exchange rate analysis for international transfers

### Critical User Scenarios
- Setting up accounts and tracking transactions in multiple currencies
- Determining tax obligations across multiple countries of residence
- Generating reports for foreign account reporting compliance
- Adjusting budgets when moving to a new international location
- Comparing options for transferring money between international accounts

### Performance Benchmarks
- Process 1,000+ multi-currency transactions in under 5 seconds
- Generate tax reports for 3+ countries simultaneously in under 10 seconds
- Perform currency conversions for 5 years of history in under 3 seconds
- Calculate cost-of-living adjustments between 20+ locations in under 2 seconds

### Edge Cases and Error Conditions
- Handling of currencies with extreme exchange rate volatility
- Proper management of countries with changing tax treaties
- Recovery from missing exchange rate data
- Handling of accounts in countries with currency controls
- Proper calculation during periods of currency redenomination

### Required Test Coverage Metrics
- 100% code coverage for all currency conversion algorithms
- Comprehensive test cases for tax calculations in at least 5 major jurisdictions
- Verification against real-world exchange rate historical data
- Performance tests for operations on large international transaction sets

## Success Criteria

The implementation will be considered successful when:

1. Users can accurately track financial transactions across multiple currencies with proper historical conversion
2. The system correctly applies country-specific tax rules to appropriate income streams
3. Users receive clear guidance on foreign account reporting requirements based on their specific situation
4. Cost-of-living differences are properly analyzed when users transition between international locations
5. The system provides actionable insights for optimizing international money transfers
6. All calculations maintain accuracy despite currency fluctuations and complex international scenarios
7. The system maintains performance with realistic international financial activity volume
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

The implementation should focus on creating a robust system for managing the complex financial situations faced by professionals working across international borders, with particular attention to currency management, tax compliance, and cost optimization.