# Edge-Enabled Retail IoT Microservices Framework

## Overview
This project is a specialized event-driven microservices framework designed for retail IoT environments, enabling seamless communication between in-store edge devices and cloud services. It focuses on lightweight operation, offline capabilities, efficient bandwidth usage, and dynamic service discovery to create a resilient retail technology ecosystem that functions reliably even with limited connectivity.

## Persona Description
Priya builds retail store systems connecting point-of-sale, inventory, and customer analytics using IoT devices. Her primary goal is to create a lightweight framework that can run on edge devices with limited resources while maintaining seamless coordination with cloud services.

## Key Requirements

1. **Edge-compatible Event Processing with Offline Operation Modes**
   - Implement local event processing that functions without cloud connectivity
   - Create event storage mechanisms for offline operation with later synchronization
   - Support prioritization of critical retail operations during connectivity loss
   - Include conflict resolution strategies for reconnection scenarios
   - This feature is critical for retail environments where internet connectivity may be unreliable but business operations must continue uninterrupted

2. **Bandwidth-efficient Event Batching and Compression**
   - Develop intelligent event batching based on priority and bandwidth availability
   - Implement efficient binary serialization formats for IoT device communication
   - Create adaptive compression strategies based on device capabilities and network conditions
   - Include delta-encoding for similar sequential events
   - This feature optimizes network usage in retail environments with limited or costly bandwidth

3. **Device Capability Discovery with Dynamic Service Registration**
   - Create an automatic device capability discovery mechanism
   - Implement dynamic service registration as devices join the network
   - Support capability negotiation between devices with different resources
   - Include graceful degradation based on available capabilities
   - This feature enables plug-and-play operation of diverse retail devices without manual configuration

4. **Store-level Event Partitioning with Regional Aggregation**
   - Implement event partitioning based on physical store boundaries
   - Create regional event aggregation for multi-store analytics
   - Support for store-specific event handling rules and policies
   - Include cross-store event correlation for inventory and customer tracking
   - This feature maintains data locality while enabling chain-wide operations and analytics

5. **Power-aware Processing Prioritization for Battery-operated Devices**
   - Develop power consumption profiling for different operations
   - Implement adaptive processing based on battery levels
   - Create sleep/wake scheduling for non-critical operations
   - Include power state management across device collections
   - This feature extends battery life for mobile retail devices while ensuring critical functions remain available

## Technical Requirements

### Testability Requirements
- Support for simulating networks of IoT devices with varying capabilities
- Ability to test offline scenarios and reconnection handling
- Support for testing under constrained resource conditions
- Verification of power consumption patterns

### Performance Expectations
- Support for minimum 100 IoT devices per retail location
- Maximum 50ms latency for in-store event processing
- Ability to operate for at least a 12-hour retail day on battery power
- Efficient synchronization after offline periods (at least 1000 events/minute)

### Integration Points
- Compatible with common retail IoT devices (POS, inventory scanners, beacons)
- Support for standard IoT protocols (MQTT, CoAP)
- Integration with cloud-based analytics and management systems
- Support for existing inventory and customer management systems

### Key Constraints
- Must operate on devices with as little as 256MB RAM and 1GHz CPU
- Must function in environments with intermittent connectivity
- Power consumption must be optimized for battery-operated devices
- Data storage must be efficient for devices with limited capacity

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Lightweight Event Processing Engine**
   - Efficient event processing for resource-constrained devices
   - Support for local and distributed event handling
   - Prioritization mechanisms for critical retail operations
   - Offline operation with event storage and replay

2. **Network and Communication Management**
   - Bandwidth-efficient communication protocols
   - Intelligent batching and compression
   - Reliable delivery with store-and-forward capabilities
   - Adaptive behavior based on network conditions

3. **Device and Service Discovery**
   - Automatic capability discovery and registration
   - Service advertisement and discovery
   - Version and compatibility management
   - Dynamic service composition based on available devices

4. **Data Locality and Aggregation**
   - Store-level data partitioning
   - Local-first processing with regional aggregation
   - Cross-store data correlation
   - Hierarchical event processing (device, store, region, chain)

5. **Resource Management**
   - Battery and power consumption optimization
   - Storage management for limited capacity devices
   - Adaptive CPU usage based on device capabilities
   - Resource monitoring and management

## Testing Requirements

### Key Functionalities that Must be Verified
- Offline operation and successful synchronization upon reconnection
- Efficient bandwidth usage through batching and compression
- Successful device discovery and capability negotiation
- Proper store-level event partitioning and regional aggregation
- Power consumption optimization for battery-operated devices

### Critical User Scenarios
- Complete retail transaction processing during internet outage
- Deployment of new devices with automatic capability discovery
- Cross-store inventory reconciliation
- Battery operation throughout a complete business day
- Recovery after unexpected device shutdown or network failure

### Performance Benchmarks
- Process 100 sales transactions per minute on edge devices
- Maintain local response time under 50ms for customer-facing operations
- Operate on battery power for 12+ hours with typical retail workloads
- Synchronize 10,000+ offline events within 10 minutes of reconnection

### Edge Cases and Error Conditions
- Extended offline operation beyond local storage capacity
- Network reconnection with conflict resolution
- Partial device failures in the store network
- Extreme low battery conditions
- Handling of incompatible device capabilities

### Required Test Coverage Metrics
- Minimum 90% line coverage for all code
- 100% coverage of offline operation and synchronization logic
- 100% coverage of power management functionality
- 100% coverage of device discovery and capability negotiation

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

1. The system demonstrates reliable operation in both connected and offline modes
2. Network communication is optimized for bandwidth efficiency
3. Devices can be dynamically discovered and integrated into the system
4. Events are properly partitioned by store with support for regional aggregation
5. Battery life is maximized through power-aware processing
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