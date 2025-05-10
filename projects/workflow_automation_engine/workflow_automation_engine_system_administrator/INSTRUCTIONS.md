# Remote Systems Automation Engine

A specialized workflow automation engine for system administrators to manage servers across multiple data centers without requiring agent installation.

## Overview

This project implements a Python library for defining, executing, and monitoring server maintenance workflows across distributed environments. The system enables secure SSH-based execution, implements progressive rollout strategies, provides maintenance window scheduling, includes configuration verification, and optimizes parallel execution while respecting system constraints.

## Persona Description

Miguel manages hundreds of servers across multiple data centers and needs to automate routine maintenance, updates, and troubleshooting procedures. He requires reliable automation that can work with existing systems without installing agents.

## Key Requirements

1. **SSH-Based Execution**: Implement functionality to securely run commands on remote systems without additional agents.
   - Critical for Miguel because he cannot install additional software on many production systems due to security policies and change management restrictions.
   - System must use secure SSH connections with appropriate authentication methods and execute commands reliably across different operating systems and configurations.

2. **Progressive Execution**: Develop capabilities for applying changes to server groups in controlled waves.
   - Essential for Miguel to minimize risk when applying changes across large server fleets.
   - Should support defining server groups, execution ordering, verification steps between waves, and automatic rollback if issues are detected.

3. **Maintenance Window Scheduling**: Create coordination of tasks during approved change periods.
   - Vital for Miguel to comply with organization policies that restrict when changes can be made to production systems.
   - Must support defining different maintenance windows for different server groups and ensure tasks only execute during approved timeframes.

4. **Configuration Verification**: Implement comparison of system state before and after changes.
   - Necessary for Miguel to validate that changes were applied correctly and to detect any unexpected modifications.
   - Should capture relevant system state before changes, apply modifications, then verify the new state meets expectations.

5. **Parallel Execution Optimization**: Develop maximization of efficiency while respecting system constraints.
   - Critical for Miguel to complete maintenance tasks within limited maintenance windows while avoiding overloading systems or networks.
   - Must intelligently parallelize tasks across server groups while respecting defined concurrency limits and dependencies.

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest without requiring actual SSH connections
- Mock SSH servers must be available for testing command execution and error scenarios
- Test fixtures should provide sample server inventories and maintenance workflows
- Configuration verification logic must be testable with sample before/after states
- Parallelization strategies must be verifiable without actual distributed execution

### Performance Expectations
- Support for managing at least 1,000 servers across multiple data centers
- Ability to execute commands on 100+ servers simultaneously (when appropriate)
- Command execution overhead less than 100ms per server (excluding network latency)
- Complete verification and state comparison in under 5 seconds per server
- Workflow engine capable of processing 10,000+ tasks per maintenance window

### Integration Points
- SSH subsystem for remote command execution
- Server inventory and configuration management systems
- Monitoring systems for health checks and verification
- Change management and approval systems
- Notification systems for status updates and alerts

### Key Constraints
- No UI components - all functionality must be accessible via Python API
- No requirement for agent installation on managed systems
- Must handle unreliable network connections gracefully
- All credentials must be handled securely (no plaintext storage)
- System must maintain detailed audit logs of all executed commands

## Core Functionality

The system must provide a Python library that enables:

1. **Server Management Workflow Definition**: A programmatic interface for defining maintenance workflows with:
   - Server grouping and targeting strategies
   - Task dependencies and execution order
   - Progressive execution rules and verification steps
   - Maintenance window constraints
   - Rollback procedures and failure handling

2. **Secure Remote Execution**: A robust execution system that:
   - Establishes secure SSH connections using appropriate authentication
   - Executes commands reliably across different operating systems
   - Handles connection failures and retries appropriately
   - Captures and processes command output
   - Maintains security best practices for credential handling

3. **Progressive Deployment System**: A controlled execution mechanism that:
   - Applies changes to server groups in ordered waves
   - Performs verification between deployment waves
   - Implements automatic rollback on failure
   - Provides detailed status reporting
   - Adjusts execution based on verification results

4. **Maintenance Window Management**: A scheduling system that:
   - Defines and enforces maintenance window constraints
   - Schedules tasks to execute only during approved periods
   - Optimizes task ordering to fit within available windows
   - Handles tasks that exceed their allotted window
   - Provides window forecasting and capacity planning

5. **Configuration Verification**: A comprehensive verification system that:
   - Captures system state before changes
   - Defines expected post-change state
   - Compares actual vs. expected states after changes
   - Identifies configuration drift and unexpected changes
   - Generates detailed verification reports

6. **Parallel Execution Engine**: An intelligent parallelization system that:
   - Optimizes execution across server groups
   - Respects defined concurrency limits and system constraints
   - Balances speed vs. system load
   - Adapts to performance characteristics of different server groups
   - Provides real-time execution monitoring and throttling

## Testing Requirements

### Key Functionalities to Verify
- Secure and reliable execution of commands via SSH
- Proper implementation of progressive deployment strategies
- Accurate maintenance window enforcement
- Comprehensive configuration state verification
- Optimal parallelization while respecting constraints

### Critical User Scenarios
- OS patching across multiple data centers with progressive rollout
- Configuration standardization across heterogeneous server environments
- Emergency security update deployment within compliance constraints
- Complex multi-step maintenance procedure with verification
- Troubleshooting workflow with conditional execution paths

### Performance Benchmarks
- Connection establishment and command execution in under 500ms per server
- Support for parallel execution on at least 100 servers (when appropriate)
- Configuration verification in under 5 seconds per server
- Complete processing of 1,000 server batch in under 10 minutes
- Workflow compilation and validation in under 1 second

### Edge Cases and Error Conditions
- Handling of SSH connection failures and network interruptions
- Proper behavior when servers are unreachable or unresponsive
- Recovery from partial deployments and interrupted workflows
- Appropriate action when maintenance windows expire mid-execution
- Handling of unexpected system states during verification

### Required Test Coverage Metrics
- Minimum 90% line coverage for core workflow engine
- 100% coverage of SSH command execution paths
- 100% coverage of configuration verification logic
- All error handling and recovery paths must be tested
- Test parametrization for different server environments and failure scenarios

## Success Criteria

The implementation will be considered successful if it demonstrates:

1. The ability to securely execute commands across multiple server environments without agent installation
2. Reliable progressive execution with appropriate verification between waves
3. Strict adherence to defined maintenance windows across all operations
4. Accurate configuration verification that detects unexpected changes
5. Efficient parallel execution that maximizes throughput while respecting system constraints
6. All tests pass with the specified coverage metrics
7. Performance meets or exceeds the defined benchmarks

## Getting Started

To set up the development environment:

1. Initialize the project with `uv init --lib`
2. Install dependencies with `uv sync`
3. Run tests with `uv run pytest`
4. Run a single test with `uv run pytest path/to/test.py::test_function_name`
5. Format code with `uv run ruff format`
6. Lint code with `uv run ruff check .`
7. Type check with `uv run pyright`

To execute sample maintenance workflows during development:

```python
import sysflow

# Define server inventory
inventory = sysflow.Inventory()
inventory.add_group("web_servers", ["web01.example.com", "web02.example.com", "web03.example.com"])
inventory.add_group("db_servers", ["db01.example.com", "db02.example.com"])
inventory.add_group("cache_servers", ["cache01.example.com", "cache02.example.com"])

# Define authentication
auth = sysflow.SSHAuth.from_keyfile("/path/to/private_key")

# Define a maintenance workflow
workflow = sysflow.MaintenanceWorkflow("os_patching")

# Add tasks
workflow.add_task("backup", "tar -czf /backup/$(hostname)-$(date +%Y%m%d).tar.gz /etc", targets=["*"])
workflow.add_task("update_repos", "apt-get update", targets=["*"])
workflow.add_task("upgrade_packages", "apt-get -y upgrade", targets=["*"], depends_on=["update_repos"])
workflow.add_task("restart_services", "systemctl restart nginx", targets=["web_servers"], depends_on=["upgrade_packages"])
workflow.add_task("verify_web", "curl -s http://localhost/health | grep -q 'OK'", targets=["web_servers"], depends_on=["restart_services"])

# Configure progressive execution
workflow.set_progressive_execution({
    "groups": [
        ["web01.example.com"],  # Canary server
        ["web02.example.com", "web03.example.com"],  # Rest of web servers
        ["db_servers"],  # Database servers
        ["cache_servers"]  # Cache servers
    ],
    "verification_tasks": ["verify_web"],
    "auto_rollback": True
})

# Define configuration verification
workflow.add_verification("verify_package_versions", {
    "before_tasks": ["backup"],
    "after_tasks": ["upgrade_packages"],
    "commands": {
        "package_versions": "dpkg -l | grep -E 'openssl|bash|kernel'"
    },
    "comparisons": {
        "package_versions": {
            "type": "regex_match",
            "pattern": r"ii\s+openssl\s+(\S+)",
            "expected_change": "version_increase"
        }
    }
})

# Set maintenance window
workflow.set_maintenance_window({
    "web_servers": "Sunday 01:00-03:00",
    "db_servers": "Sunday 03:00-05:00",
    "cache_servers": "Sunday 01:00-05:00"
})

# Configure parallel execution
workflow.set_parallelization({
    "max_parallel_servers": 10,
    "max_parallel_per_group": 5,
    "delay_between_servers": "2s"
})

# Execute workflow
engine = sysflow.Engine(inventory, auth)
result = engine.execute(workflow)

# Inspect results
print(f"Overall status: {result.status}")
print(f"Servers updated: {len(result.successful_servers)}")
print(f"Servers failed: {len(result.failed_servers)}")
print(f"Verification results: {result.verification_results}")
```