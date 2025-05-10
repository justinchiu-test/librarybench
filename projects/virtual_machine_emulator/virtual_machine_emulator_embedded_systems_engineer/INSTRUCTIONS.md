# Embedded Systems Virtual Machine Emulator

## Overview
A specialized virtual machine emulator that accurately simulates resource-constrained embedded environments, allowing engineers to test algorithms, firmware, and resource utilization before deploying to actual hardware. The emulator focuses on modeling hardware limitations, interrupt handling, real-time constraints, power consumption, and peripheral interfaces.

## Persona Description
Priya develops firmware for resource-constrained devices and uses a virtual machine to test algorithms before deploying to actual hardware. She needs an emulator that accurately represents the limitations of embedded environments.

## Key Requirements
1. **Resource Constraint Simulation**: Implement configurable memory and processing limitations that accurately reflect target embedded hardware. This is essential for Priya to validate that her code will function correctly within the strict resource boundaries of actual devices, preventing deployment of firmware that would exceed available resources and fail in production environments.

2. **Interrupt Handling Framework**: Create a comprehensive system for modeling hardware-triggered events and interrupt service routines. This feature is critical for Priya to test how her firmware responds to external signals, timer events, and peripheral notifications, ensuring that her interrupt handlers are efficient and correctly prioritized for real-world operation.

3. **Real-time Operation Modeling**: Develop mechanisms for enforcing and validating strict timing requirements common in embedded systems. This allows Priya to verify that her firmware meets critical deadlines and timing constraints before deployment, identifying potential timing violations that could cause system failures in time-sensitive applications.

4. **Power Consumption Estimation**: Implement analysis tools that estimate energy usage based on instruction execution patterns and peripheral activity. This capability helps Priya optimize her firmware for battery-operated devices, identifying power-hungry code segments and validating that her algorithms meet power budgets for extended operation in the field.

5. **Peripheral Device Simulation**: Design interfaces for virtual sensors, actuators, and communication protocols commonly used in embedded systems. This feature enables Priya to test her firmware's interaction with external components before connecting to actual hardware, ensuring compatibility and proper handling of sensor data, control signals, and communication protocols.

## Technical Requirements

### Testability Requirements
- All resource limitations must be precisely configurable and measurable
- Interrupt triggering must be reproducible for deterministic testing
- Timing violations must be clearly detectable and reportable
- Power consumption estimates must be consistent and comparable across runs
- Peripheral interactions must be simulatable with controlled input patterns

### Performance Expectations
- The emulator should support clock frequencies representative of target embedded processors (typically 1-200 MHz)
- Interrupt latency should be accurately modeled to within microsecond precision
- Memory access patterns should reflect the characteristics of embedded architectures
- Power estimation should be accurate enough to identify relative differences between implementations
- The system should execute fast enough to run comprehensive tests in reasonable time (at least 10x real-time for most scenarios)

### Integration Points
- Well-defined interfaces for loading firmware images
- Configurable memory maps matching typical embedded architectures
- Peripheral device simulation APIs for sensors and actuators
- Communication protocol endpoints (I2C, SPI, UART, etc.)
- Export mechanisms for resource utilization and timing reports

### Key Constraints
- The emulator must accurately model the behavior of specific embedded architectures
- Resource limitations must be strictly enforceable (RAM, ROM, stack size, etc.)
- Timing behavior must be deterministic for reliable real-time testing
- The implementation must support both cycle-accurate and accelerated execution modes
- The system must be usable for automated testing of embedded firmware

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A configurable embedded processor emulator with accurate instruction timing
2. Memory management with strict size limitations and access timing
3. An interrupt controller supporting multiple priority levels and sources
4. A scheduler for real-time task management and deadline tracking
5. Peripheral device simulations with realistic timing and behavior
6. Communication protocol implementations (I2C, SPI, UART, etc.)
7. Power consumption tracking and analysis tools
8. Resource utilization monitoring and reporting
9. Clock and timer systems with configurable frequencies
10. Test automation capabilities for firmware validation

The system should allow embedded systems engineers to load firmware, configure the virtual hardware environment to match target devices, execute code with realistic timing and resource constraints, and collect detailed performance metrics for optimization and validation purposes.

## Testing Requirements

### Key Functionalities to Verify
- Correct enforcement of memory constraints and access patterns
- Accurate interrupt handling with proper prioritization
- Real-time deadline enforcement and violation detection
- Reasonable accuracy of power consumption estimates
- Proper functionality of peripheral device simulations
- Accurate modeling of communication protocols
- Reliable resource utilization tracking

### Critical User Scenarios
- Loading and executing firmware within constrained memory environments
- Testing interrupt handlers with various triggering patterns
- Validating real-time behavior with strict deadlines
- Optimizing algorithms for power efficiency
- Integrating firmware with simulated peripheral devices
- Testing communication protocol implementations
- Measuring and optimizing resource utilization

### Performance Benchmarks
- Ability to simulate processors running at up to 200 MHz
- Interrupt latency modeling accurate to within 10 microseconds
- Memory access timing reflective of actual embedded hardware
- Power estimation correlating within 20% of actual hardware measurements
- Execution speed of at least 10x real-time for typical embedded applications
- Support for firmware images up to 2MB with appropriate memory constraints

### Edge Cases and Error Conditions
- Handling of stack overflows in constrained environments
- Proper detection of memory access violations
- Management of interrupt priority inversions
- Detection of real-time deadline misses
- Handling of peripheral device failure conditions
- Proper management of communication protocol errors
- Graceful reporting of resource exhaustion

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of memory constraint enforcement
- 100% coverage of interrupt handling mechanisms
- 100% coverage of real-time scheduling and deadline tracking
- All peripheral device simulations must have specific test cases
- All error handling paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. An embedded systems engineer can use it to validate firmware before hardware deployment
2. The system accurately models resource constraints of typical embedded platforms
3. Interrupt handling behaves consistently with real hardware expectations
4. Real-time deadlines are properly enforced and violations detected
5. Power consumption estimates provide useful guidance for optimization
6. Peripheral device simulations correctly model timing and behavior characteristics
7. All test cases pass with the specified coverage requirements
8. Documentation clearly explains how to configure the emulator for different target platforms

## Project Setup and Development

To set up the development environment:

1. Create a new project using UV:
   ```
   uv init --lib
   ```

2. Run the project:
   ```
   uv run python your_script.py
   ```

3. Install additional dependencies:
   ```
   uv sync
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```