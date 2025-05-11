# Campaign Performance Report Generator

A specialized automated report generation framework for marketing managers to compile performance metrics from various digital platforms into cohesive, visually engaging reports.

## Overview

The Campaign Performance Report Generator is a Python-based library designed to automate the collection, analysis, and presentation of digital marketing campaign data. It connects directly to advertising and social media platforms, processes performance metrics, and generates comprehensive reports that effectively communicate campaign results. The system enables marketing managers to focus on strategy and insight rather than manual data aggregation.

## Persona Description

Diego manages digital marketing campaigns and needs to compile performance metrics from various platforms into cohesive reports for clients and leadership. His goal is to create visually engaging reports that tell a story about campaign performance with minimal manual data processing.

## Key Requirements

1. **Marketing Platform API Integrations**: Implement direct API connections to major advertising platforms (Google Ads, Meta/Facebook Ads, LinkedIn, Twitter) and social media analytics.
   - *Critical for Diego because*: Manually downloading data from each platform is extremely time-consuming and error-prone, especially when managing multiple campaigns across multiple platforms.

2. **Marketing KPI Framework**: Develop a comprehensive system for calculating standardized marketing KPIs and attribution models that transform raw platform data into meaningful metrics.
   - *Critical for Diego because*: Different platforms report metrics differently, and Diego needs to present unified, cross-platform KPIs that clearly communicate performance regardless of where campaigns run.

3. **Creative Asset Embedding**: Create functionality to dynamically embed actual ad creatives, social media posts, and landing page screenshots within reports.
   - *Critical for Diego because*: Marketing reports are significantly more valuable when the performance data is directly connected to the creative assets, providing context for why certain campaigns performed better than others.

4. **Competitive Benchmarking**: Build a system to incorporate industry benchmarks and competitive performance data for comparison against campaign results.
   - *Critical for Diego because*: Stakeholders always want to know how campaign performance compares to industry standards and competitors, providing crucial context for evaluating success.

5. **Conversion Funnel Visualization**: Implement sophisticated conversion funnel analytics that track user progression through marketing touchpoints.
   - *Critical for Diego because*: Understanding the entire customer journey from initial awareness to conversion is essential for optimizing campaign performance and allocation of marketing budget.

## Technical Requirements

### Testability Requirements
- All API connectors must be testable with mock responses that simulate platform data
- KPI calculations must be verifiable against manually calculated values with test datasets
- Report generation must be testable with synthetic campaign data
- Creative asset handling must be testable with sample image files

### Performance Expectations
- Data extraction across all marketing platforms must complete within 10 minutes
- Report generation must complete within 1 minute for standard campaign reports
- The system must efficiently handle campaigns with up to 50 different ad variations
- Memory usage must remain reasonable even when processing image-heavy reports

### Integration Points
- Direct API connections to major advertising and social media platforms
- Import capabilities for CSV/Excel exports from platforms without accessible APIs
- Integration with image and creative asset repositories
- Export capabilities to PDF, PowerPoint, and interactive HTML formats

### Key Constraints
- Must handle authentication securely for multiple marketing platforms
- Must accommodate frequent changes in platform APIs and data structures
- Must process and store creative assets efficiently
- Must support multiple client accounts with appropriate data separation

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Campaign Performance Report Generator must provide the following core functionality:

1. **Data Acquisition and Normalization**
   - Connect to and extract data from various marketing platforms via APIs
   - Normalize data from different platforms into a consistent format
   - Handle authentication and rate limiting for each platform
   - Support both real-time and historical data retrieval

2. **Marketing Analytics Processing**
   - Calculate standardized KPIs across platforms (CTR, CPC, ROAS, etc.)
   - Implement attribution models for conversion tracking
   - Perform campaign comparison and trend analysis
   - Calculate statistical significance for A/B test results

3. **Creative Asset Management**
   - Retrieve and store creative assets from campaigns
   - Process images for appropriate inclusion in reports
   - Link performance metrics directly to creative variations
   - Support various creative formats (images, videos, landing pages)

4. **Benchmark Integration**
   - Maintain industry benchmark datasets by vertical
   - Compare campaign performance against relevant benchmarks
   - Incorporate competitive intelligence when available
   - Generate percentile rankings for key metrics

5. **Report Generation**
   - Create formatted reports from marketing-specific templates
   - Generate appropriate visualizations for marketing data
   - Build interactive conversion funnels with drill-down capabilities
   - Structure reports to tell a coherent story about campaign performance

## Testing Requirements

### Key Functionalities to Verify

1. **Platform API Integration**
   - Verify that connectors can successfully authenticate and retrieve data
   - Test error handling when APIs change or become unavailable
   - Verify that rate limiting and pagination are handled correctly
   - Confirm that data from different platforms is normalized consistently

2. **Marketing Metric Calculation**
   - Verify all KPI calculations against manually calculated values
   - Test attribution models with various customer journey scenarios
   - Verify trend analysis across campaign timeframes
   - Confirm statistical validity of performance comparisons

3. **Creative Asset Handling**
   - Verify that creative assets are retrieved and stored correctly
   - Test image processing for different report formats
   - Confirm proper linking between assets and performance data
   - Verify that reports remain performant with many creative elements

4. **Benchmark Comparison**
   - Verify accurate integration of benchmark data
   - Test comparison logic for different metrics and verticals
   - Confirm percentile calculations and rankings
   - Verify appropriate contextual presentation of comparative data

5. **Report Generation Process**
   - Test the complete pipeline from data acquisition to final report
   - Verify that reports are structured according to specifications
   - Test performance with campaigns of different sizes and complexities
   - Verify that conversion funnels accurately represent user journeys

### Critical User Scenarios

1. Generating a monthly performance report for a multi-channel campaign
2. Creating a campaign comparison report showing performance differences between variants
3. Generating an executive summary with key insights and benchmark comparisons
4. Producing a detailed conversion funnel analysis with drop-off points
5. Creating a creative performance report showing which assets performed best

### Performance Benchmarks

- API data retrieval from all platforms must complete within 10 minutes
- KPI calculations must process data from 50 ad variations in under 1 minute
- Report generation must complete within 1 minute for standard reports
- Creative asset processing must handle up to 100 images efficiently
- Memory usage must not exceed reasonable limits even with image-heavy reports

### Edge Cases and Error Conditions

- Handling of API changes or temporary outages from marketing platforms
- Proper treatment of campaigns that span multiple reporting periods
- Graceful degradation when certain platforms or data points are unavailable
- Appropriate handling of statistical outliers in performance data
- Correct operation during platform maintenance windows

### Required Test Coverage Metrics

- Minimum 90% line coverage for all code
- 100% coverage of API connector interfaces
- 100% coverage of KPI calculation functions
- Comprehensive coverage of error handling and edge cases
- Integration tests for complete report generation workflows

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

A successful implementation of the Campaign Performance Report Generator will meet the following criteria:

1. **Automation Efficiency**: Reduces the time required to generate marketing campaign reports by at least 80% compared to manual processes.

2. **Data Integration**: Successfully consolidates data from at least 5 major marketing platforms into a unified reporting framework.

3. **Insight Generation**: Effectively highlights key performance trends, outliers, and opportunities within marketing campaigns.

4. **Visualization Quality**: Produces visually engaging reports that effectively communicate campaign performance through appropriate charts and graphics.

5. **Creative Context**: Successfully incorporates actual campaign creative assets into reports with direct performance linkage.

6. **Comparison Framework**: Provides meaningful benchmark comparisons that help contextualize campaign performance.

7. **Scalability**: Efficiently handles reporting for multiple clients and campaigns without performance degradation.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:

```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```