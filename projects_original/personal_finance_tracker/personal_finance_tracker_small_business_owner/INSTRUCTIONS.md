# Small Business and Personal Finance Management System

## Overview
A specialized financial management system designed for small business owners who need to maintain clear separation between business and personal finances while having a unified view of their complete financial picture. The system provides tools for tracking business entities, monitoring owner transactions, generating simplified accounting reports, managing sales tax, and appropriately categorizing business expenses.

## Persona Description
Elena runs a small retail business and needs to manage both personal finances and simple business accounting without mixing the two. She requires clear separation of business and personal expenses while maintaining an overview of her complete financial picture.

## Key Requirements
1. **Business entity tracking maintaining separate books for different business activities**  
   Elena operates a primary retail business but has occasional side projects and consulting work. She needs a system that maintains separate accounting records for each business entity or revenue stream while allowing unified reporting and analysis across all her business activities. Each entity needs its own chart of accounts, transaction records, and performance metrics.

2. **Owner's draw and contribution monitoring showing personal/business money flows**  
   As a business owner, Elena regularly moves funds between personal and business accounts through owner's draws, capital contributions, and expense reimbursements. The system must track these transfers with proper accounting treatment, maintain accurate capital account balances, and provide clear visibility into the flow of funds between her personal and business finances.

3. **Simplified profit and loss statements generated from categorized transactions**  
   Elena needs straightforward financial reporting without the complexity of full-fledged accounting software. The system should generate basic profit and loss statements from categorized transactions, showing revenue streams, expense categories, and bottom-line profitability for each business entity and time period, with month-to-month and year-to-year comparisons.

4. **Sales tax collection and remittance tracking with payment deadline alerts**  
   Elena's retail business requires collecting and remitting sales tax to multiple jurisdictions. The system needs to track collected tax by jurisdiction, calculate tax liabilities, monitor payment deadlines, and maintain records of filed returns and payments to ensure compliance and prevent penalties for missed deadlines.

5. **Business expense categorization aligned with tax schedule C categories**  
   To simplify tax preparation, Elena needs business expenses to be automatically categorized according to IRS Schedule C categories. The system should apply intelligent categorization rules, maintain proper documentation for deductions, flag potentially non-deductible expenses, and generate tax-ready expense summaries for her accountant.

## Technical Requirements
- **Testability Requirements:**
  - Account separation must be verifiable through comprehensive audit trails
  - Tax calculations must be validated against current tax rules
  - Financial reports must reconcile with transaction data
  - Owner's equity calculations must balance across all transfers

- **Performance Expectations:**
  - System must support at least 10,000 transactions per year across all entities
  - Report generation must complete in under 3 seconds
  - Transaction categorization must achieve 90%+ accuracy
  - Tax liability calculations must process in real-time as transactions are entered

- **Integration Points:**
  - Import functionality for bank and credit card transactions
  - Export capabilities for tax preparation software
  - Document storage for receipts and business records
  - Optional integration with point-of-sale systems

- **Key Constraints:**
  - Clear data boundaries between different business entities
  - Proper accounting standards for owner's equity transactions
  - Compliance with tax reporting requirements
  - Audit-ready transaction records and documentation

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement these core components:

1. **Multi-Entity Management System:**
   - Business entity definition and configuration
   - Entity-specific chart of accounts
   - Cross-entity reporting and analysis
   - Entity performance comparison
   - Consolidated financial view

2. **Owner's Capital Tracking:**
   - Owner's draw recording and management
   - Capital contribution tracking
   - Personal expense reimbursement processing
   - Equity account maintenance
   - Personal/business boundary enforcement

3. **Financial Reporting Engine:**
   - Simplified profit and loss statement generation
   - Revenue and expense categorization
   - Comparative reporting (month/quarter/year)
   - Profitability analysis by product/service
   - Cash flow reporting

4. **Sales Tax Management:**
   - Multi-jurisdiction tax rate configuration
   - Tax collection tracking by transaction
   - Tax liability calculation by jurisdiction
   - Filing deadline monitoring and alerts
   - Payment and filing history

5. **Tax-Oriented Expense System:**
   - Schedule C category alignment
   - Receipt documentation management
   - Deduction optimization
   - Expense allocation across business entities
   - Tax-ready reporting

## Testing Requirements
- **Key Functionalities to Verify:**
  - Proper separation of transactions between business entities
  - Accurate tracking of owner's draws and contributions
  - Correct generation of profit and loss statements
  - Proper calculation of sales tax liabilities by jurisdiction
  - Accurate categorization of expenses according to tax categories

- **Critical User Scenarios:**
  - Creating and configuring a new business entity
  - Recording an owner's draw from the business to personal accounts
  - Generating month-end financial reports for business performance
  - Calculating quarterly sales tax obligations across multiple jurisdictions
  - Categorizing and documenting business expenses for tax purposes

- **Performance Benchmarks:**
  - System must maintain performance with 3+ years of transaction history
  - Financial reports must generate in under 5 seconds for all entities combined
  - Sales tax calculations must process in under 2 seconds for multi-jurisdiction businesses
  - Expense categorization must achieve at least 90% accuracy with typical business expenses

- **Edge Cases and Error Conditions:**
  - Handling negative owner's equity situations
  - Managing mid-year tax rate changes
  - Processing split transactions that span multiple entities
  - Detecting and preventing categorization of personal expenses as business
  - Maintaining data integrity during entity restructuring

- **Required Test Coverage Metrics:**
  - Entity separation functions: minimum 95% coverage
  - Owner's equity calculations: minimum 90% coverage
  - Financial reporting functions: minimum 90% coverage
  - Tax calculation algorithms: minimum 95% coverage

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria
- The system properly separates and tracks different business entities
- Owner's draws and contributions are accurately recorded with proper accounting treatment
- Profit and loss statements correctly reflect business performance
- Sales tax liabilities are accurately calculated with appropriate deadline tracking
- Business expenses are properly categorized according to tax requirements
- All operations maintain clear boundaries between personal and business finances
- System performance meets or exceeds the specified benchmarks
- All tests pass without manual intervention

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Environment Setup
1. Set up a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.