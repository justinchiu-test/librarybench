# Embedded Systems Virtual Machine Emulator

## Overview
A specialized virtual machine designed to simulate resource-constrained embedded environments, featuring configurable hardware limitations, interrupt handling, real-time operation modeling, power consumption estimation, and peripheral device simulation.

## Persona Description
Priya develops firmware for resource-constrained devices and uses a virtual machine to test algorithms before deploying to actual hardware. She needs an emulator that accurately represents the limitations of embedded environments.

## Key Requirements
1. **Resource constraint simulation with configurable memory and processing limitations**: Essential for Priya to test algorithms under realistic embedded system constraints, allowing her to validate that her code will function correctly within the tight memory and processing budgets of target hardware before physical deployment.

2. **Interrupt handling framework modeling hardware-triggered events**: Critical for developing and testing interrupt service routines that respond to external signals, sensors, or timers, enabling Priya to verify that her firmware correctly prioritizes and handles asynchronous events without the need for physical hardware.

3. **Real-time operation modeling with strict timing requirements**: Vital for ensuring that time-sensitive operations meet their deadlines in embedded applications, helping Priya validate that critical tasks complete within required timeframes and that the system responds to events with predictable latency.

4. **Power consumption estimation based on instruction execution patterns**: Important for optimizing battery life in portable devices, providing Priya with insights into how different algorithms and execution patterns affect energy usage so she can maximize efficiency before deploying to power-constrained hardware.

5. **Peripheral device simulation for sensors, actuators, and communication interfaces**: Necessary for testing complete embedded systems that interact with the physical world, allowing Priya to develop and validate device drivers and communication protocols for various peripherals without requiring actual hardware components.

## Technical Requirements
- **Testability Requirements**:
  - All simulated hardware constraints must be configurable and verifiable through tests
  - Interrupt handling must be deterministically testable with precise timing control
  - Real-time deadline enforcement must be measurable and verifiable
  - Power consumption estimates must be repeatable and comparable across implementations
  - Peripheral device behavior must be precisely controllable for testing scenarios

- **Performance Expectations**:
  - Simulation should run at least 10x faster than real-time when timing constraints are relaxed
  - Must support real-time execution mode with microsecond-level timing accuracy
  - Should handle at least 100 interrupt events per second
  - Power consumption calculations should add minimal overhead (less than 5%)
  - Should support at least 20 different peripheral device types simultaneously

- **Integration Points**:
  - Hardware configuration definition interface
  - Peripheral device simulation API
  - Interrupt injection framework
  - Power profiling data export
  - Integration with standard embedded protocols (I2C, SPI, UART, etc.)

- **Key Constraints**:
  - Must accurately represent timing constraints of embedded systems
  - Should reflect realistic power consumption patterns of different operations
  - Must provide deterministic execution for debugging purposes
  - Should model common embedded architectures accurately enough for valid testing

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Resource-Constrained Execution Environment**: Implement a virtual machine with configurable constraints on memory size, CPU speed, and other resources that accurately reflects limitations of embedded devices.

2. **Interrupt System**: Create a comprehensive interrupt handling framework supporting prioritization, nesting, and timing of hardware-triggered events with configurable interrupt controllers.

3. **Real-Time Scheduler**: Implement a real-time scheduling system with deadline tracking, execution time measurement, and validation of timing requirements for critical tasks.

4. **Power Profiling**: Develop an instruction-level power consumption model that estimates energy usage based on execution patterns, peripheral activity, and processor states.

5. **Peripheral Simulation**: Create a framework for simulating common embedded peripherals including sensors, communication interfaces, timers, and input/output devices with realistic behavior.

6. **Memory Hierarchy**: Implement a configurable memory system modeling different types of memory (flash, RAM, EEPROM) with appropriate access timing and limitations.

7. **Communication Protocol Support**: Provide implementations of standard embedded communication protocols (I2C, SPI, UART, CAN) with accurate timing and electrical characteristics.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct operation under various memory and processing constraints
  - Proper handling of interrupts with different priorities and timing
  - Accurate enforcement of real-time execution requirements
  - Reasonable power consumption estimates for different operations
  - Realistic behavior of simulated peripheral devices

- **Critical User Scenarios**:
  - Testing firmware with multiple concurrent interrupt sources
  - Validating algorithms under severe memory constraints
  - Measuring and optimizing code for power efficiency
  - Developing and testing device drivers for various peripherals
  - Verifying real-time response requirements for critical applications

- **Performance Benchmarks**:
  - Execute standard embedded benchmarks at least 10x faster than real-time
  - Support configurations with as little as 2KB of RAM and 16KB of program memory
  - Handle interrupt frequencies up to 10KHz with proper prioritization
  - Provide power consumption estimates with less than 10% error compared to reference values
  - Simulate at least 10 peripheral devices simultaneously with realistic timing

- **Edge Cases and Error Conditions**:
  - Handle stack overflows in constrained memory environments
  - Properly manage interrupt priority inversions and nested interrupts
  - Detect and report missed real-time deadlines with diagnostic information
  - Handle peripheral device failures and communication errors
  - Report resource exhaustion conditions with clear diagnostics

- **Required Test Coverage Metrics**:
  - 95% code coverage for the core VM implementation
  - 100% coverage for the interrupt handling system
  - 90% coverage for the real-time scheduling components
  - 90% coverage for power consumption estimation logic
  - 95% coverage for peripheral device simulation

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
1. Firmware developed and tested in the virtual machine functions correctly when deployed to actual hardware
2. Interrupt-driven code behaves identically in the simulation and on real devices
3. Real-time constraints verified in the simulation are met on the physical hardware
4. Power consumption optimizations identified in the simulator result in measurable battery life improvements
5. Device drivers developed against simulated peripherals work with actual hardware components
6. Development time is significantly reduced by enabling testing without physical hardware
7. Edge cases and error conditions can be reliably tested that would be difficult to reproduce on real hardware

To set up your environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.