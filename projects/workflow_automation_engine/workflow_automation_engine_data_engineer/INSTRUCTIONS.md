# Data Pipeline Workflow Engine

A specialized workflow automation engine for orchestrating and managing complex data transformation and validation pipelines with robust quality controls.

## Overview

This project implements a Python library for defining, executing, and monitoring complex data processing workflows with dependencies, error handling, and quality verification steps. The system provides features specifically designed for data engineers, including quality gates, incremental processing detection, data lineage tracking, and temporal dependency management.

## Persona Description

Priya processes data from multiple sources through complex transformation and validation pipelines. She needs reliable orchestration of data workflows with dependencies, error handling, and quality verification steps.

## Key Requirements

1. **Data Quality Gate Implementation**: Create functionality that enforces validation rules between processing stages.
   - Critical for Priya because data quality issues must be detected early to prevent propagation through downstream systems.
   - System should support custom validation rules with configurable severity levels and conditional execution paths based on quality metrics.

2. **Incremental Processing Detection**: Develop mechanisms for avoiding redundant work on previously processed data.
   - Essential for Priya to optimize processing time and resource utilization on large datasets.
   - Must track previously processed data records or batches and intelligently process only new or changed data.

3. **Data Lineage Tracking**: Implement comprehensive tracking of the full transformation history for compliance.
   - Vital for Priya to meet regulatory requirements and enable root cause analysis of data issues.
   - Should document source systems, transformation steps, parameters, and timestamps for all data flows.

4. **Processing Window Management**: Create functionality for handling late-arriving data and temporal dependencies.
   - Necessary for Priya to correctly process time-based data without missing records or creating inconsistencies.
   - Must support configurable time windows, late arrival policies, and reprocessing strategies.

5. **Storage Format Optimization**: Implement automatic selection of appropriate compression and partitioning strategies.
   - Critical for Priya to balance storage costs, query performance, and processing efficiency.
   - Should analyze data characteristics and access patterns to recommend or automatically apply optimal storage strategies.

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest without requiring actual data sources
- Test fixtures must provide sample datasets with known validation issues
- Lineage tracking must be verifiable with known input->output mappings
- Time-based processing should be testable with simulated timelines
- Storage optimization strategies must be testable for different data patterns

### Performance Expectations
- Support for processing datasets in the 10-100GB range
- Ability to track lineage for millions of data records
- Quality gates should add minimal overhead (<5% of processing time)
- Incremental processing should provide at least 5x speedup compared to full reprocessing
- Support for both batch and micro-batch processing patterns

### Integration Points
- Data storage systems (files, object stores, databases)
- Schema registries and metadata repositories
- External validation services and quality metrics systems
- Time series data sources with varying arrival patterns
- Data cataloging and lineage tracking systems

### Key Constraints
- No UI components - all functionality must be accessible via Python API
- Must support both local execution and integration with distributed processing frameworks
- All metadata and lineage information must be securely stored and queryable
- System should minimize data movement between processing stages
- Must handle data privacy concerns appropriately

## Core Functionality

The system must provide a Python library that enables:

1. **Data Workflow Definition**: A programmatic interface for defining data processing workflows with:
   - Task dependencies and execution order
   - Data quality validation rules and thresholds
   - Incremental processing specifications
   - Time window definitions and late arrival policies
   - Storage format and partitioning strategies

2. **Workflow Execution Engine**: An execution engine that:
   - Resolves dependencies and executes tasks in the correct order
   - Applies quality gates between processing stages
   - Identifies and processes only new or changed data
   - Manages time windows and handles late-arriving data
   - Optimizes storage formats based on data characteristics
   - Tracks complete data lineage through all transformations

3. **Quality Management System**: A robust quality control mechanism that:
   - Applies validation rules at configurable checkpoints
   - Provides metrics on data quality and validation results
   - Supports conditional execution paths based on quality metrics
   - Allows for remediation strategies for different quality issues

4. **Incremental Processing System**: An intelligent mechanism that:
   - Detects previously processed data using configurable methods
   - Determines optimal processing strategies based on data changes
   - Manages state for resumable processing
   - Provides metrics on efficiency gains from incremental processing

5. **Lineage Tracking System**: A comprehensive tracking system that:
   - Records all data sources and transformations
   - Captures transformation parameters and execution context
   - Supports forward and backward tracing of data elements
   - Provides queryable history for compliance and analysis

## Testing Requirements

### Key Functionalities to Verify
- Correct execution of workflow tasks with data passing between stages
- Proper application of quality gates with expected actions for different scenarios
- Accurate detection of incremental processing opportunities
- Complete lineage tracking through multiple transformation steps
- Appropriate handling of time windows and late-arriving data
- Optimal storage format selection based on data characteristics

### Critical User Scenarios
- Complex ETL pipeline with multiple data sources and validation steps
- Incremental processing of dataset with various change patterns
- Time-based processing with late-arriving data
- Error handling and recovery in multi-stage transformations
- Full lineage tracing for specific data elements

### Performance Benchmarks
- Process 10GB dataset with full lineage tracking in under 30 minutes
- Achieve at least 5x speedup with incremental processing on datasets with 10% changes
- Quality gate overhead less than 5% of total processing time
- Lineage querying response time under 1 second for targeted queries
- Storage optimization should improve either query performance or storage efficiency by at least 30%

### Edge Cases and Error Conditions
- Handling of completely corrupted data sources
- Recovery from mid-pipeline failures without data loss
- Processing of extremely late-arriving data (days or weeks late)
- Managing lineage when upstream systems change schemas
- Dealing with conflicting incremental updates to the same records

### Required Test Coverage Metrics
- Minimum 90% line coverage for core workflow engine
- 100% coverage of data quality gate logic
- 100% coverage of incremental processing detection
- All temporal processing logic must have both standard and edge case tests
- Test parametrization for different data patterns and quality scenarios

## Success Criteria

The implementation will be considered successful if it demonstrates:

1. The ability to define and execute complex data transformation workflows with quality gates
2. Effective detection of incremental processing opportunities with significant performance improvements
3. Comprehensive lineage tracking that meets compliance requirements
4. Proper handling of time windows and late-arriving data
5. Intelligent storage format optimization based on data characteristics
6. All tests pass with the specified coverage metrics
7. Performance meets or exceeds the defined benchmarks

## Getting Started

To set up the development environment:

1. Initialize the project with `uv init --lib`
2. Install dependencies with `uv sync`
3. Run tests with `uv run pytest`
4. Run a single test with `uv run pytest path/to/test.py::test_function_name`
5. Format code with `uv run ruff format`
6. Lint code with `uv run ruff check .`
7. Type check with `uv run pyright`

To execute sample data workflows during development:

```python
import dataflow

# Define a data workflow
workflow = dataflow.Workflow("etl_pipeline")

# Define data sources
workflow.add_source("customer_data", source_config)
workflow.add_source("transaction_data", source_config)

# Add processing tasks
workflow.add_task("clean_customer_data", cleaning_function)
workflow.add_task("transform_transactions", transform_function)
workflow.add_task("join_data", join_function, depends_on=["clean_customer_data", "transform_transactions"])
workflow.add_task("aggregate_results", aggregate_function, depends_on=["join_data"])

# Add quality gates
workflow.add_quality_gate("clean_customer_data", [
    dataflow.ValidationRule("no_null_ids", "id IS NOT NULL", severity="critical"),
    dataflow.ValidationRule("valid_email", "email MATCHES '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", severity="warning")
])

# Configure incremental processing
workflow.configure_incremental("transform_transactions", {
    "key_columns": ["transaction_id"],
    "timestamp_column": "updated_at"
})

# Configure time window
workflow.configure_time_window("aggregate_results", {
    "window_size": "1 day",
    "late_arrival_tolerance": "6 hours",
    "trigger_interval": "1 hour"
})

# Configure storage
workflow.configure_storage("aggregate_results", {
    "format": "parquet",
    "partition_by": ["date", "region"],
    "compression": "snappy"
})

# Execute workflow
engine = dataflow.Engine()
result = engine.execute(workflow, incremental=True)

# Inspect results
print(result.processed_records)
print(result.quality_metrics)
print(result.lineage)
```