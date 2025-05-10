# Fixed Income Retirement Finance Management System

## Overview
A specialized financial management system designed for retirees living on fixed income who need to carefully track essential expenses, manage medical costs, ensure regular benefit payments, and plan for occasional large expenses within limited financial flexibility.

## Persona Description
Mrs. Johnson lives on Social Security and pension income with limited financial flexibility. She needs to carefully track essential expenses, manage medical costs, and ensure her fixed income stretches through each month while planning for occasional large expenses.

## Key Requirements
1. **Fixed income allocation with priority-based spending categories for essentials**
   - Structured allocation of fixed income to essential expense categories
   - Priority-based spending framework ensuring critical needs are met first
   - Month-to-month budget carryover for unspent category amounts
   - Shortfall alerts when income doesn't cover essential expenses
   - Critical for ensuring limited income is properly directed to essential needs first while maintaining awareness of potential shortfalls

2. **Medical expense tracking categorized by insurance coverage and tax deductibility**
   - Detailed tracking of healthcare costs by type and provider
   - Insurance coverage status and reimbursement tracking
   - Categorization for tax deduction eligibility
   - Annual medical spending summaries for tax preparation
   - Essential for managing the often substantial and complex healthcare costs faced by retirees, while maximizing insurance reimbursements and tax benefits

3. **Benefit payment monitoring ensuring regular deposits arrive as scheduled**
   - Tracking of expected Social Security, pension, and other benefit deposits
   - Automatic verification of received payments against expected amounts
   - Anomaly detection for missed, delayed, or incorrect payments
   - Historical record of all benefit receipts
   - Necessary for providing early warning of any issues with critical income sources that form the foundation of retirement finances

4. **Strategic withdrawal planning from limited savings for major expenses**
   - Projection of major upcoming expenses and timing
   - Withdrawal scheduling to minimize impacts on essential spending
   - Strategic timing recommendations for large purchases
   - "What-if" planning for emergency expenses
   - Vital for managing occasional large expenses within the constraints of fixed income and limited savings

5. **Age-specific tax benefit tracking including standard deduction adjustments and tax credits**
   - Application of age-specific tax benefits available to seniors
   - Higher standard deduction tracking for age qualifications
   - Tax credit eligibility monitoring (elderly, disabled)
   - Medical expense deduction threshold calculations
   - Important for ensuring all available tax advantages for seniors are utilized to maximize effective income

## Technical Requirements
- **Testability Requirements**
  - Budget allocation algorithms must be deterministic and unit-testable
  - Payment verification systems must be testable with mocked data
  - Withdrawal planning must produce consistent recommendations
  - Tax benefit calculations must be verifiable against tax regulations
  - Essential needs prioritization must produce predictable results

- **Performance Expectations**
  - Efficient operation on modest hardware with limited resources
  - Fast computation of budget allocations and adjustments
  - Quick verification of income deposits
  - Responsive recalculation when financial parameters change
  - Lightweight data storage with minimal overhead

- **Integration Points**
  - Import capabilities for bank account transaction data
  - Medical expense import from provider statements
  - Tax preparation data export
  - Benefit payment statement import
  - Health insurance coverage verification

- **Key Constraints**
  - Simple, straightforward financial logic appropriate for older users
  - Reliability and predictability in all financial operations
  - Minimized complexity while maintaining accuracy
  - Clear distinction between actual and projected figures
  - Conservative approach to financial projections and recommendations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide these core components:

1. **Fixed Income Budget Management**
   - Essential expense categorization and prioritization
   - Monthly income allocation to spending categories
   - Budget adherence tracking and adjustment
   - Surplus/deficit management and reporting

2. **Medical Expense Tracker**
   - Healthcare cost recording and categorization
   - Insurance coverage and reimbursement tracking
   - Tax deductibility determination
   - Annual healthcare spending analysis

3. **Income Source Verification**
   - Expected payment schedule management
   - Deposit verification against expectations
   - Payment anomaly detection and alerting
   - Historical payment record maintenance

4. **Major Expense Planning**
   - Large expense identification and scheduling
   - Withdrawal timing optimization
   - Savings impact analysis
   - Emergency expense contingency planning

5. **Senior Tax Benefit Optimization**
   - Age-based tax benefit identification
   - Deduction and credit eligibility tracking
   - Medical expense deduction threshold monitoring
   - Tax-optimized withdrawal planning

6. **Financial Health Monitoring**
   - Essential needs coverage assessment
   - Cash flow adequacy analysis
   - Savings depletion rate tracking
   - Financial vulnerability identification

## Testing Requirements
- **Key Functionalities for Verification**
  - Accuracy of priority-based budget allocations
  - Proper categorization of medical expenses
  - Correct identification of benefit payment anomalies
  - Optimal withdrawal planning for major expenses
  - Accurate application of age-specific tax benefits

- **Critical User Scenarios**
  - Setting up and managing a fixed income budget with essential priorities
  - Tracking medical expenses and insurance reimbursements
  - Monitoring regular benefit payments for accuracy and timeliness
  - Planning for a major home repair expense from limited savings
  - Identifying and applying all eligible senior tax benefits

- **Performance Benchmarks**
  - Budget reallocation calculations in under 1 second
  - Verification of benefit payments against expectations in under 2 seconds
  - Analysis of withdrawal strategies for major expenses in under 5 seconds
  - Calculation of tax implications with all senior benefits in under 3 seconds
  - Complete financial health assessment in under 10 seconds

- **Edge Cases and Error Conditions**
  - Handling of insufficient income for essential expenses
  - Management of unexpected medical costs
  - Adaptation to missed or delayed benefit payments
  - Recovery from emergency withdrawals affecting budget
  - Proper handling of tax law changes affecting senior benefits
  - Graceful management of overlapping major expenses

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage across all modules
  - 100% coverage for budget allocation and benefit verification functions
  - Comprehensive test suite for medical expense categorization
  - Thorough validation of withdrawal planning algorithms
  - Complete testing of senior tax benefit calculations

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Fixed income allocations correctly prioritize essential expenses
- Medical expenses are properly categorized for insurance and tax purposes
- Benefit payment anomalies are accurately detected and reported
- Withdrawal plans for major expenses minimize impact on essential needs
- Age-specific tax benefits are correctly identified and applied
- All financial calculations match expected results with high precision
- System accommodates the financial constraints of fixed-income retirees
- Budget recommendations ensure essential needs are consistently met
- Performance meets or exceeds all benchmark requirements
- Test coverage meets or exceeds specified metrics

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.