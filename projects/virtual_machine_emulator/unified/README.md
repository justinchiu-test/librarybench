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
  - `security/` - Security-focused extensions
  - `parallel/` - Parallel computing extensions

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
├── VirtualMachine (vm_emulator.core.vm)
│   └── [Parallel Features]
└── SecureVirtualMachine (common.extensions.security.secure_vm)
    └── [Security Features]

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
from common.extensions.security.forensic_logging import ForensicLog
from common.extensions.security.control_flow import ControlFlowMonitor
```

### Security-focused Usage Example

```python
from secure_vm.emulator import VirtualMachine

# Create a VM with security features enabled
vm = VirtualMachine(
    memory_size=65536,
    enable_dep=True,
    enable_aslr=True,
    enable_stack_canaries=True,
    enable_control_flow_integrity=True
)

# Load a program
vm.load_program([0x01, 0x02, 0x03, ...])

# Execute the program and analyze security properties
result = vm.run()

# Get security analysis
security_report = vm.get_security_report()
control_flow_analysis = vm.analyze_control_flow()
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