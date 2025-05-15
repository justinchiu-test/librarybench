# Manufacturing Operations Intelligence System

A specialized automated report generation framework for operations directors to monitor production metrics, identify bottlenecks, and distribute targeted insights to different operational teams.

## Overview

The Manufacturing Operations Intelligence System is a Python-based library designed to generate comprehensive production reports that highlight efficiency metrics and quality control issues. It collects data from production systems in real-time, performs anomaly detection, and creates role-specific reports for different departments to enable quick identification of operational bottlenecks and quality concerns.

## Persona Description

Marcus oversees manufacturing operations and needs daily production reports that highlight efficiency metrics and quality control issues. His goal is to identify operational bottlenecks quickly and distribute targeted reports to different departments based on their specific responsibilities.

## Key Requirements

1. **Real-time Production Data Integration**: Implement connectors for IoT devices, production line sensors, and manufacturing execution systems to collect operational data in real-time.
   - *Critical for Marcus because*: Manufacturing efficiency depends on identifying issues as they occur, not after a production run has completed, allowing for immediate intervention and minimizing lost productivity.

2. **Anomaly Detection System**: Develop algorithms that automatically identify deviations from normal operations and highlight unusual patterns in production metrics.
   - *Critical for Marcus because*: With thousands of data points generated daily, manually reviewing all metrics is impossible, and automated detection of significant deviations is essential for timely problem-solving.

3. **Shift Comparison Analytics**: Create a framework to compare performance across different shifts while accounting for staffing levels, equipment configurations, and other variables.
   - *Critical for Marcus because*: Understanding the true drivers of performance variation between shifts allows for standardizing best practices and ensuring consistent productivity regardless of which team is working.

4. **Role-Based Report Distribution**: Build a system to generate and distribute customized report versions for different operational teams based on their specific responsibilities.
   - *Critical for Marcus because*: Each department (production, quality, maintenance, etc.) needs focused information relevant to their responsibilities without being overwhelmed by irrelevant data from other areas.

5. **Root Cause Analysis Templates**: Implement structured templates for linking quality issues to specific production factors and tracking resolution progress.
   - *Critical for Marcus because*: Systematically connecting quality problems to their causes accelerates problem resolution and enables preventive actions to avoid recurrence of similar issues.

## Technical Requirements

### Testability Requirements
- All data connectors must be testable with simulated production data
- Anomaly detection algorithms must be verifiable with labeled test datasets
- Shift comparison functionality must be testable with controlled variable scenarios
- Report generation and distribution must be testable without actual email delivery

### Performance Expectations
- Real-time data processing must handle up to 1,000 sensor inputs with sub-second latency
- Daily report generation must complete within 5 minutes for a complete facility
- Anomaly detection must process 24 hours of production data in under 2 minutes
- System must perform efficiently with 5+ years of historical production data for trend analysis

### Integration Points
- Standard connectors for industrial IoT devices and sensors
- Integration with manufacturing execution systems (MES)
- Compatibility with quality management systems (QMS)
- Output to email, shared drives, and optional dashboard systems

### Key Constraints
- Must handle periodic data gaps from sensor failures
- Must support 24/7 operation with high availability
- Must accommodate various manufacturing shift patterns
- Must maintain data integrity during network interruptions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Manufacturing Operations Intelligence System must provide the following core functionality:

1. **Production Data Acquisition**
   - Connect to and ingest data from industrial sensors and systems
   - Validate data quality and handle anomalous inputs
   - Synchronize data from different sources with varying timescales
   - Buffer data during connectivity interruptions for later processing

2. **Operational Analytics Engine**
   - Calculate key production metrics (OEE, yield, cycle time, etc.)
   - Detect anomalies and deviations from expected performance
   - Compare metrics across shifts, products, and equipment
   - Identify trends and patterns in production data

3. **Quality Control Integration**
   - Link quality defects to production parameters
   - Track defect rates and categories
   - Support root cause analysis workflows
   - Generate quality control charts and metrics

4. **Report Generation and Distribution**
   - Create role-specific report templates
   - Generate daily and shift-based production reports
   - Distribute reports to appropriate teams
   - Support scheduled and on-demand reporting

5. **Historical Analysis Framework**
   - Maintain historical production data
   - Provide comparative analysis against historical performance
   - Support long-term trend identification
   - Enable data-driven process improvement

## Testing Requirements

### Key Functionalities to Verify

1. **Data Collection Reliability**
   - Verify that connectors can reliably collect data from various sources
   - Test handling of interrupted connections and data recovery
   - Verify time synchronization across different data sources
   - Confirm appropriate handling of invalid or out-of-range data

2. **Anomaly Detection Accuracy**
   - Verify detection of common manufacturing anomalies
   - Test detection sensitivity and specificity with labeled datasets
   - Verify appropriate handling of seasonal and cyclical variations
   - Confirm that legitimate process changes are not flagged as anomalies

3. **Shift Comparison Functionality**
   - Verify accurate normalization for staffing and equipment variables
   - Test comparison logic across different shift patterns
   - Confirm proper isolation of shift-specific factors
   - Verify appropriate handling of shift transitions

4. **Report Distribution Mechanics**
   - Verify that role-based filtering correctly targets information
   - Test report generation for all defined roles
   - Confirm that sensitive information is appropriately controlled
   - Verify distribution mechanisms function as expected

5. **Root Cause Analysis Tools**
   - Verify the linking of quality issues to production parameters
   - Test tracking of resolution progress
   - Confirm appropriate template population
   - Verify historical tracking of recurring issues

### Critical User Scenarios

1. Generating daily production reports highlighting significant deviations
2. Creating shift handover reports with key issues requiring attention
3. Performing comparison analysis between shifts to identify best practices
4. Distributing targeted quality alerts to relevant departments
5. Conducting root cause analysis for a recurring quality issue

### Performance Benchmarks

- Real-time data collection must process 1,000 data points per second
- Anomaly detection must identify critical issues within 5 minutes of occurrence
- Report generation must complete within 5 minutes for comprehensive daily reports
- System must support at least 100 concurrent users accessing reports
- Historical queries must return results for 1 year of data within 30 seconds

### Edge Cases and Error Conditions

- Handling of sensor failures and data gaps
- Appropriate processing during production line changeovers
- Correct operation during facility maintenance periods
- Handling of product introductions with limited historical data
- Appropriate analysis during abnormal operating conditions (e.g., partial facility shutdown)

### Required Test Coverage Metrics

- Minimum 90% line coverage for all code
- 100% coverage of data ingestion interfaces
- 100% coverage of anomaly detection algorithms
- Comprehensive coverage of error handling and recovery mechanisms
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

A successful implementation of the Manufacturing Operations Intelligence System will meet the following criteria:

1. **Operational Visibility**: Provides clear, timely insights into manufacturing performance across all production lines.

2. **Anomaly Identification**: Automatically detects and highlights significant deviations from normal operations for immediate attention.

3. **Comparative Analysis**: Enables meaningful comparisons between shifts, products, and equipment to identify best practices and improvement opportunities.

4. **Targeted Communication**: Successfully delivers relevant, role-specific information to different operational teams without overwhelming them.

5. **Problem Resolution**: Facilitates systematic root cause analysis and tracking of quality issues to resolution.

6. **Efficiency Impact**: Reduces the time to identify and address production issues by at least 50% compared to manual methods.

7. **Data Integration**: Successfully consolidates data from multiple production systems into a unified analytical framework.

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