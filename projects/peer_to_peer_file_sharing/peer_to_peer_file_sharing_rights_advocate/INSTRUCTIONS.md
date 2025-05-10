# Censorship-Resistant Information Sharing System

## Overview
A secure peer-to-peer file sharing system designed to enable the anonymous exchange of information in restrictive network environments, incorporating traffic obfuscation, multi-layered anonymity protections, and resilient discovery mechanisms to preserve freedom of information despite network interference.

## Persona Description
Sophia promotes information freedom and censorship resistance through decentralized technologies. She needs secure, anonymous file sharing capabilities that can operate even in restrictive network environments.

## Key Requirements
1. **Traffic Obfuscation**
   - Protocol mimicry making P2P traffic appear as regular HTTPS browsing
   - Deep packet inspection resistance through traffic shaping and padding
   - Pluggable transport support for adapting to changing censorship techniques
   - Critical for bypassing network-level blocking that would prevent information exchange in restrictive environments

2. **Onion Routing Integration**
   - Multi-layered encryption protecting sender and receiver identities
   - Configurable routing path selection with trust levels
   - Exit node rotation and circuit building controls
   - Essential for providing anonymity to participants who may face consequences for sharing certain information

3. **Censorship-Resistant Peer Discovery**
   - Multiple redundant discovery mechanisms including domain fronting
   - Bootstrap node concealment through steganography
   - Adaptive discovery strategies based on network conditions
   - Necessary to enable initial connection to the network despite active blocking of known P2P infrastructure

4. **Dead Drop Functionality**
   - Asynchronous file pickup without direct peer connection
   - Time-based availability windows for enhanced security
   - Secure authentication without revealing participant identities
   - Vital for scenarios where direct connections between specific peers would raise suspicion or reveal associations

5. **Plausible Deniability in Storage**
   - Encrypted headers preventing identification of file contents
   - File sharding across multiple storage locations
   - Hidden volumes for sensitive content with deniable access
   - Critical for protecting individuals when devices are physically inspected or seized

## Technical Requirements
### Testability Requirements
- All cryptographic components must have comprehensive security tests
- Obfuscation techniques must be verified against current DPI methods
- Censorship circumvention approaches must be tested against simulated blockers
- Anonymous routing must be verified for information leakage
- Simulated adversary tests for various threat models

### Performance Expectations
- Reasonable transfer speeds despite anonymity overhead
- Minimal fingerprinting surface to avoid detection
- Acceptable latency for interactive use when necessary
- Resource usage compatible with consumer hardware
- Resilience to high packet loss and intermittent connectivity

### Integration Points
- Tor network compatibility for enhanced anonymity
- I2P network bridging capabilities
- Pluggable transport framework integration
- Standard cryptographic libraries adherence
- Steganography tools for bootstrap information

### Key Constraints
- Must operate in highly restricted network environments
- Minimal metadata generation and collection
- No dependencies on centralized services
- No permanent storage of user identification data
- Must maintain effectiveness despite partial network visibility

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Traffic Obfuscation Engine**
   - Protocol detection evasion techniques
   - Traffic pattern normalization
   - Deep packet inspection resistance mechanisms
   - Adaptive behavior based on network conditions

2. **Anonymity Network**
   - Multi-layered encryption implementation
   - Route selection and management
   - Circuit building and rotation
   - Identity protection mechanisms

3. **Resilient Discovery System**
   - Multiple discovery protocol implementations
   - Bootstrapping from concealed information
   - Fallback mechanisms when primary methods are blocked
   - Network condition-based strategy selection

4. **Asynchronous Exchange Framework**
   - Dead drop coordination protocol
   - Secure time-based access mechanism
   - Anonymous authentication system
   - Reliable pickup verification

5. **Deniable Storage Engine**
   - Header encryption and content separation
   - Distributed storage with redundancy
   - Hidden volume management
   - Secure deletion and plausible coverup

## Testing Requirements
### Key Functionalities to Verify
- Effectiveness of traffic obfuscation against detection systems
- Anonymity preservation through routing infrastructure
- Success rate of peer discovery in restricted environments
- Reliability of asynchronous file exchange
- Security of storage system against forensic analysis

### Critical Scenarios to Test
- Operation in networks with deep packet inspection
- Performance under active probing and fingerprinting attempts
- Discovery success with various blocking techniques active
- Dead drop functionality with high latency and timeouts
- Deniable storage under simulated forensic examination

### Performance Benchmarks
- Traffic analysis resistance score against current detection methods
- Discovery success rates in simulated restrictive environments
- Anonymity set size and unlinkability metrics
- Time required for successful dead drop operations
- Storage overhead for deniability features

### Edge Cases and Error Conditions
- Adaptive censorship that learns and blocks in real-time
- Highly degraded network conditions (extreme jitter, blocking, loss)
- Targeted attacks against specific protocol weaknesses
- Incomplete dead drop operations due to network failure
- Forced shutdown during sensitive operations
- Partial compromise of routing infrastructure

### Required Test Coverage
- 100% coverage of cryptographic and security-critical code
- ≥95% coverage of obfuscation components
- ≥90% coverage for discovery mechanisms
- ≥90% coverage for asynchronous exchange protocols
- ≥95% coverage for deniable storage systems

## Success Criteria
The implementation will be considered successful when:

1. Traffic is undetectable as P2P communication by current DPI technologies
2. User anonymity is preserved even when some network nodes are compromised
3. The system can establish connections in networks with active P2P blocking
4. Files can be exchanged without direct connections between peers
5. Stored data provides plausible deniability under examination
6. All five key requirements are fully implemented and testable via pytest
7. The system remains functional in the world's most restrictive network environments
8. Independent security audit verifies absence of critical vulnerabilities

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.