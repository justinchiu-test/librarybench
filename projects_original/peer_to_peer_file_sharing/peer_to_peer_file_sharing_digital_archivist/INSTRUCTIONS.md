# DistriArchive - Distributed Digital Preservation Network

## Overview
DistriArchive is a specialized peer-to-peer file sharing library designed for digital preservation, focusing on creating redundant, resilient storage across multiple independent locations. It ensures long-term preservation through geographic distribution, rigorous integrity checking, comprehensive metadata management, and preservation-specific data formats.

## Persona Description
Dr. Patel preserves digital cultural heritage by creating distributed archives of important materials. She needs redundant, resilient storage across multiple independent locations to ensure long-term preservation.

## Key Requirements

1. **Replication Management**
   - Implement a system to track, manage, and ensure sufficient copies of archived materials exist across the network
   - Critical for Dr. Patel to maintain preservation redundancy standards for cultural heritage materials
   - Must support configurable replication policies based on material importance, size, and preservation requirements
   - Should include automated replication repair when copies fall below minimum thresholds

2. **Geographic Diversity Optimization**
   - Create algorithms to distribute data across different physical locations for disaster resilience
   - Essential for protecting against regional disasters, political instability, or infrastructure failures
   - Must incorporate location metadata and network latency to infer geographic distribution
   - Should optimize for maximum physical separation of critical materials

3. **Integrity Checking with Scheduled Verification**
   - Develop a comprehensive system for periodic verification of stored artifacts against checksums
   - Vital for ensuring bit-level preservation over long time periods
   - Must support multiple hash algorithms for future-proofing (SHA-256, SHA-3, etc.)
   - Should include scheduled verification and automatic reporting of corruption

4. **Catalog Synchronization**
   - Implement mechanisms to maintain consistent metadata across all archive nodes
   - Necessary for coordinated preservation efforts and resource discovery
   - Must handle schema evolution as metadata standards change over time
   - Should resolve conflicts when different nodes update metadata independently

5. **Preservation-Specific Formats**
   - Create a framework for embedding provenance and authenticity information directly with preserved content
   - Crucial for maintaining context and establishing chain of custody for cultural heritage materials
   - Must include cryptographic signing for authenticity verification
   - Should support standard preservation metadata (PREMIS, METS) in a distributed context

## Technical Requirements

- **Testability Requirements**
  - All preservation functions must have high test coverage (>95%)
  - Long-term processes must be accelerated in testing through injectable time controls
  - Corruption detection must be testable with deliberate data manipulation
  - Geographic distribution must be testable with simulated node locations

- **Performance Expectations**
  - System must scale to handle archives in the multi-terabyte range
  - Integrity verification must process at least 100GB of data per day on modest hardware
  - Metadata operations must complete within seconds even with millions of catalog entries
  - Replication processes must utilize available bandwidth efficiently with throttling capabilities

- **Integration Points**
  - Standard metadata interchange formats (DC, MODS, PREMIS, METS)
  - Cryptographic verification using standard libraries (hashlib, cryptography)
  - Filesystem abstraction for cross-platform storage
  - Network layer abstraction for different connectivity scenarios

- **Key Constraints**
  - Implementation must be pure Python for maximum portability across preservation nodes
  - All operations must be designed for long-term stability (decades rather than years)
  - Storage formats must be self-describing and resistant to format obsolescence
  - All core functionality must operate without UI components

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The DistriArchive implementation should provide these core functions:

1. **Distributed Archive Management**
   - Network-wide inventory of preserved content
   - Policy-based replication and distribution
   - Long-term preservation planning and execution

2. **Replication and Distribution**
   - Copy creation and verification across the network
   - Geographic analysis and optimization
   - Replication health monitoring and repair

3. **Integrity Management**
   - Multiple hash algorithm support for all content
   - Scheduled verification processes
   - Corruption detection and reporting
   - Automatic repair from intact copies

4. **Metadata System**
   - Distributed catalog implementation
   - Conflict resolution for metadata updates
   - Schema evolution handling
   - Search and retrieval capabilities

5. **Preservation Packaging**
   - Content packaging with embedded metadata
   - Provenance and authenticity records
   - Self-describing format implementation
   - Migration path planning for format obsolescence

## Testing Requirements

- **Key Functionalities to Verify**
  - Replication actually achieves required redundancy levels
  - Geographic distribution properly maximizes physical separation
  - Integrity checking correctly identifies corrupted files
  - Catalog synchronization properly resolves conflicts
  - Preservation formats correctly embed and maintain provenance information

- **Critical User Scenarios**
  - Ingesting new cultural heritage materials into the distributed archive
  - Recovering content after simulated node failures
  - Detecting and repairing corrupted archive items
  - Updating metadata across a distributed network of preservation nodes
  - Verifying authenticity of preserved content

- **Performance Benchmarks**
  - Must process at least 1TB of test data in verification tests
  - Metadata operations must scale to at least 1 million catalog entries
  - Replication must effectively utilize available bandwidth (at least 80% efficiency)
  - Geographic distribution algorithms must complete analysis in under 60 seconds for 100 nodes

- **Edge Cases and Error Handling**
  - Resilience when majority of nodes are offline
  - Recovery from corrupted metadata catalog
  - Handling of incomplete or damaged preservation packages
  - Operation with extremely limited bandwidth
  - Recovery from cryptographic verification failures

- **Test Coverage Requirements**
  - Core preservation functions must have 100% test coverage
  - Edge cases and error conditions must be thoroughly tested
  - Performance tests must verify scaling capabilities
  - Tests must simulate long-term operations (years/decades) through time manipulation

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

1. Digital materials can be reliably preserved across a distributed network
2. Replication management maintains the specified number of copies
3. Geographic diversity ensures physical separation of replicas
4. Integrity checking successfully identifies and helps repair corruption
5. Catalog synchronization maintains consistent metadata
6. Preservation formats properly maintain provenance and authenticity
7. All components perform efficiently at archive-scale data volumes

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