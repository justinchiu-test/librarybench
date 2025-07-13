# PyMemTrace for Web Applications

## Overview
A specialized memory profiling tool designed for web application developers to diagnose and resolve memory issues in long-running web processes. This implementation focuses on request-scoped memory tracking, identifying memory leaks in web frameworks like Django, and optimizing memory usage for better scalability under high load conditions.

## Persona Description
A Django developer whose application crashes under high load due to memory exhaustion. He needs to identify memory leaks in long-running web processes and optimize request handling for better scalability.

## Key Requirements

1. **Request-scoped Memory Profiling with Middleware Integration**
   - Track memory allocation and deallocation per HTTP request
   - Provide middleware for automatic request memory profiling
   - Correlate memory usage with request URLs, methods, and parameters
   - Support for async request handling and memory tracking
   - Essential for identifying which endpoints consume excessive memory

2. **Session and Cache Memory Impact Visualization**
   - Monitor memory usage of session storage backends
   - Track cache memory consumption and hit/miss ratios
   - Visualize memory growth from session accumulation
   - Identify memory leaks in custom session handlers
   - Critical for optimizing memory usage in stateful web applications

3. **Memory Growth Correlation with Request Patterns**
   - Analyze memory trends across different request types
   - Identify request sequences that cause memory accumulation
   - Detect memory leaks from unclosed resources
   - Track memory usage patterns during peak traffic
   - Vital for understanding memory behavior under various load conditions

4. **Celery Task Memory Profiling Across Workers**
   - Profile memory usage in background task execution
   - Track memory consumption across distributed workers
   - Monitor memory leaks in long-running tasks
   - Support for task retry memory impact analysis
   - Essential for optimizing asynchronous task processing

5. **Database Query Result Set Memory Tracking**
   - Monitor memory usage of ORM query results
   - Track memory overhead from lazy loading
   - Identify N+1 query memory impact
   - Analyze memory efficiency of bulk operations
   - Critical for optimizing database-heavy applications

## Technical Requirements

### Testability Requirements
- All functionality must be implemented as Python modules with no UI components
- Comprehensive test coverage using pytest with Django test fixtures
- Mock request/response cycle for isolated testing
- Test fixtures for various web application scenarios
- Performance benchmarks to ensure minimal request overhead

### Performance Expectations
- Request profiling overhead must not exceed 2% of response time
- Support for handling 10,000+ requests per minute
- Memory snapshots with minimal blocking (< 10ms)
- Efficient storage of request memory profiles
- Low memory footprint for the profiler itself (<50MB)

### Integration Points
- Django/Flask/FastAPI middleware compatibility
- WSGI/ASGI application support
- Celery task decorator integration
- Database connection pooling hooks
- Export to APM tools (Datadog, New Relic format)

### Key Constraints
- Must work with Python 3.8+ standard library
- Thread-safe for multi-threaded web servers
- Process-safe for multi-process deployments
- Compatible with async frameworks
- Must not interfere with request/response cycle

## Core Functionality

The memory profiler must provide a comprehensive library for tracking and analyzing memory usage in web applications:

1. **Request Memory Profiler**
   - Middleware for automatic request profiling
   - Memory allocation tracking per request lifecycle
   - Request metadata correlation
   - Memory leak detection between requests

2. **Session/Cache Memory Analyzer**
   - Session backend memory monitoring
   - Cache memory usage tracking
   - Memory growth trend analysis
   - Optimization recommendations

3. **Pattern Analysis Engine**
   - Request pattern memory correlation
   - Memory anomaly detection
   - Load test memory analysis
   - Memory usage prediction

4. **Background Task Profiler**
   - Celery task memory tracking
   - Worker memory distribution analysis
   - Task queue memory monitoring
   - Memory-based task routing suggestions

5. **Database Memory Tracker**
   - ORM query memory profiling
   - Connection pool memory usage
   - Query result set analysis
   - Bulk operation optimization

## Testing Requirements

### Key Functionalities to Verify
- Accurate per-request memory measurement
- Correct middleware integration without side effects
- Proper Celery task memory tracking
- Database query memory profiling accuracy
- Thread-safety in concurrent request handling

### Critical User Scenarios
- Handling 1000 concurrent requests without memory leaks
- Identifying memory leaks in long-running processes
- Profiling memory during traffic spikes
- Tracking memory in distributed Celery deployments
- Optimizing ORM query memory usage

### Performance Benchmarks
- Request overhead < 2% for typical web requests
- Memory profile storage < 1KB per request
- Support for 10,000+ requests per minute
- Celery task profiling overhead < 3%
- Real-time memory updates with < 50ms latency

### Edge Cases and Error Conditions
- Handling of request timeouts during profiling
- Recovery from profiler crashes
- Memory tracking during server restarts
- Concurrent request modifications
- Database connection pool exhaustion

### Required Test Coverage Metrics
- Code coverage > 90%
- Branch coverage > 85%
- Integration tests for all web frameworks
- Load tests with realistic traffic patterns
- Memory leak tests for profiler itself

**IMPORTANT**: All tests must be run with pytest-json-report to generate a pytest_results.json file:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria

The implementation will be considered successful when:

1. **All functional requirements are met** with comprehensive test coverage
2. **Request profiling accuracy** is within 2% of actual memory usage
3. **Performance overhead** remains below 2% for typical web requests
4. **Integration works seamlessly** with Django, Flask, and FastAPI
5. **Memory leak detection** identifies 95%+ of common leak patterns
6. **All tests pass** when run with pytest and a valid pytest_results.json file is generated
7. **Documentation** includes clear examples for common web frameworks

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Implementation Guidelines

Use `uv venv` to set up the virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

Focus on creating a production-ready library that web developers can easily integrate into existing applications with minimal configuration. The implementation should prioritize low overhead, accurate measurements, and actionable insights for memory optimization.