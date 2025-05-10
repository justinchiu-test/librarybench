# Edge-Optimized Retail IoT Microservices Framework

## Overview
A lightweight microservices framework designed specifically for retail environments with distributed IoT devices, enabling seamless coordination between edge devices and cloud services. This framework supports resource-constrained environments with offline capabilities, efficient data transmission, and dynamic service discovery while maintaining operational continuity across retail locations.

## Persona Description
Priya builds retail store systems connecting point-of-sale, inventory, and customer analytics using IoT devices. Her primary goal is to create a lightweight framework that can run on edge devices with limited resources while maintaining seamless coordination with cloud services.

## Key Requirements

1. **Edge-compatible Event Processing with Offline Operation Modes**
   - Implement lightweight event processing that operates within resource constraints of edge devices
   - Create store and forward mechanisms for handling network disconnections
   - This feature is critical for Priya as it ensures retail operations continue even during internet outages, preventing lost sales and maintaining business continuity in stores with unreliable connectivity

2. **Bandwidth-efficient Event Batching and Compression**
   - Develop intelligent event batching based on priority, size, and timing considerations
   - Implement context-aware compression optimized for retail data patterns
   - This capability allows Priya to minimize data transfer costs and operate effectively in stores with limited bandwidth, while ensuring timely delivery of business-critical information

3. **Device Capability Discovery with Dynamic Service Registration**
   - Create a service discovery mechanism suitable for heterogeneous device environments
   - Implement capability advertisement that adapts service interactions based on device features
   - This feature enables Priya's systems to automatically integrate new devices (POS terminals, inventory scanners, digital signage) with minimal configuration, supporting rapid deployment and hardware flexibility

4. **Store-level Event Partitioning with Regional Aggregation**
   - Develop partitioning strategies that isolate store-specific event domains
   - Create hierarchical aggregation for regional and enterprise-level analytics
   - This capability ensures each store's operations remain independent while enabling cross-store analysis and reporting, providing both operational isolation and enterprise visibility

5. **Power-aware Processing Prioritization for Battery-operated Devices**
   - Implement intelligent workload scheduling based on device power constraints
   - Create adaptive duty cycling for energy-intensive operations
   - This feature extends the operational time of battery-powered retail devices like handheld scanners and mobile POS systems, reducing charging frequency and ensuring devices remain operational throughout business hours

## Technical Requirements

### Testability Requirements
- All components must be testable on resource-constrained hardware
- Offline operation scenarios must be testable through network simulation
- Bandwidth efficiency must be measurable and verifiable in tests
- Device discovery must be testable with virtual device simulation
- Power consumption patterns must be profiled and verified in tests

### Performance Expectations
- Framework must run on devices with as little as 128MB RAM and 1GHz single-core CPU
- Offline operation must store at least 24 hours of typical transaction volume
- Bandwidth usage must not exceed 10MB per hour per device during normal operation
- Device discovery must complete within 30 seconds of network connection
- Battery-powered devices must maintain 8+ hours of operation with the framework

### Integration Points
- Integration with retail POS systems and electronic payment terminals
- Connectivity with inventory management scanners and systems
- Interfaces for customer loyalty devices and applications
- Communication with digital signage and in-store displays
- Hooks for integration with enterprise analytics platforms

### Key Constraints
- Must operate on heterogeneous device types with varying capabilities
- Must support efficient operation over cellular and unreliable Wi-Fi networks
- Should minimize power consumption on battery-operated devices
- Must maintain data integrity during extended offline periods
- Should operate with minimal on-site IT support requirements

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide the following core functionality:

1. **Edge Event Processing**
   - Lightweight event processing engine for constrained devices
   - Configurable event priority handling
   - Local event persistence for offline operation

2. **Network Optimization**
   - Adaptive event batching based on network conditions
   - Specialized compression for retail data types
   - Bandwidth-aware transmission scheduling

3. **Device Discovery and Management**
   - Zero-configuration service discovery protocol
   - Capability-based service registration
   - Dynamic service routing based on available resources

4. **Multi-level Event Architecture**
   - Store-level event isolation
   - Regional event aggregation
   - Enterprise-wide event distribution

5. **Resource Optimization**
   - Power-aware processing scheduler
   - Memory-efficient event handling
   - CPU usage optimization for constrained devices

6. **Retail Domain Patterns**
   - Transaction integrity across distributed components
   - Inventory synchronization patterns
   - Customer identity resolution

## Testing Requirements

### Key Functionalities That Must Be Verified
- Event processing continues during network disconnection and reconciles upon reconnection
- Bandwidth consumption remains within efficient parameters under various conditions
- Devices are correctly discovered and their capabilities accurately represented
- Events remain properly partitioned by store while enabling correct aggregation
- Battery life meets operational requirements on power-constrained devices

### Critical User Scenarios
- Store operates normally during internet outage and synchronizes upon reconnection
- System efficiently handles end-of-day data transfers to enterprise systems
- New device is deployed in store and automatically integrates with existing services
- Regional manager obtains cross-store analytics without disrupting individual operations
- Mobile devices operate throughout full business day without recharging

### Performance Benchmarks
- System maintains transaction processing times below 500ms even on constrained hardware
- Network usage remains below threshold during peak business hours
- Device discovery completes within expected timeframe
- Query performance for aggregated data meets interactive requirements
- Battery consumption remains within defined power budget

### Edge Cases and Error Conditions
- Extended offline operation (multiple days)
- Extremely limited bandwidth scenarios
- Heterogeneous device environment with capability mismatches
- Partial store power outage affecting subset of devices
- Corrupted data recovery after device failure

### Required Test Coverage Metrics
- 95% code coverage across all components
- 100% coverage of offline operation and recovery logic
- All network efficiency mechanisms explicitly tested
- Complete testing of device discovery across various scenarios
- Comprehensive power consumption profiling under various workloads

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Retail operations continue without disruption during network outages
- Data transmission costs reduced by at least 40% compared to non-optimized approaches
- New devices can be deployed by store staff without IT support
- Store managers and regional managers receive appropriate analytics at their respective levels
- Battery-powered devices reliably operate for full business day
- System operates effectively across all store locations regardless of connectivity quality
- All critical retail functions (sales, returns, inventory) maintain sub-second response times
- System can be deployed on existing retail hardware with minimal upgrades

## Getting Started

To set up the development environment for this project:

1. Initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install dependencies using `uv sync`

3. Run tests using `uv run pytest`

4. To execute specific Python scripts:
   ```
   uv run python your_script.py
   ```

5. For running linters and type checking:
   ```
   uv run ruff check .
   uv run pyright
   ```

Remember to design the framework as a library with well-documented APIs, not as an application with user interfaces. All functionality should be exposed through programmatic interfaces that can be easily tested and integrated into larger systems.