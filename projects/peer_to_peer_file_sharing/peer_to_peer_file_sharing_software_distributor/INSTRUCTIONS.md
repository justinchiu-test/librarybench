# Distributed Open Source Software Distribution Network

## Overview
A high-performance peer-to-peer distribution system optimized for large open source software packages, featuring swarm downloading, seeding incentives, cryptographic integrity verification, differential updates, and fallback mechanisms to ensure reliable and efficient software distribution.

## Persona Description
Wei maintains alternative distribution channels for large open source software packages. He needs efficient ways to share these packages while reducing bandwidth costs and improving download speeds.

## Key Requirements
1. **Swarm-Based Package Distribution**
   - Multi-source parallel downloading from available peers
   - Dynamic peer selection based on performance and availability
   - Chunk-based transfer with rarest-first piece selection
   - Essential for maximizing download speeds by utilizing the combined bandwidth of multiple sources, reducing dependency on any single distribution point

2. **Seeding Incentive System**
   - Ratio-based contribution tracking
   - Prioritization for active contributors
   - Recognition and reward mechanisms for persistent seeders
   - Critical for maintaining a healthy distribution network by encouraging users to continue sharing packages after downloading, ensuring sustainable bandwidth contribution

3. **Cryptographic Integrity Verification**
   - Multiple hash algorithm support (SHA-256, SHA-3, etc.)
   - Digital signature verification using developer keys
   - Chunk-level verification during downloads
   - Vital for ensuring downloaded software exactly matches the original, intended release and hasn't been tampered with or corrupted during distribution

4. **Differential Update Mechanism**
   - Binary diff algorithm implementation
   - Version history tracking and management
   - Minimal transfer for incremental software updates
   - Necessary for efficiently distributing frequent updates by transmitting only the changed portions, saving substantial bandwidth for both distributors and users

5. **HTTP Mirror Integration**
   - Fallback to traditional HTTP sources when P2P is limited
   - Automatic mirror selection based on geographic proximity
   - Hybrid download capability combining P2P and HTTP
   - Essential for ensuring universal accessibility of software packages even for users behind restrictive firewalls or in environments where P2P is blocked

## Technical Requirements
### Testability Requirements
- All components must have comprehensive unit tests
- Swarm behavior must be verified in simulated network environments
- Integrity verification must have 100% test coverage
- Differential update generation must be tested against real-world packages
- Mirror integration must be tested with various failure scenarios

### Performance Expectations
- Support for packages up to 20GB in size
- Efficient handling of software repositories with thousands of packages
- Download speeds at least 90% of theoretical maximum bandwidth
- Differential updates achieving 90%+ size reduction for typical version increments
- Responsive mirror selection and fallback under 1 second

### Integration Points
- Standard package repository format compatibility
- Continuous integration system hooks
- Package signing infrastructure integration
- Content delivery network (CDN) interface options
- Build system integrations for automatic distribution

### Key Constraints
- Must support users behind firewalls and restrictive networks
- Must operate without requiring root/administrator privileges
- Minimal dependency requirements for bootstrap client
- No centralized tracking or monitoring infrastructure
- Must handle unreliable and asymmetric connections

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Swarm Distribution Engine**
   - Peer discovery and management
   - Chunk tracking and request optimization
   - Parallel download coordination
   - Bandwidth utilization optimization

2. **Contribution Accounting System**
   - Upload/download ratio tracking
   - User contribution metrics
   - Priority allocation algorithms
   - Recognition mechanism for persistent seeders

3. **Integrity Assurance Framework**
   - Cryptographic hash verification
   - Signature validation system
   - Certificate and key management
   - Tamper detection and alerts

4. **Binary Differential System**
   - Efficient binary comparison algorithms
   - Patch generation and application
   - Version chain management
   - Update packaging and distribution

5. **Mirror Integration Layer**
   - Mirror server discovery and evaluation
   - Geographic proximity determination
   - Availability and performance monitoring
   - Seamless transition between sources

## Testing Requirements
### Key Functionalities to Verify
- Efficient package distribution across varied network conditions
- Effective incentivization of continued seeding
- Accurate detection of corrupted or tampered packages
- Correct generation and application of differential updates
- Seamless fallback to mirrors when P2P is unavailable

### Critical Scenarios to Test
- Distribution with varying peer availability and capabilities
- Long-term network behavior with simulated incentive system
- Integrity verification with both valid and tampered packages
- Differential updates between multiple software versions
- Mirror fallback under various P2P blocking scenarios

### Performance Benchmarks
- Download efficiency vs. direct HTTP (equal or better in most cases)
- Seeder retention rate improvement with incentives
- Verification speed for large packages
- Size reduction and bandwidth savings from differential updates
- Fallback response time under network restrictions

### Edge Cases and Error Conditions
- Extremely limited peer availability
- Network partitions during transfers
- Corrupt chunks from malicious or faulty peers
- Complex binary differences between versions
- Complete P2P blocking with slow or unreliable mirrors
- Recovery from interrupted downloads

### Required Test Coverage
- ≥90% line coverage for swarm distribution code
- 100% coverage for integrity verification components
- ≥90% coverage for incentive system
- ≥95% coverage for differential update algorithms
- ≥90% coverage for mirror integration layer

## Success Criteria
The implementation will be considered successful when:

1. Users experience faster download speeds compared to traditional distribution
2. A higher percentage of users continue seeding after completing downloads
3. Package integrity is guaranteed even when distributed across thousands of peers
4. Bandwidth requirements for updates are significantly reduced through differential updates
5. Software remains accessible to all users regardless of network restrictions
6. All five key requirements are fully implemented and testable via pytest
7. The system significantly reduces primary distribution infrastructure costs
8. Software projects report wider and more reliable distribution

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.