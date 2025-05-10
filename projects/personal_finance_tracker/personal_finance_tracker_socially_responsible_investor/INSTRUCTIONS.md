# Values-Aligned Investment Management System

## Overview
A specialized financial management system designed for socially responsible investors who want to align their investments with their ethical values while optimizing financial returns. This solution provides tools for ethical screening, impact tracking, shareholder voting analysis, exposure assessment, and values-based budgeting to enable a holistic approach to aligning financial decisions with personal values.

## Persona Description
Miguel aligns his investments with his ethical values and wants to track both financial performance and social impact. He needs to evaluate investments against environmental, social, and governance (ESG) criteria while optimizing his portfolio returns.

## Key Requirements
1. **Ethical investment screening using customizable value-based criteria**
   - Support for user-defined ethical frameworks and priorities
   - Multi-factor screening against environmental, social, governance, and custom criteria
   - Investment scoring and ranking based on values alignment
   - Threshold-based filtering for investment consideration
   - Critical for ensuring investments align with personal values while providing flexibility in defining what those values entail

2. **Impact metric tracking beyond pure financial returns (carbon avoided, community investment)**
   - Quantification of non-financial impacts of investments
   - Environmental metrics (carbon footprint, waste reduction, resource efficiency)
   - Social metrics (community investment, labor practices, human rights)
   - Governance metrics (board diversity, executive compensation, transparency)
   - Essential for understanding the real-world impact of investments beyond financial performance

3. **Shareholder voting record assessment for companies in portfolio**
   - Tracking of company proxy voting history on ethical issues
   - Analysis of management versus shareholder proposal voting patterns
   - Alignment assessment between voting records and investor values
   - Historical comparison of voting patterns over time
   - Necessary for engaging with companies as an active shareholder and ensuring proper stewardship of ownership rights

4. **Industry and sector exposure analysis highlighting concentration in specific areas**
   - Segmentation of investments by industry, sector, and controversy exposure
   - Identification of hidden connections between different investments
   - Supply chain and subsidiary relationship mapping
   - Controversial exposure flagging and quantification
   - Vital for understanding portfolio composition and avoiding unintended exposure to problematic industries or practices

5. **Values-aligned budget categories showing spending alignment with personal principles**
   - Extension of ethical framework from investments to personal spending
   - Categorization of expenses based on values impact
   - Spending pattern analysis for values consistency
   - Impact improvement recommendations across financial life
   - Important for creating consistency between investment choices and daily financial decisions

## Technical Requirements
- **Testability Requirements**
  - Ethical scoring algorithms must be deterministic and unit-testable
  - Impact calculations must be verifiable against known benchmarks
  - Portfolio analysis functions must produce consistent results
  - Values-based categorization must be testable with defined rules
  - Performance must be measurable under various data volume scenarios

- **Performance Expectations**
  - Support for screening large investment universes (5,000+ securities)
  - Fast recalculation of portfolio scores when criteria change
  - Efficient handling of complex impact metric calculations
  - Quick industry and sector analysis across diverse portfolios
  - Responsive operation when categorizing high transaction volumes

- **Integration Points**
  - Import capabilities for investment holdings and transactions
  - Access to ESG and ethical investing data sources
  - Integration with proxy voting records and databases
  - Connection to industry classification standards
  - Import of personal financial transaction data

- **Key Constraints**
  - Transparency in all scoring and assessment methodologies
  - Clear documentation of data sources and calculation methods
  - Flexibility to accommodate diverse ethical frameworks
  - Regular updates to reflect changing company practices
  - Accuracy in impact quantification while acknowledging limitations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide these core components:

1. **Ethical Framework Management**
   - Value definition and prioritization
   - Ethical criteria creation and weighting
   - Scoring threshold configuration
   - Framework version control and evolution

2. **Investment Screening and Analysis**
   - Security evaluation against ethical criteria
   - Portfolio-level ethical performance assessment
   - Comparative analysis of investment alternatives
   - Recommendation engine for portfolio improvement

3. **Impact Measurement and Reporting**
   - Multi-dimensional impact quantification
   - Impact comparison against benchmarks
   - Progress tracking over time
   - Comprehensive impact reporting

4. **Proxy Voting and Corporate Governance**
   - Voting record collection and categorization
   - Alignment analysis with investor values
   - Historical voting pattern tracking
   - Shareholder engagement opportunity identification

5. **Portfolio Composition Analysis**
   - Industry and sector classification
   - Exposure assessment and quantification
   - Relationship mapping between holdings
   - Controversial exposure identification

6. **Values-Based Personal Finance**
   - Transaction categorization by values alignment
   - Spending pattern impact analysis
   - Consistency assessment between investments and spending
   - Improvement recommendation generation

## Testing Requirements
- **Key Functionalities for Verification**
  - Accuracy of ethical screening methodologies
  - Precision of impact metric calculations
  - Correctness of voting record assessments
  - Proper industry and sector exposure analysis
  - Accurate values-based transaction categorization

- **Critical User Scenarios**
  - Defining a custom ethical framework and screening investments
  - Tracking multiple impact metrics across a diverse portfolio
  - Analyzing shareholder voting records of portfolio companies
  - Identifying problematic industry exposures and hidden connections
  - Categorizing personal spending according to values alignment

- **Performance Benchmarks**
  - Screening of 5,000+ securities against multiple criteria in under 30 seconds
  - Calculation of comprehensive impact metrics for 100+ holdings in under 10 seconds
  - Analysis of 5+ years of voting records for 50+ companies in under 15 seconds
  - Complete industry and controversy exposure analysis in under 5 seconds
  - Categorization of 10,000+ transactions by values in under 20 seconds

- **Edge Cases and Error Conditions**
  - Handling of investments with limited ESG disclosure
  - Management of conflicting ethical criteria
  - Adaptation to changing corporate practices and structures
  - Recovery from incomplete or contradictory data sources
  - Proper handling of complex ownership structures
  - Graceful management of subjective ethical boundaries

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage across all modules
  - 100% coverage for ethical scoring and impact calculation functions
  - Comprehensive test suite for industry classification algorithms
  - Thorough validation of voting record analysis
  - Complete testing of values-based categorization logic

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Ethical screening correctly identifies investments matching defined criteria
- Impact metrics accurately reflect real-world effects of investments
- Voting record assessments properly categorize corporate governance actions
- Industry and sector analysis correctly identifies all relevant exposures
- Values-based transaction categorization aligns with defined ethical framework
- All portfolio calculations match expected results with high precision
- System accommodates diverse ethical frameworks without bias
- Impact quantification is transparent and methodologically sound
- Performance meets or exceeds all benchmark requirements
- Test coverage meets or exceeds specified metrics

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.