# Secure Systems Vulnerability Simulator

A specialized virtual machine emulator designed for security research and education, providing a controlled environment to safely demonstrate and analyze memory corruption, code injection, privilege escalation, and other low-level security vulnerabilities without real-world consequences.

## Features

- Configurable memory protection system with adjustable enforcement levels
- Safe environment for demonstrating buffer overflows, format string vulnerabilities, and other attacks
- Comprehensive permission and privilege level system
- Control flow integrity monitoring and visualization
- Detection mechanisms for virtualization or protection boundary breaches
- Support for ROP, JOP, and other advanced exploitation techniques
- Data execution prevention (DEP) and ASLR implementations
- Detailed forensic logging of system state

## Installation

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-json-report

# Run tests
pytest --json-report --json-report-file=pytest_results.json
```

## Usage

This package provides a programmable API for security research and education. It doesn't include a UI or command-line interface.

Example:

```python
from secure_vm.emulator import VirtualMachine
from secure_vm.memory import MemoryProtection
from secure_vm.attacks import BufferOverflow

# Create a VM with custom memory protection settings
vm = VirtualMachine(
    memory_size=4096,
    protection=MemoryProtection(
        dep_enabled=True,
        aslr_level="medium",
        stack_canaries=True
    )
)

# Load a vulnerable program
vm.load_program([...])

# Setup and execute a buffer overflow attack
attack = BufferOverflow(
    buffer_address=0x1000,
    overflow_size=128,
    payload=b"\x90" * 50 + shellcode
)

# Execute the attack and get the result
result = attack.execute(vm)
print(result.success)
print(result.execution_trace)
```