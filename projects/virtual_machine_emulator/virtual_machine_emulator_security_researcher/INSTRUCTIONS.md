# Security-Focused Virtual Machine Emulator

## Overview
A specialized virtual machine emulator designed for security researchers to safely study low-level vulnerabilities, exploitation techniques, and protection mechanisms. The emulator provides a controlled environment to demonstrate memory corruption, code injection, and other attack vectors without real-world consequences.

## Persona Description
Dr. Chen studies low-level security vulnerabilities and exploitation techniques. He needs a controlled environment to demonstrate memory corruption, code injection, and other attack vectors without real-world consequences.

## Key Requirements
1. **Memory Protection Simulation**: Implement a configurable memory protection system that can be enabled, disabled, or selectively bypassed. This is essential for Dr. Chen to demonstrate how different protection mechanisms work, how they can be circumvented, and how vulnerability mitigations like address space layout randomization (ASLR), stack canaries, and non-executable memory protect against various attack vectors.

2. **Exploitation Playground**: Design a safe environment for demonstrating buffer overflows, code injection, return-oriented programming, and other exploitation techniques. This feature is critical for Dr. Chen to create practical demonstrations of security concepts, allowing him to show the mechanics of exploitation techniques in a controlled setting where the consequences are contained and observable.

3. **Permission and Privilege Level Modeling**: Develop a comprehensive permission system that models different access levels and privilege transitions. This allows Dr. Chen to illustrate how privilege escalation attacks work, how permission boundaries should be enforced, and how privilege separation acts as a security mechanism, making abstract security concepts concrete through practical demonstration.

4. **Control Flow Integrity Visualization**: Create tools for visualizing normal and compromised execution paths through code, highlighting control flow hijacking. This feature is vital for Dr. Chen to demonstrate how attacks alter program execution and how control flow integrity protections can detect and prevent such attacks, providing clear visual evidence of both attack mechanics and protection effectiveness.

5. **Isolation Breach Detection**: Implement mechanisms that identify when virtualization boundaries are compromised, detecting attempts to escape the virtual environment. This capability is crucial for Dr. Chen to show advanced attack techniques that target the isolation mechanisms themselves, while also demonstrating the importance of containment and the principles of defense in depth in security design.

## Technical Requirements

### Testability Requirements
- All security mechanisms must be independently configurable for testing different scenarios
- Exploitation attempts must be reproducible for reliable testing
- Memory corruption events must be detectable and quantifiable
- Control flow changes must be trackable and verifiable
- Security violation events must generate detailed logs for analysis

### Performance Expectations
- The emulator should execute code at a rate sufficient for interactive demonstrations
- Memory corruption detection should have minimal performance impact when enabled
- Logging and monitoring should not significantly impact execution speed
- State snapshots should be creatable and restorable quickly for comparison testing
- The system should handle programs with at least 10MB of memory space

### Integration Points
- Well-defined interfaces for creating and loading potentially malicious code
- Hooks for monitoring memory access and modifications
- Event system for tracking security violations and exploitation attempts
- Export mechanisms for execution traces and memory dumps
- Interfaces for implementing custom protection mechanisms

### Key Constraints
- The emulator must maintain strict isolation from the host system
- All potentially dangerous operations must be contained within the virtual environment
- The implementation must support detailed tracing without sacrificing usability
- Memory state must be inspectable at any point during execution
- The system must be usable for educational demonstrations of security concepts

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A stack-based virtual machine with detailed memory access controls
2. A memory management system with configurable protection mechanisms
3. An execution engine that supports precise tracking of control flow
4. Permission and privilege level management with transition validation
5. Monitoring systems for detecting memory corruption and control flow hijacking
6. Tools for creating and executing demonstration exploits safely
7. Logging and analysis capabilities for security events
8. Snapshot and comparison tools for before/after exploit analysis
9. Configurable security mechanism enablement and bypass
10. Isolation verification and breach detection

The system should allow security researchers to create demonstration scenarios that illustrate various attack vectors and protection mechanisms, execute these scenarios in a controlled environment, and collect detailed information about the results for analysis and educational purposes.

## Testing Requirements

### Key Functionalities to Verify
- Correct implementation of memory protection mechanisms
- Accurate detection of buffer overflows and memory corruption
- Proper enforcement of permission and privilege boundaries
- Reliable tracking of control flow integrity
- Effective containment of exploitation attempts
- Accurate logging of security violations
- Proper isolation between the virtual environment and host system

### Critical User Scenarios
- Demonstrating a buffer overflow attack and its detection
- Showing code injection and execution prevention
- Illustrating privilege escalation attempts and their prevention
- Demonstrating return-oriented programming attacks
- Creating and detecting control flow hijacking
- Testing different memory protection configurations
- Comparing execution with and without security features enabled

### Performance Benchmarks
- Execution speed sufficient for interactive demonstrations (>1000 instructions per second)
- Memory protection checks adding less than 20% overhead
- Control flow integrity verification adding less than 15% overhead
- Security logging adding less than 10% overhead
- System capable of handling programs with at least 10MB of memory
- State snapshots createable in under 1 second for typical program states

### Edge Cases and Error Conditions
- Handling of attempts to access memory outside allocated regions
- Proper management of stack overflows and underflows
- Detection of attempts to execute data as code when prohibited
- Identification of attempts to modify protected memory regions
- Management of privilege escalation attempts
- Detection of control flow integrity violations
- Handling of attempts to bypass security mechanisms

### Required Test Coverage Metrics
- Minimum 95% line coverage across all security-related modules
- 100% coverage of memory protection mechanisms
- 100% coverage of privilege enforcement code
- All attack detection mechanisms must have specific test cases
- All protection bypass scenarios must be tested
- All error handling paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. A security researcher can use it to safely demonstrate at least five common exploitation techniques
2. The system correctly detects and logs all attempted memory protection violations
3. Control flow integrity visualization clearly shows the difference between normal and compromised execution
4. Permission and privilege level enforcement correctly prevents unauthorized operations
5. Isolation breach attempts are reliably detected and contained
6. The emulator provides sufficient detail for educational analysis of security vulnerabilities
7. All test cases pass with the specified coverage requirements
8. Documentation clearly explains the security mechanisms and how to use them for demonstrations

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