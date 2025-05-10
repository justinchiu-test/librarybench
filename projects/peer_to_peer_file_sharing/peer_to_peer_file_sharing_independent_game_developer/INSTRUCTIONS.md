# GameAssetShare - P2P Asset Distribution for Distributed Game Development Teams

## Overview
GameAssetShare is a specialized peer-to-peer file sharing system designed for independent game development teams working collaboratively across different locations. It provides efficient management and distribution of large game assets, builds, and resource files with version tracking, selective synchronization, and bandwidth optimization features specifically tailored to game development workflows.

## Persona Description
Hiroshi creates indie games with a small, globally distributed team of collaborators. He needs to share large asset files and builds without the costs of cloud storage or the complexity of setting up centralized servers.

## Key Requirements
1. **Creative Workflow Integration with Version Tagging**
   - Asset management system with iterative version tracking for different asset iterations
   - Critical for Hiroshi's team to maintain clear chronology of asset evolution, allowing team members to reference specific versions of assets during development and preventing confusion when multiple iterations exist
   - Must include metadata tagging, version history, and the ability to retrieve specific historical versions of any shared asset

2. **Selective Synchronization by File Type**
   - Filtering system to share only relevant game resources based on developer roles and needs
   - Essential because Hiroshi's team includes specialists (artists, sound designers, programmers) who need different asset subsets - artists don't need code files, programmers don't need raw 3D models, etc.
   - Implementation should support complex filtering rules based on file extensions, directory structures, asset types, and custom tags

3. **Bandwidth Scheduling for Large Transfers**
   - Configurable transfer timing to optimize network usage during off-hours
   - Important for Hiroshi's globally distributed team spanning multiple time zones, allowing large asset transfers (textures, models, audio) to occur during non-working hours to avoid disrupting active development
   - Requires scheduling engine, transfer queuing, bandwidth throttling, and automatic prioritization logic

4. **Asset Preview Generation**
   - Lightweight preview creation for quick assessment before full download
   - Vital for Hiroshi's team to evaluate assets without downloading large files first, saving significant time and bandwidth when team members need to determine if they require the full asset
   - Must support multiple asset types (3D models, textures, audio, etc.) with appropriate preview generation for each

5. **Build Distribution with Integrity Verification**
   - Secure sharing of game builds with checksum validation
   - Critical to ensure all team members test identical versions of the game build, preventing inconsistent testing results and "works on my machine" problems that arise from corrupted or incomplete transfers
   - Should include build metadata, dependency tracking, and cryptographic verification of transferred files

## Technical Requirements
- **Testability Requirements**
  - Simulation of large file transfers with varied network conditions
  - Mocked game asset files of various types (textures, models, audio)
  - Validation suite for verifying asset integrity post-transfer
  - Test harnesses for scheduled transfer operations
  - Automated verification of preview generation accuracy

- **Performance Expectations**
  - Support for individual files up to 10GB (high-resolution textures, audio files, etc.)
  - Aggregate project sizes up to 100GB
  - Transfer resumption with near-zero redundancy after interruption
  - Preview generation under 5 seconds for common asset types
  - Network utilization optimized for maximum throughput during scheduled windows

- **Integration Points**
  - Common game asset formats (FBX, OBJ, PNG, WAV, etc.)
  - Version control system compatibility (Git-LFS style approach)
  - Game engine asset pipelines (Unity, Unreal, Godot)
  - Common compression formats used in game development
  - Standard metadata formats for game assets

- **Key Constraints**
  - Must operate without dedicated server infrastructure
  - Must handle team members in different time zones efficiently
  - Must work across varied internet connection qualities
  - Must minimize impact on active development work
  - Must integrate with existing game development workflows

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
GameAssetShare must provide a complete peer-to-peer solution for game asset sharing with these core components:

1. A robust P2P file transfer system optimized for large binary files common in game development
2. An asset versioning system that tracks iterations and maintains version history
3. A flexible filtering and synchronization engine for selective asset distribution
4. A preview generation system supporting common game development file formats
5. A scheduling and bandwidth management system for optimizing transfer timing
6. A build distribution system with integrity verification and dependency tracking
7. A metadata management system for organizing and categorizing game assets
8. An authentication and access control mechanism for team collaboration

The system should provide well-defined Python APIs that can be integrated into game development workflows and toolchains, with clear programmatic access to all key features.

## Testing Requirements
The implementation must include comprehensive test suites verifying:

- **Key Functionalities**
  - Validation of correct version tracking and retrieval
  - Verification of filtering rules for selective synchronization
  - Confirmation of scheduled transfers executing as configured
  - Validation of preview accuracy compared to original assets
  - Verification of build integrity after distribution

- **Critical User Scenarios**
  - An artist uploading new texture assets that are selectively synchronized to team members
  - A developer scheduling large asset transfers during overnight hours
  - Team members examining previews before deciding to download full assets
  - The lead developer distributing a new build for testing with integrity verification
  - Multiple team members collaborating on iterative asset development across time zones

- **Performance Benchmarks**
  - Successful transfer resumption after interruption with >99% efficiency
  - Preview generation performance within specified time limits for various asset types
  - Bandwidth utilization at least 90% of theoretical maximum during transfer windows
  - Version tracking with minimal metadata overhead (<5% of asset size)
  - Resource utilization within acceptable limits during background operations

- **Edge Cases and Error Conditions**
  - Recovery from incomplete or corrupted transfers
  - Handling of conflicts when multiple team members update the same asset
  - Graceful operation with team members on severely limited connections
  - Proper handling of unusual or malformed game asset files
  - Recovery from unexpected peer disconnections during critical operations

- **Required Test Coverage Metrics**
  - Minimum 90% statement coverage for all modules
  - Comprehensive tests for each game asset type and operation
  - Performance tests validating operation within specified constraints
  - Stress tests with realistic game development asset sets
  - Coverage of all error recovery paths

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. Game assets can be shared with complete version history and tagging
2. Team members can selectively synchronize only the assets relevant to their role
3. Large transfers can be scheduled to minimize disruption to active work
4. Preview generation allows for quick assessment before full asset download
5. Game builds distribute with guaranteed integrity verification
6. The system operates efficiently across different time zones and connection qualities
7. The solution integrates smoothly with existing game development workflows
8. All operations maintain data integrity and version consistency

To set up your development environment, follow these steps:

1. Use `uv init --lib` to set up the project and create your `pyproject.toml`
2. Install dependencies with `uv sync`
3. Run your code with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format your code with `uv run ruff format`
6. Lint your code with `uv run ruff check .`
7. Type check with `uv run pyright`