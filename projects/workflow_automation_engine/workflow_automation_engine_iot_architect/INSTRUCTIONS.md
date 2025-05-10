# IoT Workflow Automation Engine

A specialized workflow automation engine for processing data from connected devices and orchestrating real-time responses with edge computing capabilities.

## Overview

This project implements a Python library for defining, executing, and monitoring IoT workflows that process high-volume device data, coordinate actions across connected systems, leverage edge computing, implement statistical processing, and maintain digital twin synchronization. The system is specifically designed for IoT solutions that require real-time event processing and device control.

## Persona Description

Raj designs systems that process data from thousands of connected devices and need to respond to events in real-time. He requires workflow automation that can handle high-volume event processing with conditional logic and device control.

## Key Requirements

1. **Event Stream Processing**: Implement functionality for handling high-volume device data with pattern recognition.
   - Critical for Raj because IoT solutions generate massive data streams that must be processed efficiently to extract actionable insights and trigger appropriate responses.
   - System should ingest, filter, aggregate, and analyze event streams in real-time with support for complex pattern detection across multiple devices and time windows.

2. **Device Command Orchestration**: Develop coordination of actions across multiple connected systems.
   - Essential for Raj to control and synchronize operations across heterogeneous device ecosystems based on processed events and business rules.
   - Must securely transmit commands to devices through various protocols, handle acknowledgments and retries, and manage command prioritization and sequencing.

3. **Edge Computing Integration**: Create functionality for executing portions of workflows on local gateways.
   - Vital for Raj to reduce latency, minimize bandwidth usage, and ensure operation during connectivity disruptions.
   - Should distribute workflow processing between cloud and edge devices based on resource availability, latency requirements, and data locality.

4. **Telemetry Aggregation**: Implement statistical processing across device groups.
   - Necessary for Raj to derive meaningful insights from distributed sensor networks and enable higher-level decision making.
   - Must collect, normalize, and apply statistical functions to telemetry data from multiple devices with support for various time windows and aggregation methods.

5. **Digital Twin Synchronization**: Develop maintenance of virtual representations of physical devices.
   - Critical for Raj to maintain accurate virtual models that reflect the current state of physical devices for monitoring, simulation, and predictive applications.
   - Should synchronize physical and virtual states bidirectionally with appropriate conflict resolution and historical state tracking.

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest without requiring actual IoT devices
- Mock device simulators must support high-volume data generation and command response
- Edge computing distribution must be testable in local development environments
- Statistical processing algorithms must produce deterministic results for verification
- Digital twin synchronization must be verifiable with known device state transitions

### Performance Expectations
- Support for processing at least 10,000 events per second from distributed devices
- Command orchestration with end-to-end latency under 200ms for critical operations
- Edge computing decision making in under 50ms for local processing cases
- Statistical aggregation across 1,000+ devices completed in under 5 seconds
- Digital twin state updates propagated in under 100ms

### Integration Points
- Device connectivity protocols (MQTT, CoAP, HTTP, etc.)
- Edge computing platforms and gateways
- Time-series databases and analytics engines
- Device management and provisioning systems
- Cloud computing services for scalable processing

### Key Constraints
- No UI components - all functionality must be accessible via Python API
- Must operate efficiently with limited computing resources on edge devices
- System should be resilient to intermittent connectivity
- Must handle secure credential management for device communication
- Should minimize bandwidth usage between edge and cloud components

## Core Functionality

The system must provide a Python library that enables:

1. **Event Stream Processing Engine**: A high-performance processing system that:
   - Ingests events from multiple device sources and protocols
   - Filters, transforms, and enriches event data
   - Detects complex patterns across event streams
   - Implements windowing, joining, and aggregation operations
   - Triggers actions based on detected patterns

2. **Command Orchestration System**: A robust control mechanism that:
   - Defines command sequences with dependencies and conditions
   - Translates high-level instructions to device-specific commands
   - Manages command delivery, acknowledgment, and retry logic
   - Implements priority-based scheduling and conflict resolution
   - Provides comprehensive command audit trails

3. **Edge Computing Framework**: A distributed execution system that:
   - Partitions workflows between cloud and edge components
   - Synchronizes workflow definitions and state across locations
   - Manages resource allocation for edge processing
   - Handles store-and-forward during connectivity disruptions
   - Provides consistent execution semantics across environments

4. **Telemetry Aggregation Engine**: A statistical processing system that:
   - Collects telemetry from device groups and normalizes formats
   - Applies various statistical functions (average, median, percentiles, etc.)
   - Implements time-based windows and aggregation periods
   - Detects anomalies and outliers in aggregated data
   - Provides derived metrics and calculated KPIs

5. **Digital Twin System**: A comprehensive virtualization framework that:
   - Maintains virtual device models with properties and behaviors
   - Synchronizes state between physical and virtual representations
   - Implements bidirectional state propagation with conflict resolution
   - Tracks historical state transitions and property values
   - Enables simulations and predictive operations

## Testing Requirements

### Key Functionalities to Verify
- Correct processing of high-volume event streams with pattern detection
- Proper command orchestration with sequencing and acknowledgments
- Effective distribution of workflow execution between cloud and edge
- Accurate statistical aggregation across device groups
- Reliable synchronization between physical devices and digital twins

### Critical User Scenarios
- Predictive maintenance workflow with real-time anomaly detection
- Coordinated equipment control across manufacturing production line
- Edge-based emergency response with limited connectivity
- Fleet-wide firmware updates with rolling deployment
- Environmental monitoring with statistical trend analysis

### Performance Benchmarks
- Event processing throughput of at least 10,000 events per second
- Command round-trip latency under 200ms for 99% of operations
- Edge computing decision latency under 50ms for local operations
- Statistical aggregation of 1,000 device readings in under 5 seconds
- Digital twin synchronization latency under 100ms for state updates

### Edge Cases and Error Conditions
- Handling of connectivity loss between cloud and edge components
- Recovery from partial command execution across device groups
- Proper behavior during edge device resource constraints
- Appropriate action when device states conflict with digital twins
- Graceful degradation during event processing overload

### Required Test Coverage Metrics
- Minimum 90% line coverage for core workflow engine
- 100% coverage of event processing pattern detection
- 100% coverage of command orchestration paths
- All statistical aggregation functions must be tested
- Complete verification of digital twin synchronization scenarios

## Success Criteria

The implementation will be considered successful if it demonstrates:

1. The ability to process high-volume device data streams with complex pattern recognition
2. Reliable orchestration of commands across heterogeneous device ecosystems
3. Effective distribution of workflow execution between cloud and edge environments
4. Accurate statistical processing of telemetry data across device groups
5. Consistent synchronization between physical devices and their digital twins
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

To execute sample IoT workflows during development:

```python
import iotflow

# Define device registry
devices = iotflow.DeviceRegistry()
devices.add_group("temperature_sensors", [f"temp-sensor-{i:03d}" for i in range(1, 101)])
devices.add_group("hvac_controllers", [f"hvac-ctrl-{i:03d}" for i in range(1, 21)])
devices.add_group("power_meters", [f"power-meter-{i:03d}" for i in range(1, 51)])

# Configure connectivity
connectivity = iotflow.ConnectivityManager()
connectivity.add_protocol("mqtt", {
    "broker": "mqtt.example.com",
    "port": 8883,
    "tls": True,
    "client_id": "iotflow-engine"
})
connectivity.add_protocol("http", {
    "base_url": "https://api.example.com/devices",
    "auth": iotflow.Auth.bearer_token("token")
})

# Define digital twin models
twin_manager = iotflow.TwinManager()
twin_manager.define_model("temperature_sensor", {
    "properties": {
        "temperature": {"type": "float", "unit": "celsius"},
        "humidity": {"type": "float", "unit": "percent"},
        "battery": {"type": "float", "unit": "percent"},
        "last_reading": {"type": "timestamp"}
    },
    "telemetry": ["temperature", "humidity", "battery"],
    "commands": ["calibrate", "set_reporting_interval"]
})
twin_manager.define_model("hvac_controller", {
    "properties": {
        "mode": {"type": "enum", "values": ["off", "cool", "heat", "auto"]},
        "setpoint": {"type": "float", "unit": "celsius"},
        "fan_speed": {"type": "enum", "values": ["low", "medium", "high", "auto"]},
        "power_state": {"type": "boolean"}
    },
    "telemetry": ["current_temperature", "current_humidity", "power_consumption"],
    "commands": ["set_mode", "set_temperature", "set_fan_speed", "power_toggle"]
})

# Define an event processing workflow
workflow = iotflow.IoTWorkflow("hvac_optimization")

# Add event stream processing
workflow.add_stream_processor("temperature_monitoring", {
    "sources": [{
        "group": "temperature_sensors",
        "topic": "telemetry/+/temperature",
        "mapping": {"device_id": "topic[1]", "temperature": "payload.value"}
    }],
    "window": {"type": "tumbling", "size": "5m"},
    "processing": [
        {"type": "filter", "expression": "temperature > 0 and temperature < 50"},
        {"type": "aggregate", "by": ["device_id"], "functions": [
            {"name": "avg_temp", "function": "avg", "field": "temperature"},
            {"name": "max_temp", "function": "max", "field": "temperature"},
            {"name": "min_temp", "function": "min", "field": "temperature"}
        ]}
    ],
    "patterns": [
        {
            "name": "temperature_anomaly",
            "condition": "max_temp - min_temp > 5 within 5m",
            "actions": ["log_anomaly", "update_twin"]
        },
        {
            "name": "high_temperature",
            "condition": "avg_temp > 30 for 3 consecutive windows",
            "actions": ["activate_cooling"]
        }
    ]
})

# Add command orchestration
workflow.add_command_sequence("activate_cooling", {
    "target": {"group": "hvac_controllers", "selection": "nearest", "parameters": {"to_device": "context.device_id"}},
    "steps": [
        {"command": "set_mode", "parameters": {"mode": "cool"}},
        {"command": "set_temperature", "parameters": {"temperature": 23.5}},
        {"command": "set_fan_speed", "parameters": {"speed": "auto"}}
    ],
    "error_handling": {"strategy": "retry", "max_attempts": 3, "backoff": "exponential"}
})

# Configure edge computing
workflow.set_edge_distribution({
    "temperature_monitoring": {
        "components": ["filter", "aggregate"],
        "edge_resources": {"min_memory_mb": 64, "min_cpu_ghz": 1.0},
        "optimization": "latency"
    },
    "activate_cooling": {
        "components": ["nearest_selection", "command_execution"],
        "edge_resources": {"min_memory_mb": 32, "min_cpu_ghz": 0.5},
        "optimization": "reliability"
    }
})

# Configure telemetry aggregation
workflow.add_telemetry_aggregation("energy_monitoring", {
    "sources": [{
        "group": "power_meters",
        "topic": "telemetry/+/power",
        "mapping": {"device_id": "topic[1]", "power": "payload.value"}
    }],
    "dimensions": ["building", "floor", "zone"],
    "metrics": [
        {"name": "total_power", "function": "sum", "field": "power"},
        {"name": "avg_power_per_device", "function": "avg", "field": "power"},
        {"name": "peak_power", "function": "max", "field": "power"}
    ],
    "windows": [
        {"name": "real_time", "duration": "1m"},
        {"name": "hourly", "duration": "1h"},
        {"name": "daily", "duration": "1d"}
    ]
})

# Configure digital twin synchronization
workflow.configure_twin_sync({
    "temperature_sensors": {
        "telemetry_mapping": {
            "temperature": "payload.temperature",
            "humidity": "payload.humidity",
            "battery": "payload.battery"
        },
        "update_frequency": "1m",
        "conflict_resolution": "latest_timestamp"
    },
    "hvac_controllers": {
        "command_acknowledgment": {
            "method": "reported_properties",
            "timeout": "30s",
            "retry_strategy": "exponential_backoff"
        },
        "state_consistency": {
            "validation": "command_vs_reported",
            "healing": "auto"
        }
    }
})

# Execute the workflow
engine = iotflow.Engine(devices, connectivity, twin_manager)
execution = engine.deploy(workflow)

# In a production scenario, the workflow would run continuously
# For testing, we can simulate some events
if execution.status == "deployed":
    simulator = iotflow.DeviceSimulator(devices)
    scenario = simulator.create_scenario("summer_afternoon")
    scenario.add_temperature_pattern({
        "group": "temperature_sensors",
        "base_value": 28.5,
        "random_variance": 1.5,
        "time_pattern": "sine_wave",
        "period": "24h",
        "amplitude": 5.0
    })
    simulator.run_scenario(scenario, duration="1h", accelerated=True)
    
    # Check results
    results = execution.get_metrics()
    print(f"Events processed: {results.events_processed}")
    print(f"Commands issued: {results.commands_issued}")
    print(f"Edge execution ratio: {results.edge_execution_ratio}")
    print(f"Anomalies detected: {len(results.detected_patterns['temperature_anomaly'])}")
    print(f"Average power consumption: {results.aggregations['energy_monitoring']['hourly']['avg_power_per_device']}")
    print(f"Digital twin sync accuracy: {results.twin_sync_accuracy}")
```