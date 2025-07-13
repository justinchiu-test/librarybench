# PyTemplate for Business Report Generation

## Overview
A specialized template rendering engine for creating automated business reports from data warehouse sources, featuring powerful data transformation capabilities, visualizations, and conditional formatting for business analysts.

## Persona Description
A business analyst creating automated reports from data warehouses who needs powerful data transformation capabilities. She requires templates that can handle large datasets and produce formatted reports with charts and tables.

## Key Requirements
1. **SQL query integration with result set templating**: The engine must seamlessly execute SQL queries and incorporate results directly into templates, supporting parameterized queries and multiple data sources. This is critical for creating data-driven reports that pull from various warehouse tables and views.

2. **Data aggregation and pivot table generation**: Built-in functions for aggregating data (sum, average, count, etc.) and creating pivot tables from raw query results. This enables analysts to transform normalized data into business-friendly summary views without external tools.

3. **Chart rendering with customizable visualizations**: Generate charts (bar, line, pie, scatter) directly within templates using Python visualization libraries, with full control over styling and layout. This is essential for creating visually compelling reports that communicate insights effectively.

4. **Conditional formatting based on data values**: Apply formatting rules based on data thresholds and conditions (highlight negative values, color-code performance metrics). This helps readers quickly identify important patterns and outliers in the data.

5. **Report scheduling with parameter injection**: Support for parameterized report generation where date ranges, filters, and other parameters can be injected at runtime. This enables scheduled report generation for different time periods and business units without template modification.

## Technical Requirements
- **Testability**: All data processing and visualization logic must be testable via pytest with mock data sources
- **Performance**: Must handle result sets with 100,000+ rows efficiently with streaming processing
- **Integration**: Clean API for connecting to various data sources (SQL databases, data warehouses)
- **Key Constraints**: No UI components; must support large datasets without memory issues; thread-safe for concurrent report generation

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- SQL query executor with connection pooling and parameterization support
- Data transformation pipeline with aggregation, filtering, and pivot capabilities
- Chart generation system using matplotlib/seaborn with template-friendly API
- Conditional formatting engine with rule-based styling
- Parameter injection system for runtime report customization
- Result set streaming for memory-efficient large data handling
- Data type detection and automatic formatting (currencies, percentages, dates)
- Cross-referencing system for multi-query reports

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **SQL integration tests**: Verify query execution and result incorporation with mock databases
- **Aggregation tests**: Validate correct calculation of sums, averages, and pivot tables
- **Chart generation tests**: Ensure correct chart rendering with various data types
- **Formatting tests**: Verify conditional formatting rules apply correctly
- **Parameter injection tests**: Validate runtime parameter substitution and validation
- **Performance tests**: Benchmark handling of large datasets (100k+ rows)
- **Edge cases**: Handle empty result sets, null values, data type mismatches
- **Memory tests**: Verify streaming processing doesn't cause memory issues

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
The implementation is successful when:
- SQL queries execute and integrate seamlessly into report templates
- Data aggregations and pivot tables calculate correctly for complex datasets
- Charts render accurately with proper scaling and labeling
- Conditional formatting highlights data patterns effectively
- Parameterized reports generate correctly for different date ranges and filters
- Large datasets (100k+ rows) process without memory errors
- Reports generate in under 30 seconds for typical business scenarios
- All tests pass with comprehensive data handling validation

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file