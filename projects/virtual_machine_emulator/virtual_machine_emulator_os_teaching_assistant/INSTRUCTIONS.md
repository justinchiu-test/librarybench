# Operating Systems Concept Virtual Machine

## Overview
A specialized virtual machine implementation focused on demonstrating operating system concepts like process scheduling, memory management, system calls, and resource contention, designed specifically for classroom and laboratory teaching scenarios.

## Persona Description
Sophia conducts lab sessions for an operating systems course and needs to demonstrate concepts like process scheduling, memory allocation, and system calls. She wants a simplified environment that isolates these concepts from the complexity of real operating systems.

## Key Requirements
1. **Process and thread simulation with various scheduling algorithms (round-robin, priority-based)**: Essential for Sophia to demonstrate different scheduling strategies in action, allowing students to visualize how the CPU allocates time to different processes and understand the tradeoffs of different algorithms in terms of fairness, response time, and throughput.

2. **Memory management visualization showing segmentation, paging, and address translation**: Crucial for illustrating complex memory concepts that students often struggle with, providing clear visibility into how virtual addresses map to physical memory, how page tables work, and how segmentation and paging differ in their approaches to memory management.

3. **System call interface demonstrating the boundary between user code and kernel operations**: Key to teaching the fundamental concept of privilege separation in operating systems, allowing students to understand how applications request services from the kernel, how parameters are passed safely across privilege boundaries, and how the system maintains security and stability.

4. **Resource contention scenarios illustrating deadlocks and race conditions**: Vital for demonstrating these challenging concurrency concepts that are difficult to reproduce reliably in real systems, giving students the ability to observe, analyze, and resolve synchronization problems in a controlled environment.

5. **Virtual device drivers showing hardware abstraction and I/O operations**: Important for teaching how operating systems interact with hardware through abstraction layers, helping students understand device management, interrupt handling, buffering strategies, and the distinction between synchronous and asynchronous I/O.

## Technical Requirements
- **Testability Requirements**:
  - All scheduler implementations must be independently testable with deterministic workloads
  - Memory management operations must verify correct address translation and protection
  - System call mechanisms must be testable for correct privilege enforcement
  - Concurrency scenarios must reliably reproduce race conditions and deadlocks
  - I/O subsystems must be testable with simulated device behavior

- **Performance Expectations**:
  - Must support at least 20 simultaneous simulated processes
  - Context switching should occur at a visible but not distracting rate (approximately 10 per second) for demonstration purposes
  - Memory operations should execute quickly enough for interactive demonstration
  - Should operate with minimal resource usage on standard laptop hardware
  - Must provide the option to artificially slow execution for clearer demonstration

- **Integration Points**:
  - Process definition API for creating custom demonstration scenarios
  - Hooks for collecting and exporting execution statistics
  - Configuration interface for all scheduler parameters
  - Flexible memory configuration system
  - Virtual device specification interface

- **Key Constraints**:
  - Simulation must remain simple enough to be fully understandable by undergraduate students
  - Must prioritize clarity and educational value over realistic performance
  - All internal states must be observable and explainable
  - Should isolate individual OS concepts for focused learning

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Process Management System**: Implement a complete process lifecycle management system supporting creation, scheduling, execution, and termination of simulated processes, with support for multiple scheduling algorithms.

2. **Virtual Memory Manager**: Create a memory management subsystem with support for segmentation, paging, and address translation, tracking allocations, mapping virtual to physical addresses, and enforcing protection.

3. **System Call Interface**: Implement a privilege separation mechanism with defined system calls, parameter validation, and mode switching between user and kernel execution contexts.

4. **Concurrency Control**: Provide primitives for synchronization including mutexes, semaphores, and condition variables, with the ability to create and detect deadlock and race condition scenarios.

5. **I/O Subsystem**: Create a virtual device framework with device drivers, interrupt handling, and both synchronous and asynchronous I/O operations.

6. **Resource Monitoring**: Implement comprehensive tracking of all system resources including CPU utilization, memory usage, I/O operations, and waiting times to analyze system performance.

7. **State Visualization**: Provide mechanisms for extracting detailed system state information for all components at any point during execution for analysis and demonstration.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct implementation of all supported scheduling algorithms
  - Proper address translation and protection in the memory management system
  - Accurate privilege enforcement in the system call interface
  - Reliable reproduction of concurrency problems and their solutions
  - Correct handling of I/O operations across different device types

- **Critical User Scenarios**:
  - Demonstrating scheduling behavior with mixed workloads
  - Showing memory allocation and address translation in action
  - Illustrating safe system call handling and privilege separation
  - Creating and resolving deadlock scenarios
  - Demonstrating device driver operation and interrupt handling

- **Performance Benchmarks**:
  - Support at least 20 concurrent processes with interactive scheduling visualization
  - Complete 1000 context switches per second when not in slowed demonstration mode
  - Handle a virtual memory space of at least 1GB with page sizes from 4KB to 4MB
  - Process at least 500 system calls per second
  - Support at least 10 different virtual device types simultaneously

- **Edge Cases and Error Conditions**:
  - Handle process crashes without affecting the overall system
  - Proper detection and reporting of memory access violations
  - Appropriate handling of invalid system call parameters
  - Detection of deadlock conditions with clear reporting
  - Recovery from device errors and I/O failures

- **Required Test Coverage Metrics**:
  - 95% code coverage for the process scheduling subsystem
  - 95% coverage for the memory management implementation
  - 90% coverage for the system call interface
  - 90% coverage for the concurrency control mechanisms
  - 90% coverage for the I/O subsystem

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
1. Students can clearly observe the effects of different scheduling algorithms on process execution
2. Memory management visualization successfully demonstrates address translation and protection mechanisms
3. The system call interface clearly shows the transition between user and kernel modes
4. Deadlocks and race conditions can be reliably created and resolved in demonstration scenarios
5. I/O operations visibly demonstrate the interaction between software and simulated hardware
6. Lab exercises can be completed with students gaining measurable understanding of OS concepts
7. The system is performant enough to run interactive demonstrations on standard classroom hardware

To set up your environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.