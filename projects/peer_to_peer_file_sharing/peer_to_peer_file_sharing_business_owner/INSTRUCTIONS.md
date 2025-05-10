# Secure Architectural File Collaboration System

## Overview
A controlled peer-to-peer file sharing solution for small architectural firms, enabling secure collaboration on large design files with fine-grained access controls, client-friendly sharing options, and comprehensive audit capabilities without the need for expensive enterprise infrastructure.

## Persona Description
Carlos runs a small architectural firm collaborating on large design files with contractors and clients. He needs secure file sharing without expensive enterprise file servers or cloud storage with complicated access controls.

## Key Requirements
1. **Access Control Lists**
   - Granular permission system for directories and files
   - Group-based and individual access control
   - Temporary and expiring access options
   - Essential for securely managing who can access specific project files, enabling collaboration with contractors and consultants while maintaining control over confidential designs

2. **Client-Friendly Sharing Links**
   - Web-accessible view-only links for clients
   - Simplified download capabilities for non-technical users
   - Optional authentication for sensitive content
   - Critical for sharing design files with clients who don't have specialized software or technical expertise, allowing for easy feedback without complex software installation

3. **Automated Directory Synchronization**
   - Configurable rules for project folder synchronization
   - Exclusion patterns for temporary and local files
   - Bandwidth-aware background synchronization
   - Necessary for keeping design teams in sync with minimal manual intervention, ensuring everyone works with the latest versions while excluding non-essential files

4. **Comprehensive Audit Logging**
   - Detailed tracking of file access and transfers
   - User activity monitoring and reporting
   - Timestamp and IP-based access records
   - Vital for maintaining project records, accountability, and compliance with client confidentiality requirements in the architectural industry

5. **Visual Directory Comparison**
   - Side-by-side visualization of directory differences
   - Change highlighting between versions
   - Visual representation of file modifications
   - Critical for quickly identifying changes between project iterations, helping coordinate design updates and prevent accidental overwrites

## Technical Requirements
### Testability Requirements
- All security components must have comprehensive coverage
- ACL enforcement must be verified through automated testing
- Directory synchronization must have deterministic test cases
- Audit logging must be validated for completeness
- Directory comparison must have quality assurance tests

### Performance Expectations
- Support for design files up to 2GB in size
- Efficient handling of project directories with 10,000+ files
- Minimal memory footprint for background synchronization
- Quick generation of comparison data
- Responsive access control checks even with complex rules

### Integration Points
- Common architectural file format support (.dwg, .rvt, etc.)
- Standard authentication mechanisms (OAuth, SAML)
- Email notification systems
- Backup and archiving solutions
- Project management tool hooks

### Key Constraints
- Must operate without dedicated server infrastructure
- Client access must work through standard web browsers
- All security measures must be verifiable
- Minimal setup requirements for new project participants
- Data must remain under firm's direct control

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Access Control System**
   - Permission definition and storage
   - Rule evaluation and enforcement
   - User and group management
   - Access request handling

2. **Client Sharing Portal**
   - Secure link generation and management
   - Web-accessible content preparation
   - Authentication for protected resources
   - Download and viewing capabilities

3. **Synchronization Engine**
   - Rule-based file selection
   - Change detection and conflict resolution
   - Background transfer management
   - Status tracking and reporting

4. **Audit System**
   - Activity capture and storage
   - Secure tamper-evident logging
   - Query and reporting capabilities
   - Retention policy management

5. **Directory Comparison**
   - Efficient directory scanning and indexing
   - Metadata and content comparison
   - Difference classification and summarization
   - Data structures for visual representation

## Testing Requirements
### Key Functionalities to Verify
- Correct enforcement of complex access control rules
- Secure and functional client access through generated links
- Accurate synchronization following configured rules
- Complete and tamper-evident audit trail creation
- Precise directory comparison with different change types

### Critical Scenarios to Test
- Multi-user collaboration with varying permission levels
- Client access from different browsers and devices
- Synchronization with conflicting changes
- Audit trail for sensitive operations
- Directory comparison with complex project structures

### Performance Benchmarks
- ACL evaluation time < 100ms even for complex rule sets
- Client link generation and validation < 1s
- Synchronization scanning rate > 1000 files/second
- Audit logging with minimal performance impact
- Directory comparison completed in < 30s for 10,000 files

### Edge Cases and Error Conditions
- Handling permission conflicts and inheritance edge cases
- Recovery from interrupted client downloads
- Synchronization with intermittent connectivity
- Audit system behavior during storage constraints
- Comparison of extremely large or complex directories
- Recovery from corrupted metadata or index files

### Required Test Coverage
- 100% coverage of access control enforcement code
- ≥95% coverage for client sharing components
- ≥90% coverage for synchronization engine
- 100% coverage for audit logging system
- ≥90% coverage for directory comparison algorithms

## Success Criteria
The implementation will be considered successful when:

1. Architectural teams can securely collaborate with appropriate access controls
2. Clients can easily view and download shared designs without technical challenges
3. Project directories stay synchronized with minimal manual intervention
4. All file activities are properly tracked for project records and accountability
5. Team members can quickly identify and understand changes between versions
6. All five key requirements are fully implemented and testable via pytest
7. The system significantly reduces IT costs compared to enterprise solutions
8. Project delivery time decreases due to improved collaboration efficiency

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.