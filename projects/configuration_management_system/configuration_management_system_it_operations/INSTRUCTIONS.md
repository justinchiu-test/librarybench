# Geographic Configuration Management System

## Overview
A specialized configuration management system designed for global IT operations that need to manage configuration variations across geographic regions while maintaining corporate standards. This system provides regional configuration inheritance, scheduled configuration changes with timezone awareness, regulatory compliance mapping, deployment window automation, and infrastructure inventory integration.

## Persona Description
Diego oversees IT systems for a global corporation with location-specific requirements and varying compliance regulations. His primary goal is to manage configuration variations across geographic regions while maintaining a core set of corporate standards.

## Key Requirements
1. **Geographic Configuration Inheritance with Region-specific Overrides** - Implements a hierarchical configuration system with global defaults and progressively more specific regional overrides (continent, country, datacenter), allowing both standardization and regional adaptation. This is critical for Diego because his organization must maintain consistent core configurations while accommodating regional variations for performance optimization, legal compliance, and localization requirements.

2. **Scheduled Configuration Changes with Timezone Awareness** - Provides robust scheduling functionality for configuration changes that accounts for timezone differences, regional business hours, and local holidays, ensuring changes deploy at appropriate local times. This feature is essential because Diego's global infrastructure requires updates that must be timed according to regional business hours to minimize disruption, with proper handling of timezone complexities.

3. **Regulatory Compliance Mapping by Jurisdiction** - Maps configuration requirements to specific regulatory frameworks by jurisdiction, automatically applying the appropriate compliance rules based on geographic location. This addresses Diego's challenge of managing systems that must simultaneously comply with multiple regulatory regimes (GDPR in Europe, CCPA in California, LGPD in Brazil, etc.) without creating separate configuration silos for each region.

4. **Configuration Deployment Windows with Automated Scheduling** - Enforces configurable maintenance windows for each region with automated scheduling of configuration deployments to occur only during approved periods. This functionality is vital as Diego must ensure configuration changes adhere to strict change management policies that specify when changes can be made in each region, often with different rules for different system criticality levels.

5. **Infrastructure Inventory Integration Showing Configuration Status per Device** - Integrates with infrastructure inventory systems to maintain an accurate mapping between configurations and the physical/virtual assets they apply to, with real-time status reporting. This gives Diego the visibility needed to manage configurations across thousands of devices globally, quickly identifying which systems have outdated configurations or failed deployments.

## Technical Requirements
- **Testability Requirements**: Regional inheritance logic must be fully testable with mocked geographic data. Timezone and scheduling functionality must be testable with simulated time. Compliance mapping must be verifiable without requiring actual compliance databases.

- **Performance Expectations**: Configuration resolution with regional inheritance must complete within 200ms even for complex hierarchies. Scheduled operations must handle at least 10,000 devices across 24 timezones without scheduling conflicts or resource contention.

- **Integration Points**:
  - Must integrate with common CMDB and asset management systems
  - Must support standard calendar and scheduling protocols
  - Must provide adapters for compliance databases
  - Must integrate with change management and ticketing systems

- **Key Constraints**:
  - Must support disconnected operation for remote sites
  - Must handle high-latency connections between regions
  - Must accommodate emergency changes outside normal windows
  - Must operate correctly across international date line

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality required for this globally-distributed configuration management system includes:

1. **Geographic Hierarchy Model**:
   - Global-to-local configuration inheritance
   - Region-specific override resolution
   - Location-based configuration retrieval
   - Inheritance path visualization

2. **Timezone-aware Scheduling Engine**:
   - International time handling with DST support
   - Business hours definition by region
   - Holiday calendar integration
   - Local time translation and normalization

3. **Regulatory Compliance Framework**:
   - Jurisdiction-to-regulation mapping
   - Configuration rule definition by regulation
   - Compliance validation by location
   - Cross-jurisdiction conflict resolution

4. **Deployment Window Management**:
   - Maintenance window definition and enforcement
   - Change freeze calendar support
   - Automated deployment scheduling
   - Emergency override protocols

5. **Infrastructure Inventory System**:
   - Configuration-to-asset mapping
   - Deployment status tracking
   - Configuration version monitoring
   - Asset group and collection management

6. **Global Distribution Mechanism**:
   - Efficient configuration distribution
   - Bandwidth-aware synchronization
   - Delta-based updates
   - Conflict detection and resolution

## Testing Requirements
The implementation must include comprehensive pytest tests that validate all aspects of the system:

- **Key Functionalities to Verify**:
  - Correct resolution of configurations through geographic inheritance
  - Proper scheduling of changes across multiple timezones
  - Accurate application of regulatory requirements by jurisdiction
  - Correct enforcement of deployment windows
  - Accurate tracking of configuration status across infrastructure

- **Critical User Scenarios**:
  - Deploying a global configuration change with regional variations
  - Scheduling configuration updates across multiple timezones
  - Ensuring configurations meet all applicable regulations
  - Managing changes within approved maintenance windows
  - Identifying systems with outdated or non-compliant configurations

- **Performance Benchmarks**:
  - Configuration resolution must handle 10,000 regional variations within 5 seconds
  - Scheduling engine must process 1,000 scheduled changes per minute
  - Compliance validation must complete for 500 rule checks within 3 seconds
  - Window management must handle 100 concurrent window evaluations
  - Inventory integration must process 1,000 status updates per second

- **Edge Cases and Error Conditions**:
  - Handling conflicting regional overrides
  - Managing changes across international date line
  - Resolving conflicting regulatory requirements
  - Processing changes during timezone transitions (DST)
  - Recovering from interrupted global deployments

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all modules
  - 100% coverage of geographic resolution logic
  - All timezone handling code must have DST transition tests
  - All compliance rules must have validation tests
  - All error recovery paths must be tested

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
The implementation will be considered successful when:

1. Geographic configuration inheritance correctly applies regional overrides while maintaining global standards.
2. Scheduled configuration changes account for timezone differences and regional business hours.
3. Regulatory compliance mapping correctly applies requirements by jurisdiction.
4. Configuration deployment windows are properly enforced with automated scheduling.
5. Infrastructure inventory integration accurately shows configuration status across all devices.
6. All specified performance benchmarks are met consistently.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
To set up the development environment:

1. Navigate to the project directory
2. Create a virtual environment using `uv venv`
3. Activate the environment with `source .venv/bin/activate`
4. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

The pytest_results.json file must be submitted as evidence that all tests pass successfully.