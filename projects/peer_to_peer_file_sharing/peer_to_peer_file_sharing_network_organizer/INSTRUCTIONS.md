# Community Mesh Content Distribution System

## Overview
A resilient peer-to-peer content sharing platform designed for community mesh networks, enabling local-first data sharing, collaborative caching, and equitable resource distribution without requiring external internet connectivity or centralized infrastructure.

## Persona Description
Amara builds community-owned internet infrastructure in neighborhoods without reliable broadband access. She needs local file sharing capabilities that can operate independently of external internet connections.

## Key Requirements
1. **Local-First Discovery and Routing**
   - Automatic discovery of peers on the same physical network segment
   - Subnet-aware routing prioritizing local connections
   - Topology mapping of the community network
   - Essential for optimizing data flow within the mesh network, reducing unnecessary hops and ensuring content stays within the local infrastructure when possible

2. **Shared Cache Coordination**
   - Distributed cache management across network nodes
   - Content popularity tracking and retention policies
   - Cooperative fetching of external resources
   - Critical for minimizing redundant external downloads in bandwidth-constrained environments, allowing the community to collaboratively build a local information repository

3. **Bandwidth Fairness Mechanisms**
   - Equitable resource allocation algorithms
   - Usage monitoring and quota management
   - Congestion detection and mitigation
   - Necessary for preventing individual users from monopolizing limited network resources, ensuring all community members have fair access to shared bandwidth

4. **Public Resource Designation**
   - Content tagging for community-wide sharing
   - Access level management for different content types
   - Distribution policies for public resources
   - Vital for creating a commons of locally relevant information that benefits the entire community, from educational materials to local news and announcements

5. **Usage Analytics and Reporting**
   - Network utilization metrics collection
   - Content popularity and access patterns
   - Impact measurement for community benefit
   - Essential for demonstrating the value of the mesh network to potential participants, securing funding, and making data-driven decisions about network expansion

## Technical Requirements
### Testability Requirements
- All components must have comprehensive unit tests
- Network topology simulations for testing routing algorithms
- Distributed cache behavior validation
- Fairness mechanism testing with various usage scenarios
- Analytics accuracy verification against known patterns

### Performance Expectations
- Support for at least 200 active nodes in a mesh
- Efficient operation on low-cost, limited hardware
- Responsiveness with high-latency inter-node connections
- Graceful degradation under network stress
- Minimal memory footprint on network devices

### Integration Points
- Compatible with standard mesh networking hardware
- Support for various Wi-Fi mesh protocols
- Integration with community captive portal systems
- Export capabilities for network monitoring tools
- Compatibility with local content management systems

### Key Constraints
- Must operate without external internet dependencies
- Suitable for low-power, limited hardware devices
- No cloud services requirements for core functionality
- Configurable through simple text files
- Resource usage appropriate for shared infrastructure

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Local Network Intelligence**
   - Peer discovery on local subnets
   - Network topology mapping and visualization data
   - Route optimization for local traffic
   - Connection quality monitoring

2. **Distributed Cache System**
   - Content indexing and metadata management
   - Replication and distribution policies
   - Cache eviction and retention strategies
   - Collaborative external resource fetching

3. **Resource Allocation Framework**
   - Bandwidth monitoring and accounting
   - Fair scheduling algorithms
   - Usage quota enforcement
   - Congestion detection and management

4. **Community Content Management**
   - Content classification and tagging system
   - Access control and permission management
   - Distribution policy enforcement
   - Content integrity verification

5. **Analytics Engine**
   - Metrics collection and aggregation
   - Statistical analysis of usage patterns
   - Reporting data generation
   - Impact assessment calculations

## Testing Requirements
### Key Functionalities to Verify
- Effective local-first routing in various network topologies
- Efficient cache coordination reducing redundant downloads
- Fair resource allocation under different load scenarios
- Proper management of content with different sharing levels
- Accurate analytics collection reflecting actual network usage

### Critical Scenarios to Test
- Network operation with purely local connectivity
- Cache behavior with limited storage across nodes
- Bandwidth allocation during peak usage periods
- Community-wide distribution of designated public content
- Analytics generation for various network activities

### Performance Benchmarks
- Discovery time for new peers on local network
- Cache hit rate improvement over uncached operation
- Fairness index (Jain's fairness index) > 0.8 under load
- Distribution time for public resources to all nodes
- Analytics processing overhead < 5% of system resources

### Edge Cases and Error Conditions
- Network partitions and merges
- Device failures during content transfer
- Storage exhaustion on cache nodes
- Extreme bandwidth contention
- Conflicting resource allocation policies
- Recovery from corrupted content or indices

### Required Test Coverage
- ≥90% line coverage for routing and discovery code
- ≥85% coverage for cache coordination components
- 100% coverage for fairness enforcement algorithms
- ≥90% coverage for public resource designation system
- ≥85% coverage for analytics collection mechanisms

## Success Criteria
The implementation will be considered successful when:

1. Network traffic is optimized to prioritize local connections
2. External download requirements are minimized through effective caching
3. All community members receive fair access to limited bandwidth
4. Locally relevant content is easily shared with the entire community
5. Network value can be demonstrated through comprehensive analytics
6. All five key requirements are fully implemented and testable via pytest
7. The system operates effectively on affordable, community-grade hardware
8. Network resource utilization improves compared to uncoordinated approaches

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.