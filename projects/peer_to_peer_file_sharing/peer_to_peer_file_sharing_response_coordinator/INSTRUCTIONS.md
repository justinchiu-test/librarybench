# Emergency Response Information Network

## Overview
A rapid-deployment peer-to-peer file sharing system designed for disaster scenarios, enabling emergency responders to quickly establish local information networks for distributing critical resources, situation reports, and coordination data when conventional communication infrastructure is compromised or unavailable.

## Persona Description
Priya organizes emergency response teams during natural disasters when communication infrastructure is compromised. She needs to establish ad-hoc file sharing networks for distributing maps, situation reports, and resource allocations.

## Key Requirements
1. **Rapid Network Bootstrapping**
   - One-touch network establishment with minimal configuration
   - Automatic peer discovery on any available network medium
   - Resilient connection maintenance during unstable conditions
   - Critical for quickly establishing communication channels when responders arrive at disaster sites, requiring minimal technical expertise and setup time even under high-stress conditions

2. **Prioritized Message Distribution**
   - Multi-level message prioritization system
   - Guaranteed delivery for critical communications
   - Bandwidth allocation based on message importance
   - Essential for ensuring that life-saving information and critical updates propagate first when network capacity is limited, following established emergency management protocols

3. **Low-Power Operation Mode**
   - Battery-optimized communication protocols
   - Configurable power-saving settings
   - Energy usage monitoring and management
   - Vital for extending device battery life in disaster zones without reliable power sources, ensuring communication capability persists throughout extended response operations

4. **Offline Geographical Information Support**
   - Embedded map functionality without external services
   - Geospatial tagging of shared resources and reports
   - Location-based filtering and organization
   - Necessary for coordinating response activities with geographical context when online mapping services are unavailable, helping responders navigate unfamiliar areas

5. **Cross-Platform Compatibility**
   - Support for diverse device types commonly used in field operations
   - Progressive capability adaptation based on device capabilities
   - Common data format support across all platforms
   - Critical for accommodating whatever devices are available during disaster response, creating a unified information network regardless of hardware diversity

## Technical Requirements
### Testability Requirements
- All components must function in simulated disaster conditions
- Network formation must be testable with various device configurations
- Priority system tests must verify critical message delivery
- Power consumption must be measurable and verifiable
- Offline mapping functionality must be thoroughly tested

### Performance Expectations
- Network bootstrap time < 60 seconds from cold start
- High-priority message propagation < 30 seconds across network
- Battery impact reduced by at least 50% in power-saving mode
- Support for at least 100 nodes in a single disaster-zone network
- Stable operation with 50% packet loss and high latency

### Integration Points
- Common disaster response tool compatibility
- GPS and location service integration
- Standard emergency data format support
- Integration with radio and alternative communication systems
- Field equipment connectivity options

### Key Constraints
- Must operate without external infrastructure dependencies
- Minimal resource requirements for operation on limited devices
- No internet connectivity requirement for core functionality
- Simple API for integration with emergency management software
- Data integrity must be maintained even in challenging conditions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Emergency Network Formation**
   - Rapid peer discovery methods
   - Connection establishment and maintenance
   - Network health monitoring
   - Resilient topology management

2. **Priority-Based Message System**
   - Message classification and tagging
   - Priority queue management
   - Guaranteed delivery mechanisms
   - Adaptive retransmission strategies

3. **Power Management Framework**
   - Communication efficiency optimization
   - Energy-aware protocol adjustments
   - Battery state monitoring integration
   - Scheduled activity management

4. **Offline Geospatial Engine**
   - Compact map data storage and rendering
   - Location-based indexing system
   - Geospatial query capabilities
   - Position tracking and mapping

5. **Multi-Platform Adaptation Layer**
   - Device capability detection
   - Format conversion for compatibility
   - Progressive functionality adaptation
   - Unified API across platforms

## Testing Requirements
### Key Functionalities to Verify
- Successful network formation under difficult conditions
- Correct message delivery according to priority levels
- Extended battery life in power-saving modes
- Accurate geospatial functionality without online services
- Proper operation across multiple device types

### Critical Scenarios to Test
- Network establishment in various challenging environments
- Message distribution during partial network failures
- Battery performance during sustained operation
- Geospatial functionality with complex response scenarios
- Cross-platform information exchange and compatibility

### Performance Benchmarks
- 100% success rate for critical message delivery
- Network formation time under varying conditions
- Power consumption reduction measured on standard devices
- Map rendering and query performance on limited hardware
- Cross-platform data exchange latency

### Edge Cases and Error Conditions
- Extreme network degradation and recovery
- Device failures during critical operations
- Near-depleted battery operation
- Corrupted or incomplete geospatial data
- Incompatible device joining the network
- Recovery from complete communication breakdown

### Required Test Coverage
- 100% coverage of network bootstrap mechanisms
- 100% coverage of priority message handling
- ≥95% coverage for power management components
- ≥90% coverage for offline geospatial functionality
- ≥95% coverage for cross-platform adaptation layer

## Success Criteria
The implementation will be considered successful when:

1. Response teams can establish functional communication networks within minutes of arrival
2. Critical information reliably reaches all team members despite network challenges
3. Devices maintain operational battery life throughout extended deployments
4. Responders can effectively coordinate using geographical information without external services
5. All available devices can be incorporated into the emergency network regardless of type
6. All five key requirements are fully implemented and testable via pytest
7. The system enables faster information sharing compared to traditional emergency methods
8. Response coordinators report improved team coordination in training exercises

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.