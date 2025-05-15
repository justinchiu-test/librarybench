# EmergencyShare - Resilient File Distribution for Disaster Response

## Overview
EmergencyShare is a specialized peer-to-peer file sharing library designed for emergency response operations when standard communication infrastructure is compromised. It focuses on rapid network establishment, prioritized message distribution, power efficiency, geographical organization, and cross-platform compatibility to enable effective information sharing during crisis situations.

## Persona Description
Priya organizes emergency response teams during natural disasters when communication infrastructure is compromised. She needs to establish ad-hoc file sharing networks for distributing maps, situation reports, and resource allocations.

## Key Requirements

1. **Rapid Network Bootstrapping**
   - Implement a simplified network formation system requiring minimal configuration in emergency situations
   - Critical for Priya to quickly establish communication channels when standard infrastructure is unavailable
   - Must establish functional file sharing within 60 seconds of device discovery
   - Should support automatic role assignment based on device capabilities and position

2. **Prioritized Message Distribution**
   - Create a message classification and routing system ensuring critical information propagates first
   - Essential for transmitting time-sensitive information like evacuation orders or medical needs
   - Must support at least three priority levels with preemptive routing for highest priority
   - Should include delivery confirmation for critical messages

3. **Low-Power Operation**
   - Develop power-aware protocols and scheduling to extend battery life of devices in the field
   - Vital when operating in disaster zones with limited or no power infrastructure
   - Must reduce power consumption by at least 50% compared to standard P2P protocols
   - Should adapt aggressively to remaining battery levels with progressive feature reduction

4. **Offline Map Support**
   - Implement geographical organization of shared resources with offline map capabilities
   - Crucial for coordinating response activities across a disaster area without internet access
   - Must support attaching location data to shared files and visualizing distribution by area
   - Should enable geographic queries to find resources within specific operational zones

5. **Cross-Platform Compatibility**
   - Create a highly compatible system working across whatever devices are available in the field
   - Important for accommodating the diverse equipment emergency responders might have access to
   - Must support at least Android, iOS, Windows, and Linux-based devices
   - Should degrade gracefully on devices with limited capabilities

## Technical Requirements

- **Testability Requirements**
  - Emergency network formation must be testable in simulated infrastructure-loss scenarios
  - Priority-based message distribution must be verifiable with instrumented message flows
  - Power consumption must be measurable and comparable across different operational modes
  - Geographic functions must be testable with simulated location data

- **Performance Expectations**
  - Network bootstrap must complete within 60 seconds from cold start
  - High-priority messages must reach all reachable nodes within 30 seconds
  - System must operate for at least 24 hours on a standard smartphone battery
  - Operations must remain responsive even with limited processing resources

- **Integration Points**
  - Standard geolocation data formats (GeoJSON, KML, etc.)
  - Common emergency response file formats (PDFs, images, spreadsheets)
  - Basic device power management interfaces
  - Common network interfaces found on various devices

- **Key Constraints**
  - All functionality must operate without internet connectivity
  - Implementation must be pure Python for maximum portability and compatibility
  - System must run with minimal memory and CPU usage
  - All operations must be designed for extreme reliability and fault tolerance

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The EmergencyShare implementation should provide these core functions:

1. **Emergency Network Establishment**
   - Rapid peer discovery using available network interfaces
   - Simplified authentication and trust establishment
   - Automatic network topology optimization
   - Role-based node configuration

2. **Critical Message Management**
   - Priority-based message classification
   - Preemptive routing for high-priority content
   - Store-and-forward with intelligent retry
   - Delivery confirmation and acknowledgment

3. **Power-Aware Operation**
   - Battery state monitoring and reporting
   - Adaptive duty cycling for network activities
   - Progressive feature reduction as power decreases
   - Scheduled wake-up for critical message checking

4. **Geographic Data Organization**
   - Location tagging for shared resources
   - Spatial indexing for efficient area-based queries
   - Map-based data organization without online services
   - Distance-aware routing and replication

5. **Multi-Platform Compatibility**
   - Platform detection and capability assessment
   - Adaptive feature availability based on device type
   - Common denominator protocol support
   - Format conversion for cross-device compatibility

## Testing Requirements

- **Key Functionalities to Verify**
  - Network forms correctly with minimal configuration in simulated disaster conditions
  - Critical messages are delivered before lower-priority content
  - Power optimization significantly extends operational time on battery
  - Geographic organization correctly associates resources with locations
  - System functions across simulated representations of different platforms

- **Critical User Scenarios**
  - Emergency response team rapidly establishing a sharing network after infrastructure loss
  - Incident command distributing prioritized situation reports and task assignments
  - Field teams operating devices for extended periods without recharging
  - Coordinating resource distribution across a geographically distributed disaster area
  - Team members using a mix of available devices to access the emergency network

- **Performance Benchmarks**
  - Network bootstrap must complete in under 60 seconds with 20+ simulated devices
  - Priority routing must deliver critical messages at least 5x faster than low-priority content
  - Power-saving mode must reduce battery consumption by at least 50%
  - Geographic queries must complete within 2 seconds even with 1000+ location-tagged resources
  - System must maintain functionality with at least 95% reliability in simulated failure conditions

- **Edge Cases and Error Handling**
  - Correct operation with highly intermittent connectivity between nodes
  - Graceful handling of device failures during critical operations
  - Recovery from network partitioning and re-merging
  - Proper behavior when battery reaches critical levels
  - Handling of conflicting geographic information

- **Test Coverage Requirements**
  - All emergency operations must have 100% test coverage
  - Battery efficiency must be verified with simulated power profiles
  - Geographic functions must be tested with diverse location scenarios
  - Cross-platform compatibility must be verified with platform-specific test cases

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

1. Emergency response teams can quickly establish functional file sharing networks
2. Critical information propagates with appropriate priority during emergencies
3. Devices operate efficiently to maximize battery life in the field
4. Resources can be organized and accessed based on geographic relevance
5. The system works effectively across different device types commonly found in emergency response
6. All functions operate reliably under the challenging conditions of disaster response
7. The system is simple enough to be deployed and used during high-stress emergency situations

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