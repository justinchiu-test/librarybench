# Database Performance Monitoring System

## Overview
A specialized database monitoring platform that provides deep insights into database engine performance, query efficiency, connection pool utilization, storage growth patterns, and backup operations to help database administrators optimize performance, prevent outages, and ensure data integrity.

## Persona Description
Dr. Chen manages database systems supporting critical applications. He needs detailed insights into database performance and resource utilization patterns to optimize queries and prevent outages.

## Key Requirements

1. **Database-Specific Metrics Collection**
   - Implement specialized monitoring for major database engines (MySQL, PostgreSQL, SQL Server, Oracle, MongoDB)
   - This is critical because database administrators need visibility into engine-specific performance metrics not available in general system monitoring
   - The collection must capture detailed internal database states like buffer pool utilization, lock contention, and query cache effectiveness

2. **Query Performance Tracking**
   - Create a query analysis system that identifies slow-running or resource-intensive database operations
   - This is essential because inefficient queries are often the primary cause of database performance issues
   - The tracking must capture execution plans, resource consumption, and timing patterns to pinpoint optimization opportunities

3. **Connection Pool Monitoring**
   - Develop monitoring for database connection pools to analyze usage patterns and detect saturation
   - This is vital because connection pool exhaustion is a common cause of application performance degradation and outages
   - The monitoring must identify connection leaks, usage patterns, and potential bottlenecks in application-database interaction

4. **Storage Growth Forecasting**
   - Implement storage analytics that track database volume growth and predict future capacity needs
   - This is important because unexpected storage exhaustion can cause database outages or corruption
   - The forecasting must account for different growth patterns across tables, indexes, and transaction logs

5. **Backup Operation Verification**
   - Create a monitoring system that confirms successful completion and integrity of database backup operations
   - This is crucial because incomplete or corrupted backups may only be discovered during recovery attempts
   - The verification must validate backup completion, integrity, and recoverability to ensure disaster recovery readiness

## Technical Requirements

- **Testability Requirements**
  - All components must have unit tests with minimum 90% code coverage
  - Mock database interfaces for testing without actual database instances
  - Test fixtures for various database engines, versions, and configurations
  - Parameterized tests to validate behavior across different database technologies
  - Performance tests to verify minimal impact on monitored database systems

- **Performance Expectations**
  - Monitoring overhead must not exceed 2% of database server resources
  - Query performance analysis must process at least 1000 queries per minute
  - Connection pool monitoring must refresh at least every 15 seconds
  - Storage forecasting calculations must complete within 5 minutes for databases up to 1TB
  - Backup verification must complete within 10% of the backup operation time

- **Integration Points**
  - Database engine management interfaces (MySQL, PostgreSQL, SQL Server, Oracle, MongoDB)
  - SQL query execution and explain plan analysis
  - Database backup systems and verification APIs
  - Storage subsystem access for capacity analysis
  - Application connection pool monitoring interfaces

- **Key Constraints**
  - Must operate with minimal privileges to reduce security risks
  - Cannot interfere with database transaction processing or cause blocking
  - Query analysis must not store sensitive data contained in SQL statements
  - Must be compatible with various database versions and configurations
  - Storage requirements must be proportional to the size and activity of monitored databases

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Database Engine Analytics**
   - Collection of engine-specific performance metrics (buffer pool, cache hit ratios, etc.)
   - Instance-level resource utilization (CPU, memory, disk I/O, network)
   - Wait statistics and blocking analysis
   - Internal fragmentation and optimization opportunities
   - Version-specific feature utilization and configuration optimization

2. **SQL Query Performance Analysis**
   - Capture and analysis of slow-running queries
   - Execution plan evaluation and optimization suggestions
   - Resource consumption attribution to specific queries and users
   - Query pattern identification to detect repetitive inefficient access
   - Historical query performance trending and regression detection

3. **Connection Management Intelligence**
   - Real-time monitoring of connection pool utilization
   - Application-to-database connection mapping
   - Connection lifetime analysis and leak detection
   - Peak usage pattern identification
   - Saturation prediction and capacity planning

4. **Storage Analytics and Prediction**
   - Detailed size tracking of databases, tables, indexes, and logs
   - Growth rate calculation with seasonal and trend analysis
   - Capacity forecasting with confidence intervals
   - Anomalous growth detection and alerting
   - Storage efficiency recommendations (compression, archiving, purging)

5. **Backup Integrity Assurance**
   - Monitoring of backup job execution and completion
   - Backup size and duration trend analysis
   - Integrity verification through checksums or sample restores
   - Recovery time objective (RTO) validation
   - Backup chain completeness verification for point-in-time recovery

## Testing Requirements

- **Key Functionalities to Verify**
  - Accuracy of database engine metric collection across different database systems
  - Effectiveness of slow query detection and resource attribution
  - Precision of connection pool utilization monitoring and leak detection
  - Reliability of storage growth predictions compared to actual growth
  - Thoroughness of backup operation verification and integrity checking

- **Critical User Scenarios**
  - Identifying the root cause of database performance degradation
  - Pinpointing resource-intensive queries impacting system performance
  - Detecting application connection leaks before they cause pool exhaustion
  - Forecasting storage needs to prevent capacity-related outages
  - Verifying backup integrity to ensure recoverability

- **Performance Benchmarks**
  - Database metric collection must not increase database load by more than 2%
  - Query analysis must identify 99% of queries consuming more than 1000 ms
  - Connection pool monitoring must detect leaks within 5 minutes of occurrence
  - Storage forecasting must be accurate within 15% for 30-day projections
  - Backup verification must detect 100% of incomplete or corrupted backups

- **Edge Cases and Error Conditions**
  - System behavior during extreme database load or resource exhaustion
  - Handling of database version upgrades or configuration changes
  - Recovery after monitoring interruptions to maintain historical continuity
  - Management of very large numbers of slow queries or connections
  - Proper functioning with degraded permissions or restricted access

- **Test Coverage Requirements**
  - Minimum 90% code coverage across all components
  - 100% coverage for database connection and query parsing logic
  - All supported database engines must have specific test cases
  - Error handling paths must be thoroughly tested
  - Performance impact scenarios must be verified through dedicated tests

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

A successful implementation will:

1. Collect and analyze database-specific metrics for at least 5 major database engines with less than 2% performance impact
2. Identify at least 95% of slow or resource-intensive queries with accurate execution statistics
3. Monitor connection pool utilization with 99% accuracy and detect connection leaks within 5 minutes
4. Forecast database storage growth with at least 85% accuracy for 30-day projections
5. Verify 100% of database backups for completion and integrity
6. Support databases ranging from 1GB to 10TB in size
7. Provide actionable performance optimization recommendations based on collected metrics
8. Achieve 90% test coverage across all monitoring modules

## Setup and Development

To set up your development environment:

1. Use `uv init --lib` to initialize the project structure and setup the virtual environment
2. Install dependencies with `uv sync`
3. Run the application with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format code with `uv run ruff format`