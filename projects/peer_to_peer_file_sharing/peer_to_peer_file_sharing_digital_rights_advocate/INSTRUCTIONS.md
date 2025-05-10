# Censorship-Resistant Peer-to-Peer File Sharing System

## Overview
A secure, anonymous file sharing library that enables users to distribute information even in restrictive network environments. This system employs traffic obfuscation, onion routing, and resilient peer discovery to ensure files can be shared freely regardless of network restrictions or surveillance.

## Persona Description
Sophia promotes information freedom and censorship resistance through decentralized technologies. She needs secure, anonymous file sharing capabilities that can operate even in restrictive network environments.

## Key Requirements

1. **Traffic Obfuscation**
   - Implement protocol obfuscation techniques that make P2P communication appear as regular HTTPS web browsing
   - Critical for Sophia because network deep packet inspection is often used to identify and block P2P traffic in restrictive environments
   - Must support pluggable transport mechanisms to adapt to evolving censorship techniques

2. **Onion Routing Integration**
   - Create a multi-layered encryption system similar to Tor that routes communications through multiple peers
   - Essential because it provides anonymity for both the sender and receiver, protecting users from surveillance
   - Should include circuit-building capabilities with at least 3 hops for adequate anonymity protection

3. **Censorship-Resistant Peer Discovery**
   - Develop multiple fallback discovery mechanisms that work even when primary methods are blocked
   - Vital for ensuring the network remains functional when authorities attempt to disrupt peer discovery
   - Must include methods like domain fronting, bootstrap nodes, and distributed rendezvous points

4. **Dead Drop Functionality**
   - Build a system allowing scheduled pickup of shared files without direct peer-to-peer contact
   - Important because it reduces the risk profile by eliminating the need for simultaneous online presence
   - Should support time-delayed retrieval with automatic cleanup of dropped files

5. **Plausible Deniability Storage**
   - Implement encrypted headers and content separation in storage architecture
   - Critical for protecting users from forced disclosure, as files should not be identifiable without proper keys
   - Must include hidden volume capabilities and encryption that doesn't reveal the existence of protected data

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest and support mocking of network connections
- Traffic obfuscation modules must be testable without actual network traffic
- Simulated network censorship environments must be creatable for testing resilience features
- The testing framework must support verifying the anonymity properties without compromising them

### Performance Expectations
- The system must function on low-bandwidth connections (as low as 256 Kbps)
- File transfers should continue working despite up to 40% packet loss
- The overhead from anonymity features should not exceed 100% of the original file size
- Peer discovery must complete within 30 seconds even under adverse network conditions

### Integration Points
- The system should integrate with standard Python cryptography libraries
- A pluggable transport interface for adding new obfuscation methods
- Integration with existing Tor libraries for onion routing (optional direct implementation)
- Standard file system interfaces for accessing and storing content

### Key Constraints
- Must function without any centralized coordination points
- All network traffic must be encrypted end-to-end
- No logs should be kept of transfer activities to protect user privacy
- The system must be stateless where possible to minimize forensic evidence
- No metadata about files should be stored in plaintext

## Core Functionality

The implementation must provide a Python library with the following core modules:

1. **Secure Network Layer**
   - Establishes encrypted connections between peers
   - Implements traffic obfuscation to avoid detection
   - Handles NAT traversal for connecting peers behind firewalls
   - Recovers gracefully from connection interruptions

2. **Anonymity Routing System**
   - Creates and manages onion routing circuits
   - Handles encryption/decryption of data at each routing hop
   - Implements circuit selection and rotation strategies
   - Provides protections against timing and correlation attacks

3. **Resilient Peer Discovery**
   - Implements multiple discovery methods that operate independently
   - Manages peer connection information securely
   - Provides fallback mechanisms when primary discovery is blocked
   - Includes bootstrap mechanisms for initial network entry

4. **Secure File Transfer**
   - Handles chunking of files for efficient transfer
   - Implements dead drop functionality for asynchronous sharing
   - Provides cryptographic verification of file integrity
   - Supports resumable transfers for interrupted connections

5. **Deniable Storage Manager**
   - Implements encrypted storage with plausible deniability features
   - Manages separation of file content and metadata
   - Provides secure deletion capabilities when needed
   - Includes hidden volume capabilities for critical content

## Testing Requirements

### Key Functionalities to Verify
- Successful file transfer under various network conditions
- Effectiveness of traffic obfuscation against pattern detection
- Anonymity preservation through the onion routing system
- Resilience of peer discovery when primary methods are blocked
- Security of the plausible deniability storage implementation

### Critical User Scenarios
- Complete file sharing process between two peers in a censored network environment
- Recovery from intentionally dropped connections during transfer
- Successful dead drop placement and retrieval without direct contact
- Network behavior when a large percentage of peers suddenly disappear
- System response to simulated censorship and blocking techniques

### Performance Benchmarks
- File transfer speeds under different network conditions and constraints
- Time to discover peers using different discovery mechanisms
- Memory and CPU usage during high-load operations
- Recovery time after network disruptions
- Overhead of encryption and anonymity features

### Edge Cases and Error Conditions
- Behavior when all primary discovery methods are simultaneously blocked
- System response to malicious peers attempting to deanonymize users
- Recovery when a peer in an onion routing circuit suddenly drops
- Data integrity verification when transfers are corrupted
- System behavior under extreme packet loss conditions

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of encryption and anonymity-critical code paths
- All error handling code paths must be explicitly tested
- Performance tests must cover 10th, 50th, and 90th percentile network conditions
- All five key requirements must have dedicated test suites

## Success Criteria

1. **Censorship Circumvention Effectiveness**
   - The system successfully transfers files in network environments with simulated DPI and traffic blocking
   - All network traffic successfully evades standard pattern detection methods
   - Peer discovery functions even when primary connection methods are blocked

2. **Anonymity Protection**
   - Network traffic analysis cannot determine the original source or final destination of transfers
   - Traffic correlation attacks are unsuccessful in identifying communication patterns
   - No metadata leakage occurs that could compromise user identity

3. **Resilience Under Adverse Conditions**
   - The system recovers from 90% of simulated network failures without user intervention
   - Files transfer successfully despite intermittent connectivity
   - Dead drop functionality works reliably for asynchronous file retrieval

4. **Security of Storage Solution**
   - Hidden volumes cannot be detected without appropriate credentials
   - File content remains secure even if the application directory is compromised
   - No evidence of specific file transfers remains after secure deletion

5. **Usability as a Library**
   - The API is well-documented and follows consistent patterns
   - Integration requires minimal configuration for basic use cases
   - The library can be imported and used in other Python applications

## Setup and Development

To set up the development environment and start implementing the project:

1. Create a new Python library project using `uv`:
   ```
   uv init --lib
   ```

2. Install development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Format code:
   ```
   uv run ruff format
   ```

5. Lint code:
   ```
   uv run ruff check .
   ```

6. Type check:
   ```
   uv run pyright
   ```

7. Run a specific script:
   ```
   uv run python script.py
   ```

Remember that all functionality must be implemented as Python modules and classes with no UI components. The entire system should be usable as a library that can be imported and integrated into other applications.