# High-Scale Media Streaming Microservices Framework

## Overview
This project is a specialized event-driven microservices framework designed for video streaming platforms that handle millions of concurrent viewers. It focuses on backpressure handling, content metadata synchronization, viewer experience prioritization, efficient caching, and analytics processing to create a robust backend that delivers seamless viewing experiences even during usage spikes.

## Persona Description
Olivia designs backend systems for a video streaming service handling millions of concurrent viewers. Her primary goal is to create a microservices framework that efficiently manages content delivery, user preferences, and viewing statistics while maintaining a seamless viewing experience during usage spikes.

## Key Requirements

1. **Backpressure Handling with Graceful Degradation Patterns**
   - Implement backpressure detection across service boundaries
   - Create graceful degradation strategies for handling load spikes
   - Support for prioritization of critical viewer experience functionality
   - Include adaptive rate limiting based on system capacity
   - This feature is critical for maintaining system stability during viral content spikes or unexpected traffic surges while preserving core viewing functionality

2. **Content Metadata Synchronization Across Service Boundaries**
   - Develop consistent metadata propagation between content services
   - Create conflict resolution for concurrent metadata updates
   - Support for metadata versioning with backward compatibility
   - Include efficient delta-based synchronization
   - This feature ensures viewers see consistent content information across different parts of the platform (recommendations, search, playback) even as it's updated

3. **Viewer Experience Prioritization with Tiered Service Levels**
   - Implement experience quality tiers with degradation paths
   - Create playback continuity preservation during service disruption
   - Support for personalization persistence even during system stress
   - Include quality of service monitoring with viewer impact metrics
   - This feature maintains the most critical aspects of viewing experience during system stress by intelligently reducing non-essential features

4. **Caching Strategies with Invalidation Event Propagation**
   - Develop multi-level caching for content and metadata
   - Create efficient cache invalidation through event propagation
   - Support for popularity-based caching strategies
   - Include geographic content distribution optimization
   - This feature optimizes content delivery speed and reduces backend load through intelligent caching while ensuring viewers always see the latest content

5. **Analytics Event Batching with Real-time and Historical Processing Paths**
   - Implement dual-path analytics for real-time and historical processing
   - Create efficient event batching based on analytics importance
   - Support for sampling strategies during extreme load
   - Include guaranteed delivery for business-critical metrics
   - This feature balances the need for real-time metrics for system operation with comprehensive historical data collection for business intelligence

## Technical Requirements

### Testability Requirements
- Support for simulating millions of concurrent viewers
- Ability to test degradation strategies under load
- Testing of metadata consistency across services
- Verification of caching and invalidation mechanisms

### Performance Expectations
- Support for at least 1 million concurrent viewers
- Maximum 200ms latency for playback-critical operations
- Ability to handle 10x traffic spikes through degradation
- Support for processing 100,000+ analytics events per second

### Integration Points
- Integration with content delivery networks (CDNs)
- Support for video encoding and transcoding pipelines
- Compatibility with recommendation and personalization engines
- Integration with business intelligence and analytics platforms

### Key Constraints
- Must maintain playback continuity as the highest priority
- Must operate efficiently across global regions
- Must preserve accurate analytics even during degraded operation
- Must scale horizontally for all components

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Load Management and Backpressure System**
   - Backpressure detection and propagation
   - Graceful degradation strategies
   - Priority-based request handling
   - Adaptive rate limiting

2. **Content Metadata Management**
   - Consistent metadata distribution
   - Conflict detection and resolution
   - Version management and compatibility
   - Efficient synchronization mechanisms

3. **Service Quality Management**
   - Experience quality tiering
   - Playback continuity preservation
   - Personalization persistence
   - Quality of service monitoring

4. **Caching Infrastructure**
   - Multi-level content and metadata caching
   - Event-based cache invalidation
   - Dynamic caching strategies
   - Geographic distribution optimization

5. **Analytics Processing System**
   - Dual-path analytics processing
   - Efficient event batching and sampling
   - Prioritized metric collection
   - Guaranteed delivery mechanisms

## Testing Requirements

### Key Functionalities that Must be Verified
- Graceful degradation under extreme load
- Consistent metadata across services
- Preservation of core viewing experience during system stress
- Efficient cache invalidation and updates
- Accurate analytics under various load conditions

### Critical User Scenarios
- Viral content causing massive traffic spikes
- Content metadata updates propagating correctly
- Viewer experience during partial system failure
- Cache behavior with frequently changing content
- Analytics accuracy during sampled collection

### Performance Benchmarks
- Handle 1 million+ concurrent viewers
- Maintain playback start latency under 200ms at P99
- Process 100,000+ analytics events per second
- Propagate metadata updates to all services within 1 second

### Edge Cases and Error Conditions
- Cascading failures between dependent services
- Metadata inconsistencies during rapid updates
- Regional service degradation
- Cache poisoning or invalidation storms
- Analytics data loss during extreme conditions

### Required Test Coverage Metrics
- Minimum 90% line coverage for all code
- 100% coverage of degradation path logic
- 100% coverage of metadata synchronization mechanisms
- 100% coverage of caching and invalidation logic
- 100% coverage of analytics processing paths

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

The implementation will be considered successful if:

1. The system gracefully handles backpressure during traffic spikes
2. Content metadata remains consistent across service boundaries
3. Core viewing experience is preserved during system degradation
4. Caching improves performance with timely invalidation
5. Analytics are processed through appropriate real-time or historical paths
6. Performance meets the specified benchmarks
7. All test cases pass with the required coverage

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up the development environment:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Install test dependencies
uv pip install pytest pytest-json-report

# Run tests and generate the required JSON report
pytest --json-report --json-report-file=pytest_results.json
```

CRITICAL: Generating and providing the pytest_results.json file is a mandatory requirement for project completion. This file serves as evidence that all functionality has been implemented correctly and passes all tests.