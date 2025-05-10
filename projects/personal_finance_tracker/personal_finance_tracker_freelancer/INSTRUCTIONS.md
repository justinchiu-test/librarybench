# Variable Income Financial Management System

## Overview
A specialized financial management system designed for freelancers and independent contractors who need to navigate irregular income patterns, project-based earnings, and the complex financial landscape of self-employment. This system provides powerful tools for income smoothing, project profitability tracking, tax management, and financial stability planning.

## Persona Description
Jamal works as a freelance designer with irregular income patterns and project-based earnings. He needs to manage cash flow during lean periods, track business expenses for tax purposes, and ensure financial stability despite unpredictable revenue.

## Key Requirements
1. **Income smoothing calculations that normalize variable earnings for consistent budgeting**
   - Algorithms for creating a virtual "salary" from irregular income
   - Historical income pattern analysis for predictive modeling
   - Dynamic budget adjustments based on current and projected income
   - Automatic allocation of surplus income during high-earning periods
   - Critical for creating financial stability with unpredictable revenue streams and managing feast-or-famine income cycles

2. **Project profitability analysis comparing time invested against revenue generated**
   - Project-level income and expense tracking
   - Time tracking integration and hourly rate calculations
   - Client and project type profitability comparisons
   - Historical trend analysis of project profitability
   - Essential for identifying high-value work and clients to optimize earning potential and work efficiency

3. **Tax obligation forecasting with quarterly estimated payment scheduling**
   - Automatic tax rate and obligation calculations for self-employment
   - Quarterly estimated payment scheduling and reminders
   - Tax deduction categorization and tracking
   - Year-to-date income and tax visualization
   - Necessary for proactively managing tax obligations and avoiding penalties common with self-employment

4. **Business versus personal expense separation maintaining clear boundaries for deductions**
   - Dual categorization system for personal and business transactions
   - Tax deduction flagging and documentation
   - Receipt management and organization
   - Expense allocation for mixed-use items and partial deductions
   - Vital for maximizing legitimate tax deductions while maintaining clean records for potential audits

5. **Cash runway visualization showing how long current funds will last at different spending levels**
   - Dynamic cash flow projections based on current balances and spending
   - Scenario modeling for different income and expense situations
   - Emergency fund adequacy calculations
   - Early warning system for potential cash flow issues
   - Important for proactively managing financial stability in the face of income volatility

## Technical Requirements
- **Testability Requirements**
  - Financial calculations must be deterministic and unit-testable
  - Time-based forecasting must support mocked dates for testing
  - Tax calculations must be verifiable against known tax scenarios
  - Historical data analysis must be testable with synthetic data sets
  - Performance must be measurable under various data volume scenarios

- **Performance Expectations**
  - Support for high-volume transaction history (10+ years)
  - Quick recalculation for tax impact simulations (under 1 second)
  - Efficient handling of complex profitability calculations across multiple projects
  - Fast generation of financial projections and what-if scenarios
  - Responsive operation even with large historical datasets

- **Integration Points**
  - Import capabilities for bank, credit card, and payment platform statements
  - Export functionality for tax preparation software
  - Optional time tracking data import
  - Standard formats for accounting system interoperability
  - Invoice and payment tracking integration

- **Key Constraints**
  - All data must be storable locally for privacy
  - System must maintain strict separation of business and personal finances
  - Tax calculations must be clearly annotated with relevant regulations
  - High accuracy requirements for financial projections
  - Clear audit trail for all business expenses

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide these core components:

1. **Variable Income Management Engine**
   - Income pattern analysis and forecasting
   - Income smoothing algorithms
   - Cash flow projection and management
   - Buffer fund allocation and management

2. **Project and Client Profitability Tracker**
   - Project-based income and expense recording
   - Time tracking and hourly rate calculation
   - Client and project type profitability analysis
   - Historical comparison and trend identification

3. **Self-Employment Tax Manager**
   - Tax rate and obligation calculations
   - Quarterly estimated payment scheduling
   - Deduction tracking and categorization
   - Year-end tax preparation support

4. **Dual-Purpose Finance Categorization**
   - Business vs. personal transaction separation
   - Tax deduction identification and documentation
   - Partial allocation support for mixed expenses
   - Historical categorization pattern recognition

5. **Financial Stability Planning**
   - Cash runway calculation and visualization
   - Emergency fund adequacy assessment
   - Scenario planning for income fluctuations
   - Early warning indicators for financial instability

6. **Reporting and Analytics**
   - Income volatility analysis
   - Project and client profitability reporting
   - Tax obligation forecasting
   - Business performance metrics
   - Cash flow and runway projections

## Testing Requirements
- **Key Functionalities for Verification**
  - Accuracy of income smoothing algorithms
  - Precision of project profitability calculations
  - Correctness of tax obligation forecasts
  - Proper separation of business and personal expenses
  - Accuracy of cash runway projections

- **Critical User Scenarios**
  - Recording inconsistent income over time and generating stable budget
  - Tracking and analyzing profitability of multiple client projects
  - Calculating and scheduling quarterly estimated tax payments
  - Managing business expenses and identifying tax deductions
  - Predicting cash runway during low-income periods

- **Performance Benchmarks**
  - Support for at least 5,000 transactions per year with fast retrieval
  - Generation of tax forecasts with multiple scenarios in under 5 seconds
  - Profitability analysis across 100+ projects in under 3 seconds
  - Cash runway projections with variable parameters in under 2 seconds
  - Income pattern analysis of 5+ years of data in under 10 seconds

- **Edge Cases and Error Conditions**
  - Handling of extremely irregular income patterns
  - Management of projects with highly variable profitability
  - Adaptation to significant tax code changes
  - Recovery from incorrectly categorized transactions
  - Proper handling of unusual business expense scenarios
  - Accurate projections despite limited historical data

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage across all modules
  - 100% coverage for tax calculation and financial projection functions
  - Comprehensive test suite for income smoothing algorithms
  - Thorough validation of project profitability calculations
  - Complete testing of business/personal categorization logic

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Income smoothing algorithms produce stable budgets despite irregular income
- Project profitability analysis accurately reflects true hourly rates
- Tax calculations match expected results for various self-employment scenarios
- Business and personal expenses are properly categorized and tracked
- Cash runway projections provide accurate financial stability forecasts
- All financial calculations match expected results with precision to 2 decimal places
- System accommodates significant income volatility without data distortion
- Tax deduction categorization aligns with current tax regulations
- Performance meets or exceeds all benchmark requirements
- Test coverage meets or exceeds specified metrics

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.