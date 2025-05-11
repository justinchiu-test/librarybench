# Educational Course Site Generator

A specialized static site generator designed for educators to create structured course websites with interactive learning elements, progress tracking, and downloadable resources.

## Overview

This project implements a Python library for generating comprehensive educational websites that organize course materials in a hierarchical structure with interactive learning elements. It focuses on the needs of educators who want to provide students with well-organized, searchable, and interactive learning resources.

## Persona Description

Professor Wong develops instructional materials for computer science courses and needs to publish course syllabi, lecture notes, assignments, and code examples in an organized, searchable format for students.

## Key Requirements

1. **Hierarchical Content Organization**: Create a system for structuring educational content in nested hierarchies (courses containing modules containing lessons and individual resources).
   - Critical for Professor Wong because computer science courses have natural hierarchical structures, and students need clear navigation between related concepts and progressive learning paths.
   - Must maintain relationships between content at different levels while preserving contextual navigation.

2. **Quiz and Exercise Generation**: Convert structured quiz and exercise data into interactive learning elements that can be embedded within course content.
   - Essential for Professor Wong because interactive self-assessment helps students gauge their understanding of material and reinforces learning concepts.
   - Should support multiple question types and provide immediate feedback on student responses.

3. **Progress Tracking**: Implement client-side progress tracking that allows students to mark completed sections and visualize their learning journey.
   - Important for Professor Wong because it helps students maintain momentum through the course and easily identify what material they've covered and what remains.
   - Must work without server-side state management and persist progress between sessions.

4. **Code Playground Integration**: Create embeddable, interactive programming environments within course content where students can experiment with code examples.
   - Valuable for Professor Wong because computer science education requires hands-on coding practice, and integrated examples allow students to experiment without switching contexts.
   - Should support syntax highlighting, execution, and example code modification.

5. **Downloadable Resource Packaging**: Generate downloadable bundles of course materials for offline access, properly organized to mirror the online structure.
   - Critical for Professor Wong because students may need to access materials in environments without reliable internet connections or want to preserve materials for future reference.
   - Must include proper indexing and organization that maintains relationships between resources.

## Technical Requirements

### Testability Requirements
- All components must be individually testable through well-defined interfaces
- Implement fixtures for testing with sample course content and hierarchies
- Support snapshot testing for generated HTML and interactive elements
- Test suites must validate the structure and functionality of interactive components
- Support for simulating user interactions with progress tracking and quizzes

### Performance Expectations
- Generate a complete course site with 200+ content pages in under 60 seconds
- Quiz generation should process 100+ questions in under 5 seconds
- Progress tracking operations should be near-instantaneous for user interactions
- Code playground initialization should take under 1 second
- Resource package generation should process 50MB of content in under 30 seconds

### Integration Points
- Code execution environments for interactive examples
- Quiz data formats and assessment algorithms
- Local storage or other client-side persistence mechanisms
- Archive formats for downloadable packages
- Content delivery networks for optimized resource delivery

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must generate completely static HTML that works without server-side processing
- Interactive elements must function using only client-side technologies
- Progress tracking must preserve privacy and work offline
- Output must be fully accessible and meet educational standards
- Content must be easily updatable by non-technical educators

## Core Functionality

The Educational Course Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **Course Structure and Navigation**
   - Process hierarchical course structures from configuration files
   - Generate consistent navigation that reflects content relationships
   - Create breadcrumbs and contextual navigation elements
   - Support for prerequisite relationships and suggested learning paths
   - Implement search functionality across course materials

2. **Interactive Assessment Engine**
   - Process quiz and exercise data from structured formats
   - Generate interactive quiz elements with various question types
   - Implement scoring and feedback mechanisms
   - Support for hints and progressive disclosure
   - Generate printable assessment versions for offline use

3. **Progress Tracking System**
   - Create client-side progress tracking with local storage
   - Implement completion marking for course elements
   - Generate progress visualization (progress bars, completion checkmarks)
   - Support for exporting and importing progress data
   - Implement achievement and milestone tracking

4. **Code Execution Environment**
   - Generate embeddable code playgrounds for various languages
   - Support for preset examples with reset capability
   - Implement syntax highlighting and error reporting
   - Create sandboxed execution environments for student experiments
   - Support for saving and sharing code snippets

5. **Resource Packaging System**
   - Implement bundling of course resources in downloadable formats
   - Generate proper indexing and navigation for offline use
   - Support for selective packaging of course sections
   - Create self-contained packages with necessary assets
   - Implement resource updates and differential downloads

## Testing Requirements

### Key Functionalities to Verify

1. **Course Structure and Navigation**
   - Test course hierarchy generation from various input formats
   - Verify proper nesting and relationships between content elements
   - Test navigation generation and contextual linking
   - Confirm search index creation and query functionality
   - Verify breadcrumb and path generation

2. **Interactive Assessment Components**
   - Test quiz generation with various question types
   - Verify scoring and feedback mechanisms
   - Test hint systems and progressive disclosure
   - Confirm accessibility of quiz components
   - Verify offline assessment functionality

3. **Progress Tracking**
   - Test client-side storage and retrieval of progress data
   - Verify progress visualization accuracy
   - Test persistence between sessions
   - Confirm proper handling of course updates with existing progress
   - Verify export and import functionality

4. **Code Playground Implementation**
   - Test embedded code environments for various languages
   - Verify syntax highlighting and code execution
   - Test error handling and reporting
   - Confirm preservation of student modifications
   - Verify accessibility of coding environments

5. **Downloadable Resources**
   - Test package generation with various content types
   - Verify preservation of structure and relationships
   - Test differential packaging for updates
   - Confirm proper indexing and navigation in packages
   - Verify integrity of packaged resources

### Critical User Scenarios

1. Navigating through a hierarchical course structure from overview to specific lessons
2. Completing interactive quizzes and receiving appropriate feedback
3. Tracking progress through a course and resuming from the last completed section
4. Experimenting with code examples and seeing results in real-time
5. Downloading course materials for offline use and navigating them effectively

### Performance Benchmarks

- Full course site with 200+ pages should build in under 60 seconds
- Interactive elements should initialize in under 500ms
- Search queries should return results in under 200ms
- Resource packages should generate at a rate of at least 2MB/second
- Memory usage should not exceed 1GB for typical course sizes

### Edge Cases and Error Conditions

- Test handling of circular references in course prerequisites
- Verify behavior with extremely large code samples
- Test progress tracking with incomplete or corrupted local storage
- Verify graceful degradation when JavaScript is disabled
- Test with unusual content structures and deeply nested hierarchies
- Validate behavior with special characters and multilingual content

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for interactive element generation
- 100% coverage for progress tracking mechanisms
- Integration tests for the entire build pipeline
- Performance tests for both small and large course sites

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

The Educational Course Site Generator will be considered successful if it:

1. Correctly organizes course content in intuitive hierarchical structures with clear navigation
2. Properly generates interactive quizzes and exercises with appropriate feedback mechanisms
3. Implements reliable client-side progress tracking that persists between sessions
4. Creates functional code playgrounds that allow experimentation with programming concepts
5. Generates well-organized downloadable resource packages for offline use
6. Builds course sites efficiently with proper search and navigation features
7. Produces accessible, standards-compliant HTML output
8. Creates all necessary course structure elements and learning paths

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up your development environment:

1. Create a virtual environment using UV:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: When testing, you must generate the pytest_results.json file:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

This file is MANDATORY proof that all tests pass and must be included with your implementation.