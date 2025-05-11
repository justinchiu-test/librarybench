# Multi-Currency International Finance Management System

## Overview
A specialized financial management system designed for professionals who work across international boundaries, dealing with multiple currencies, international tax obligations, and financial accounts in different countries. The system provides comprehensive tools for multi-currency management, international tax compliance, cross-border financial reporting, and optimizing global financial decisions.

## Persona Description
Priya works internationally and deals with multiple currencies, international tax obligations, and financial accounts in different countries. She needs to track assets and liabilities across national boundaries while optimizing for complex international tax situations.

## Key Requirements
1. **Multi-currency support with historical exchange rate tracking and conversion**  
   Priya regularly transacts in multiple currencies and needs to understand her financial position in both local currencies and her base currency. The system must maintain historical exchange rate data, automatically convert transactions between currencies, track realized and unrealized currency gains/losses, and provide a consolidated financial view with appropriate currency translation for reporting and analysis.

2. **Country-specific tax rule application for different income streams**  
   With income sources in multiple countries, Priya faces complex tax situations governed by different national regulations. The system needs to categorize income according to source country, apply appropriate country-specific tax rules (rates, deductions, credits), account for tax treaties between countries, and optimize tax positions while ensuring compliance with all applicable jurisdictions.

3. **Foreign account reporting compliance for tax requirements like FBAR or FATCA**  
   As someone with financial accounts in multiple countries, Priya must comply with foreign account reporting requirements such as the US Foreign Bank Account Report (FBAR) and Foreign Account Tax Compliance Act (FATCA). The system must track foreign account balances, monitor reporting thresholds, generate required reporting information, and provide alerts for filing deadlines to ensure compliance and avoid penalties.

4. **International cost-of-living adjustments when moving between assignments**  
   Priya periodically relocates between countries and needs to adjust her financial planning based on different cost-of-living environments. The system should provide location-based budget calibration, automatically adjust spending categories based on local norms, compare purchasing power between locations, and help maintain consistent lifestyles across international moves despite varying local costs.

5. **Remittance optimization identifying the most cost-effective ways to move money internationally**  
   Priya frequently transfers money between accounts in different countries and currencies. The system must analyze and compare various transfer methods (bank wires, fintech platforms, cryptocurrency), track transfer fees and exchange rate margins, recommend optimal timing for transfers based on currency trends, and select the most cost-effective method for each international money movement.

## Technical Requirements
- **Testability Requirements:**
  - Currency conversion functions must be tested with historical exchange rate data
  - Tax calculations must be validated against official country-specific rules
  - Foreign account reporting thresholds must be accurately monitored
  - Remittance option comparisons must be testable with varied market conditions

- **Performance Expectations:**
  - System must handle at least 10 different currencies simultaneously
  - Tax calculations must complete in under 3 seconds for multi-country scenarios
  - Foreign account balance tracking must support daily updates across 20+ accounts
  - Cost-of-living comparisons must process in under 2 seconds between any countries

- **Integration Points:**
  - Exchange rate data source integration
  - International tax rule database with regular updates
  - Foreign account data aggregation
  - Remittance service rate and fee information

- **Key Constraints:**
  - Currency conversion must be accurate to at least 4 decimal places
  - Tax calculations must adapt to changing international tax laws
  - All date handling must properly account for different time zones
  - System must maintain audit trails for cross-border transactions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement these core components:

1. **Multi-Currency Management System:**
   - Currency definition and configuration
   - Historical exchange rate database
   - Automatic currency conversion
   - Unrealized/realized gain/loss tracking
   - Base currency reporting with appropriate translations

2. **International Tax Engine:**
   - Country-specific tax rule repository
   - Source-based income categorization
   - Multi-jurisdiction tax calculation
   - Tax treaty application
   - Foreign tax credit optimization

3. **Foreign Account Compliance Tracker:**
   - Account registry with jurisdictional tagging
   - Balance history tracking in original and base currencies
   - Threshold monitoring for reporting requirements
   - Filing deadline management
   - Compliance report generation

4. **Global Cost-of-Living Analyzer:**
   - Location-based expense normalization
   - Budget adaptation for different countries
   - Purchasing power comparison
   - Lifestyle maintenance calculation
   - Relocation financial planning

5. **Cross-Border Transfer Optimizer:**
   - Transfer method comparison
   - Fee and exchange rate analysis
   - Timing recommendation based on market conditions
   - Transfer history tracking
   - Recurring transfer optimization

## Testing Requirements
- **Key Functionalities to Verify:**
  - Accurate currency conversion using historical exchange rates
  - Correct application of country-specific tax rules to various income streams
  - Proper monitoring of foreign account balances for reporting requirements
  - Accurate cost-of-living adjustments between different locations
  - Optimal selection of money transfer methods based on costs and exchange rates

- **Critical User Scenarios:**
  - Recording income in a foreign currency and viewing consolidated financial reports
  - Calculating tax obligations for income earned across multiple countries
  - Tracking foreign account balances and determining reporting requirements
  - Adjusting a budget when relocating from one country to another
  - Transferring money between accounts in different countries in the most cost-effective way

- **Performance Benchmarks:**
  - Currency conversions must process 1,000+ transactions in under 5 seconds
  - Tax calculations must handle 5+ countries' rules simultaneously
  - Foreign account monitoring must track up to 50 accounts across 10+ countries
  - Cost-of-living comparisons must be available for at least 100 major global cities

- **Edge Cases and Error Conditions:**
  - Handling currencies with extreme value differences or redenominations
  - Managing conflicting tax rules between countries
  - Adapting to changing reporting thresholds for foreign accounts
  - Processing relocations to countries with limited cost-of-living data
  - Optimizing transfers during periods of high currency volatility

- **Required Test Coverage Metrics:**
  - Currency conversion functions: minimum 95% coverage
  - Tax calculation modules: minimum 90% coverage
  - Foreign account reporting functions: minimum 95% coverage
  - Remittance optimization algorithms: minimum 90% coverage

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
- The system accurately handles multiple currencies with proper exchange rate conversion
- Tax obligations are correctly calculated according to country-specific rules
- Foreign account reporting requirements are properly tracked and monitored
- Cost-of-living adjustments accurately reflect differences between locations
- Money transfers between countries are optimized for cost-effectiveness
- All calculations maintain accuracy across different international scenarios
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