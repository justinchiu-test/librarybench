# Memory Profiler Tool - API Developer Fatima Instructions

You are tasked with implementing a memory profiler tool specifically designed for Fatima, an API developer building RESTful services who needs to optimize memory usage for concurrent request handling. She wants to understand memory sharing patterns and identify per-request memory overhead.

## Core Requirements

### 1. Concurrent request memory isolation analysis
- Track memory usage per concurrent request
- Identify shared vs isolated memory segments
- Detect memory leaks across request boundaries
- Measure request memory lifecycle
- Analyze concurrent request interference

### 2. Memory leak detection in connection pooling
- Monitor connection pool memory usage
- Detect connection object leaks
- Track pool growth and shrinkage patterns
- Identify stale connection memory
- Generate pool optimization recommendations

### 3. Request payload memory impact assessment
- Measure memory cost of different payload sizes
- Track serialization/deserialization overhead
- Identify memory-intensive content types
- Analyze streaming vs buffering trade-offs
- Calculate per-endpoint memory requirements

### 4. Memory-based rate limiting recommendations
- Calculate memory cost per request type
- Suggest memory-aware rate limits
- Model memory exhaustion scenarios
- Generate throttling strategies
- Provide burst capacity calculations

### 5. API version migration memory impact analysis
- Compare memory usage across API versions
- Identify memory regression risks
- Track deprecated endpoint memory costs
- Analyze backward compatibility overhead
- Generate migration impact reports

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Design for high-concurrency environments
- Support popular web frameworks (Flask, FastAPI, Django)

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Test with concurrent request scenarios
- Validate memory isolation accuracy
- Test with various payload sizes
- Ensure framework compatibility

## Project Structure

```
memory_profiler_tool_api_developer/
├── src/
│   ├── __init__.py
│   ├── request_isolator.py      # Request memory isolation
│   ├── pool_monitor.py          # Connection pool analysis
│   ├── payload_analyzer.py      # Payload memory impact
│   ├── rate_limiter.py          # Memory-based rate limiting
│   └── version_comparator.py    # API version analysis
├── tests/
│   ├── __init__.py
│   ├── test_request_isolator.py
│   ├── test_pool_monitor.py
│   ├── test_payload_analyzer.py
│   ├── test_rate_limiter.py
│   └── test_version_comparator.py
├── requirements.txt
└── README.md
```

Remember: This tool must help API developers understand and optimize memory usage in high-concurrency web services while maintaining performance and reliability.