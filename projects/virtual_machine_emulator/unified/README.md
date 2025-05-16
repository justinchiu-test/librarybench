# Unified Virtual Machine Emulator Libraries

## Overview
This is a unified implementation of virtual machine emulator functionality that brings together multiple specialized VM implementations into a cohesive library structure. The architecture has been refactored to provide a common core library while preserving the original package names and functionality for backward compatibility.

The library is designed to support both security-focused and parallel computing research use cases through a flexible, extensible architecture.

## Architecture

### Core Components
The library is structured with these main components:

- **`common/core`** - The shared core library with base components:
  - `instruction.py` - Instruction representation and types
  - `memory.py` - Memory system with segments and access controls
  - `processor.py` - Processor with registers and execution logic
  - `vm.py` - Virtual machine orchestration and thread management
  - `program.py` - Program representation and loading
  - `exceptions.py` - Common exception types

- **`common/extensions`** - Specialized extensions for specific domains:
  - `security/` - Security-focused extensions:
    - `attack_vectors.py` - Simulation of different attack techniques
    - `control_flow.py` - Control flow integrity monitoring
    - `forensic_logging.py` - Detailed security event logging
    - `memory_protection.py` - Memory protection mechanisms
    - `privilege.py` - Privilege level management
    - `secure_vm.py` - Security-focused VM extensions
    - `vulnerability_detection.py` - Detection of security vulnerabilities
  - `parallel/` - Parallel computing extensions:
    - `coherence.py` - Memory coherence protocols
    - `parallel_vm.py` - Parallel-focused VM extensions
    - `race_detection.py` - Race condition detection
    - `synchronization.py` - Synchronization primitives
    - `thread.py` - Thread management

- **`secure_vm`** - Security-focused VM implementation
  - Uses common core components and security extensions
  - Adds security-specific features like control flow integrity, forensics

- **`vm_emulator`** - Parallel computing VM implementation
  - Uses common core components and parallel extensions
  - Adds features for race detection, memory coherence, synchronization

### Design Principles

The architecture follows these key principles:

1. **Backward Compatibility**: Preserves original package names and APIs
2. **Core Abstraction**: Common, reusable functionality in the core library
3. **Extension Mechanism**: Domain-specific features through extensions
4. **Clear Separation**: Distinct concerns in separate modules
5. **Composition**: Building higher-level components through composition

### Class Hierarchy

```
BaseVirtualMachine (common.core.vm)
├── ParallelVirtualMachine (common.extensions.parallel.parallel_vm)
│   └── VirtualMachine (vm_emulator.core.vm)
└── SecureVirtualMachine (common.extensions.security.secure_vm)
    └── VirtualMachine (secure_vm.emulator)

BaseProcessor (common.core.processor)
├── Processor (vm_emulator.core.processor)
└── CPU (secure_vm.cpu)

MemorySystem (common.core.memory)
├── Memory (vm_emulator.core.memory)
└── Memory (secure_vm.memory)
```

## Extension System

The unified library provides two primary extension categories:

### Security Extensions

- **Memory Protection**: DEP, ASLR, stack canaries, shadow memory
- **Control Flow Integrity**: Shadow stack, control flow monitoring
- **Vulnerability Detection**: Buffer overflows, code injection, ROP chains
- **Forensic Logging**: Detailed event recording and analysis
- **Privilege Management**: Privilege levels, protected mode transitions

### Parallel Computing Extensions

- **Race Detection**: Data race identification and analysis
- **Memory Coherence**: Cache coherence protocols (MESI)
- **Synchronization Primitives**: Locks, barriers, atomic operations
- **Scheduling**: Thread scheduling and management
- **Execution Tracing**: Parallel execution tracing and visualization

## Test Status

The current test status shows:
- **Parallel Computing Tests**: 100% pass rate (all tests pass)
- **Security Tests**: 84% pass rate (18 out of 114 tests fail)

The parallel computing implementation has been successfully refactored, while the security implementation still has some issues to resolve, primarily related to memory segmentation and control flow integration.

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly or use the common components:

```python
# Option 1: Import from original packages (preserved for backward compatibility)
from secure_vm.emulator import VirtualMachine as SecureVM
from vm_emulator.core.vm import VirtualMachine as ParallelVM

# Option 2: Import from common package (for shared functionality)
from common.core.memory import MemorySystem
from common.core.processor import Processor
from common.core.vm import VirtualMachine as BaseVM

# Option 3: Import extensions directly
from common.extensions.security.forensic_logging import ForensicLogger
from common.extensions.security.control_flow import ControlFlowMonitor
from common.extensions.parallel.race_detection import RaceDetector
```

### Security-focused Usage Example

```python
from secure_vm.emulator import VirtualMachine
from common.extensions.security.memory_protection import MemoryProtection, MemoryProtectionLevel

# Create a VM with security features enabled
protection = MemoryProtection(
    level=MemoryProtectionLevel.MAXIMUM,
    dep_enabled=True,
    aslr_enabled=True,
    stack_canaries=True
)

vm = VirtualMachine(
    memory_size=65536,
    protection=protection,
    enable_forensics=True,
    detailed_logging=True
)

# Load a program
vm.load_program([0x01, 0x02, 0x03, ...])

# Execute the program and analyze security properties
result = vm.run()

# Get control flow visualization
control_flow = vm.get_control_flow_visualization()

# Get forensic logs
forensic_logs = vm.get_forensic_logs()
```

### Parallel Computing Usage Example

```python
from vm_emulator.core.vm import VirtualMachine

# Create a multi-core VM
vm = VirtualMachine(num_processors=4, memory_size=65536)

# Create multiple threads
thread1 = vm.create_thread(entry_point=0x1000)
thread2 = vm.create_thread(entry_point=0x2000)

# Run VM and detect race conditions
vm.run()

# Get race detection results
race_report = vm.get_race_report()
```

## Testing
Tests are preserved for each persona implementation:

```bash
cd tests
pytest
```

Run specific persona tests:

```bash
# Security researcher tests
pytest tests/security_researcher/

# Parallel computing researcher tests
pytest tests/parallel_researcher/
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Next Steps

Several issues remain to be addressed:

1. **Memory Segmentation Issues**: Fix segmentation faults in security tests
2. **Circular Dependencies**: Resolve circular imports between visualization.py and emulator.py
3. **Security Extensions Integration**: Complete integration of attack simulation with unified memory model
4. **Documentation Improvements**: Add comprehensive docstrings to all new classes and methods