# StoryWeaver - A Fiction Writer's Knowledge Management System

## Overview
StoryWeaver is a specialized knowledge management system designed specifically for fiction writers who need to track complex worldbuilding elements, character relationships, plot arcs, and narrative timelines across multiple volumes or stories. The system enables writers to maintain consistency in their fictional universe while developing intricate storylines and character development arcs.

## Persona Description
Amara is writing a fantasy novel series with complex worldbuilding, character relationships, and plot arcs spanning multiple volumes. She needs to maintain consistency across her fictional universe while developing intricate storylines.

## Key Requirements
1. **Character relationship mapping** - Create a comprehensive system for tracking character interactions, conflicts, alliances, and development arcs throughout a series. This is crucial for writers like Amara who need to maintain consistent character development across multiple books while ensuring that relationship dynamics evolve coherently.

2. **Worldbuilding consistency checking** - Implement mechanisms to detect and highlight contradictions in fictional elements such as magic systems, cultural practices, geography, or historical events. This feature is essential to help writers avoid continuity errors that break immersion for readers and undermine the integrity of complex fictional worlds.

3. **Narrative timeline visualization** - Develop functionality to track both the in-world chronology (when events happen in the fictional timeline) and narrative presentation (when events are revealed to the reader). This dual timeline approach is vital for writers who employ non-linear storytelling techniques while needing to keep track of the actual sequence of fictional events.

4. **Plot thread tracking** - Create a system to monitor introduced narrative elements, ensuring all plot threads reach appropriate resolution. This helps writers avoid the common issue of "dangling plotlines" where story elements are introduced but never resolved, which is particularly challenging when managing complex narratives across multiple volumes.

5. **Inspiration collection** - Implement a method to link real-world research, images, concepts, and references to their fictional interpretations or applications. This feature allows writers to maintain connections between their inspirational source material and how it manifests in their creative work, enhancing the depth and authenticity of their worldbuilding.

## Technical Requirements
- **Testability Requirements**:
  - All functionality must be implemented in well-defined modules that can be tested independently
  - Character relationship mapping must support serialization/deserialization for test verification
  - Timeline visualization logic must be testable without requiring actual visualization rendering
  - Worldbuilding consistency checks must be implemented as testable rule-based systems
  - Plot thread status tracking must support programmatic verification of completion status

- **Performance Expectations**:
  - System must efficiently handle projects with 100+ characters and 1000+ notes
  - Consistency checking algorithms should complete in under 5 seconds for typical worldbuilding datasets
  - Relationship graph operations should scale efficiently with the number of characters and connections
  - Search operations across the entire knowledge base should return results in under 1 second
  - Background indexing of content should not impact the performance of other operations

- **Integration Points**:
  - Plain text (Markdown) notes as the primary storage format for maximum portability
  - Support for embedding structured metadata in notes using YAML front matter
  - Export capabilities for character relationships and timelines to common formats (JSON, CSV)
  - Import functionality for external research materials with automatic linking to relevant fiction elements
  - Extensible plugin system for custom relationship types and consistency rules

- **Key Constraints**:
  - All data must be stored locally in text-based formats without requiring cloud services
  - No user interface components - all functionality exposed through APIs only
  - Implementation must be cross-platform compatible
  - System must operate efficiently with limited memory usage
  - Support for git-based version control for the entire knowledge base

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
StoryWeaver needs to implement these core capabilities:

1. **Knowledge Graph System**: A flexible graph database for representing entities (characters, locations, items) and their relationships, supporting:
   - Custom relationship types with properties (strength, type, directionality)
   - Temporal aspects of relationships (changes over time)
   - Efficient querying for relationship patterns and paths between entities

2. **Bidirectional Linking Engine**: A system for connecting notes, characters, plot elements, and worldbuilding details with:
   - Explicit linking using a wiki-like syntax
   - Automatic recognition and suggestion of implicit connections
   - Visualization of connection networks using ASCII/text graphs

3. **Consistency Validation Framework**: A rule-based system to:
   - Define logical constraints for worldbuilding elements
   - Check for violations of established rules or contradictions
   - Flag timeline inconsistencies or character behavior discrepancies
   - Generate reports of potential issues for review

4. **Timeline Management**: A specialized system for managing both chronological and narrative time:
   - Support for multiple calendar systems (for fantasy worlds)
   - Parallel timeline tracking for different characters/locations
   - Visualization of timeline branches and convergences
   - Detection of causality violations

5. **Research Integration**: A system to:
   - Import and tag reference materials
   - Connect research to fictional elements
   - Track inspiration sources for worldbuilding elements
   - Organize reference materials by relevance to story components

## Testing Requirements
The implementation must include comprehensive tests that verify all aspects of the system:

- **Key Functionalities to Verify**:
  - Character relationship graph correctly tracks complex relationships and their changes over time
  - Worldbuilding consistency checker accurately identifies contradictions in defined rules
  - Timeline management handles both in-world and narrative time correctly
  - Plot thread tracking accurately identifies unresolved narrative elements
  - Research integration properly links source materials to fictional interpretations

- **Critical User Scenarios**:
  - Adding new characters and defining their relationships with existing characters
  - Updating worldbuilding rules and checking existing content for consistency
  - Recording events on both in-world and narrative timelines with automatic consistency verification
  - Tracking the introduction and resolution of plot threads across multiple documents
  - Importing research materials and linking them to relevant fictional elements

- **Performance Benchmarks**:
  - Relationship graph operations must complete in under 100ms for graphs with up to 200 nodes
  - Consistency checking must process 10,000 worldbuilding facts in under 5 seconds
  - Full-text search across 1GB of notes must return results in under 1 second
  - Timeline operations must support at least 1,000 events without performance degradation
  - System startup time must not exceed 2 seconds regardless of knowledge base size

- **Edge Cases and Error Conditions**:
  - Handling circular relationship dependencies
  - Managing conflicting worldbuilding rules
  - Dealing with timeline paradoxes or causality issues
  - Recovering from corrupted knowledge base files
  - Handling extremely large character casts or complex relationship networks

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for consistency checking algorithms
  - 100% coverage for timeline logic
  - 100% coverage for plot thread status tracking
  - 95% branch coverage for character relationship graph operations

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
The implementation will be considered successful if it meets the following criteria:

1. Writers can create, track, and visualize complex character relationships with temporal dimensions
2. The system can detect and report inconsistencies in worldbuilding elements
3. Both in-world chronology and narrative presentation timelines can be managed and visualized
4. The system tracks plot threads from introduction to resolution with status reporting
5. Research materials can be linked to their fictional interpretations with bi-directional navigation

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment:
1. Use `uv venv` to create a virtual environment
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL REMINDER: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```