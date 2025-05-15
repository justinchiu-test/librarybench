# SecureShare - Peer-to-Peer File Sharing for Architectural Firms

## Overview
SecureShare is a business-focused peer-to-peer file sharing library designed specifically for architectural firms that need to securely share large design files with contractors and clients without relying on expensive enterprise file servers or complex cloud storage solutions. The system provides granular access controls, audit capabilities, and efficient synchronization mechanisms tailored to collaborative design workflows.

## Persona Description
Carlos runs a small architectural firm collaborating on large design files with contractors and clients. He needs secure file sharing without expensive enterprise file servers or cloud storage with complicated access controls.

## Key Requirements

1. **Access Control Lists**
   - Implement a robust ACL system that restricts file visibility to specific peer groups or individuals
   - This is critical for Carlos as architectural plans often contain sensitive client information and proprietary design details that should only be accessible to authorized parties
   - The ACL system should support different permission levels (read, write, etc.) for different collaborators

2. **Client-friendly Sharing Links**
   - Develop a mechanism for generating temporary access links that allow limited participation without requiring full software installation
   - Essential for client reviews and approvals, as clients may not have technical expertise to install and configure P2P software
   - Links should be time-limited and revocable to maintain security during the review process

3. **Automated Synchronization of Project Directories**
   - Create a system for automated synchronization of project directories with customizable inclusion/exclusion rules
   - Critical for maintaining consistent project files across the firm's team members, contractors, and consultants
   - Must handle large architectural files efficiently while ensuring everyone has the most current version

4. **Audit Logging**
   - Implement comprehensive logging of all file access and transfer activities for project records
   - Necessary for project management, billing purposes, and tracking who has accessed which version of files
   - Should include timestamps, user identification, action performed, and file metadata

5. **Visual Directory Comparison**
   - Develop functionality to highlight differences between shared folder versions across peers
   - Essential for Carlos to quickly identify what has changed in complex project structures with many files
   - Critical for maintaining version consistency across multiple collaborators working on different aspects of projects

## Technical Requirements

- **Testability Requirements**
  - All components must be designed with clear interfaces that can be tested independently
  - Mock network layers must be supported to simulate real-world conditions without actual network traffic
  - Test fixtures must represent realistic architectural project structures (deeply nested folders, large files)
  - Performance tests must verify the system can handle files of typical CAD size (50-500MB)

- **Performance Expectations**
  - Directory synchronization must complete within 30 seconds for typical project structures (1000+ files)
  - Access control verification must not add more than 100ms latency to file operations
  - Visual difference comparison must complete within 5 seconds for folders with up to 1000 files
  - System must efficiently handle architectural files (CAD, BIM, rendering files) without excessive memory usage

- **Integration Points**
  - File system interface must be abstracted to allow easy testing without actually writing files
  - Network layer must support mocking for testing without actual peer connections
  - Access control and audit logging systems must provide clear APIs for integration with other components
  - Directory comparison engine must expose APIs for potential integration with external diff tools

- **Key Constraints**
  - All functionality must be implemented without UI components, focusing on API-driven approach
  - Implementation must be pure Python to ensure cross-platform compatibility
  - No dependencies on external databases; all data must be stored in files or in-memory structures
  - Network operations must be designed to work in typical office network environments with NAT/firewalls

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The SecureShare implementation should provide these core functions:

1. **Peer Management and Discovery**
   - Peer registration and authentication system
   - Peer grouping for project-based access control
   - Client/contractor authorization with different permission levels

2. **Access Control Management**
   - ACL definition and enforcement for files and directories
   - Permission checking intercepting all file operations
   - Time-limited access token generation for client sharing links

3. **File Synchronization**
   - Efficient file and directory synchronization with delta transfers
   - Rule-based inclusion/exclusion filtering of content
   - Conflict detection and resolution strategies

4. **Logging and Auditing**
   - Comprehensive event logging for all file operations
   - Secure, tamper-evident audit log storage
   - Query interface for retrieving audit information

5. **Directory Comparison**
   - Efficient algorithm for detecting differences between directory structures
   - Metadata comparison (timestamps, sizes, permissions)
   - Output format suitable for programmatic processing

## Testing Requirements

- **Key Functionalities to Verify**
  - ACL enforcement properly restricts access based on defined permissions
  - Sharing links function correctly with proper time limitations
  - Directory synchronization correctly applies inclusion/exclusion rules
  - Audit logs capture all required information for file operations
  - Directory comparison correctly identifies added, removed, and modified files

- **Critical User Scenarios**
  - Adding a new contractor with limited access to specific project files
  - Client reviewing shared files via temporary link without full software installation
  - Synchronizing updated project files across multiple team members
  - Retrieving audit logs for client billing and project tracking
  - Comparing directories after synchronization to verify consistency

- **Performance Benchmarks**
  - Transfer rates must exceed 10MB/s on local networks for large architectural files
  - ACL verification must process at least 100 permission checks per second
  - Synchronization must handle at least 10,000 files without memory issues
  - Audit logging must not slow down file operations by more than 5%

- **Edge Cases and Error Handling**
  - Graceful handling of permission denied scenarios
  - Recovery from interrupted synchronization
  - Handling of conflicting simultaneous edits
  - Dealing with malformed or corrupted ACL definitions
  - Managing expired sharing links
  - Handling network disruptions during file transfers

- **Test Coverage Requirements**
  - Minimum 90% code coverage for core functionality
  - 100% coverage for ACL enforcement and audit logging components
  - All error handling paths must be tested
  - All file operation types must have both positive and negative tests

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

1. The P2P file sharing system properly enforces access controls, preventing unauthorized access while allowing collaboration
2. Client-friendly sharing links work correctly with proper time limitations
3. Directory synchronization correctly handles architectural project files with proper inclusion/exclusion rules
4. Audit logging captures comprehensive information about all file operations
5. Directory comparison accurately identifies differences between shared folders
6. All components are implemented as well-structured Python modules with clear APIs
7. The system meets the specified performance benchmarks for typical architectural workflows

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