# ResistShare - Censorship-Resistant File Sharing Network

## Overview
ResistShare is a specialized peer-to-peer file sharing library designed to operate in restrictive network environments, providing secure and anonymous file sharing capabilities. It focuses on traffic obfuscation, anonymity routing, censorship-resistant discovery, dead drop functionality, and plausible deniability to enable information freedom and circumvent network restrictions.

## Persona Description
Sophia promotes information freedom and censorship resistance through decentralized technologies. She needs secure, anonymous file sharing capabilities that can operate even in restrictive network environments.

## Key Requirements

1. **Traffic Obfuscation**
   - Implement techniques to make P2P communication appear as regular web browsing
   - Critical for Sophia's work in regions where P2P traffic may be blocked or monitored
   - Must disguise protocol signatures to evade deep packet inspection
   - Should adapt to changing network conditions and detection methods

2. **Onion Routing Integration**
   - Create a multi-layered encryption system providing anonymity for participating peers
   - Essential for protecting the identity of users sharing sensitive information
   - Must route traffic through multiple intermediaries with layered encryption
   - Should minimize metadata leakage that could compromise anonymity

3. **Censorship-Resistant Peer Discovery**
   - Develop multiple fallback mechanisms for finding peers despite blocking attempts
   - Vital for maintaining network functionality when primary discovery methods are blocked
   - Must support diverse discovery techniques (DHT, domain fronting, rendezvous points, etc.)
   - Should automatically switch methods based on local network restrictions

4. **Dead Drop Functionality**
   - Implement a system allowing scheduled pickup of shared files without direct contact
   - Important for scenarios where direct peer connections may be risky or impossible
   - Must support time-delayed and indirect file transfers
   - Should include methods to verify file integrity and authenticity

5. **Plausible Deniability in Storage**
   - Create encrypted storage with separated headers and content for protection against forced disclosure
   - Critical for protecting users in situations where they may be compelled to reveal content
   - Must support hidden volumes with mathematically deniable existence
   - Should include emergency measures for rapid content protection

## Technical Requirements

- **Testability Requirements**
  - Obfuscation must be testable against simulated deep packet inspection
  - Anonymity must be verifiable through metadata analysis
  - Censorship resistance must be testable in simulated restrictive network environments
  - Security properties must be formally verifiable where possible

- **Performance Expectations**
  - System must still provide reasonable performance despite security overhead
  - Obfuscation techniques should not reduce throughput by more than 50%
  - Anonymity routing must maintain acceptable latency for interactive use
  - Storage operations must complete within reasonable timeframes even with encryption

- **Integration Points**
  - Standard cryptographic libraries for secure operations
  - Network traffic analysis evasion techniques
  - Established anonymity networks where appropriate
  - Secure storage mechanisms with plausible deniability

- **Key Constraints**
  - Implementation must be pure Python for maximum portability
  - All cryptographic operations must use well-reviewed, standard libraries
  - System must avoid dependencies that may be blocked in restrictive regions
  - All operations must prioritize user safety and information security

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The ResistShare implementation should provide these core functions:

1. **Traffic Disguise System**
   - Protocol obfuscation and transformation
   - Traffic pattern normalization
   - DPI evasion techniques
   - Adaptive camouflage strategies

2. **Anonymous Routing**
   - Multi-hop encrypted routing
   - Path selection and rotation
   - Traffic mixing and padding
   - Metadata minimization

3. **Resilient Discovery**
   - Multi-method peer discovery
   - Fallback mechanisms
   - Bootstrap node rotation
   - Steganographic rendezvous

4. **Indirect File Transfer**
   - Dead drop creation and management
   - Time-delayed pickup mechanisms
   - Out-of-band coordination
   - Secure retrieval verification

5. **Protected Storage**
   - Deniable encryption implementation
   - Header/content separation
   - Hidden volume management
   - Emergency protection measures

## Testing Requirements

- **Key Functionalities to Verify**
  - Traffic successfully evades detection by common DPI techniques
  - Routing effectively hides the origin and destination of transfers
  - Peer discovery works despite simulated blocking of primary methods
  - Dead drop file transfers complete successfully without direct contact
  - Storage provides plausible deniability under forensic analysis

- **Critical User Scenarios**
  - Sharing sensitive information in a network environment with deep packet inspection
  - Maintaining anonymity when connecting to peers in a monitored network
  - Discovering and connecting to the network when primary discovery methods are blocked
  - Exchanging files with another user without establishing a direct connection
  - Protecting stored content against forced disclosure

- **Performance Benchmarks**
  - Obfuscated transfers must achieve at least a specified minimum throughput
  - Anonymous routing must complete transfers within acceptable time frames
  - Discovery must find peers within 60 seconds even with primary methods blocked
  - Dead drops must reliably transfer files of at least specified size
  - Storage operations must maintain reasonable performance despite encryption

- **Edge Cases and Error Handling**
  - Correct behavior when all standard discovery methods are blocked
  - Graceful handling of compromised routing nodes
  - Recovery from interrupted transfers in high-risk situations
  - Proper function during active network interference
  - Safe failure modes for all security-critical operations

- **Test Coverage Requirements**
  - Security-critical components must have 100% test coverage
  - Obfuscation must be tested against multiple DPI simulation models
  - Anonymity must be verified with rigorous metadata analysis
  - Censorship resistance must be tested against diverse blocking techniques
  - Storage security must be verified with forensic analysis tools

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

1. Network traffic successfully evades detection and blocking
2. Users can share files while maintaining strong anonymity
3. The network remains accessible even when primary discovery methods are blocked
4. Files can be exchanged without requiring direct connections
5. Stored content maintains plausible deniability against forced disclosure
6. All security properties are formally verified through rigorous testing
7. The system remains usable despite the security overhead

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