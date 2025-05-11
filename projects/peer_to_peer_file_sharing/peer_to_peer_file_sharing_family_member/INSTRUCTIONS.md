# FamilyShare - Private Media Sharing for Non-Technical Users

## Overview
FamilyShare is a simplified peer-to-peer file sharing library focused on privately sharing personal photos and videos among family members without relying on commercial cloud services. It emphasizes simplicity, automatic discovery, network privacy, media optimization, and familiar organizational structures while hiding technical complexity.

## Persona Description
Miguel wants to share photos and videos with family members without uploading personal memories to commercial cloud services. He needs an easy-to-use, private sharing network accessible to non-technical relatives.

## Key Requirements

1. **Simple Interface Abstractions**
   - Create a clean, minimal API that hides technical complexity but enables intuitive file sharing operations
   - Essential for Miguel's family members who have limited technical expertise
   - Must abstract away technical concepts like DHTs, peer discovery, and networking
   - Should focus on high-level operations like "share album with Mom" rather than network details

2. **Automatic Device Discovery**
   - Implement zero-configuration network discovery for finding family members on the same network
   - Critical for eliminating manual configuration steps that would confuse non-technical users
   - Must work reliably across home networks with various router configurations
   - Should identify and remember family devices with friendly names rather than technical identifiers

3. **Closed Network Operation**
   - Develop a secure invitation and authentication system restricting sharing to explicitly trusted devices
   - Vital for ensuring family photos and videos remain private and aren't accidentally shared publicly
   - Must provide simple but effective methods to add new trusted family devices
   - Should enforce privacy boundaries while making the security model understandable to non-experts

4. **Media-Specific Optimizations**
   - Create automatic transcoding capabilities to optimize media files for different receiving devices
   - Important for accommodating various family devices with different capabilities and storage constraints
   - Must handle common photo and video formats, adapting resolution and bitrate appropriately
   - Should balance quality and file size based on device capabilities and connection quality

5. **Album Organization**
   - Implement familiar album-based organization that maintains standard photo collection structures
   - Essential for providing a familiar way to browse and organize family memories
   - Must support hierarchical album structures with descriptive metadata
   - Should preserve original organization while enabling family-friendly navigation

## Technical Requirements

- **Testability Requirements**
  - All user operations must be testable through a programmatic API
  - Network discovery must be testable in isolated test environments
  - Media handling must be testable with sample files of different formats and sizes
  - Family sharing patterns must be simulatable in testing

- **Performance Expectations**
  - Device discovery must complete within 5 seconds on typical home networks
  - Media browsing operations must respond within 500ms even with large collections
  - Transcoding must optimize media without noticeable quality loss
  - Sharing operations must provide clear progress indicators for long-running transfers

- **Integration Points**
  - Standard media file format handling (JPEG, PNG, MP4, etc.)
  - Common network discovery protocols (mDNS, SSDP, etc.)
  - Local file system abstractions for storage
  - Metadata extraction from media files

- **Key Constraints**
  - All functionality must be implemented without UI components
  - Operation must be possible on limited home network bandwidth
  - Security must be strong but without complex configuration
  - All technical complexity must be hidden behind simple APIs

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The FamilyShare implementation should provide these core functions:

1. **Simple Sharing API**
   - High-level operations for common family sharing tasks
   - Abstraction layer hiding technical network details
   - Error handling designed for non-technical users

2. **Device Discovery and Management**
   - Automatic discovery of family devices on local networks
   - Persistent device identification and naming
   - Robust handling of network changes and device mobility

3. **Privacy and Security**
   - Trust establishment between family devices
   - Invitation system for adding new family members
   - Encryption for data in transit between devices

4. **Media Handling**
   - Intelligent media format conversion
   - Thumbnail generation for efficient browsing
   - Optimization for different device capabilities

5. **Album Management**
   - Hierarchical album structure
   - Metadata extraction and organization
   - Conflict resolution for shared albums

## Testing Requirements

- **Key Functionalities to Verify**
  - Library successfully hides networking complexity behind simple operations
  - Automatic discovery correctly identifies family devices on the network
  - Closed network properly restricts access to trusted devices only
  - Media transcoding appropriately adapts content for different devices
  - Album organization maintains familiar browsing structures

- **Critical User Scenarios**
  - Sharing a new photo album with multiple family members
  - Adding a new family member's device to the trusted network
  - Browsing shared memories across different device types
  - Handling large video files with automatic optimization
  - Managing overlapping albums from different family members

- **Performance Benchmarks**
  - Discovery must identify family devices within 5 seconds on standard networks
  - Album browsing must remain responsive with 10,000+ photos
  - Media optimization must process at least 10 photos per minute
  - Sharing operations must utilize at least 50% of available bandwidth
  - Memory usage must remain reasonable on limited devices

- **Edge Cases and Error Handling**
  - Graceful behavior when network connectivity is intermittent
  - Handling of partial transfers when connections are interrupted
  - Recovery from power loss during sharing operations
  - Dealing with untrusted device connection attempts
  - Managing extremely large media collections

- **Test Coverage Requirements**
  - All public API functions must have 100% test coverage
  - Network discovery must be tested with various simulated network topologies
  - Media handling must be tested with diverse file formats and sizes
  - Security functions must have thorough test coverage for all edge cases

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

1. It enables sharing of photos and videos without requiring technical knowledge
2. Family devices are automatically discovered when on the same network
3. Sharing is strictly limited to explicitly trusted family devices
4. Media files are appropriately optimized for different receiving devices
5. Photos and videos are organized in familiar album structures
6. All operations are secure, reliable, and easy to understand
7. Performance remains good even with large media collections

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