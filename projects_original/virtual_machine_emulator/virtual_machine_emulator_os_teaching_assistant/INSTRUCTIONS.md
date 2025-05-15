# Operating Systems Concept Simulator

## Overview
A specialized virtual machine emulator designed to demonstrate fundamental operating system concepts like process scheduling, memory allocation, system calls, and resource management. This simulator provides a simplified, controllable environment for teaching operating systems principles without the complexity of real-world OS code.

## Persona Description
Sophia conducts lab sessions for an operating systems course and needs to demonstrate concepts like process scheduling, memory allocation, and system calls. She wants a simplified environment that isolates these concepts from the complexity of real operating systems.

## Key Requirements
1. **Process and Thread Simulation**: Implement a comprehensive process and thread management system with various scheduling algorithms (round-robin, priority-based, shortest-job-first). This feature is critical for teaching students how operating systems manage multiple concurrent tasks, handle context switching, and make scheduling decisions that impact system performance and fairness.

2. **Memory Management Visualization**: Create a detailed virtual memory system showing segmentation, paging, and address translation mechanisms, with insights into allocation policies. This capability is essential for helping students understand the complex relationship between logical addresses used by programs and physical memory resources, while visualizing concepts like fragmentation and page replacement strategies.

3. **System Call Interface**: Develop a clear system call boundary demonstrating the transition between user code and kernel operations, with proper privilege separation. This feature allows students to understand the fundamental isolation mechanism in operating systems that protects kernel resources while providing services to user applications, illustrating a key OS architectural principle.

4. **Resource Contention Scenarios**: Implement reproducible demonstrations of deadlocks, race conditions, and synchronization primitives in multi-process environments. These scenarios help students recognize common concurrency problems and learn how to apply appropriate synchronization techniques to solve them, a crucial skill for systems programming.

5. **Virtual Device Drivers**: Create simulated hardware abstractions showing device driver operations and I/O processing. This feature demonstrates how operating systems manage and abstract hardware devices, helping students understand the layered architecture of system software and how user applications interact with physical hardware through multiple abstraction layers.

## Technical Requirements
- **Testability Requirements**:
  - All components must have deterministic execution for repeatable testing
  - Scheduling algorithms must produce consistent, predictable process execution order
  - Memory management operations must be traceable and verifiable
  - System call behavior must be testable with mock processes
  - Resource contention scenarios must reliably reproduce specific conditions
  
- **Performance Expectations**:
  - Must support simulation of at least 50 concurrent processes for scheduling demonstrations
  - Context switching should complete in under 10ms per switch
  - Memory operations should process at least 1000 address translations per second
  - System call overhead should be minimal and consistent
  - Complete scenarios should execute within a reasonable timeframe for lab sessions (1-5 minutes)

- **Integration Points**:
  - Modular architecture allowing individual components to be tested in isolation
  - Clean separation between user space and kernel space operations
  - Standardized interfaces between system components (scheduler, memory manager, device drivers)
  - Observable internal state for all subsystems
  - Export mechanism for execution traces and visualizations

- **Key Constraints**:
  - Implementation must be in pure Python for educational clarity
  - No dependencies beyond standard library to ensure portability
  - System must be deterministic to ensure reproducible demonstrations
  - All components must be well-documented with educational explanations
  - Memory footprint must remain reasonable (< 512MB) for student machines

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this operating systems concept simulator includes:

1. A virtual CPU with registers, instruction execution, and privilege levels

2. A process management system with creation, termination, and state transitions

3. Multiple scheduling algorithms with configurable parameters

4. A virtual memory system with address translation and page management

5. A comprehensive system call interface with proper privilege transitions

6. Synchronization primitives (mutexes, semaphores, condition variables)

7. Simulated device drivers for basic I/O operations

8. Resource allocation and deadlock management systems

9. Detailed execution tracing for analyzing system behavior

10. Configurable system parameters for demonstrating performance trade-offs

11. Scenario presets for common teaching examples (producer-consumer, dining philosophers)

12. State visualization exporters for all major subsystems

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Correct implementation of all scheduling algorithms
  - Proper process lifecycle management (creation, execution, termination)
  - Accurate virtual memory translation and management
  - Correct system call handling with privilege separation
  - Proper implementation of synchronization primitives
  - Accurate detection and handling of deadlock conditions
  - Proper operation of device driver abstractions

- **Critical User Scenarios**:
  - Demonstrating scheduling algorithms with variable process loads
  - Showing memory allocation and fragmentation with different strategies
  - Illustrating system call processing and protection boundaries
  - Reproducing classic concurrency problems and solutions
  - Demonstrating I/O operations through device driver abstractions
  - Creating and resolving deadlock situations

- **Performance Benchmarks**:
  - Support for at least 50 concurrent processes with responsive scheduling
  - Memory management handling at least 10,000 pages with translation
  - System call processing with overhead under 5ms per call
  - Complete scenario execution for typical lab demonstrations under 5 minutes
  - Resource contention scenarios that clearly demonstrate timing-dependent issues

- **Edge Cases and Error Conditions**:
  - Handling of resource exhaustion (memory, process table, etc.)
  - Proper detection and reporting of illegal operations
  - Correct behavior with extreme scheduling conditions
  - Recovery from deadlock situations
  - Handling of invalid memory accesses and protection violations

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all components
  - 100% coverage for scheduling algorithms
  - At least 95% branch coverage for critical synchronization code
  - Complete coverage of system call interfaces
  - At least 85% coverage for memory management operations

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

1. Correctly implements multiple scheduling algorithms with observable differences in behavior

2. Provides a clear visualization of memory management operations including segmentation and paging

3. Implements a proper system call interface with privilege separation

4. Successfully demonstrates classic resource contention scenarios with appropriate solutions

5. Includes functional virtual device drivers that show hardware abstraction principles

6. Produces consistent, deterministic results for repeatable demonstrations

7. Supports creation of educational scenarios that clearly illustrate OS concepts

8. Provides detailed execution traces for analysis and understanding

9. Maintains clear separation of concerns between different OS components

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