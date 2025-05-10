# Financial Independence and Early Retirement System

## Overview
A comprehensive financial management system designed for individuals pursuing financial independence and early retirement (FIRE). This solution provides sophisticated tools for tracking savings rates, modeling safe withdrawal strategies, comparing geographic arbitrage opportunities, optimizing tax-efficient withdrawals, and calculating Coast FIRE metrics to facilitate a well-planned transition from working life to financial independence.

## Persona Description
Dr. Chen is pursuing financial independence and early retirement (FIRE) through aggressive saving and investing. He needs detailed projections of passive income, withdrawal strategies, and portfolio longevity to plan his transition from working life.

## Key Requirements
1. **Savings rate analysis showing percentage of income preserved and path to independence**
   - Calculation of savings rate as percentage of net and gross income
   - Projection of time to financial independence based on savings rate and returns
   - Historical tracking of savings rate fluctuations
   - Visualization of savings rate impact on FIRE timeline
   - Critical for tracking the primary metric that determines time to financial independence and maintaining motivation by showing progress

2. **Safe withdrawal rate simulations based on different market performance scenarios**
   - Implementation of standard withdrawal methodologies (4% rule, variable percentage, etc.)
   - Monte Carlo simulations of portfolio longevity under different market conditions
   - Historical sequence of returns analysis using real market data
   - Customizable withdrawal strategies based on personal risk tolerance
   - Essential for determining sustainable withdrawal rates and evaluating the longevity of accumulated assets in retirement

3. **Geographic arbitrage comparisons of living costs in different retirement locations**
   - Cost of living calculator for different geographic locations
   - Purchasing power analysis for portfolio in various regions
   - Tax implication modeling for different domiciles
   - Comparison of healthcare costs and quality metrics by location
   - Necessary for optimizing retirement funds by potentially relocating to areas with lower costs but high quality of life

4. **Tax-optimized withdrawal sequencing across different account types (401k, IRA, taxable)**
   - Tax-efficient withdrawal strategy development across account types
   - Roth conversion ladder planning and implementation
   - Required Minimum Distribution (RMD) projections and management
   - Tax bracket management for retirement income
   - Vital for minimizing tax burden during the withdrawal phase, extending portfolio longevity

5. **Coast FIRE calculator showing when investments could grow to support retirement without additional contributions**
   - Calculation of Coast FIRE number and date based on current portfolio
   - Projection of portfolio growth during "coasting" phase
   - Partial contribution modeling for semi-retirement scenarios
   - Visualization of different Coast FIRE paths and timelines
   - Important for providing flexibility in retirement planning and allowing for a staged approach to reducing work

## Technical Requirements
- **Testability Requirements**
  - Financial projections must be deterministic and unit-testable
  - Simulation engines must support seeded randomization for testing
  - Tax calculations must be verifiable against known tax scenarios
  - Geographic data comparisons must be testable with mocked data sets
  - Time-based projections must support accelerated time scales for testing

- **Performance Expectations**
  - Support for at least 10,000 Monte Carlo simulation runs in reasonable time
  - Fast calculation of complex tax optimization strategies
  - Efficient handling of multi-decade financial projections
  - Quick comparison of numerous geographic locations
  - Responsive recalculation when parameters change

- **Integration Points**
  - Import capabilities for financial account data and balances
  - Access to historical market performance data
  - Integration with cost-of-living databases
  - Tax rate and rule data sources
  - Export functionality for retirement planning reports

- **Key Constraints**
  - Clear communication of uncertainty in long-term projections
  - Transparent methodology for all financial calculations
  - Regular updates for tax law changes
  - Accurate representation of market volatility in simulations
  - Sensible default values with customization options

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide these core components:

1. **Financial Independence Tracking**
   - Savings rate calculation and tracking
   - FIRE number determination (25x, 30x, or custom multiple of expenses)
   - Progress tracking toward financial independence
   - Projection of independence date based on current trajectory

2. **Withdrawal Strategy Simulation**
   - Safe withdrawal rate determination
   - Monte Carlo simulation engine for portfolio longevity
   - Historical sequence of returns analysis
   - Customizable withdrawal rule implementation

3. **Geographic Arbitrage Analysis**
   - Cost of living database and comparison tools
   - Purchasing power and lifestyle equivalence calculations
   - Healthcare cost and quality analysis
   - Regional tax burden estimation

4. **Tax-Efficient Withdrawal Planning**
   - Account type-aware withdrawal sequencing
   - Tax bracket optimization algorithms
   - Roth conversion strategy planning
   - RMD projection and management

5. **Coast FIRE Calculation**
   - Coast FIRE threshold determination
   - Growth projection during coasting phase
   - Part-time work and partial contribution modeling
   - Transition planning from full work to coast to full retirement

6. **Reporting and Analytics**
   - Financial independence probability assessment
   - Withdrawal strategy comparison
   - Geographic location ranking
   - Tax efficiency metrics
   - Portfolio longevity projections

## Testing Requirements
- **Key Functionalities for Verification**
  - Accuracy of savings rate and FIRE timeline calculations
  - Statistical validity of Monte Carlo retirement simulations
  - Precision of geographic cost-of-living comparisons
  - Correctness of tax-optimized withdrawal sequencing
  - Accuracy of Coast FIRE threshold determinations

- **Critical User Scenarios**
  - Calculating time to financial independence based on savings rate
  - Running withdrawal simulations to determine portfolio longevity
  - Comparing potential retirement locations based on cost of living
  - Developing a tax-efficient withdrawal strategy across account types
  - Determining Coast FIRE threshold and partial retirement options

- **Performance Benchmarks**
  - Execution of 10,000 Monte Carlo simulations in under 30 seconds
  - Comparison of 20+ geographic locations in under 5 seconds
  - Generation of optimal withdrawal strategies in under 10 seconds
  - Calculation of detailed tax implications across 30+ years in under 15 seconds
  - Real-time updates of FIRE projections when inputs change

- **Edge Cases and Error Conditions**
  - Handling of extreme market volatility in simulations
  - Management of complex tax situations (e.g., foreign income)
  - Adaptation to unusual income and expense patterns
  - Proper handling of early retirement with penalties
  - Recovery from invalid financial assumptions
  - Graceful handling of incomplete financial data

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage across all modules
  - 100% coverage for simulation and financial calculation functions
  - Comprehensive test suite for tax optimization algorithms
  - Thorough validation of Monte Carlo simulation statistical properties
  - Complete testing of geographic arbitrage comparison logic

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Savings rate calculations accurately predict time to financial independence
- Monte Carlo simulations provide statistically valid withdrawal success rates
- Geographic arbitrage comparisons show meaningful cost of living differences
- Tax-optimized withdrawal strategies demonstrably improve portfolio longevity
- Coast FIRE calculations correctly identify the threshold for reduced contributions
- All financial projections match expected results from established models
- System accommodates various FIRE approaches (lean, traditional, fat)
- Portfolio simulations reflect realistic market behavior and volatility
- Performance meets or exceeds all benchmark requirements
- Test coverage meets or exceeds specified metrics

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.