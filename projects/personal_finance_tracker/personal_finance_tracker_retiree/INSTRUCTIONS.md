# Fixed Income Financial Management System

## Overview
A specialized financial management system designed for retirees living on fixed income from Social Security, pensions, and limited savings. The system provides tools for essential expense prioritization, medical cost tracking, benefit payment monitoring, strategic withdrawal planning, and age-specific tax benefit management to help maximize financial security with limited flexibility.

## Persona Description
Mrs. Johnson lives on Social Security and pension income with limited financial flexibility. She needs to carefully track essential expenses, manage medical costs, and ensure her fixed income stretches through each month while planning for occasional large expenses.

## Key Requirements
1. **Fixed income allocation with priority-based spending categories for essentials**  
   Mrs. Johnson has a limited, consistent monthly income that must cover all expenses. The system needs a priority-based budgeting framework that allocates income first to essential categories (housing, utilities, food, medicine), then to important secondary expenses, and finally to discretionary spending, with clear visibility into how much remains available in each category throughout the month.

2. **Medical expense tracking categorized by insurance coverage and tax deductibility**  
   Healthcare costs represent a significant portion of Mrs. Johnson's budget and have tax implications. The system must track medical expenses with detailed categorization by type of care, insurance coverage status (covered, partially covered, not covered), out-of-pocket requirements, and tax deductibility to facilitate both insurance claims and tax preparation.

3. **Benefit payment monitoring ensuring regular deposits arrive as scheduled**  
   Mrs. Johnson depends on reliable, timely deposits from Social Security and pension providers. The system needs to monitor expected deposit dates, verify deposit amounts against expected benefits, alert for missed, delayed, or incorrect payments, and maintain a comprehensive history of all benefit payments for reference and verification.

4. **Strategic withdrawal planning from limited savings for major expenses**  
   With minimal savings, Mrs. Johnson must carefully plan for occasional large expenses. The system should help identify upcoming major expenses (home repairs, dental work, new appliances), determine optimal timing for withdrawals from limited savings, assess impact on monthly cash flow, and help rebuild savings afterward according to a sustainable schedule.

5. **Age-specific tax benefit tracking including standard deduction adjustments and tax credits**  
   As a senior citizen, Mrs. Johnson qualifies for specific tax benefits. The system must track applicable age-related tax provisions (increased standard deduction, elderly tax credit, medical expense deduction threshold adjustments), identify qualified expenditures throughout the year, estimate tax implications, and optimize financial decisions for tax advantage.

## Technical Requirements
- **Testability Requirements:**
  - Priority-based budget allocation must be verified with various income scenarios
  - Medical expense categorization must be tested against current healthcare regulations
  - Benefit payment monitoring must detect various anomaly patterns
  - Tax calculation functions must be validated against senior-specific tax rules

- **Performance Expectations:**
  - Budget allocations must recalculate instantly when changes occur
  - System must support at least 7 years of financial history for trend analysis
  - Medical expense tracking must handle at least 500 transactions per year
  - Cash flow projections must cover 24+ months for long-term planning

- **Integration Points:**
  - Import capabilities for bank account transactions
  - Medicare and insurance explanation of benefits processing
  - Social Security and pension payment verification
  - Export functionality for tax preparation

- **Key Constraints:**
  - All calculations must be precise to the penny (critical for fixed income)
  - System must be sensitive to minimum balance requirements to avoid bank fees
  - Workflows must accommodate regular monthly cycles of income and expenses
  - Low-risk approach to financial recommendations given limited flexibility

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement these core components:

1. **Priority-Based Budget System:**
   - Tiered expense category framework (essential, important, discretionary)
   - Fixed income allocation algorithm
   - Daily available balance tracking
   - Spending pattern analysis
   - Month-to-month budget consistency monitoring

2. **Medical Expense Manager:**
   - Healthcare cost tracking with detailed metadata
   - Insurance coverage status tracking
   - Deductible and out-of-pocket maximum monitoring
   - Tax-qualified expense identification
   - Year-end medical expense summarization

3. **Benefit Payment Monitor:**
   - Expected payment calendar
   - Deposit verification system
   - Payment anomaly detection
   - Historical benefit tracking
   - Payment source documentation

4. **Strategic Savings Withdrawal Planner:**
   - Major expense forecasting
   - Optimal withdrawal timing calculator
   - Cash flow impact analysis
   - Savings rebuilding scheduler
   - Emergency fund protection mechanisms

5. **Senior Tax Benefit Optimizer:**
   - Age-specific tax provision database
   - Qualified expense tracking
   - Tax-advantaged decision support
   - Standard deduction vs. itemization analysis
   - Medicare premium tax implications

## Testing Requirements
- **Key Functionalities to Verify:**
  - Correct allocation of fixed income to prioritized expense categories
  - Accurate categorization of medical expenses by coverage and tax status
  - Proper monitoring and verification of benefit payments
  - Appropriate planning for withdrawals from limited savings
  - Correct application of age-specific tax benefits

- **Critical User Scenarios:**
  - Creating a monthly budget on fixed Social Security and pension income
  - Tracking medical expenses for an unexpected health condition
  - Monitoring and verifying monthly benefit deposits
  - Planning for a major home repair expense using limited savings
  - Optimizing financial decisions for senior-specific tax advantages

- **Performance Benchmarks:**
  - Budget adjustments must recalculate in under 1 second
  - Medical expense categorization must process 50+ entries at once
  - Benefit monitoring must track 5+ different payment sources simultaneously
  - Tax benefit calculations must evaluate 10+ scenarios in under 3 seconds

- **Edge Cases and Error Conditions:**
  - Handling unexpected benefit payment reductions
  - Managing months with extraordinary medical expenses
  - Accommodating irregular large expenses with minimal savings
  - Adapting to changes in tax laws affecting seniors
  - Recovering from overdraft or minimum balance fee situations

- **Required Test Coverage Metrics:**
  - Budget allocation algorithms: minimum 95% coverage
  - Medical expense categorization: minimum 90% coverage
  - Benefit payment monitoring: minimum 90% coverage
  - Tax benefit optimization: minimum 85% coverage

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
- The system effectively manages fixed income with priority-based budget categories
- Medical expenses are accurately tracked by insurance coverage and tax deductibility
- Benefit payments are properly monitored to ensure timely and correct deposits
- Withdrawals from limited savings are strategically planned for major expenses
- Age-specific tax benefits are correctly identified and optimized
- All calculations maintain penny-perfect accuracy for critical fixed-income management
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