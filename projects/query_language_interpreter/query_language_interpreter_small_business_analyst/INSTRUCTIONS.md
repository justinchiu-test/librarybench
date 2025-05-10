# Business Intelligence Query Engine

A query language interpreter optimized for small business analytics without dedicated database infrastructure.

## Overview

The Business Intelligence Query Engine provides a lightweight but powerful query system for small business analysts to extract actionable insights from disparate data sources. This project variant focuses on enabling retail business analysis across CSV exports from various business systems without requiring specialized database expertise or infrastructure, with built-in retail metrics calculation and reporting features.

## Persona Description

Marcus manages analytics for a growing e-commerce business without dedicated database infrastructure. He needs to query sales data, customer information, and inventory across multiple CSV exports from different business systems.

## Key Requirements

1. **Business metrics library with pre-defined calculations for common retail KPIs**
   - Implement calculations for standard retail metrics (conversion rate, average order value, customer lifetime value, inventory turnover)
   - Support custom metric definitions using a simple syntax
   - Include trending functions to compare metrics across time periods (YoY, MoM, WoW)
   - Essential for Marcus to quickly assess business performance without manually coding complex calculations for each report

2. **Scheduled query execution generating automated reports at regular intervals**
   - Develop a scheduling system to run predefined queries on a recurring basis
   - Support various scheduling patterns (hourly, daily, weekly, monthly)
   - Generate consistent report outputs in multiple formats (CSV, JSON, Excel)
   - Critical for maintaining up-to-date business intelligence without manual effort, allowing Marcus to focus on analysis rather than data extraction

3. **Excel-compatible formula translation allowing spreadsheet users to write familiar expressions**
   - Create a translation layer between Excel-style formulas and the query language
   - Support common Excel functions (VLOOKUP, SUMIF, COUNTIF, pivot-table-like operations)
   - Provide clear error messages that help spreadsheet users correct syntax issues
   - Important for reducing the learning curve by enabling Marcus and his team to leverage their existing spreadsheet knowledge

4. **Anomaly highlighting automatically flagging unusual patterns in business data**
   - Implement statistical methods for detecting outliers in business metrics
   - Support different detection algorithms based on data characteristics and seasonality
   - Prioritize anomalies by potential business impact
   - Critical for proactively identifying issues or opportunities that might be missed in routine reporting

5. **Multi-currency support with automatic conversion based on transaction dates**
   - Enable storing and querying monetary values in multiple currencies
   - Maintain historical exchange rates and apply correct rates based on transaction dates
   - Support reporting in a normalized currency with transparent conversion
   - Essential for Marcus's e-commerce business that processes transactions in multiple currencies while needing consolidated reporting

## Technical Requirements

### Testability Requirements
- All functions must be unit-testable with pytest
- Test all KPI calculations against reference values
- Verify correct execution of scheduled queries using time mocking
- Test currency conversions against historical exchange rates
- Simulate anomaly detection with artificially generated datasets

### Performance Expectations
- Process CSV files up to 1GB in size without memory issues
- Execute common business queries in under 5 seconds
- Support incremental processing for scheduled reports
- Handle at least 100,000 transactions in trending calculations
- Process 5 years of historical data for seasonal anomaly detection

### Integration Points
- Import data from CSV, Excel, JSON, and simple API endpoints
- Export results to business-friendly formats (Excel, CSV, JSON)
- Connect with email systems for automated report distribution
- Maintain compatibility with common data analysis tools
- Support exchange rate data updates from external sources

### Key Constraints
- Must operate without requiring a database server installation
- All operations must work on standard business hardware
- Storage format must be accessible by non-technical users if needed
- Preserve data relationships across disparate export files
- Maintain backward compatibility with existing Excel reports

### Implementation Notes
IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Business Intelligence Query Engine must implement the following core functionality:

1. **Data Import and Management**
   - Parse and normalize data from various business system exports
   - Maintain metadata about different data sources and relationships
   - Handle incremental data updates efficiently
   - Preserve historical data for trend analysis

2. **Query Language Processor**
   - Implement SQL-like syntax with business-oriented extensions
   - Support Excel-compatible formula translation
   - Provide a library of retail-specific functions and aggregations
   - Enable joining data across different business system exports

3. **Business Metrics Engine**
   - Calculate standard and custom retail KPIs
   - Implement trend analysis functions
   - Support segmentation and cohort analysis
   - Enable comparative analysis across time periods

4. **Scheduling and Automation**
   - Manage recurring query execution
   - Track query dependencies for efficient updating
   - Generate consistent report outputs
   - Support notifications and distribution

5. **Analysis Helpers**
   - Implement anomaly detection algorithms
   - Support currency normalization functions
   - Provide data quality checks and warnings
   - Enable "what-if" scenario modeling

## Testing Requirements

### Key Functionalities to Verify
- Correct calculation of all predefined retail KPIs
- Accurate translation of Excel-style formulas
- Proper execution of scheduled queries at specified intervals
- Reliable anomaly detection across different data patterns
- Accurate currency conversion based on historical rates

### Critical User Scenarios
- Generating a weekly sales report with year-over-year comparisons
- Creating a customer segmentation analysis based on purchase patterns
- Identifying inventory issues by comparing sales velocity to stock levels
- Analyzing profit margins across product categories with multi-currency transactions
- Detecting unusual patterns in customer returns or abandoned carts

### Performance Benchmarks
- Complete import of 100MB CSV file in under 30 seconds
- Execute KPI dashboard queries in under 5 seconds
- Process historical trend analysis for 3 years of data in under 60 seconds
- Generate scheduled reports with minimal performance impact on the system
- Respond to ad-hoc queries while scheduled operations are running

### Edge Cases and Error Conditions
- Handling inconsistent CSV formats from different export systems
- Processing incomplete data when business systems change
- Managing currency conversions during periods of high exchange rate volatility
- Detecting anomalies correctly despite seasonal variations
- Continuing scheduled operations despite temporary data source failures

### Required Test Coverage Metrics
- Minimum 90% code coverage for all core functions
- 100% coverage of KPI calculation functions
- All Excel formula translations tested against actual Excel outputs
- Anomaly detection tested against datasets with known anomalies
- Currency conversion tested with historical exchange rate data

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. **Functional Completeness**
   - All five key requirements are fully implemented
   - Business metric calculations match reference values in test scenarios
   - Scheduled queries execute reliably at specified intervals
   - Excel formulas translate correctly to equivalent query operations
   - Anomaly detection finds significant deviations while minimizing false positives

2. **Performance Goals**
   - Meets all performance benchmarks specified
   - Schedules and executes daily reports in under 10 minutes
   - Supports interactive query response times (under 10 seconds) for typical operations
   - Handles the expected data volumes without memory issues

3. **Usability for Target Persona**
   - Successfully imports data from all common business system exports
   - Generates reports matching the format of existing manual processes
   - Provides clear error messages for common input issues
   - Requires minimal technical expertise for routine operations

4. **Quality and Reliability**
   - Successfully passes all automated tests
   - Maintains data integrity across processing steps
   - Produces consistent results with identical inputs
   - Detects and handles common data quality issues