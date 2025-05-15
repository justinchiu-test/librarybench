# E-Commerce Analytics Query Language Interpreter

## Overview
This specialized Query Language Interpreter enables small business analysts to easily query and analyze sales data, customer information, and inventory across multiple CSV exports from different business systems without requiring dedicated database infrastructure. The interpreter includes built-in retail metrics, supports scheduled reporting, handles Excel formulas, automatically highlights anomalies, and provides multi-currency support.

## Persona Description
Marcus manages analytics for a growing e-commerce business without dedicated database infrastructure. He needs to query sales data, customer information, and inventory across multiple CSV exports from different business systems.

## Key Requirements
1. **Business metrics library with pre-defined calculations for common retail KPIs**: Provides built-in formulas for essential retail metrics (conversion rates, average order value, customer lifetime value, inventory turnover, etc.), saving analysts time and ensuring consistent calculation methods across all reports and analyses.

2. **Scheduled query execution generating automated reports at regular intervals**: Enables setting up recurring queries that automatically run at specified times (daily, weekly, monthly), generating up-to-date reports without manual intervention, crucial for regular business monitoring and consistent decision-making.

3. **Excel-compatible formula translation allowing spreadsheet users to write familiar expressions**: Allows analysts to use Excel-style formulas (SUM, VLOOKUP, IF statements, etc.) within queries, minimizing the learning curve for business users with spreadsheet backgrounds and leveraging their existing formula knowledge.

4. **Anomaly highlighting automatically flagging unusual patterns in business data**: Automatically identifies and highlights statistical outliers, unexpected trends, or suspicious patterns in sales, inventory, or customer behavior, enabling quick detection of data quality issues or business opportunities that require attention.

5. **Multi-currency support with automatic conversion based on transaction dates**: Seamlessly handles transactions in different currencies, automatically converting amounts using appropriate historical exchange rates based on transaction dates, ensuring accurate financial reporting and analysis across international operations.

## Technical Requirements
### Testability Requirements
- All business metric calculations must be independently testable with precise expected outputs
- Scheduled execution functionality must be testable through time simulation, without waiting for actual intervals
- Excel formula translation must be verified against actual Excel outputs for equivalent expressions
- Anomaly detection algorithms must be testable with predetermined datasets containing known anomalies
- Currency conversion operations must be tested against historical exchange rate data

### Performance Expectations
- Must handle data volumes typical for small to medium businesses (up to 1 million transactions per year)
- Query response times should not exceed 3 seconds for typical business analyses
- Scheduled reports should generate within 5 minutes, even for complex cross-system analyses
- Memory utilization should remain under 1GB even when processing multi-year datasets
- Background scheduling should have minimal impact on system resources

### Integration Points
- CSV file import with robust handling of common formatting variations
- Export capabilities for Excel, PDF, and CSV formats
- Optional API for integration with business intelligence tools
- Filesystem integration for scheduled report storage
- Historical exchange rate data source for currency conversion

### Key Constraints
- Must operate without external database dependencies
- Implementation must work reliably on standard business workstations
- All operations must produce results identical to those obtained through manual spreadsheet analysis
- No internet connectivity requirements for core functionality (except exchange rate updates)
- Financial calculations must maintain cent-level precision

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this E-Commerce Analytics Query Language Interpreter includes:

1. **Query Engine**:
   - SQL-like syntax for data operations on CSV and JSON business data
   - Support for joining data across different business system exports
   - Excel-compatible function support within query expressions
   - Execution planning optimized for business analytics patterns

2. **Business Metrics Library**:
   - Pre-defined calculations for standard retail and e-commerce KPIs
   - Customizable metric definitions with parameter support
   - Hierarchical metrics with drill-down capabilities
   - Documentation and formula explanation for each metric

3. **Scheduling Framework**:
   - Configuration system for defining recurring query schedules
   - Report generation and storage in various formats
   - Execution history logging and failure handling
   - Resource utilization controls for background processing

4. **Anomaly Detection System**:
   - Statistical models for identifying outliers in business data
   - Configurable sensitivity and detection thresholds
   - Multiple detection algorithms for different data patterns
   - Contextual analysis considering business cycles and seasonality

5. **Currency Management**:
   - Exchange rate data management with historical tracking
   - Automatic currency conversion in query operations
   - Currency-aware aggregations and calculations
   - Reporting with multiple currency views

## Testing Requirements
### Key Functionalities to Verify
- Accuracy of all business metric calculations compared to industry standards
- Correct execution of scheduled queries according to defined intervals
- Precise translation of Excel formulas into equivalent query operations
- Accurate identification of known anomalies in test datasets
- Correct currency conversions using historical exchange rates

### Critical User Scenarios
- Analyzing sales performance across product categories and time periods
- Tracking inventory levels and identifying potential stockout situations
- Evaluating customer segments based on purchase history and value
- Generating end-of-month financial reports with multi-currency data
- Identifying unusual transactions or patterns requiring investigation

### Performance Benchmarks
- Query execution time must not exceed 3 seconds for typical business reports on datasets up to 500MB
- Scheduled report generation must complete within 5 minutes, even for complex reports
- Memory usage must remain under 1GB during normal operation
- CPU utilization during background operations must not exceed 20% of available resources
- Dataset import operations must process at least 10,000 records per second

### Edge Cases and Error Conditions
- Handling inconsistent or missing data in business exports
- Proper management of currency conversions with missing exchange rates
- Graceful degradation when scheduled query execution fails
- Appropriate handling of Excel formulas without direct query equivalents
- Correct behavior with fiscal year boundaries and accounting periods

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage for financial calculation and currency conversion functions
- All business metrics must have dedicated test cases with known correct results
- All error handling paths must be explicitly tested
- Performance tests must verify system behavior with maximum expected data volumes

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
A successful implementation will:

1. Enable accurate calculation of standard retail business metrics, verified through tests comparing results to industry-standard definitions
2. Support scheduled execution of queries with configurable intervals, demonstrated by tests using simulated time progression
3. Correctly translate Excel-style formulas into query operations, validated through comparison with actual Excel calculations
4. Identify anomalies in business data with configurable sensitivity, verified using datasets with known outliers
5. Properly handle multi-currency data with accurate conversion based on transaction dates, confirmed through tests with historical exchange rate data

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up your development environment:

```bash
# From within the project directory
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```