# Insurance Risk Assessment Language Toolkit

## Overview
A specialized Domain Specific Language toolkit for defining, analyzing, and implementing complex underwriting and risk assessment rules. This toolkit enables actuaries and underwriters to express precise risk calculation logic while ensuring consistency across different insurance products and maintaining compliance with insurance regulations.

## Persona Description
Olivia leads risk management for an insurance company that needs to define complex underwriting rules. Her primary goal is to create a risk assessment language that allows actuaries and underwriters to precisely define risk calculation logic while ensuring consistency across different insurance products.

## Key Requirements
1. **Statistical model integration with uncertainty quantification**: Seamless incorporation of statistical and actuarial models with explicit handling of uncertainty ranges, confidence intervals, and probability distributions. This is critical because actuarial science fundamentally depends on statistical modeling, and proper uncertainty quantification is essential for accurate risk pricing, capital reserving, and regulatory compliance.

2. **Risk factor relationship visualization with correlation analysis**: Tools to visualize and analyze the relationships between different risk factors, including direct and indirect correlations, mutual dependencies, and combined effects. This is essential because understanding how risk factors interrelate helps underwriters identify hidden risk concentrations, prevent pricing errors based on assumed independence, and develop more nuanced pricing strategies.

3. **Historical data validation against previous assessments**: Mechanisms to validate newly defined risk rules against historical data and previous underwriting decisions to ensure consistency and identify unexpected deviations. This is vital because consistency in underwriting decisions is important for regulatory compliance and customer fairness, and historical validation helps detect unintended consequences of rule changes.

4. **Compliance verification with insurance regulations**: Automated checking of risk assessment rules against relevant insurance regulations, rate filing requirements, and anti-discrimination laws. This is necessary because the insurance industry is heavily regulated with complex compliance requirements that vary by jurisdiction, product type, and customer segment, and automated verification reduces compliance risk.

5. **Sensitivity analysis identifying critical decision factors**: Analytical capabilities to determine which factors have the greatest impact on risk assessment outcomes across different scenarios and customer profiles. This is crucial because understanding factor sensitivity helps prioritize data collection efforts, calibrate pricing models more effectively, and explain underwriting decisions to stakeholders and customers.

## Technical Requirements
- **Testability Requirements**:
  - Each risk rule must be automatically verifiable against historical data
  - Statistical models must be testable with simulated and historical datasets
  - Compliance checking must validate against current regulatory requirements
  - Sensitivity analysis must demonstrate accurate impact attribution
  - All components must achieve at least 90% test coverage

- **Performance Expectations**:
  - Rule evaluation must complete for a single risk assessment in under 500ms
  - Batch processing must handle 10,000+ policy applications in under 10 minutes
  - Statistical model integration must support models with 100+ variables
  - System must process historical validation against 1 million+ previous cases in under 60 minutes

- **Integration Points**:
  - Actuarial modeling systems and libraries
  - Policy administration and underwriting platforms
  - Regulatory compliance databases
  - Claims management systems
  - Customer data repositories and third-party data sources
  - Business intelligence and reporting systems

- **Key Constraints**:
  - Implementation must be in Python with no UI components
  - All risk assessment logic must be expressible through the DSL without requiring custom code
  - Rule definitions must be storable as human-readable text files
  - System must maintain audit trails of all rule changes and applications
  - Performance must scale to handle enterprise-level policy volumes

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Insurance Risk Assessment DSL Toolkit must provide:

1. A domain-specific language parser and interpreter specialized for risk assessment
2. Integration mechanisms for statistical and actuarial models
3. Visualization tools for risk factor relationships and correlations
4. Historical data validation capabilities
5. Regulatory compliance checking framework
6. Sensitivity analysis algorithms for factor impact assessment
7. Rule version control and audit trail maintenance
8. Documentation generators for regulatory filings and internal review
9. Performance optimization for high-volume underwriting operations
10. Test utilities for validating rule accuracy against known outcomes

The system should enable actuaries and underwriters to define elements such as:
- Risk factor definitions and categorizations
- Rating variables and their permissible values
- Pricing algorithms and premium calculations
- Underwriting decision trees and eligibility criteria
- Exception handling for special cases
- Territorial rating plans
- Experience rating modifications
- Regulatory compliance constraints
- Reinsurance thresholds and considerations

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct parsing of DSL syntax into executable risk assessment logic
  - Accurate integration with statistical models and distributions
  - Proper visualization of risk factor relationships
  - Correct validation against historical underwriting decisions
  - Comprehensive compliance checking against regulatory requirements

- **Critical User Scenarios**:
  - Actuary defines new rating algorithm for an insurance product
  - Underwriter creates eligibility rules for a specialized risk segment
  - Compliance officer validates rate plan against regulatory requirements
  - Data scientist analyzes sensitivity of risk factors across customer segments
  - Product manager compares rule performance against historical profitability

- **Performance Benchmarks**:
  - Evaluate 100+ risk factors for a single policy in under 500ms
  - Process batch rating for 10,000 policies in under 10 minutes
  - Validate rule changes against 5 years of historical data in under 30 minutes
  - Generate sensitivity analysis across 50+ factors in under 5 minutes

- **Edge Cases and Error Conditions**:
  - Handling of missing or incomplete applicant data
  - Detection of statistical anomalies in model outputs
  - Management of conflicting regulatory requirements across jurisdictions
  - Behavior during catastrophic event scenarios
  - Graceful degradation when third-party data sources are unavailable

- **Required Test Coverage Metrics**:
  - Minimum 90% code coverage across all modules
  - 100% coverage of risk rule parser and interpreter
  - 100% coverage of compliance verification components
  - 95% coverage of statistical model integration

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
The implementation will be considered successful when:

1. All five key requirements are fully implemented and operational
2. Each requirement passes its associated test scenarios
3. The system demonstrates the ability to express complex insurance risk logic
4. Statistical models are properly integrated with uncertainty quantification
5. Risk factor relationships are accurately visualized and analyzed
6. Historical data validation correctly identifies deviations from past decisions
7. Compliance verification successfully identifies regulatory issues
8. Sensitivity analysis accurately identifies critical decision factors

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
To set up the development environment:

1. Create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```