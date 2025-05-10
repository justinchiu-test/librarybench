# Distributed Log Query Interpreter

A specialized query language interpreter for analyzing distributed system logs with support for pattern matching, event sequence detection, and contextual log analysis.

## Overview

This project implements a query language interpreter designed specifically for analyzing logs from distributed cloud applications. It allows engineers to perform complex queries across various log formats without centralizing them in a database. The interpreter includes optimized pattern matching, event sequence detection, and session reconstruction capabilities essential for troubleshooting distributed systems.

## Persona Description

Sophia troubleshoots cloud application issues by analyzing distributed system logs in various formats. She needs to perform complex queries across log files without transferring them to a centralized database.

## Key Requirements

1. **Regular Expression Pattern Matching**
   - Implement high-performance regex matching optimized for common log file formats
   - Support named capture groups for extracting structured data from log entries
   - Include predefined patterns for common log components (timestamps, IP addresses, request IDs)
   - Enable fuzzy matching for error messages with varying details
   - Critical for Sophia to quickly locate specific log patterns across thousands of log entries while troubleshooting issues

2. **Event Sequence Detection**
   - Implement temporal pattern matching to identify specific sequences of events
   - Support time-window constraints between sequential events
   - Enable counting and statistical analysis of detected sequences
   - Include visualization hooks for detected event sequences
   - Essential for identifying causal chains in distributed systems, such as cascading failures or request flows across services

3. **Log Level Filtering with Context Preservation**
   - Filter logs by severity level (INFO, WARN, ERROR, etc.)
   - Automatically include surrounding context entries regardless of their level
   - Support configurable context window sizes before and after matches
   - Enable exclusion patterns to reduce noise
   - Crucial for focusing on important log entries while maintaining enough context to understand the system state around those entries

4. **Session Reconstruction**
   - Group related operations by tracing identifiers (request ID, session ID, correlation ID)
   - Reconstruct complete request flows across multiple services and log files
   - Support for different trace ID formats and propagation methods
   - Enable timeline visualization of reconstructed sessions
   - Important for understanding the complete lifecycle of operations in distributed systems, especially during failure investigations

5. **Distributed Query Execution**
   - Execute queries directly on multiple remote servers where logs reside
   - Aggregate and correlate results from multiple sources
   - Optimize for minimal data transfer between nodes
   - Support both real-time and historical log analysis
   - Critical for performing analysis at scale without centralizing large log volumes, reducing network overhead and analysis time

## Technical Requirements

### Testability Requirements
- Regular expression engine must be testable against known log patterns
- Event sequence detection must identify predefined sequences in test logs
- Context preservation logic should be verifiable with controlled log streams
- Session reconstruction must be testable with synthetic distributed traces
- Distributed execution should work with local mock nodes for testing

### Performance Expectations
- Process log files at a rate of at least 100MB/second on standard hardware
- Support regex matching across gigabytes of log data in under a minute
- Complete distributed queries across 10 nodes in less than 30 seconds
- Session reconstruction for a single request should take less than 5 seconds
- Memory usage should scale linearly with query complexity, not log size

### Integration Points
- Read logs from various formats (plaintext, JSON, XML, custom formats)
- Support for compressed log files and log rotation schemes
- Integration with common logging frameworks (syslog, log4j, etc.)
- Export capabilities to incident management systems
- Hooks for custom log format parsers

### Key Constraints
- Must operate without requiring logs to be moved to a central database
- All operations must be possible on live production systems
- Queries must not significantly impact system performance
- No schema or structure should be required for logs
- Security and access controls must be preserved

## Core Functionality

The core of this Query Language Interpreter includes:

1. **Log Parser**
   - Detect and adapt to various log formats
   - Extract structured data from semi-structured logs
   - Handle multi-line log entries
   - Support timestamp normalization across timezones

2. **Query Engine**
   - Optimize regex matching for log-specific patterns
   - Support temporal and causal operators
   - Execute distributed query plans efficiently
   - Stream results for large log volumes

3. **Pattern Matching System**
   - High-performance regex implementation
   - Predefined matchers for common log elements
   - Fuzzy matching capabilities for error messages
   - Stateful pattern recognition for sequences

4. **Session Analyzer**
   - Trace ID detection and extraction
   - Cross-log correlation based on IDs
   - Temporal ordering of distributed events
   - Gap detection in request flows

5. **Distributed Coordinator**
   - Dispatch queries to appropriate nodes
   - Aggregate and correlate distributed results
   - Manage query timeouts and failures
   - Optimize for network efficiency

## Testing Requirements

### Key Functionalities to Verify
- Correct matching of complex regex patterns in logs
- Accurate detection of event sequences within time windows
- Proper context preservation around filtered log entries
- Complete session reconstruction across distributed logs
- Efficient distributed query execution across multiple nodes

### Critical User Scenarios
- Troubleshooting a production incident with error spikes
- Analyzing the performance of a distributed transaction
- Identifying cascade failures across microservices
- Reconstructing user sessions that experienced errors
- Finding correlation between system events and user issues

### Performance Benchmarks
- Execute simple regex search across 1GB of logs in under 10 seconds
- Complete complex event sequence detection in 5GB of logs within 30 seconds
- Reconstruct 1000 distributed sessions in under 60 seconds
- Distribute and execute queries across 10 nodes in under 5 seconds
- Memory usage below 2GB for typical operations

### Edge Cases and Error Conditions
- Handling malformed log entries
- Dealing with clock skew across distributed systems
- Managing incomplete trace information
- Recovering from node failures during distributed queries
- Processing logs during high-volume write periods

### Required Test Coverage Metrics
- 95% code coverage for core query engine
- 100% coverage for regex pattern matching functions
- Comprehensive tests for distributed execution scenarios
- Performance tests with realistic log volumes and formats
- Verification of session reconstruction with known test traces

## Success Criteria

1. All regular expression patterns correctly match their intended log entries
2. Event sequences are accurately detected with proper time-window constraints
3. Context entries are correctly preserved around filtered log entries
4. Complete sessions are reconstructed across distributed logs with accurate timing
5. Distributed queries execute efficiently with minimal data transfer
6. Engineers can identify root causes significantly faster than with manual log inspection
7. System scales to handle log volumes from large-scale distributed applications
8. Query syntax is intuitive for engineers with SQL or grep experience

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install regex pandas
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```