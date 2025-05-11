# API Performance Analysis Framework

## Overview
A specialized network protocol analysis library designed for API performance engineers to analyze HTTP/HTTPS traffic patterns, identify performance bottlenecks, optimize request/response payloads, evaluate caching effectiveness, and track dependencies between microservices in complex API ecosystems.

## Persona Description
Sophia optimizes web APIs for a high-traffic e-commerce platform. She needs to analyze HTTP/HTTPS traffic patterns to identify performance bottlenecks, inefficient requests, and opportunities for optimization in API implementations.

## Key Requirements

1. **API Call Aggregation and Analysis**  
   Create a module that groups similar API endpoints and measures their performance characteristics across multiple dimensions. This is critical for Sophia because it allows her to understand the overall performance profile of each endpoint, identify consistency issues, and prioritize optimization efforts based on call frequency and performance impact.

2. **Payload Efficiency Analysis**  
   Implement functionality to identify redundant or unnecessary data in API requests and responses. This feature is essential for Sophia to reduce bandwidth usage, improve response times, and create more efficient API contracts, which directly impacts user experience and infrastructure costs for high-volume APIs.

3. **Cache Effectiveness Measurement**  
   Develop capabilities to analyze cache hit/miss ratios and identify opportunities for improved caching strategies. This is crucial for Sophia because proper caching can dramatically reduce backend load and improve response times, particularly for an e-commerce platform where product and catalog data are frequently requested.

4. **Session Flow Visualization**  
   Build a system to map and analyze typical user interaction sequences and their associated API calls. This allows Sophia to understand how APIs are used in real user sessions, identify opportunities for request batching or prefetching, and optimize the critical paths that most impact user experience.

5. **Microservice Dependency Tracking**  
   Create functionality to discover and analyze cross-service communication patterns and bottlenecks in a microservice architecture. This feature is vital for Sophia to understand how API latency cascades across services, identify optimization opportunities in service interactions, and improve the overall responsiveness of the distributed system.

## Technical Requirements

### Testability Requirements
- All components must be testable with realistic HTTP/HTTPS traffic datasets
- API aggregation algorithms must be testable with known endpoint patterns
- Payload analysis must be verifiable against reference optimization opportunities
- Cache effectiveness metrics must be validated against known caching behaviors
- Dependency tracking must be testable with simulated microservice communications

### Performance Expectations
- Process at least 1M HTTP requests in under 10 minutes
- Group and analyze at least 10,000 distinct API endpoints
- Handle response payloads up to 10MB in size
- Support analysis of distributed traces across at least 20 interconnected services
- Generate performance insights with less than 5-second latency for interactive analysis

### Integration Points
- Import traffic from standard PCAP/PCAPNG files and HTTP proxy logs
- Support for parsing distributed tracing data (Jaeger, Zipkin, OpenTelemetry)
- Export analysis reports in formats compatible with performance dashboards
- Integration with OpenAPI/Swagger specifications for enhanced API context
- Support for authenticated API traffic with proper credential handling

### Key Constraints
- Must handle HTTPS with limited TLS visibility (metadata only when keys unavailable)
- Should work with sampling-based data without requiring 100% traffic capture
- Must protect sensitive data in payloads (PII, authentication tokens, etc.)
- Should operate effectively with high-cardinality data (many unique URLs/endpoints)
- Must handle compressed HTTP payloads (gzip, brotli, etc.)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The API Performance Analysis Framework should provide the following core functionality:

1. **HTTP/HTTPS Traffic Analysis Engine**
   - Parse and decode HTTP/HTTPS requests and responses
   - Normalize and group similar API endpoints
   - Calculate detailed performance metrics per endpoint
   - Analyze traffic patterns and trends over time

2. **Payload Optimization System**
   - Analyze request and response bodies for optimization opportunities
   - Identify redundant data fields and unnecessary inclusions
   - Detect inefficient data formats and serialization methods
   - Provide recommendations for payload size reduction

3. **Caching Analysis Tools**
   - Detect cacheable resources that aren't being cached
   - Analyze cache header usage and effectiveness
   - Measure hit and miss ratios for cached resources
   - Identify inconsistent cache policies

4. **User Session Analysis**
   - Reconstruct API call sequences within user sessions
   - Identify common interaction patterns and their performance
   - Analyze critical path operations and their optimizability
   - Detect opportunities for request batching or prefetching

5. **Microservice Communication Analysis**
   - Track API calls between services in a distributed architecture
   - Measure cross-service latency and dependencies
   - Identify cascading delays across service boundaries
   - Detect circular dependencies and optimization opportunities

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of HTTP/HTTPS protocol parsing
- Correctness of API endpoint grouping and normalization
- Precision of performance metric calculations
- Effectiveness of payload optimization recommendations
- Completeness of microservice dependency tracking

### Critical User Scenarios
- Analyzing API performance during peak traffic periods
- Identifying redundant data in JSON responses from a product catalog API
- Evaluating caching strategies for frequently accessed resources
- Mapping API call sequences during typical e-commerce checkout flows
- Troubleshooting latency issues in microservice communication chains

### Performance Benchmarks
- Process at least 5,000 HTTP requests per second on reference hardware
- Complete API aggregation for 50,000 requests in under 30 seconds
- Analyze payload efficiency for 1,000 distinct endpoints in under 60 seconds
- Reconstruct and analyze 100 user sessions in under 10 seconds
- Map dependencies across 15 microservices in under 15 seconds

### Edge Cases and Error Conditions
- Handling malformed HTTP requests and responses
- Processing incomplete captures where only requests or responses are visible
- Analyzing HTTP/2 and HTTP/3 protocol interactions
- Dealing with highly dynamic APIs where endpoints have high cardinality
- Handling WebSocket and long-polling API communication patterns

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 95% coverage for API call aggregation
- 95% coverage for payload efficiency analysis
- 90% coverage for cache effectiveness measurement
- 95% coverage for microservice dependency tracking

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

The API Performance Analysis Framework implementation will be considered successful when:

1. It can accurately group and analyze API endpoints with at least 95% correct grouping
2. It successfully identifies at least 85% of payload optimization opportunities in test datasets
3. It correctly measures cache effectiveness metrics and identifies improvement opportunities
4. It reconstructs user session flows with proper sequencing and timing information
5. It accurately maps dependencies between microservices with correct latency attribution

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Project Setup and Environment

To set up the project environment:

1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Install development dependencies including pytest-json-report

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

The pytest_results.json file serves as verification that all functionality works as required and all tests pass successfully. This file must be generated and included with your submission.