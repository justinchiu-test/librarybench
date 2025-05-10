# Business & Personal Finance Integration System

A personal finance tracker designed for small business owners that maintains clear separation between business and personal finances while providing a unified financial overview.

## Overview

This library provides a comprehensive financial management system specifically tailored for small business owners who need to manage both business and personal finances. It focuses on maintaining clear separation between business and personal accounts while providing an integrated view of the owner's complete financial situation.

## Persona Description

Elena runs a small retail business and needs to manage both personal finances and simple business accounting without mixing the two. She requires clear separation of business and personal expenses while maintaining an overview of her complete financial picture.

## Key Requirements

1. **Business entity tracking maintaining separate books for different business activities**
   - Support for multiple business entities with isolated accounting
   - Distinct chart of accounts for each business activity
   - Consolidated reporting across all business entities
   - This feature is critical for maintaining proper legal separation between different business ventures while still enabling unified oversight

2. **Owner's draw and contribution monitoring showing personal/business money flows**
   - Tracking of capital contributions to business entities
   - Owner's draw/distribution recording and categorization
   - Clear visualization of money flow between personal and business accounts
   - This feature helps maintain the critical boundary between personal and business finances while documenting legitimate transfers between them

3. **Simplified profit and loss statements generated from categorized transactions**
   - Automatic generation of basic financial statements from transaction data
   - Customizable income and expense categories aligned with accounting standards
   - Period comparison (month-to-month, year-to-year) reporting
   - This feature provides small business owners with essential financial insights without requiring advanced accounting knowledge

4. **Sales tax collection and remittance tracking with payment deadline alerts**
   - Calculation of sales tax obligations based on transactions
   - Jurisdiction-specific tax rate support
   - Payment scheduling and deadline management
   - This feature helps small business owners comply with complex sales tax requirements across different jurisdictions

5. **Business expense categorization aligned with tax schedule C categories**
   - Expense categories mapped directly to tax form requirements
   - Percentage allocation for mixed personal/business expenses
   - Supporting documentation attachment for audit defense
   - This feature simplifies tax preparation by organizing business expenses according to IRS requirements throughout the year

## Technical Requirements

### Testability Requirements
- All accounting functions must have unit tests with 100% code coverage
- Test data representing realistic business and personal financial scenarios
- Mock implementations for date/time dependencies to enable deterministic testing
- Verification of tax calculations against reference examples

### Performance Expectations
- Support for 5+ years of daily business transactions (10,000+ transactions)
- Financial statement generation in under 3 seconds
- Real-time calculation of tax obligations
- Report generation optimized for speed even with large datasets

### Integration Points
- Import functionality for bank statements and accounting software exports
- Export capabilities for tax preparation
- Document storage integration for receipts and invoices
- Optional calendar integration for payment deadlines

### Key Constraints
- Clear separation of business and personal data with proper access controls
- Compliance with basic accounting principles
- No transmission of sensitive financial data to external services
- Support for multiple business entities with different fiscal years

## Core Functionality

The system must provide these core components:

1. **Multi-Entity Financial Management**:
   - Business entity creation and configuration
   - Entity-specific chart of accounts
   - Personal finance account management
   - Unified overview across all entities

2. **Transaction Management and Categorization**:
   - Multi-account transaction recording
   - Business vs. personal categorization
   - Split transactions with allocation between entities
   - Recurring transaction management

3. **Business Financial Analysis**:
   - Profit and loss statement generation
   - Revenue and expense tracking by category
   - Cash flow analysis
   - Basic financial ratio calculation

4. **Tax Management and Compliance**:
   - Sales tax calculation and tracking
   - Tax payment scheduling
   - Business expense categorization for income tax
   - Tax deduction optimization recommendations

5. **Owner's Equity Tracking**:
   - Capital contribution recording
   - Owner's draw management
   - Personal/business boundary monitoring
   - Equity position reporting

## Testing Requirements

### Key Functionalities to Verify
- Proper separation of transactions between business and personal entities
- Accurate calculation of profit/loss for business activities
- Correct sales tax calculation across different jurisdictions
- Proper tracking of owner's equity changes
- Accurate categorization of expenses for tax purposes

### Critical User Scenarios
- Setting up separate business and personal accounts
- Recording transactions and properly categorizing between business and personal
- Tracking money movement between personal and business accounts
- Generating profit and loss statements for business entities
- Preparing for tax filing with properly categorized expenses

### Performance Benchmarks
- Financial statement generation with 5,000+ transactions in under 3 seconds
- Tax calculation for 1,000+ taxable transactions in under 2 seconds
- Complete data import of 1,000+ transactions in under 10 seconds
- Report generation with multiple business entities in under 5 seconds

### Edge Cases and Error Conditions
- Handling mixed personal/business expenses requiring allocation
- Proper management of transactions affecting multiple entities
- Recovery from incorrectly categorized transactions
- Handling different fiscal years across business entities
- Proper calculation of complex sales tax scenarios (multiple jurisdictions)

### Required Test Coverage Metrics
- 100% code coverage for all financial calculation algorithms
- Comprehensive tests for tax calculations with various scenarios
- Integration tests verifying proper data separation between entities
- Performance tests for report generation with large datasets

## Success Criteria

The implementation will be considered successful when:

1. Business and personal finances remain clearly separated while providing a unified view
2. Owner's draws and contributions are properly tracked and categorized
3. Financial statements accurately reflect the business's financial position
4. Sales tax obligations are correctly calculated with appropriate remittance tracking
5. Business expenses are categorized in a way that simplifies tax preparation
6. The system maintains performance with 5+ years of transaction history
7. Users can clearly see money flow between personal and business accounts
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

The implementation should focus on creating a robust system that maintains proper separation between business and personal finances while providing small business owners with the tools they need to manage their complete financial picture.