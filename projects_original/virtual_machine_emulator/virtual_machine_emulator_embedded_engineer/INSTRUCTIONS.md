# Resource-Constrained Embedded Systems Emulator

## Overview
A specialized virtual machine emulator focused on accurately simulating resource-constrained embedded environments, allowing firmware developers to test algorithms, timing constraints, interrupt handling, and power consumption patterns before deploying to actual hardware.

## Persona Description
Priya develops firmware for resource-constrained devices and uses a virtual machine to test algorithms before deploying to actual hardware. She needs an emulator that accurately represents the limitations of embedded environments.

## Key Requirements
1. **Resource Constraint Simulation**: Implement precise simulation of configurable memory limitations, processing power constraints, and peripheral availability. This feature is critical for Priya to understand how her algorithms will behave in the highly constrained environments of embedded systems, allowing her to identify memory leaks, stack overflows, and performance bottlenecks before deployment.

2. **Interrupt Handling Framework**: Create a comprehensive interrupt management system modeling hardware-triggered events, prioritization, and real-time responses. This capability is essential for developing reliable embedded firmware, as interrupts are fundamental to how embedded systems respond to external stimuli and timing events in real-world deployments.

3. **Real-time Operation Modeling**: Develop a timing simulation with strict requirements, deadlines, and periodicity guarantees common in embedded systems. This feature enables Priya to verify that her code meets critical timing constraints and can respond to events within specified deadlines—a fundamental requirement for many embedded applications like control systems and safety-critical devices.

4. **Power Consumption Estimation**: Implement a detailed power modeling system that estimates energy usage based on instruction patterns, sleep states, and peripheral activity. This capability allows Priya to optimize her firmware for battery-powered devices, identify power-hungry operations, and estimate battery life under various usage scenarios.

5. **Peripheral Device Simulation**: Create accurate simulations of common embedded peripherals including sensors, actuators, and communication interfaces with realistic timing and behavior characteristics. This feature enables comprehensive testing of device interaction code, protocol implementations, and error handling without requiring physical hardware for each development iteration.

## Technical Requirements
- **Testability Requirements**:
  - All simulated constraints must be configurable with precise values
  - Interrupt behavior must be deterministic and reproducible
  - Timing simulations must be accurate within microsecond resolution
  - Power estimations must be consistent and comparable across runs
  - Peripheral interactions must be recordable and replayable
  
- **Performance Expectations**:
  - Must be able to simulate execution faster than real-time when needed (up to 100x speedup)
  - Must support cycle-accurate execution for precise timing verification
  - Interrupt latency must be measurable with sub-microsecond precision
  - Power modeling overhead should not exceed 10% of execution time
  - Must handle at least 50 concurrent peripheral simulations without significant slowdown

- **Integration Points**:
  - Standard interface for loading compiled firmware binary images
  - API for custom peripheral device implementation
  - Export formats for timing traces, power profiles, and execution logs
  - Integration with standard embedded debugging protocols (SWD, JTAG simulation)
  - Support for common embedded C/C++ compilation toolchains

- **Key Constraints**:
  - Implementation must be in pure Python for portability and educational value
  - No dependencies beyond standard library to ensure easy deployment
  - All constraints must be configurable to match various target devices
  - Simulations must be deterministic to ensure reproducible testing
  - System must be able to run on standard development machines without special hardware

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this resource-constrained embedded systems emulator includes:

1. A virtual CPU with configurable characteristics (clock speed, word size, pipeline stages)

2. Precise memory models simulating different types (Flash, RAM, EEPROM) with appropriate constraints

3. A comprehensive interrupt controller with prioritization and nested handling

4. Real-time clock and timer peripherals with microsecond resolution

5. Power state management with deep sleep, idle, and active operating modes

6. Common communication interface simulations (UART, SPI, I2C, CAN)

7. Sensor input simulation with configurable noise, drift, and failure modes

8. Actuator output simulation with appropriate timing and physical constraints

9. Data collection systems for execution timing, power consumption, and peripheral activity

10. Resource utilization monitoring for stack, heap, and program memory

11. Simulation speed controls (real-time, accelerated, or cycle-accurate modes)

12. Event logging and tracing facilities for debugging and analysis

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Accurate enforcement of all resource constraints
  - Correct interrupt handling with proper prioritization
  - Precise timing of real-time operations
  - Reasonable power consumption estimation
  - Realistic peripheral device behavior
  - Proper operation under various memory constraints

- **Critical User Scenarios**:
  - Testing algorithms under extreme memory constraints
  - Verifying interrupt-driven code with multiple interrupt sources
  - Validating real-time code meeting strict deadlines
  - Optimizing firmware for power consumption
  - Debugging complex peripheral interactions
  - Simulating failure conditions and error handling

- **Performance Benchmarks**:
  - Simulation of 8-bit MCU at minimum 10MHz effective clock rate on average hardware
  - Interrupt latency measurement accurate to within 1 microsecond
  - Power estimation within 10% of actual hardware measurements for reference implementations
  - Support for programs using up to 1MB of program memory
  - Simulation of at least 10 concurrent active peripherals at real-time speed

- **Edge Cases and Error Conditions**:
  - Handling of stack overflows and memory corruption
  - Proper behavior during peripheral failure simulation
  - Accurate reporting of timing violations
  - Correct operation with extreme interrupt loads
  - Appropriate behavior at resource exhaustion boundaries

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for core simulation components
  - 100% coverage for interrupt handling logic
  - At least 95% branch coverage for power state transitions
  - Complete coverage of peripheral interface implementations
  - At least 85% coverage for timing-critical code paths

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
The implementation will be considered successful if it:

1. Accurately enforces configurable resource constraints matching real embedded systems

2. Provides a complete interrupt handling framework with proper prioritization and timing

3. Successfully models real-time operations with verifiable timing guarantees

4. Generates reasonable power consumption estimates that help optimize firmware

5. Includes realistic simulations of common embedded peripherals

6. Allows detection of common embedded development issues (stack overflow, timing violations)

7. Provides useful data for optimizing algorithms before hardware deployment

8. Enables faster development cycles by reducing hardware testing requirements

9. Supports reproduction of complex timing-dependent scenarios

10. Successfully passes all test cases demonstrating the required functionality

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
To set up the development environment:

1. Create a virtual environment using:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: For test execution and reporting:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion. This file must be included as proof that all tests pass successfully.