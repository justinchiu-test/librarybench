# Small Business and Personal Finance Management System

## Overview
A specialized financial management system designed for small business owners who need to maintain clear separation between business and personal finances while having visibility across both domains. This solution provides tools for tracking business entities, monitoring owner's draw and contributions, generating simplified financial statements, managing sales tax, and properly categorizing business expenses.

## Persona Description
Elena runs a small retail business and needs to manage both personal finances and simple business accounting without mixing the two. She requires clear separation of business and personal expenses while maintaining an overview of her complete financial picture.

## Key Requirements
1. **Business entity tracking maintaining separate books for different business activities**
   - Support for multiple business entities with distinct financial tracking
   - Separation of accounts, transactions, and reporting by entity
   - Cross-entity financial overview capabilities
   - Entity-specific tax and financial rule configuration
   - Critical for maintaining proper legal and financial separation between different business ventures and personal finances

2. **Owner's draw and contribution monitoring showing personal/business money flows**
   - Tracking of all financial movements between personal and business accounts
   - Categorization of owner's equity transactions (capital contributions, draws)
   - Historical analysis of business/personal financial boundaries
   - Impact analysis of owner's transactions on business financial health
   - Essential for maintaining proper accounting records and understanding the true profitability of the business apart from personal finances

3. **Simplified profit and loss statements generated from categorized transactions**
   - Automatic generation of basic financial statements
   - Customizable income and expense categories
   - Period comparison capabilities (month-to-month, year-to-year)
   - Profitability metrics and trend analysis
   - Necessary for making data-driven business decisions without the complexity of full-featured accounting software

4. **Sales tax collection and remittance tracking with payment deadline alerts**
   - Calculation of sales tax liabilities based on transaction location and type
   - Tracking of collected sales tax separate from revenue
   - Scheduling of sales tax filing and payment deadlines
   - Historical record of sales tax remittances and filings
   - Vital for ensuring compliance with sales tax obligations and avoiding penalties

5. **Business expense categorization aligned with tax schedule C categories**
   - Predefined expense categories matching tax reporting requirements
   - Transaction tagging for tax deduction eligibility
   - Receipt and documentation management for business expenses
   - Year-end tax preparation support with category summaries
   - Important for maximizing legitimate business deductions while maintaining proper documentation for potential audits

## Technical Requirements
- **Testability Requirements**
  - Financial calculations must be deterministic and unit-testable
  - Business rule application must be testable with known outcomes
  - Tax calculations must be verifiable against known tax scenarios
  - Report generation must produce consistent outputs for testing
  - Multiple entity separation must be thoroughly testable

- **Performance Expectations**
  - Support for high-volume transaction processing across multiple entities
  - Fast generation of financial reports for arbitrary time periods
  - Efficient calculation of sales tax obligations across jurisdictions
  - Quick recategorization of transactions when rules change
  - Responsive operation even with years of transaction history

- **Integration Points**
  - Import capabilities for bank, credit card, and payment platform statements
  - Export functionality for tax preparation and accounting software
  - Standard formats for financial data interchange
  - Optional point-of-sale system integration
  - Inventory management system compatibility

- **Key Constraints**
  - Strict data separation between personal and business finances
  - Clear audit trail for all inter-entity transactions
  - Transparent methodology for all financial calculations
  - Compliance with basic accounting principles
  - Accurate tax rate and rule application

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide these core components:

1. **Multi-Entity Financial Management**
   - Entity creation and configuration
   - Entity-specific account and category management
   - Inter-entity transaction handling
   - Consolidated and entity-specific reporting

2. **Owner's Equity Tracking**
   - Capital contribution and draw recording
   - Owner's equity balance calculation
   - Personal/business boundary monitoring
   - Financial flow analysis between entities

3. **Basic Financial Statement Generation**
   - Income statement (profit & loss) creation
   - Balance sheet preparation
   - Cash flow reporting
   - Financial metric calculation and trending

4. **Sales Tax Management**
   - Tax rate configuration by jurisdiction
   - Taxable transaction identification
   - Tax collection and liability tracking
   - Filing period management and remittance scheduling

5. **Business Expense Categorization**
   - Tax-aligned category definition
   - Transaction categorization rules
   - Receipt and documentation management
   - Tax preparation export and reporting

6. **Reporting and Analytics**
   - Business performance metrics
   - Profitability analysis by product/service line
   - Cash flow and liquidity monitoring
   - Tax liability and deduction optimization

## Testing Requirements
- **Key Functionalities for Verification**
  - Proper separation of transactions between business and personal entities
  - Accurate tracking of owner's draw and contributions
  - Correctness of generated financial statements
  - Precision of sales tax calculations and tracking
  - Proper business expense categorization and reporting

- **Critical User Scenarios**
  - Setting up and managing multiple business entities alongside personal finances
  - Recording and analyzing owner's financial interactions with the business
  - Generating and interpreting basic financial statements
  - Managing sales tax collection and remittance requirements
  - Categorizing and tracking business expenses for tax purposes

- **Performance Benchmarks**
  - Support for at least 10,000 transactions per entity with fast retrieval
  - Generation of financial reports covering 5+ years in under 5 seconds
  - Sales tax calculations across multiple jurisdictions in real-time
  - Recategorization of 1,000+ transactions in under 10 seconds
  - Export of tax-ready reports in under 5 seconds

- **Edge Cases and Error Conditions**
  - Handling of complex inter-entity transactions
  - Management of retroactive categorization changes
  - Adaptation to changing tax rates and jurisdictions
  - Recovery from incorrectly categorized transactions
  - Proper handling of partial payments and split transactions
  - Graceful management of transactions spanning multiple reporting periods

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage across all modules
  - 100% coverage for entity separation and financial calculation functions
  - Comprehensive test suite for sales tax calculation logic
  - Thorough validation of financial statement generation
  - Complete testing of expense categorization rules

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Business and personal finances remain properly separated
- Owner's draws and contributions are accurately tracked and categorized
- Financial statements match expected results and balance properly
- Sales tax calculations are accurate for all applicable jurisdictions
- Business expenses align correctly with tax reporting categories
- All financial calculations match expected results with precision to 2 decimal places
- Entity-specific reporting maintains proper data isolation
- Tax-relevant data is organized for straightforward preparation
- Performance meets or exceeds all benchmark requirements
- Test coverage meets or exceeds specified metrics

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.