# GameAssetShare - P2P Collaboration for Indie Game Development

## Overview
GameAssetShare is a specialized peer-to-peer file sharing library designed for indie game development teams to share large asset files and builds without relying on expensive cloud storage solutions. It features workflow integration, selective synchronization, bandwidth scheduling, preview generation, and integrity verification tailored for game development needs.

## Persona Description
Hiroshi creates indie games with a small, globally distributed team of collaborators. He needs to share large asset files and builds without the costs of cloud storage or the complexity of setting up centralized servers.

## Key Requirements

1. **Creative Workflow Integration**
   - Implement a version tagging system for tracking different iterations of game assets
   - Essential for Hiroshi's team to maintain a clear history of asset evolution
   - Must support annotation and metadata for each version to document design decisions
   - Should integrate with common asset creation workflows to minimize disruption

2. **Selective Synchronization**
   - Create a sophisticated filtering system to share only relevant game resources by file type
   - Critical for efficiently working with large game assets where team members need different subsets
   - Must support complex inclusion/exclusion rules based on file type, path, size, and metadata
   - Should optimize transfer efficiency by avoiding unnecessary duplication of large assets

3. **Bandwidth Scheduling**
   - Develop a scheduling system for conducting large transfers during off-hours
   - Important for not disrupting the team's productivity with bandwidth-intensive transfers
   - Must support time-based scheduling with timezone awareness for the global team
   - Should include bandwidth throttling to allow work to continue during transfers

4. **Preview Generation**
   - Implement lightweight preview creation for quick assessment of assets before full download
   - Vital for team members to evaluate assets without committing to lengthy downloads
   - Must support common game asset formats (3D models, textures, audio, etc.)
   - Should generate appropriately sized previews based on asset type and receiving device capabilities

5. **Build Distribution with Integrity Verification**
   - Create a reliable system for distributing game builds with verification to ensure identical testing
   - Critical for consistent quality assurance across the distributed team
   - Must provide cryptographic verification of build integrity
   - Should include intelligent resumption of interrupted transfers for large build files

## Technical Requirements

- **Testability Requirements**
  - All components must be designed with mocks for game assets and network behavior
  - Network throttling and scheduling must be time-shiftable for testing
  - Preview generation must be testable with standard game asset formats
  - Integrity verification must be testable with deliberate corruption scenarios

- **Performance Expectations**
  - System must efficiently handle typical game assets (textures up to 4K, 3D models with 100K+ polygons)
  - Selective synchronization must filter assets within seconds even for large projects (10,000+ files)
  - Preview generation must complete within 3 seconds per asset
  - Build transfers must achieve at least 80% of available bandwidth when scheduled

- **Integration Points**
  - Common game asset formats (FBX, OBJ, PNG, WAV, etc.)
  - Standard game project structures (Unity, Unreal, Godot, etc.)
  - Version control system awareness (Git, Perforce, etc.)
  - Build systems and packaging formats

- **Key Constraints**
  - Implementation must be pure Python to ensure cross-platform compatibility
  - No dependencies on external cloud services or central servers
  - All functionality must be implemented without UI components
  - System must operate effectively over residential internet connections

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The GameAssetShare implementation should provide these core functions:

1. **Game Asset Management**
   - Asset metadata tracking and organization
   - Version history and tagging
   - Asset categorization and relationship tracking
   - Workflow state management

2. **Intelligent Synchronization**
   - Rule-based filtering and selective sync
   - Optimized binary delta transfers for iterative assets
   - Dependency awareness for complex asset relationships
   - Background synchronization with progress reporting

3. **Transfer Optimization**
   - Scheduled transfers with timezone awareness
   - Bandwidth allocation and throttling
   - Resume capability for interrupted transfers
   - Prioritization based on workflow needs

4. **Asset Preview System**
   - Format-specific preview generation
   - Thumbnail creation for visual assets
   - Sample extraction for audio assets
   - Metapreview for complex assets (e.g., 3D models)

5. **Build Management**
   - Build packaging and versioning
   - Delta updates for incremental builds
   - Integrity verification and validation
   - Build metadata and changelog tracking

## Testing Requirements

- **Key Functionalities to Verify**
  - Version tagging correctly tracks asset iterations with proper metadata
  - Selective synchronization accurately filters assets based on complex rules
  - Bandwidth scheduling properly throttles and times large transfers
  - Preview generation creates useful, lightweight previews for various asset types
  - Build distribution maintains integrity across all team members

- **Critical User Scenarios**
  - Artist uploads new texture iterations while preserving version history
  - Programmer selectively syncs only code and build files, excluding art assets
  - Team schedules large asset transfer during overnight hours to avoid disruption
  - Designer quickly previews multiple sound assets before deciding which to download
  - QA team members receive and verify identical game builds for consistent testing

- **Performance Benchmarks**
  - Metadata operations must complete within 200ms even with 10,000+ assets
  - Selective sync filtering must process at least 1,000 files per second
  - Bandwidth scheduling must achieve at least 90% utilization during scheduled periods
  - Preview generation must handle at least 20 standard game assets per minute
  - Build verification must process at least 100MB per second

- **Edge Cases and Error Handling**
  - Handling extremely large individual assets (10GB+)
  - Recovery from interrupted transfers during large build distribution
  - Managing conflicting asset versions from different team members
  - Dealing with corrupted or invalid game assets
  - Adapting to highly asymmetric internet connections

- **Test Coverage Requirements**
  - Core asset management functions must have 100% test coverage
  - Synchronization logic must be tested against diverse project structures
  - Scheduling and bandwidth management must be tested with various network conditions
  - Preview generation must be tested against all supported asset types
  - Build verification must be tested with various corruption scenarios

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

1. Game development team members can efficiently share assets with clear version tracking
2. Team members can selectively synchronize only the assets relevant to their work
3. Large transfers can be scheduled to avoid disrupting productive work hours
4. Team members can quickly preview assets before committing to full downloads
5. Game builds can be distributed with verified integrity for consistent testing
6. All operations integrate smoothly with typical indie game development workflows
7. The system performs efficiently even with large assets and globally distributed teams

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