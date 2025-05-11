# OpenDistro - Efficient Peer-to-Peer Open Source Distribution

## Overview
OpenDistro is a specialized peer-to-peer file sharing library designed for distributing large open source software packages efficiently. It focuses on optimizing download speeds through swarm downloading, encouraging continued sharing with seeding incentives, ensuring software integrity, minimizing bandwidth with update diffing, and providing fallback options through mirror integration.

## Persona Description
Wei maintains alternative distribution channels for large open source software packages. He needs efficient ways to share these packages while reducing bandwidth costs and improving download speeds.

## Key Requirements

1. **Torrent-like Swarm Downloading**
   - Implement a system for optimizing transfer speeds by fetching pieces from multiple sources simultaneously
   - Critical for Wei to provide fast downloads of large software packages to many users
   - Must coordinate piece selection and bandwidth allocation across multiple peers
   - Should adapt to changing network conditions and peer availability

2. **Seeding Incentives**
   - Create mechanisms encouraging users to continue sharing after completing downloads
   - Essential for maintaining distribution capacity without centralized infrastructure
   - Must track and reward sharing contributions from peers
   - Should balance incentives to ensure equitable distribution of seeding responsibilities

3. **Integrity Verification**
   - Develop robust methods ensuring downloaded software matches original signatures
   - Vital for guaranteeing that software hasn't been tampered with during distribution
   - Must support multiple cryptographic verification methods (hashing, signing)
   - Should verify each piece during download rather than only at completion

4. **Update Diffing**
   - Implement a system for downloading only changed portions of software packages
   - Important for reducing bandwidth usage when distributing frequent updates
   - Must efficiently identify and transfer only the modified components
   - Should handle complex package structures with many files and dependencies

5. **Mirror Integration**
   - Create fallback mechanisms to traditional HTTP downloads when P2P is limited
   - Critical for ensuring availability even when P2P sharing is restricted or inefficient
   - Must seamlessly transition between P2P and HTTP sources
   - Should intelligently select the fastest available distribution method

## Technical Requirements

- **Testability Requirements**
  - All distribution mechanisms must be testable in simulated network environments
  - Performance metrics must be measurable and comparable across distribution methods
  - Integrity verification must be testable with deliberate corruption scenarios
  - Update diffing must be verifiable with diverse package update patterns

- **Performance Expectations**
  - Swarm downloading must achieve at least 5x the speed of single-peer downloads
  - Seeding ratios must balance fairly across active participants
  - Integrity verification must add negligible overhead to download process
  - Update diffing must reduce bandwidth usage by at least 80% for typical updates
  - Mirror fallback must activate within 5 seconds of P2P availability issues

- **Integration Points**
  - Standard software distribution formats (installers, packages, archives)
  - Common cryptographic verification techniques
  - Binary diffing and patching algorithms
  - HTTP client libraries for mirror integration

- **Key Constraints**
  - Implementation must be pure Python for maximum portability
  - System must work effectively without requiring special network configurations
  - All core functionality must operate without UI components
  - Distribution must be resilient against network interruptions and peer churn

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The OpenDistro implementation should provide these core functions:

1. **Efficient Software Distribution**
   - Multi-source swarm downloading
   - Piece selection and prioritization
   - Bandwidth optimization and allocation
   - Progress tracking and reporting

2. **Participation Incentive System**
   - Contribution tracking and metrics
   - Seeding rewards and recognition
   - Fair distribution of seeding load
   - Network health monitoring

3. **Software Verification**
   - Piece-level and package-level integrity checking
   - Support for multiple signature types
   - Validation against trusted sources
   - Corruption detection and recovery

4. **Efficient Update Distribution**
   - Binary diff generation and application
   - Partial package updating
   - Version management and tracking
   - Dependency-aware updating

5. **Hybrid Distribution**
   - Seamless mirror integration
   - Source selection and optimization
   - Automatic fallback mechanisms
   - Distribution method benchmarking

## Testing Requirements

- **Key Functionalities to Verify**
  - Swarm downloading correctly optimizes transfer speeds from multiple sources
  - Seeding incentives effectively encourage continued participation after download
  - Integrity verification successfully detects modified or corrupted software
  - Update diffing correctly identifies and transfers only changed portions
  - Mirror fallback seamlessly activates when P2P is limited

- **Critical User Scenarios**
  - Distributing a new major software release to thousands of users simultaneously
  - Maintaining distribution capacity through proper incentivization of seeders
  - Ensuring cryptographic integrity of security-critical software components
  - Efficiently distributing frequent updates to large software packages
  - Providing reliable downloads in environments with restricted P2P capabilities

- **Performance Benchmarks**
  - Swarm downloading must achieve at least a specified minimum speed improvement
  - Seeding ratios must maintain at least a specified minimum level across the network
  - Integrity verification must complete within a specified maximum time
  - Update diffing must achieve at least a specified minimum bandwidth reduction
  - Mirror fallback must activate within a specified maximum detection time

- **Edge Cases and Error Handling**
  - Correct operation with extremely popular packages (flash crowd scenario)
  - Resilience against malicious or corrupted peers
  - Recovery from interrupted transfers and verification failures
  - Handling of packages with complex dependency structures
  - Proper behavior when all mirrors are unavailable

- **Test Coverage Requirements**
  - All distribution mechanisms must have 100% test coverage
  - Performance-critical code paths must have comprehensive benchmarking
  - Security-related functions must be thoroughly tested against attack scenarios
  - Update diffing must be tested with diverse package evolution patterns

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

The implementation will be considered successful if:

1. It significantly improves download speeds through optimized multi-source transfers
2. It maintains a healthy distribution network through effective seeding incentives
3. It ensures software integrity through comprehensive verification
4. It reduces bandwidth usage for updates through efficient diffing
5. It provides reliable fallback options when P2P distribution is limited
6. All operations are robust against typical network issues and peer behavior
7. The system performs efficiently at scale with popular packages

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

1. Setup a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Install test dependencies with `uv pip install pytest pytest-json-report`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```