# Autonomous Vehicle Sensor Data Processing Framework

## Overview
A specialized data stream processing framework designed to ingest, synchronize, and analyze multi-modal sensor data from autonomous vehicles. The system provides high-precision time synchronization, advanced scene understanding, and reliable event detection to support autonomous driving algorithm development and safety validation.

## Persona Description
Liu processes sensor data streams from test vehicles to improve autonomous driving algorithms and ensure safety. His primary goal is to synchronize and correlate multi-modal sensor data (video, lidar, radar) while identifying environmental edge cases that require algorithm refinement.

## Key Requirements
1. **Time-synchronized sensor fusion with clock drift compensation**: Implement a precision timing system that can align data from multiple sensors (cameras, lidar, radar, ultrasonic, GPS) with nanosecond accuracy, while compensating for clock drift and variable latency across devices. This synchronization is fundamental for creating a coherent environmental model and ensuring correct fusion of data from sensors operating at different frequencies and precisions.

2. **Scene segmentation and classification for environment modeling**: Create pipelines to process raw sensor data into structured scene representations by segmenting and classifying environmental elements (vehicles, pedestrians, signs, lanes, obstacles). This structured representation enables algorithm evaluation against ground truth and helps identify challenging scenarios where perception systems struggle.

3. **Driving event detection with categorical tagging**: Develop an event detection framework that automatically identifies and categorizes significant driving events (near-misses, unusual road user behavior, unexpected obstacles, edge case weather conditions) with precise tagging for subsequent analysis. This capability is critical for building comprehensive testing datasets that include rare but safety-critical scenarios.

4. **Hardware-accelerated processing for computer vision workloads**: Design optimized processing pathways that leverage GPU acceleration for compute-intensive computer vision tasks, balancing processing speed with accuracy requirements. This acceleration enables real-time analysis of high-resolution video streams from multiple cameras, which is necessary for timely detection of safety-critical situations.

5. **Scenario extraction for simulation and regression testing**: Implement mechanisms to automatically extract complete sensor data sequences surrounding detected events, packaging them with environmental context for use in simulation environments and regression testing. This targeted scenario extraction creates a growing library of challenging situations that can be used to validate algorithm improvements against historical edge cases.

## Technical Requirements
- **Testability Requirements**:
  - Must support validation with ground truth labeled datasets
  - Needs reproducible processing with deterministic outputs
  - Requires component-level testing of individual algorithms
  - Must support comparison of processing results across algorithm versions
  - Needs automated validation of scenario extraction completeness

- **Performance Expectations**:
  - Processing of data from at least 10 cameras, 4 lidars, and 8 radars simultaneously
  - Maximum end-to-end processing latency of 100ms for real-time critical paths
  - Support for sensor data rates up to 60Hz for cameras and 20Hz for lidar
  - Storage efficiency achieving at least 5:1 compression for raw sensor data
  - Scene segmentation accuracy above 95% compared to human-labeled ground truth

- **Integration Points**:
  - Raw sensor data capture systems
  - Vehicle telemetry and CAN bus data streams
  - Annotation and ground truth labeling systems
  - Simulation environments for scenario replay
  - Algorithm development and testing frameworks
  - Map and geospatial reference data

- **Key Constraints**:
  - Must handle extremely high data volumes (terabytes per vehicle per day)
  - Processing must prioritize accuracy over speed for safety-critical features
  - System must be robust to sensor calibration variations
  - Implementation must maintain data provenance for regulatory compliance
  - Storage solution must balance accessibility with cost constraints

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide a framework for autonomous vehicle data processing that:

1. Ingests raw sensor data from multiple modalities with precise timestamping
2. Synchronizes multi-sensor data to create coherent temporal views
3. Processes raw data into structured representations through:
   - Camera image processing and computer vision analysis
   - Lidar point cloud processing and object detection
   - Radar target tracking and classification
   - Sensor fusion to create unified environmental models
4. Detects and classifies driving events and scenarios
5. Extracts and packages complete scenarios for simulation
6. Manages efficient storage and retrieval of massive sensor datasets
7. Provides interfaces for algorithm evaluation and comparison
8. Implements acceleration for compute-intensive processing operations
9. Maintains comprehensive metadata about scenarios and events

The implementation should emphasize temporal precision, processing accuracy, and the ability to efficiently handle the massive data volumes generated by autonomous vehicle sensors.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Accuracy of time synchronization across sensor types
  - Precision of scene segmentation and classification
  - Reliability of driving event detection
  - Performance of hardware-accelerated processing
  - Completeness of scenario extraction for simulation

- **Critical User Scenarios**:
  - Processing complex urban driving scenarios with multiple road users
  - Handling adverse weather conditions affecting sensor data quality
  - Detection of unusual edge cases requiring algorithm refinement
  - Temporal alignment of sensor data during high-speed maneuvers
  - Extraction of near-miss scenarios for safety analysis

- **Performance Benchmarks**:
  - Synchronization accuracy within 1ms across all sensors
  - Scene segmentation with >95% mean Intersection over Union (IoU)
  - Event detection with >90% recall of safety-critical scenarios
  - Processing throughput supporting data from at least 4 vehicles simultaneously
  - Scenario extraction with 100% inclusion of relevant sensor data

- **Edge Cases and Error Conditions**:
  - Handling of sensor failures or intermittent data loss
  - Processing of data with extreme weather or lighting conditions
  - Behavior with partially obscured sensors (dirt, precipitation)
  - Recovery from processing component failures
  - Management of corrupted or invalid sensor data

- **Required Test Coverage Metrics**:
  - 100% coverage of synchronization and fusion algorithms
  - >90% line coverage for all production code
  - 100% validation against labeled ground truth datasets
  - Comprehensive tests across diverse driving scenarios
  - Performance verification with full-scale sensor data volumes

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
A successful implementation will demonstrate:

1. Precise synchronization of multi-modal sensor data with drift compensation
2. Accurate segmentation and classification of environmental elements
3. Reliable detection and categorization of significant driving events
4. Efficient hardware-accelerated processing of computer vision workloads
5. Complete scenario extraction for simulation and regression testing
6. Scalability to handle massive autonomous vehicle data volumes
7. Comprehensive test coverage with all tests passing

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

To setup the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```