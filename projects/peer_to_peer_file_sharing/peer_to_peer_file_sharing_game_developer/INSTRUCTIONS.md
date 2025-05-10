# Game Asset Distribution Network

## Overview
A specialized peer-to-peer file sharing system optimized for distributed game development teams, enabling efficient sharing of large asset files, version tracking, and collaborative workflows without requiring expensive cloud storage infrastructure or centralized servers.

## Persona Description
Hiroshi creates indie games with a small, globally distributed team of collaborators. He needs to share large asset files and builds without the costs of cloud storage or the complexity of setting up centralized servers.

## Key Requirements
1. **Creative Workflow Integration**
   - Version tagging system for tracking asset iterations
   - Metadata preservation for creative assets (author, creation date, revision notes)
   - Branch and merge capabilities for parallel asset development
   - Essential for maintaining organization across multiple artists and designers working on the same game, ensuring proper asset versioning and attribution

2. **Selective Synchronization**
   - File type and directory-based filtering rules
   - Size-based policies for automatic or manual synchronization
   - Partial sync options for large asset packages
   - Critical for optimizing storage and bandwidth by allowing team members to download only the assets relevant to their specific role (e.g., 3D models, textures, audio)

3. **Bandwidth Scheduling**
   - Time-based transfer scheduling for non-urgent large files
   - Configurable bandwidth limits during working hours
   - Priority levels for critical vs. non-critical assets
   - Necessary for preventing large asset transfers from disrupting other work activities, especially for team members with limited internet bandwidth

4. **Preview Generation**
   - Automated thumbnail and preview creation for common game asset formats
   - Low-resolution variants of 3D models, textures, and audio
   - Streaming preview capabilities for immediate assessment
   - Vital for allowing team members to quickly evaluate assets before committing to downloading large files, improving team efficiency

5. **Build Distribution**
   - Specialized handling for packaged game builds
   - Integrity verification ensuring consistent testing environment
   - Delta updates for iterative build distribution
   - Critical for ensuring all team members can test identical versions of the game, with efficient updates that only transfer changed components

## Technical Requirements
### Testability Requirements
- All components must have comprehensive unit tests
- Asset workflow operations must be verifiable through automated testing
- Preview generation must be testable with standard asset formats
- Build integrity verification must have 100% test coverage
- File synchronization logic must be thoroughly tested for various scenarios

### Performance Expectations
- Support for assets up to 10GB in size
- Efficient handling of game projects with 100,000+ files
- Preview generation with minimal processing overhead
- Bandwidth throttling with 95%+ accuracy
- Delta compression achieving at least 90% size reduction for typical iterative changes

### Integration Points
- Common game asset format support (.fbx, .blend, .psd, .wav, etc.)
- Version control system compatibility (Git LFS-like functionality)
- Game engine project structure awareness
- External preview tools integration options
- Build system hooks for automatic distribution

### Key Constraints
- Must operate without centralized servers
- Preview generation must work with open-source tools only
- All operations must be scriptable for automation
- No cloud dependencies for core functionality
- Maximum memory usage appropriate for development machines

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Asset Version Control**
   - Version tracking and history maintenance
   - Metadata storage and indexing
   - Branch and merge operations
   - Conflict detection and resolution

2. **Selective Sync Engine**
   - Rule-based file filtering system
   - Partial download capabilities
   - Resumable transfer support
   - Sync state tracking across peers

3. **Transfer Scheduler**
   - Bandwidth monitoring and allocation
   - Time-based scheduling system
   - Priority queue management
   - Background transfer service

4. **Preview Subsystem**
   - Format-specific preview generators
   - Metadata extraction from common asset types
   - Caching and storage optimization
   - Progressive loading support

5. **Build Management**
   - Package integrity verification
   - Delta detection and compression
   - Build metadata management
   - Distribution tracking

## Testing Requirements
### Key Functionalities to Verify
- Accurate asset version tracking across distributed team
- Correct application of selective sync rules
- Effective bandwidth control during scheduled periods
- Quality of generated previews for different asset types
- Integrity of distributed builds after transfer

### Critical Scenarios to Test
- Concurrent edits to the same asset by multiple team members
- Selective synchronization with complex rule combinations
- Bandwidth limiting during active development hours
- Preview generation for all supported asset formats
- Build distribution with subsequent delta updates

### Performance Benchmarks
- Version history query speed for projects with 1000+ revisions
- Sync rule evaluation time for large project directories
- Bandwidth adherence within 5% of configured limits
- Preview generation time for standard asset sizes
- Delta compression ratio for typical build iterations

### Edge Cases and Error Conditions
- Recovery from interrupted transfers during sync
- Handling of corrupt or non-standard asset files
- Conflict resolution for incompatible concurrent changes
- Behavior when preview generation fails
- Recovery from partial or corrupted build distribution
- Network partitions between team members

### Required Test Coverage
- ≥90% line coverage for core version control mechanisms
- 100% coverage of build integrity verification
- ≥85% coverage for selective sync components
- ≥90% coverage for preview generation system
- ≥90% coverage for bandwidth management

## Success Criteria
The implementation will be considered successful when:

1. Game development team can maintain consistent asset versions across distributed members
2. Team members can efficiently sync only the assets relevant to their work
3. Large file transfers don't disrupt active development work
4. Team members can quickly evaluate assets without downloading complete files
5. All team members can test identical builds with efficient distribution
6. All five key requirements are fully implemented and testable via pytest
7. The system significantly reduces bandwidth and storage costs compared to cloud alternatives
8. Team productivity increases due to improved asset management capabilities

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.