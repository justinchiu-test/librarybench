# Values-Aligned Financial Management System

A personal finance tracker that integrates ethical considerations with financial analytics, allowing users to track both financial performance and social impact of their investments and spending.

## Overview

This library provides a financial management system designed specifically for socially responsible investors who want to align their financial activities with their ethical values. It focuses on ethical investment screening, impact metric tracking, corporate governance analysis, portfolio composition analysis, and values-aligned budgeting.

## Persona Description

Miguel aligns his investments with his ethical values and wants to track both financial performance and social impact. He needs to evaluate investments against environmental, social, and governance (ESG) criteria while optimizing his portfolio returns.

## Key Requirements

1. **Ethical investment screening using customizable value-based criteria**
   - User-defined ESG criteria with weighting capabilities
   - Investment evaluation against defined ethical standards
   - Screening rule creation, testing, and validation
   - This feature is critical for investors to filter potential investments based on their personal values, allowing them to exclude companies or sectors that violate their ethical principles

2. **Impact metric tracking beyond pure financial returns (carbon avoided, community investment)**
   - Quantification of social and environmental impact metrics
   - Comparison of impact metrics against financial performance
   - Historical tracking of impact improvements over time
   - This feature provides a more comprehensive view of investment performance that includes positive societal and environmental outcomes in addition to financial returns

3. **Shareholder voting record assessment for companies in portfolio**
   - Proxy voting history tracking for owned securities
   - Voting recommendation analysis based on ethical criteria
   - Participation rate monitoring for shareholder activism
   - This feature enables active ownership by helping investors make informed decisions about shareholder votes and track their involvement in corporate governance

4. **Industry and sector exposure analysis highlighting concentration in specific areas**
   - Portfolio composition analysis by industry, sector, and subsector
   - Ethical risk assessment based on sector concentrations
   - Diversification recommendations considering both financial and ethical factors
   - This feature helps investors understand their exposure to different industries and identify potential ethical concerns or opportunities for diversification

5. **Values-aligned budget categories showing spending alignment with personal principles**
   - Customizable ethical categorization for personal spending
   - Impact scoring for consumption choices
   - Spending pattern analysis through an ethical lens
   - This feature extends ethical alignment beyond investments to daily spending decisions, helping users ensure their entire financial life reflects their values

## Technical Requirements

### Testability Requirements
- All ethical screening algorithms must have unit tests with ≥90% code coverage
- Test data representing diverse investment types and ethical criteria
- Mock implementations for any external data providers
- Verification of impact calculations against reference standards

### Performance Expectations
- Ethical screening of 1000+ securities in under 5 seconds
- Impact metric calculation for 100+ portfolio holdings in under 3 seconds
- Portfolio analysis operations should complete in under 2 seconds
- System should remain responsive with 10+ years of transaction and investment history

### Integration Points
- Import functionality for investment portfolio data
- Export capabilities for impact reporting
- Optional integration with ESG data providers
- Data import from financial institutions when available

### Key Constraints
- Transparency in all ethical evaluation methodologies
- Clear separation between factual data and ethical interpretations
- User ownership and control of all ethical definitions and weightings
- No reliance on proprietary ESG scoring without methodology transparency

## Core Functionality

The system must provide these core components:

1. **Ethical Criteria Management**:
   - Custom criteria definition interface
   - Weighting and scoring configuration
   - Value priority ranking
   - Criteria verification and testing

2. **Investment Portfolio Analysis**:
   - Security-level ethical screening
   - Performance tracking (financial and impact)
   - Holding period return calculation
   - Comparative benchmark analysis

3. **Impact Measurement System**:
   - Quantifiable impact metric tracking
   - Impact attribution by investment
   - Historical impact trend analysis
   - Impact vs. financial return visualization

4. **Active Ownership Tools**:
   - Shareholder vote tracking
   - Proxy voting analysis
   - Engagement activity recording
   - Effectiveness assessment

5. **Values-Based Financial Planning**:
   - Ethical budget category definition
   - Spending pattern ethical analysis
   - Value alignment scoring
   - Improvement recommendation engine

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of ethical screening across diverse investment types
- Correct calculation of impact metrics and comparison with financial returns
- Proper tracking and analysis of shareholder voting history
- Accurate portfolio composition analysis by industry and sector
- Correct classification of spending according to ethical categories

### Critical User Scenarios
- Setting up personalized ethical investment criteria
- Analyzing a portfolio for both financial performance and ethical alignment
- Tracking shareholder votes and engagement activities
- Identifying industry/sector concentration and associated ethical risks
- Categorizing personal spending according to ethical considerations

### Performance Benchmarks
- Complete ethical screening of a 100-security portfolio in under 5 seconds
- Generate comprehensive impact reports in under 3 seconds
- Analyze 5+ years of shareholder voting history in under 2 seconds
- Process 10,000+ spending transactions for ethical categorization in under 10 seconds

### Edge Cases and Error Conditions
- Handling investments with incomplete or conflicting ESG data
- Proper management of complex ethical criteria with potentially contradictory elements
- Graceful handling of securities that change ethical status due to corporate actions
- Recovery from incorrect ethical categorization
- Handling of mixed ethical signals across different frameworks

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of ethical screening and impact calculation algorithms
- Comprehensive tests for various ethical frameworks and criteria
- Performance tests for operations on large portfolios and transaction sets

## Success Criteria

The implementation will be considered successful when:

1. Users can define, test, and apply custom ethical criteria to investment screening
2. Impact metrics are tracked alongside financial returns to provide a complete performance picture
3. Shareholder voting activities are properly recorded and analyzed against ethical priorities
4. Portfolio composition analysis clearly shows industry/sector concentrations and associated ethical considerations
5. Personal spending can be categorized and analyzed according to ethical values
6. All calculations are transparent and methodologies are clearly documented
7. The system maintains performance with realistic investment portfolios and spending histories
8. All tests pass with the required coverage and performance benchmarks

## Getting Started

To set up the development environment:

```bash
cd /path/to/project
uv init --lib
```

This will create a virtual environment and generate a `pyproject.toml` file. To install dependencies:

```bash
uv sync
```

To run individual Python scripts:

```bash
uv run python script.py
```

To run tests:

```bash
uv run pytest
```

The implementation should focus on creating a flexible system that allows users to evaluate and manage their finances through the lens of their personal ethical values while maintaining solid financial analysis capabilities.