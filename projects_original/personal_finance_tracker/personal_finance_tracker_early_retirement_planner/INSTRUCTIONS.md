# Financial Independence and Early Retirement Planning System

## Overview
A sophisticated financial planning system designed specifically for individuals pursuing financial independence and early retirement (FIRE). The system provides advanced tools for savings rate analysis, withdrawal strategy modeling, geographic arbitrage evaluation, tax-optimized withdrawal planning, and milestone tracking for achieving financial freedom.

## Persona Description
Dr. Chen is pursuing financial independence and early retirement (FIRE) through aggressive saving and investing. He needs detailed projections of passive income, withdrawal strategies, and portfolio longevity to plan his transition from working life.

## Key Requirements
1. **Savings rate analysis showing percentage of income preserved and path to independence**  
   Dr. Chen needs to track and optimize his savings rate as the primary driver of his path to financial independence. The system must calculate his true savings rate (accounting for pre-tax and post-tax contributions), project the timeline to financial independence based on current and target savings rates, and provide detailed analysis of how spending changes directly impact his FIRE date.

2. **Safe withdrawal rate simulations based on different market performance scenarios**  
   To ensure portfolio longevity through retirement, Dr. Chen needs robust withdrawal modeling. The system must simulate various withdrawal strategies (fixed percentage, variable percentage, floor-and-ceiling, etc.) against different market performance scenarios (historical sequences, Monte Carlo simulations, etc.) to determine safe withdrawal rates that minimize the risk of portfolio depletion over a 40+ year retirement horizon.

3. **Geographic arbitrage comparisons of living costs in different retirement locations**  
   Dr. Chen is considering relocating after achieving financial independence to areas with lower costs of living. The system needs to compare financial requirements across different potential retirement locations, adjusting for regional cost-of-living differences, tax implications, healthcare costs, and currency exchange considerations to determine how location choices affect his required portfolio size.

4. **Tax-optimized withdrawal sequencing across different account types (401k, IRA, taxable)**  
   To maximize tax efficiency in retirement, Dr. Chen needs optimization of withdrawal sequencing. The system must model optimal withdrawal strategies across various account types (taxable, tax-deferred, tax-free) based on applicable tax laws, required minimum distributions, and long-term tax minimization goals to extend portfolio longevity through tax efficiency.

5. **Coast FIRE calculator showing when investments could grow to support retirement without additional contributions**  
   Dr. Chen wants to understand when he might reach "Coast FIRE" - the point at which his existing investments, without additional contributions, would grow to support full retirement by traditional age. The system needs to calculate this milestone, showing how different partial retirement approaches (reduced work hours, lower-paying but more fulfilling work) could be financially viable once this point is reached.

## Technical Requirements
- **Testability Requirements:**
  - Savings rate calculations must be verified against established financial formulas
  - Withdrawal simulations must be benchmarked against historical market data
  - Tax calculations must be validated against current tax code specifications
  - Projection models must be tested with varied economic scenarios

- **Performance Expectations:**
  - Monte Carlo simulations must complete 10,000+ scenarios in under 30 seconds
  - Savings rate projections must recalculate instantly when parameters change
  - Geographic comparisons must handle data for 50+ locations simultaneously
  - Tax optimization must evaluate multiple withdrawal strategies within 5 seconds

- **Integration Points:**
  - Import capability for external investment account data
  - Integration with historical market return datasets
  - Cost-of-living database for geographic comparisons
  - Tax rule database with regular updates

- **Key Constraints:**
  - Calculations must be mathematically rigorous and academically defensible
  - Projections must clearly communicate uncertainty and probability
  - Portfolio modeling must support diverse asset allocations
  - System must adapt to changing tax laws and regulations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement these core components:

1. **Savings Rate Analysis Engine:**
   - True savings rate calculation accounting for all income sources and tax treatments
   - Financial independence timeline projections based on savings rate
   - Spending impact analysis on FIRE timeline
   - Savings rate optimization recommendations
   - Milestone tracking toward financial independence

2. **Withdrawal Strategy Simulator:**
   - Multiple withdrawal method implementations (fixed, variable, floor-ceiling, etc.)
   - Historical sequence and Monte Carlo simulation capabilities
   - Failure rate and portfolio survival analysis
   - Sequence of returns risk assessment
   - Dynamic spending model integration

3. **Geographic Arbitrage Calculator:**
   - Regional cost-of-living database and comparison
   - Housing cost differential analysis
   - Tax burden comparison by location
   - Healthcare cost projections by region
   - Currency exchange risk assessment for international locations

4. **Tax-Optimized Withdrawal Planner:**
   - Account-specific tax treatment modeling
   - Multi-year tax projection and optimization
   - Required Minimum Distribution (RMD) planning
   - Roth conversion strategy analysis
   - Tax-loss harvesting optimization

5. **Coast FIRE and Work Optional Planning:**
   - Coast FIRE threshold calculation
   - Partial retirement scenario modeling
   - Reduced income requirement analysis
   - Semi-retirement sustainability assessment
   - Bridge period planning between partial and full retirement

## Testing Requirements
- **Key Functionalities to Verify:**
  - Savings rate calculations accurately project time to financial independence
  - Withdrawal strategies are properly simulated across market scenarios
  - Geographic cost-of-living differences are correctly analyzed
  - Tax-optimized withdrawal sequences minimize overall tax burden
  - Coast FIRE calculations accurately project investment growth without additional contributions

- **Critical User Scenarios:**
  - Adjusting savings rate and seeing updated FIRE date projections
  - Testing portfolio sustainability with different withdrawal strategies
  - Comparing financial requirements between potential retirement locations
  - Optimizing withdrawals across different account types for tax efficiency
  - Determining the Coast FIRE threshold and exploring semi-retirement options

- **Performance Benchmarks:**
  - Monte Carlo simulations must evaluate 10,000+ randomized scenarios
  - System must handle 40+ year retirement horizon projections
  - Portfolio survival probability calculations must achieve 95% confidence intervals
  - Tax optimization must evaluate at least 20 years of withdrawal sequencing

- **Edge Cases and Error Conditions:**
  - Handling extreme market volatility scenarios
  - Adapting to major tax code changes
  - Managing inflation uncertainty in long-term projections
  - Accounting for unexpected retirement expenses
  - Adapting to changes in retirement date or financial goals

- **Required Test Coverage Metrics:**
  - Savings rate calculation functions: minimum 95% coverage
  - Withdrawal simulation engines: minimum 90% coverage
  - Tax optimization algorithms: minimum 90% coverage
  - Portfolio projection models: minimum 85% coverage

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
- The system accurately calculates savings rates and their impact on financial independence timing
- Safe withdrawal rate simulations provide reliable portfolio longevity projections
- Geographic arbitrage comparisons correctly assess cost-of-living differences between locations
- Tax-optimized withdrawal sequencing demonstrably minimizes tax burden in retirement
- Coast FIRE calculator accurately determines when investment growth alone could support retirement
- All calculations are mathematically sound and properly account for uncertainty
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