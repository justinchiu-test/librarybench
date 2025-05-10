# BusinessShare - A Secure P2P File Sharing System for Small Professional Teams

## Overview
BusinessShare is a secure peer-to-peer file sharing system designed for small architectural firms and professional services businesses that need to collaborate on large files with clients and contractors. It provides granular access controls, simplified external sharing, automated directory synchronization, comprehensive audit logging, and visual comparison tools that support efficient professional collaboration without the expense or complexity of enterprise solutions.

## Persona Description
Carlos runs a small architectural firm collaborating on large design files with contractors and clients. He needs secure file sharing without expensive enterprise file servers or cloud storage with complicated access controls.

## Key Requirements
1. **Access Control List System**
   - Granular permission management restricting file visibility to specific peer groups or individuals
   - Critical for Carlos's firm as they work with sensitive client building plans that must only be accessible to authorized team members, specific contractors, and the respective clients - preventing information leaks while enabling collaboration
   - Must include role-based permissions, group management, temporary access provisions, and the ability to revoke access instantly when needed

2. **Client-Friendly Sharing Links**
   - Simplified external sharing allowing limited participation without full software installation
   - Essential because Carlos's clients are not technical and need a frictionless way to access and review architectural designs without installing specialized software or navigating complex systems
   - Implementation should include web-accessible interfaces, temporary access tokens, simplified view-only modes, and intuitive download mechanisms

3. **Automated Directory Synchronization**
   - Configurable folder replication with selective inclusion rules for project files
   - Vital for maintaining consistent file structures across the firm, ensuring that project files are automatically distributed to the right team members as they are updated, without requiring manual file transfers
   - Requires real-time change detection, smart conflict resolution, directory mapping, and selective sync filters

4. **Comprehensive Audit Logging**
   - Detailed activity tracking for all file access and transfer actions
   - Important for Carlos to maintain professional accountability, create billable hour records, and demonstrate due diligence in handling client information - providing visibility into who accessed what files and when
   - Should include immutable activity records, access timestamps, modification tracking, and exportable reports for compliance documentation

5. **Visual Directory Comparison Tools**
   - Graphical difference highlighting between shared folder versions
   - Critical for identifying changes between iterations of project files, allowing team members to quickly understand what has been modified in complex directory structures, particularly important for architectural drawings with multiple revisions
   - Must include file-level change detection, metadata comparison, hierarchical difference visualization, and support for architectural file formats

## Technical Requirements
- **Testability Requirements**
  - Simulation of multi-user collaboration scenarios
  - Mock client access patterns via sharing links
  - Validation suite for directory synchronization accuracy
  - Verification of audit log integrity and completeness
  - Test harnesses for access control enforcement

- **Performance Expectations**
  - Support for files up to 1GB (typical for architectural drawings and models)
  - Handling of project folders with 10,000+ files
  - Directory comparison operations completing in under 30 seconds
  - Synchronization bandwidth optimized for office network environments
  - Audit logging with minimal performance impact (<3% overhead)

- **Integration Points**
  - Common architectural file formats (DWG, RVT, SKP, etc.)
  - Standard authentication systems (LDAP, OAuth)
  - Email notification systems for sharing alerts
  - Backup and archival systems
  - Billing and time-tracking software

- **Key Constraints**
  - Must operate without dedicated IT staff support
  - Must be accessible to non-technical clients
  - Must maintain strict confidentiality of client data
  - Must comply with professional standards for data handling
  - Must function reliably in small office network environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
BusinessShare must provide a comprehensive peer-to-peer solution for small business file sharing with these core components:

1. A secure P2P file transfer system with encrypted communication channels
2. A flexible access control system with fine-grained permissions and group management
3. A web-accessible sharing mechanism for external collaborators
4. An automated directory synchronization engine with conflict resolution
5. A comprehensive audit logging system for tracking all file operations
6. A directory comparison tool for identifying differences between file versions
7. A notification system for alerting users to important file activities
8. A secure authentication mechanism for verifying user identities

The system should provide clear APIs that can integrate with professional workflows, with programmatic access to all functionality and the ability to extend the system for specific business needs.

## Testing Requirements
The implementation must include comprehensive test suites verifying:

- **Key Functionalities**
  - Validation of access control restrictions enforced correctly
  - Verification of client sharing links functionality and security
  - Confirmation of directory synchronization accuracy and conflict handling
  - Validation of audit log completeness and tamper resistance
  - Verification of directory comparison results accuracy

- **Critical User Scenarios**
  - An architectural firm sharing project files with specific permissions for different team roles
  - Clients accessing shared designs through simplified web links
  - Synchronized project directories automatically updating across multiple devices
  - Administrators reviewing comprehensive audit logs of file activities
  - Team members comparing different versions of project directories to identify changes

- **Performance Benchmarks**
  - Access control decisions processing in <100ms
  - Client sharing links generating in <1 second
  - Directory synchronization completing within 5 minutes for standard project folders
  - Audit logging with <50ms additional latency per operation
  - Directory comparison completing within 30 seconds for typical project sizes

- **Edge Cases and Error Conditions**
  - Handling of permission changes while files are being accessed
  - Recovery from interrupted synchronization operations
  - Management of conflicting file changes from multiple sources
  - Protection against audit log tampering attempts
  - Graceful handling of large and complex directory structures

- **Required Test Coverage Metrics**
  - Minimum 90% statement coverage for all modules
  - Explicit security testing for access control mechanisms
  - Comprehensive validation of synchronization edge cases
  - Performance tests for operations on realistically-sized project data
  - Verification of all error handling and recovery mechanisms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. File sharing occurs with proper access controls that prevent unauthorized access
2. Clients can easily access shared content without technical knowledge
3. Directory synchronization automatically maintains consistent project files
4. Audit logging provides complete visibility into all file activities
5. Directory comparison accurately identifies changes between versions
6. The system operates efficiently with the file sizes and quantities typical in architectural work
7. All operations maintain appropriate security for client confidential information
8. The solution integrates with existing professional workflows

To set up your development environment, follow these steps:

1. Use `uv init --lib` to set up the project and create your `pyproject.toml`
2. Install dependencies with `uv sync`
3. Run your code with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format your code with `uv run ruff format`
6. Lint your code with `uv run ruff check .`
7. Type check with `uv run pyright`