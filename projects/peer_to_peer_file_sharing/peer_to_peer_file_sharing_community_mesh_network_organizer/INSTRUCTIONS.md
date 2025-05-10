# MeshShare - A Community-Focused P2P File Sharing System for Neighborhood Networks

## Overview
MeshShare is a peer-to-peer file sharing system optimized for local community mesh networks, allowing neighborhoods without reliable broadband access to efficiently share files, cache internet resources, and distribute community content. It prioritizes local-first discovery, equitable resource allocation, and usage analytics to support sustainable community internet infrastructure.

## Persona Description
Amara builds community-owned internet infrastructure in neighborhoods without reliable broadband access. She needs local file sharing capabilities that can operate independently of external internet connections.

## Key Requirements
1. **Local-First Discovery Protocol**
   - Optimization system prioritizing peers on the same physical network segment
   - Critical for Amara's neighborhood networks where local connectivity is more reliable and faster than external connections, ensuring that content already available locally doesn't unnecessarily consume precious external bandwidth
   - Must include automatic discovery of local peers, network topology awareness, and proximity-based routing optimizations

2. **Shared Cache Coordination System**
   - Collaborative caching to avoid redundant external downloads across the community
   - Essential because Amara's networks have limited external bandwidth that must be used efficiently - when one community member downloads content from the internet, others should be able to access it locally
   - Implementation should include distributed cache indexes, content addressing, cache eviction policies, and mechanisms to validate cache freshness

3. **Bandwidth Fairness Mechanisms**
   - Resource allocation algorithms ensuring equitable distribution among community members
   - Vital for maintaining community trust in the network, preventing a few heavy users from monopolizing the limited shared bandwidth and ensuring all community members have fair access to network resources
   - Requires traffic shaping, usage monitoring, fair queuing algorithms, and configurable fairness policies

4. **Public Resource Designation Framework**
   - System for marking specific content to be widely shared within the community
   - Important for distributing community-relevant material (local news, announcements, educational resources) with prioritized replication across the network to ensure high availability
   - Should include content tagging, replication policies, availability metrics, and content integrity verification

5. **Usage Analytics Collection**
   - Data gathering tools demonstrating the network's value to potential participants
   - Critical for Amara to secure community buy-in and potential funding by quantifying the benefits of the mesh network with concrete metrics about usage patterns, bandwidth savings, and community engagement
   - Must include privacy-preserving statistics collection, utilization metrics, performance analysis, and reporting capabilities

## Technical Requirements
- **Testability Requirements**
  - Simulation of mesh network topologies with variable connection qualities
  - Mocked community usage patterns based on realistic scenarios
  - Validation of fair bandwidth allocation under constrained conditions
  - Test harnesses for cache coordination efficiency
  - Metrics collection accuracy verification

- **Performance Expectations**
  - Support for mesh networks with up to 200 community nodes
  - Efficient operation on diverse hardware (from old laptops to Raspberry Pis)
  - Local transfer speeds at least 90% of theoretical maximum for the local network
  - Cache hit rates above 70% for common community content
  - Minimal overhead on low-powered devices (<=5% CPU utilization when idle)

- **Integration Points**
  - Common mesh networking protocols (B.A.T.M.A.N., OLSR)
  - Standard caching mechanisms (HTTP caching, content-addressable storage)
  - Various connection types (WiFi, ethernet, long-range wireless)
  - Community server resources when available
  - Public internet gateways with metered connections

- **Key Constraints**
  - Must function without external internet access
  - Must operate on heterogeneous and often older hardware
  - Must be resilient to frequent node joins/leaves as devices connect/disconnect
  - Must accommodate varied technical skill levels among community members
  - Must respect privacy while gathering useful aggregate statistics

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
MeshShare must provide a comprehensive solution for community mesh network file sharing with these core components:

1. A mesh-optimized P2P protocol that prioritizes local connections and minimizes external bandwidth usage
2. A distributed content cache that coordinates storage across the community network to avoid duplicate downloads
3. A fair bandwidth allocation system that prevents resource monopolization by any single user
4. A content classification framework that allows for special handling of community-relevant material
5. A privacy-preserving analytics system that gathers usage data to demonstrate network value
6. Node discovery and routing optimizations specifically designed for mesh network topologies
7. A resource scheduling system that manages bandwidth contention and prioritizes critical transfers
8. A network health monitoring system that detects and reports connectivity issues

The system should provide programmatic APIs that can be integrated with existing mesh networking solutions and community infrastructure, with clear interfaces for all features.

## Testing Requirements
The implementation must include comprehensive test suites verifying:

- **Key Functionalities**
  - Validation of local-first discovery prioritization accuracy
  - Verification of cache coordination preventing redundant downloads
  - Confirmation of bandwidth allocation fairness under various usage scenarios
  - Validation of public resource designation and prioritization
  - Verification of analytics collection accuracy and privacy preservation

- **Critical User Scenarios**
  - A new community member joining the mesh network and discovering available resources
  - Community members sharing internet-downloaded content through the local cache
  - Heavy usage periods with multiple competing transfer requests being fairly managed
  - Distribution of important community announcements as public resources
  - Network organizers evaluating usage patterns to plan infrastructure improvements

- **Performance Benchmarks**
  - Local discovery completing within 30 seconds of a new node joining
  - Cache hit rates exceeding 70% for frequently accessed content
  - Bandwidth distribution fairness index of at least 0.8 (where 1.0 is perfectly fair)
  - Public resources achieving 99% availability across active nodes
  - Analytics collection with less than 1% impact on network performance

- **Edge Cases and Error Conditions**
  - Graceful handling of nodes abruptly leaving the network
  - Recovery from network partitions when segments reconnect
  - Adaptation to highly constrained bandwidth scenarios
  - Detection and management of misbehaving nodes that attempt to monopolize resources
  - Operation during partial internet gateway availability

- **Required Test Coverage Metrics**
  - Minimum 90% statement coverage for all modules
  - Comprehensive tests for each mesh networking scenario
  - Performance tests validating operation within specified constraints
  - Stress tests with simulated community-scale usage patterns
  - Coverage of all error recovery and edge case handling paths

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. The system consistently prioritizes local connections over external bandwidth usage
2. Community-wide caching significantly reduces redundant external downloads
3. Bandwidth resources are allocated fairly across all participating nodes
4. Community-relevant content is effectively prioritized and highly available
5. Usage analytics provide clear, privacy-preserving insights into network value
6. The system performs efficiently on the diverse hardware typically found in community networks
7. The implementation can operate independently of external internet access
8. The solution integrates with existing mesh networking protocols and infrastructure

To set up your development environment, follow these steps:

1. Use `uv init --lib` to set up the project and create your `pyproject.toml`
2. Install dependencies with `uv sync`
3. Run your code with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format your code with `uv run ruff format`
6. Lint your code with `uv run ruff check .`
7. Type check with `uv run pyright`