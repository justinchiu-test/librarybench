# EmergencyShare - A Resilient P2P File Sharing System for Disaster Response

## Overview
EmergencyShare is a specialized peer-to-peer file sharing system designed for disaster response scenarios where communication infrastructure is compromised. It enables rapid deployment of ad-hoc file sharing networks for emergency teams to distribute critical information like maps, situation reports, and resource allocation plans with minimal configuration, prioritized messaging, and cross-platform compatibility.

## Persona Description
Priya organizes emergency response teams during natural disasters when communication infrastructure is compromised. She needs to establish ad-hoc file sharing networks for distributing maps, situation reports, and resource allocations.

## Key Requirements
1. **Rapid Network Bootstrapping**
   - Simplified setup system requiring minimal configuration in emergency situations
   - Critical for Priya because disaster response teams need to establish communication channels immediately upon arrival, often with stressed personnel who have limited time and technical capacity for complex setup procedures
   - Must include zero-configuration networking, automatic peer discovery, role-based automatic configuration, and resilient operation with minimal dependencies

2. **Prioritized Message Distribution**
   - Information routing system ensuring critical data propagates first
   - Essential for effective disaster response as some information (evacuation orders, medical emergency locations) has life-saving importance and must take precedence over routine updates, especially when bandwidth is severely constrained
   - Implementation should include message classification, priority-based queuing, preemptive transfer for urgent data, and delivery confirmation for critical messages

3. **Low-Power Operation Mode**
   - Energy conservation features extending battery life of field devices
   - Vital because disaster areas often lack reliable power sources, requiring devices to operate for extended periods on battery power while maintaining essential communication capabilities
   - Requires intelligent power management, reduced transmission frequencies for non-critical data, sleep modes with wake-on-message capabilities, and optimized protocols to minimize power consumption

4. **Offline Map Support**
   - Geographical organization system for location-based shared resources
   - Important for coordinating geographically distributed teams who need to associate information with specific locations, allowing responders to quickly find relevant data for their operational area
   - Should include spatial indexing, map-based data organization, distance-based relevance filtering, and support for standard geospatial formats

5. **Cross-Platform Compatibility**
   - Universal operation across diverse devices available in the field
   - Critical because disaster response teams use whatever devices are available - from smartphones to laptops to specialized equipment - requiring a system that works seamlessly across different operating systems and hardware capabilities
   - Must support at minimum Windows, macOS, Linux, Android, and iOS with consistent functionality across all platforms

## Technical Requirements
- **Testability Requirements**
  - Simulation of network conditions typical in disaster scenarios
  - Testing under extreme resource constraints (bandwidth, power, processing capability)
  - Validation of cross-platform message compatibility
  - Verification of priority-based message delivery
  - Performance testing on low-powered devices

- **Performance Expectations**
  - Network bootstrap completed in under 60 seconds from cold start
  - Critical messages propagating to all connected nodes within 2 minutes
  - Battery impact not exceeding 20% above idle power consumption
  - Support for operation on devices with as little as 512MB RAM
  - Handling of disconnected operation with automatic resynchronization

- **Integration Points**
  - Common emergency management software
  - Standard geographic data formats (GeoJSON, Shapefile, KML)
  - Various radio and communication systems (WiFi, Bluetooth, LoRa)
  - Incident management systems and protocols
  - Existing disaster response hardware

- **Key Constraints**
  - Must operate without any internet connectivity
  - Must function reliably in chaotic and highly stressed environments
  - Must be usable by personnel with minimal training
  - Must prioritize reliability over feature richness
  - Must be fault-tolerant against unpredictable network conditions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
EmergencyShare must provide a robust peer-to-peer solution for emergency communication with these core components:

1. A zero-configuration network formation system that establishes connectivity with minimal user intervention
2. A message prioritization and routing engine that ensures critical information propagates efficiently
3. A power management system that optimizes battery life while maintaining essential functionality
4. A geospatial organization framework that associates shared data with geographical contexts
5. A cross-platform compatibility layer ensuring consistent operation across diverse devices
6. A store-and-forward mechanism for handling intermittent connectivity between nodes
7. A role-based configuration system that adapts functionality based on the node's purpose
8. A lightweight security system providing basic authentication and data integrity verification

The system should provide clear, simple APIs that can be integrated into various emergency response applications and workflows, focusing on reliability and simplicity rather than feature complexity.

## Testing Requirements
The implementation must include comprehensive test suites verifying:

- **Key Functionalities**
  - Validation of network formation under adverse conditions
  - Verification of message priority handling and delivery sequencing
  - Confirmation of power consumption within specified limits
  - Validation of geospatial data organization and retrieval
  - Verification of cross-platform message compatibility

- **Critical User Scenarios**
  - Emergency teams establishing an ad-hoc network in a new disaster zone
  - Distribution of high-priority evacuation orders across the response network
  - Teams operating on battery power for extended periods in the field
  - Coordination of resources using location-based data organization
  - Diverse response teams using different device types to access the same information

- **Performance Benchmarks**
  - Network formation completing within 60 seconds with 95% reliability
  - Priority message delivery to all nodes within 2 minutes even at 50% connectivity
  - Power consumption remaining below specified thresholds on reference devices
  - Offline map operations responding within 3 seconds on low-end devices
  - Cross-platform message handling with 100% compatibility

- **Edge Cases and Error Conditions**
  - Recovery from sudden node disconnections in the middle of critical transfers
  - Adaptation to extremely constrained bandwidth (as low as 1KB/s)
  - Graceful degradation when device batteries reach critical levels
  - Handling of conflicting or outdated geospatial information
  - Operation in environments with high electromagnetic interference

- **Required Test Coverage Metrics**
  - Minimum 90% statement coverage for all modules
  - Explicit testing for each disaster scenario use case
  - Performance testing under simulated emergency conditions
  - Battery consumption validation on multiple device profiles
  - Stress testing with simulated network degradation

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. Response teams can establish functional communication networks within 1 minute of arrival
2. Critical information consistently propagates across the network with appropriate priority
3. Devices operate efficiently on battery power throughout extended emergency operations
4. Responders can easily locate geographically relevant information for their operational area
5. The system functions consistently across all commonly used device types and platforms
6. All operations maintain reliability under the challenging conditions typical in disaster response
7. The solution integrates with existing emergency management workflows and tools
8. The system can be deployed and used effectively with minimal training

To set up your development environment, follow these steps:

1. Use `uv init --lib` to set up the project and create your `pyproject.toml`
2. Install dependencies with `uv sync`
3. Run your code with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format your code with `uv run ruff format`
6. Lint your code with `uv run ruff check .`
7. Type check with `uv run pyright`