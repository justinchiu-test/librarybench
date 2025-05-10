# OS Concepts Virtual Machine Emulator

## Overview
A specialized virtual machine emulator designed for teaching operating systems concepts, allowing teaching assistants to demonstrate fundamental OS mechanisms like process scheduling, memory management, and system calls in a simplified environment that isolates these concepts from the complexity of real operating systems.

## Persona Description
Sophia conducts lab sessions for an operating systems course and needs to demonstrate concepts like process scheduling, memory allocation, and system calls. She wants a simplified environment that isolates these concepts from the complexity of real operating systems.

## Key Requirements
1. **Process and Thread Simulation**: Implement a framework for creating and managing multiple virtual processes and threads with various scheduling algorithms (round-robin, priority-based, etc.). This is critical for Sophia to demonstrate how operating systems manage multiple concurrent execution contexts and allocate CPU time, allowing students to observe the differences between scheduling policies.

2. **Memory Management Visualization**: Create a system that demonstrates segmentation, paging, and address translation mechanisms through detailed data representations. This feature is essential for Sophia to show students how operating systems manage memory space, handle memory protection, and implement virtual memory concepts that bridge the gap between logical and physical address spaces.

3. **System Call Interface**: Develop an abstraction layer that clearly demonstrates the boundary between user code and kernel operations, with detailed tracking of transitions. This allows Sophia to illustrate how operating systems provide services to user applications while maintaining security and isolation, showcasing the fundamental mechanism that enables protected execution environments.

4. **Resource Contention Scenarios**: Design simulation capabilities for illustrating deadlocks, race conditions, and synchronization problems with step-by-step visualization. This feature helps Sophia demonstrate potentially complex concurrency issues in a controlled, reproducible environment, making these abstract concepts concrete and observable for students.

5. **Virtual Device Drivers**: Implement simulated hardware devices and corresponding driver interfaces to show hardware abstraction and I/O operations. This is crucial for Sophia to demonstrate how operating systems interact with hardware through abstraction layers, illustrating device management, I/O scheduling, and the principles of hardware independence in modern operating systems.

## Technical Requirements

### Testability Requirements
- All components must have well-defined interfaces that can be tested in isolation
- Execution states must be reproducible for deterministic testing
- Process scheduling and memory management algorithms must be independently testable
- System call mechanisms must be verifiable through clear entry/exit points
- Concurrency scenarios must be testable with controlled timing and interleaving

### Performance Expectations
- The emulator should support running at least 10 simultaneous processes without significant performance degradation
- Memory management operations should complete in near-constant time regardless of memory size
- Scheduling decisions should be made in O(log n) time where n is the number of processes
- Context switching overhead should be minimal to allow for responsive demonstrations
- System calls should complete within predictable time bounds for realistic simulation

### Integration Points
- Clean separation between user-level code and kernel-level operations
- Well-defined interfaces for process creation, scheduling, and management
- Standard API for memory allocation and deallocation operations
- Event-driven architecture for device operations and interrupts
- Hooks for monitoring and collecting metrics about system operation

### Key Constraints
- The implementation must maintain a clear separation between simulated user space and kernel space
- All operations must be observable and traceable for educational purposes
- The system must support pausing, resuming, and stepping through execution
- Memory and CPU resource utilization must be accurately tracked and reported
- The emulator must support configurable parameters for different teaching scenarios

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A process management system that creates, schedules, and manages multiple execution contexts
2. A thread management system that handles concurrent execution within processes
3. A memory management system that implements segmentation, paging, and virtual address translation
4. A system call interface that clearly separates user-level code from kernel operations
5. A scheduling system with multiple configurable algorithms (FCFS, round-robin, priority-based, etc.)
6. Synchronization primitives like mutexes, semaphores, and condition variables
7. Resource allocation tracking to detect and demonstrate deadlock situations
8. Virtual devices with corresponding driver interfaces for I/O operations
9. Interrupt handling mechanism for device and timer events
10. State monitoring and reporting tools that capture system operation details

The system should allow instructors and teaching assistants to create specific scenarios that demonstrate key OS concepts, run these scenarios with controllable execution parameters, and observe the resulting behavior in detail.

## Testing Requirements

### Key Functionalities to Verify
- Correct implementation of different scheduling algorithms
- Proper virtual memory translation and protection
- Accurate system call processing and privilege transitions
- Reliable detection of resource contention issues
- Proper operation of synchronization primitives
- Effective device driver abstraction and I/O handling
- Accurate process and thread state management

### Critical User Scenarios
- Creating and scheduling multiple processes with different priorities
- Demonstrating memory allocation, protection, and virtual address translation
- Showing system call execution with privilege transitions
- Creating and resolving deadlock situations
- Demonstrating race conditions and their resolution through synchronization
- Handling device I/O operations with interrupts
- Illustrating context switching between processes and threads

### Performance Benchmarks
- Support for at least 10 concurrent processes without significant slowdown
- Memory management operations completing in under 10ms regardless of memory size
- Scheduling decisions completing in under 5ms for up to 50 processes
- System call overhead remaining below 5ms per call
- Context switching completing in under 3ms per switch
- Resource contention detection completing in under 100ms for complex scenarios

### Edge Cases and Error Conditions
- Handling processes that attempt to access protected memory
- Proper management of orphaned processes and resources
- Graceful handling of insufficient memory conditions
- Detection and management of deadlocks
- Proper handling of priority inversion
- Recovery from device failures and timeout conditions
- Management of excessive context switching (thrashing)

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of scheduling algorithms
- 100% coverage of memory management operations
- 100% coverage of system call interfaces
- All synchronization primitives must have specific test cases
- All error handling paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. A teaching assistant can use it to demonstrate all fundamental OS concepts required in a typical undergraduate course
2. The system clearly visualizes the operation of at least three different scheduling algorithms
3. Memory management operations correctly demonstrate segmentation, paging, and address translation
4. The system call interface properly shows the transition between user and kernel modes
5. Resource contention scenarios reliably demonstrate deadlocks and race conditions
6. Virtual device operations accurately reflect real-world I/O patterns
7. All test cases pass with the specified coverage requirements
8. Documentation is comprehensive enough for teaching assistants to create custom demonstration scenarios

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