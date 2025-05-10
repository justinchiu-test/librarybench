# Insurance Risk Assessment Language

A domain-specific language toolkit for defining, calculating, and analyzing insurance risk models.

## Overview

This project delivers a specialized domain-specific language toolkit that enables insurance actuaries and underwriters to define precise risk calculation logic for insurance products. The toolkit translates complex risk assessment rules into executable formulas, ensuring consistency across different insurance products while providing statistical validation, regulatory compliance checking, and sensitivity analysis capabilities without requiring programming expertise.

## Persona Description

Olivia leads risk management for an insurance company that needs to define complex underwriting rules. Her primary goal is to create a risk assessment language that allows actuaries and underwriters to precisely define risk calculation logic while ensuring consistency across different insurance products.

## Key Requirements

1. **Statistical model integration with uncertainty quantification**
   - Essential for Olivia because actuarial risk assessment depends on complex statistical models with different distributions and confidence intervals, and these must be expressed precisely in risk calculations.
   - The DSL must provide syntax for incorporating statistical models, distribution parameters, and uncertainty quantification techniques, allowing actuaries to express the mathematical core of insurance risk assessment.

2. **Risk factor relationship visualization with correlation analysis**
   - Critical because insurance risk involves multiple interconnected factors with complex correlation patterns, and Olivia needs to understand and communicate these relationships to make sound underwriting decisions.
   - The system must analyze relationships between defined risk factors to identify correlations, dependencies, and potential interaction effects, generating structured data for visualization and analysis.

3. **Historical data validation against previous assessments**
   - Vital because new risk models must be validated against historical outcomes to ensure predictive accuracy, and Olivia needs to verify that risk calculation logic performs as expected on known scenarios.
   - The toolkit must support backtesting risk models against historical data, calculating prediction accuracy metrics, and identifying scenarios where model performance deviates from expected outcomes.

4. **Compliance verification with insurance regulations**
   - Necessary because insurance risk assessment is subject to strict regulatory requirements that vary by jurisdiction and product type, and Olivia needs to ensure that risk models comply with all applicable regulations.
   - The DSL must facilitate defining regulatory constraints, validation rules, and compliance checks that verify risk assessment logic against regulatory frameworks before deployment.

5. **Sensitivity analysis identifying critical decision factors**
   - Important because understanding which factors most significantly impact risk assessments is crucial for prioritizing underwriting criteria and explaining decisions, and Olivia needs to quantify these impacts systematically.
   - The system must provide methods for performing sensitivity analysis on risk models, measuring how changes in input factors affect overall risk scores and identifying the most influential variables.

## Technical Requirements

- **Testability Requirements**
  - All risk calculation logic must be testable with simulated and historical data
  - Statistical model implementations must be validated against known distributions
  - Compliance rules must be verified through formal validation methods
  - Sensitivity analysis results must be reproducible and statistically significant
  - Risk factor correlations must achieve statistical validity thresholds

- **Performance Expectations**
  - Risk calculation must complete within 200ms for individual policies
  - Batch processing must handle 10,000 policies per minute
  - The system must support risk models with up to 500 factors and variables
  - Memory usage must not exceed 400MB for the toolkit core
  - Statistical validation should process 5 years of historical data within 5 minutes

- **Integration Points**
  - Actuarial systems for statistical model integration
  - Policy administration systems for underwriting automation
  - Compliance management systems for regulatory verification
  - Data warehouses for historical data access
  - Reporting platforms for risk analytics visualization

- **Key Constraints**
  - Must maintain data privacy compliance (GDPR, HIPAA, etc.)
  - Must provide full auditability of all risk calculations
  - Must handle missing or incomplete data with appropriate strategies
  - Must support versioning of risk models with change tracking
  - Must accommodate different calculation methods by jurisdiction

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces. The visualization capabilities should generate structured data that could be visualized by external tools, not implementing the visualization itself.

## Core Functionality

The core functionality of the Insurance Risk Assessment Language encompasses:

1. **Risk Model Definition Language**
   - Insurance domain-specific syntax for risk factors and calculations
   - Statistical distribution parameter specification
   - Conditional logic for underwriting rules
   - Factor weighting and scoring methodology
   - Product-specific risk calculation templates

2. **Statistical Analysis Framework**
   - Distribution fitting and parameter estimation
   - Confidence interval calculation
   - Correlation and covariance analysis
   - Uncertainty quantification methods
   - Monte Carlo simulation capabilities

3. **Validation and Verification System**
   - Historical data comparison methods
   - Model performance metric calculation
   - Outlier detection and analysis
   - Cross-validation techniques
   - Predictive accuracy assessment

4. **Regulatory Compliance Engine**
   - Regulatory rule definition and mapping
   - Jurisdiction-specific requirement checking
   - Documentation generation for compliance evidence
   - Explainability features for regulatory review
   - Audit trail creation for decision transparency

5. **Sensitivity and Scenario Analysis**
   - Factor impact measurement techniques
   - What-if scenario definition and execution
   - Stress testing methodology
   - Key factor identification algorithms
   - Decision boundary analysis

## Testing Requirements

- **Key Functionalities to Verify**
  - Risk calculation accuracy and consistency
  - Statistical model implementation correctness
  - Regulatory compliance validation effectiveness
  - Historical data validation methodology
  - Sensitivity analysis result accuracy

- **Critical User Scenarios**
  - Actuary defining a new risk model for an insurance product
  - Underwriter applying risk assessment to a specific policy application
  - Compliance officer verifying model against regulatory requirements
  - Product manager analyzing risk factor importance for pricing decisions
  - Data scientist validating model performance against historical outcomes

- **Performance Benchmarks**
  - Risk calculation: < 200ms per individual risk assessment
  - Batch processing: > 10,000 assessments per minute
  - Statistical validation: < 5 minutes for 5 years of historical data
  - Compliance checking: < 10 seconds for full regulatory validation
  - Sensitivity analysis: < 30 seconds for comprehensive factor analysis

- **Edge Cases and Error Conditions**
  - Handling incomplete or contradictory risk factor data
  - Managing statistical anomalies and outliers
  - Addressing conflicts between regulatory requirements
  - Graceful degradation when historical data is limited
  - Handling complex correlation structures and multicollinearity

- **Required Test Coverage Metrics**
  - Minimum 95% code coverage for all modules
  - 100% coverage of risk calculation core algorithms
  - Complete verification of regulatory compliance rules
  - All statistical model implementations must be validated
  - Full coverage of sensitivity analysis algorithms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Actuaries can define complete risk models without writing traditional code
2. Risk calculations produce results consistent with actuarial expectations
3. The system correctly identifies 95% of regulatory compliance issues before deployment
4. Historical validation achieves 90% accuracy in predicting known outcomes
5. Sensitivity analysis correctly identifies the most influential risk factors
6. Risk models maintain consistency across different insurance products
7. The test suite validates all core functionality with at least 95% coverage
8. Performance benchmarks are met under typical insurance industry workloads

## Getting Started

To set up the development environment:

```bash
# Initialize the project
uv init --lib

# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run a specific test
uv run pytest tests/test_risk_model.py::test_statistical_validation

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

When implementing this project, remember to focus on creating a library that can be integrated into insurance underwriting systems rather than a standalone application with user interfaces. All functionality should be exposed through well-defined APIs, with a clear separation between the risk assessment language and any future visualization or UI components.