# PyTemplate for Data Pipeline Code Generation

## Overview
A specialized template rendering engine for generating ETL pipeline code across multiple data platforms, featuring SQL dialect translation, reusable transformation patterns, and comprehensive error handling templates.

## Persona Description
A data engineer generating ETL pipeline code who needs templates for various data transformation patterns. He wants to create reusable templates for common data processing tasks across different platforms.

## Key Requirements
1. **SQL dialect translation for multiple databases**: Automatically translate SQL queries between different database dialects (PostgreSQL, MySQL, Snowflake, BigQuery, Redshift) while preserving functionality. This is critical for maintaining portable data pipelines that can run on different infrastructure.

2. **Data transformation pattern library**: Provide a comprehensive library of common transformation patterns (SCD Type 2, data quality checks, aggregations, pivots) that can be customized and combined. This enables rapid pipeline development using proven patterns.

3. **Pipeline DAG generation with dependencies**: Generate directed acyclic graphs (DAGs) for orchestrators like Airflow, Prefect, or Dagster with proper dependency management. This is essential for creating maintainable and monitorable data workflows.

4. **Error handling and retry logic templates**: Include sophisticated error handling patterns with exponential backoff, dead letter queues, and alerting integration. This ensures pipelines are resilient and can recover from transient failures automatically.

5. **Performance optimization hint generation**: Analyze transformations and generate platform-specific optimization hints (partitioning strategies, indexing recommendations, query rewrites). This is crucial for ensuring pipelines can handle production-scale data volumes efficiently.

## Technical Requirements
- **Testability**: All code generation and SQL translation logic must be testable via pytest
- **Performance**: Must generate complex pipelines (100+ transformations) quickly
- **Integration**: Clean API for integration with data orchestration tools and version control
- **Key Constraints**: No UI components; generated code must be production-ready; support modern data stack tools

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- SQL dialect translator with syntax and function mapping
- Transformation pattern library with parameterization support
- DAG generator for multiple orchestration platforms
- Error handling template system with platform-specific patterns
- Performance analyzer with optimization recommendations
- Data quality check generator with customizable rules
- Incremental load pattern templates
- Schema evolution handling templates

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **SQL translation tests**: Verify accurate translation between all supported dialects
- **Pattern library tests**: Validate correct implementation of transformation patterns
- **DAG generation tests**: Ensure valid DAG creation for different orchestrators
- **Error handling tests**: Verify retry logic and failure recovery patterns
- **Optimization tests**: Validate performance hint accuracy and applicability
- **Integration tests**: Ensure generated code runs on target platforms
- **Edge cases**: Handle complex queries, nested CTEs, window functions
- **Compatibility tests**: Verify support for different platform versions

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
- SQL translation maintains functionality across 5+ database dialects
- Pattern library covers 20+ common transformation scenarios
- Generated DAGs execute successfully on target orchestrators
- Error handling provides 99.9% pipeline reliability for transient failures
- Performance hints improve query execution by at least 50%
- Complex pipelines (100+ steps) generate in under 10 seconds
- Generated code passes linting and best practice checks
- All tests pass with comprehensive platform coverage

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file