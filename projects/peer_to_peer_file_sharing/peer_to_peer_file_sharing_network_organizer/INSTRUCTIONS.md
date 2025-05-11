# CommunityMesh - Peer-to-Peer File Sharing for Neighborhood Networks

## Overview
CommunityMesh is a resilient peer-to-peer file sharing library designed for community-owned networks in areas with limited broadband access. It prioritizes local-first discovery, shared caching, bandwidth fairness, public resource designation, and usage analytics to create a community-centered file sharing infrastructure that operates independently from external internet connections.

## Persona Description
Amara builds community-owned internet infrastructure in neighborhoods without reliable broadband access. She needs local file sharing capabilities that can operate independently of external internet connections.

## Key Requirements

1. **Local-First Discovery**
   - Implement discovery mechanisms that prioritize peers on the same physical network segment
   - Critical for establishing efficient connections within the neighborhood network
   - Must work without reliance on external internet services or DNS
   - Should identify nearby peers with minimal latency and bandwidth use

2. **Shared Cache Coordination**
   - Create a collaborative caching system to avoid redundant external downloads across the community
   - Essential for conserving limited external bandwidth available to the neighborhood
   - Must coordinate cache inventory across multiple devices with different storage capacities
   - Should implement intelligent cache eviction policies based on community usage patterns

3. **Bandwidth Fairness**
   - Develop algorithms ensuring equitable resource allocation among community members
   - Vital for preventing any single user from monopolizing limited shared bandwidth
   - Must dynamically adjust allocation based on network conditions and usage patterns
   - Should support configurable fairness policies to match community governance decisions

4. **Public Resource Designation**
   - Create a system allowing specific content to be marked for wide sharing within the community
   - Important for distributing community notices, educational materials, and local media
   - Must support metadata for describing community resources and their purpose
   - Should include permissions that reflect community sharing norms

5. **Usage Analytics**
   - Implement privacy-preserving analytics to demonstrate the network's value to potential participants
   - Critical for growth and sustainability of the community network initiative
   - Must aggregate utilization data without compromising individual privacy
   - Should generate reports on network health, popular resources, and community benefits

## Technical Requirements

- **Testability Requirements**
  - All components must be testable in simulated neighborhood network topologies
  - Community dynamics must be modelable with configurable peer behaviors
  - Analytics must be verifiable without compromising simulated privacy
  - Cache performance must be measurable under various usage patterns

- **Performance Expectations**
  - System must operate effectively on modest consumer hardware
  - Local discovery must identify nearby peers within 5 seconds
  - Shared caching must reduce external bandwidth usage by at least 60%
  - Fairness algorithms must prevent any single peer from using more than a configurable percentage of resources

- **Integration Points**
  - Common home networking equipment (consumer routers, mesh WiFi systems)
  - Basic network monitoring tools for health assessment
  - Standard caching strategies and protocols
  - Simple reporting formats for community engagement

- **Key Constraints**
  - Implementation must be pure Python for maximum device compatibility
  - All core functionality must operate without external internet
  - Privacy must be preserved in all operations, especially analytics
  - System must work with limited technical support infrastructure

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The CommunityMesh implementation should provide these core functions:

1. **Neighborhood Network Discovery**
   - Local-first peer identification and connection
   - Network topology mapping and optimization
   - Resilient peer tracking with persistent identification
   - Discovery protocol efficiency for limited networks

2. **Community Cache Management**
   - Distributed cache inventory system
   - Coordination of cache responsibilities
   - Deduplication of stored content
   - Intelligent prefetching and retention

3. **Resource Allocation**
   - Fair bandwidth distribution algorithms
   - Congestion detection and management
   - Prioritization framework for critical resources
   - Adaptive throttling based on network conditions

4. **Community Content System**
   - Public resource designation and discovery
   - Metadata for community-relevant content
   - Distribution optimization for widely-shared resources
   - Update propagation for community materials

5. **Network Analytics**
   - Privacy-preserving usage monitoring
   - Aggregated benefit reporting
   - Network health diagnostics
   - Growth and adoption tracking

## Testing Requirements

- **Key Functionalities to Verify**
  - Discovery correctly prioritizes peers on the same network segment
  - Caching effectively prevents redundant external downloads
  - Bandwidth allocation remains fair even under heavy load
  - Public resources are properly designated and widely available
  - Analytics provide useful insights while preserving privacy

- **Critical User Scenarios**
  - New device joining the community network and discovering local peers
  - Multiple community members accessing the same external resource
  - Network operating at capacity with competing bandwidth demands
  - Community leader publishing important notices for all residents
  - Generating reports to demonstrate network benefits to potential participants

- **Performance Benchmarks**
  - Local discovery must find at least a specified number of peers in each network segment within 5 seconds
  - Cache hit rate must exceed 60% for typical community usage patterns
  - No single peer should be able to consume more than a configurable percentage of bandwidth
  - Public resources must propagate to 95% of active peers within 10 minutes
  - Analytics processing must not consume more than 5% of system resources

- **Edge Cases and Error Handling**
  - Correct operation when external internet is completely unavailable
  - Graceful handling of peers with vastly different storage or bandwidth capabilities
  - Recovery from network partitions within the community
  - Handling of excessive public resource publishing
  - Management of malicious peers attempting to circumvent fairness

- **Test Coverage Requirements**
  - All public APIs must have 100% test coverage
  - Fairness algorithms must be tested under various load scenarios
  - Cache coordination must be tested with diverse community sizes and resource patterns
  - Privacy mechanisms must be verified to prevent individual data exposure

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

1. It enables effective file sharing within community networks with limited external connectivity
2. Local peers are quickly discovered and prioritized for efficient connections
3. Shared caching significantly reduces redundant external downloads
4. Bandwidth allocation remains fair and equitable among community members
5. Community resources can be easily designated and widely shared
6. Usage analytics provide valuable insights while preserving privacy
7. The system operates efficiently on typical consumer hardware found in underserved communities

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

1. Setup a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Install test dependencies with `uv pip install pytest pytest-json-report`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```