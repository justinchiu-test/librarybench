# E-Commerce Business Intelligence Query Interpreter

A specialized query language interpreter for small business analytics that processes sales data, customer information, and inventory across multiple data sources without requiring dedicated database infrastructure.

## Overview

This project implements a query language interpreter designed specifically for small business analytics needs. It allows business analysts to query and analyze data from various business systems (sales, customer, inventory) stored in different formats like CSV files, without requiring dedicated database infrastructure. The interpreter includes business-specific metrics, automatic reporting, and anomaly detection capabilities tailored for e-commerce operations.

## Persona Description

Marcus manages analytics for a growing e-commerce business without dedicated database infrastructure. He needs to query sales data, customer information, and inventory across multiple CSV exports from different business systems.

## Key Requirements

1. **Business Metrics Library**
   - Implement pre-defined calculations for common retail KPIs (gross margin, customer acquisition cost, inventory turnover, etc.)
   - Support custom metric definitions using a formula syntax
   - Include trend analysis for metrics over configurable time periods
   - Enable comparison of metrics across different product categories, time periods, or customer segments
   - Critical for Marcus to quickly assess business performance without manually calculating metrics for each analysis

2. **Scheduled Query Execution**
   - Support definition of queries that run automatically at specified intervals
   - Generate reports in common formats (CSV, Excel, JSON) with consistent formatting
   - Include notification system for completed reports or triggered alerts
   - Maintain execution history with result snapshots for trend analysis
   - Essential for Marcus to automate routine reports for different stakeholders and track business metrics over time

3. **Excel-Compatible Formula Translation**
   - Parse and execute Excel-like formulas within queries (SUM, AVERAGE, VLOOKUP equivalents)
   - Support cell references translated to field names (e.g., A1:B10 → row/column ranges)
   - Enable conditional expressions similar to Excel's IF, AND, OR functions
   - Provide mapping between Excel worksheet structures and data sources
   - Important for enabling non-technical staff familiar with Excel to write and understand queries

4. **Anomaly Highlighting**
   - Automatically identify statistical outliers in business data
   - Detect significant changes in key metrics compared to historical patterns
   - Flag unusual combinations or correlations between different business measures
   - Support definition of business rules for custom anomaly detection
   - Crucial for Marcus to quickly identify potential issues or opportunities in business data that might otherwise go unnoticed

5. **Multi-Currency Support**
   - Automatically convert monetary values between currencies based on transaction dates
   - Maintain historical exchange rate data for accurate financial reporting
   - Support reporting in a base currency with original currency annotations
   - Handle currency-specific formatting in reports
   - Critical for Marcus's business which operates across multiple countries with different currencies

## Technical Requirements

### Testability Requirements
- All business metric calculations must be verifiable against manual calculations
- Scheduled execution must be testable with artificial time advancement
- Currency conversion must be testable with mock exchange rate data
- Anomaly detection algorithms must identify known test cases
- Excel formula compatibility should be verifiable with equivalent Excel calculations

### Performance Expectations
- Process up to 1 million sales transactions in under 30 seconds
- Handle CSV files up to 500MB without memory issues
- Generate scheduled reports for previous day's data in under 5 minutes
- Support simultaneous querying of at least 10 different data sources
- Anomaly detection should not increase query time by more than 50%

### Integration Points
- Import data from CSV exports from various business systems
- Export results to Excel, CSV, and JSON formats
- Send email notifications with report attachments
- API endpoints for integration with business dashboards
- Read exchange rate data from standard financial data sources

### Key Constraints
- Must operate without external database dependencies
- All operations must be performable on a standard business laptop
- No dependency on cloud services for core functionality
- Sensitive customer data must remain on local systems
- Must be usable by staff with SQL or Excel knowledge, but limited programming experience

## Core Functionality

The core of this Query Language Interpreter includes:

1. **Business Data Parser**
   - Parse CSV exports with header detection
   - Handle common business data formats (dates, currencies, product codes)
   - Detect and manage data type inconsistencies
   - Support incremental data loading

2. **Query Execution Engine**
   - Optimize queries for business analytics patterns
   - Support joins across different data sources
   - Execute aggregations and grouping operations
   - Apply business rules and filtering

3. **Business Metrics Calculator**
   - Calculate standard retail and e-commerce KPIs
   - Support custom metric definitions
   - Apply appropriate time period comparisons
   - Format results according to business conventions

4. **Scheduling System**
   - Manage query scheduling with cron-like syntax
   - Handle execution history and result storage
   - Generate notifications for completed reports
   - Manage report distribution to stakeholders

5. **Anomaly Detection Engine**
   - Apply statistical methods for outlier detection
   - Compare results against historical patterns
   - Implement business rule checking
   - Highlight anomalies in generated reports

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of all business metric calculations
- Correct execution of scheduled queries at specified times
- Proper currency conversion based on transaction dates
- Accurate translation of Excel-like formulas
- Reliable detection of known anomalies

### Critical User Scenarios
- Generating daily sales reports across multiple product categories
- Analyzing customer purchase patterns by demographic segments
- Tracking inventory levels and flagging potential stockouts
- Comparing performance metrics across different time periods
- Identifying unusual transactions or customer behaviors

### Performance Benchmarks
- Complete queries on 1 year of daily sales data (approximately 500MB) in under 60 seconds
- Process customer segmentation analysis on 100,000 customers in under 30 seconds
- Generate daily scheduled reports in under 5 minutes
- Handle concurrent queries without significant performance degradation
- Memory usage below 2GB for typical operations

### Edge Cases and Error Conditions
- Handling missing data in some CSV exports
- Dealing with format changes in source system exports
- Managing duplicate transaction records
- Processing transactions with invalid or missing currency information
- Recovering gracefully from interrupted scheduled queries

### Required Test Coverage Metrics
- 95% code coverage for business metric calculations
- Comprehensive tests for currency conversion scenarios
- Verification of all Excel formula translations
- Performance tests for realistic data volumes
- Validation of anomaly detection with known test cases

## Success Criteria

1. All business metrics calculations match manual verification
2. Scheduled reports generate at specified times with correct data
3. Excel-compatible formulas produce identical results to Excel calculations
4. Anomaly detection successfully identifies unusual patterns in test data
5. Multi-currency reporting correctly converts amounts based on transaction dates
6. Complete set of daily business reports generates in under 10 minutes
7. System operates without dedicated database infrastructure
8. Business stakeholders can understand and create basic queries

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install pandas numpy
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```