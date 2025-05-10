# Educational Course Site Generator

A specialized static site generator for creating structured, interactive educational content with built-in learning assessment capabilities.

## Overview

This project is a Python library for transforming educational content into comprehensive, organized course websites. It focuses on hierarchical organization, interactive learning elements, progress tracking, and code-focused learning experiences particularly suited for computer science education.

## Persona Description

Professor Wong develops instructional materials for computer science courses and needs to publish course syllabi, lecture notes, assignments, and code examples in an organized, searchable format for students.

## Key Requirements

1. **Hierarchical Content Organization**: Implement a system for organizing educational content into nested structures (courses containing modules containing lessons). This hierarchical organization is essential for Professor Wong to structure complex computer science curricula in a logical progression, allowing students to navigate naturally from foundational concepts to advanced topics.

2. **Interactive Quiz Generation**: Create a system that transforms structured quiz data into interactive learning assessments directly within the static site. These embedded assessments allow Professor Wong's students to verify their understanding throughout the learning process, with automatic feedback that reinforces key concepts without requiring external quiz systems.

3. **Progress Tracking System**: Implement client-side progress tracking allowing students to mark completed sections and visualize their journey through course materials. This helps students monitor their advancement through Professor Wong's curricula, providing motivation through visible progress indicators and helping them resume study from where they previously left off.

4. **Code Playground Integration**: Embed runnable programming environments within lesson content for interactive coding exercises. As a computer science professor, this allows Professor Wong to move beyond passive code examples to interactive experiences where students can experiment with concepts, modify code, and see immediate results without switching to a separate development environment.

5. **Downloadable Resource Packaging**: Generate downloadable bundles of course materials (lecture notes, code examples, assignments) for offline access. Many of Professor Wong's students work in environments with unreliable internet access, so providing downloadable, cohesive packages of course materials ensures they can continue learning regardless of connectivity challenges.

## Technical Requirements

- **Testability Requirements**:
  - Content organization structures must be verifiable through directory organization and navigation
  - Quiz generation and scoring logic must be deterministically testable
  - Progress tracking must persist correctly between sessions with testable state management
  - Code playground functionality must execute with predictable inputs and outputs
  - Resource bundling must create valid packages with verified content integrity

- **Performance Expectations**:
  - Full course site generation must complete in under 1 minute for courses with up to 50 lessons
  - Interactive quizzes must evaluate responses in under 100ms
  - Code playground execution should provide results within 2 seconds
  - Resource packages must be optimized to minimize download size (max 10MB per module)

- **Integration Points**:
  - Local storage for progress tracking
  - Code execution environments (like Pyodide for Python in browser)
  - Downloadable resource packaging formats (ZIP, PDF)
  - Integrated search systems for course content
  - Quiz data import/export formats

- **Key Constraints**:
  - All functionality must work without server-side processing
  - Code execution must be secure and sandboxed in the browser
  - Progress tracking must respect user privacy and work offline
  - Content must be accessible according to WCAG 2.1 AA standards
  - All interactive elements must have non-interactive fallbacks

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Course Structure Management**:
   - Process hierarchical content from structured directories
   - Generate consistent navigation between course elements
   - Create appropriate breadcrumbs and progress indicators
   - Support prerequisites and suggested learning paths

2. **Interactive Assessment System**:
   - Transform structured quiz data into interactive elements
   - Support multiple question types (multiple choice, code completion, etc.)
   - Provide immediate feedback based on student responses
   - Track and report quiz performance for self-assessment

3. **Learning Progress Tracker**:
   - Implement client-side storage of completion status
   - Create visual progress indicators for course components
   - Support resuming study from previous position
   - Generate progress reports and completion certificates

4. **Code Execution Environment**:
   - Embed runnable code blocks within lesson content
   - Support syntax highlighting and error reporting
   - Allow students to modify examples and see results
   - Provide starter code and solution comparisons

5. **Resource Packaging System**:
   - Bundle course materials in offline-accessible formats
   - Generate printable versions of content when appropriate
   - Ensure consistent formatting across download formats
   - Optimize media and code examples for offline use

## Testing Requirements

- **Key Functionalities to Verify**:
  - Correct generation of hierarchical course structure and navigation
  - Functional quiz system with accurate scoring and feedback
  - Persistent progress tracking across browser sessions
  - Proper execution of code examples in the embedded playground
  - Complete and correctly formatted downloadable resource packages

- **Critical User Scenarios**:
  - Student navigates through a course following the designed learning path
  - Student completes quizzes and receives appropriate feedback
  - Student modifies and runs code examples to experiment with concepts
  - Student downloads course materials for offline study
  - Student returns to the course and continues from their previous position

- **Performance Benchmarks**:
  - Site generation time for courses of varying complexity
  - Quiz response time for different question types
  - Code execution time for typical programming exercises
  - Download size and generation time for resource packages

- **Edge Cases and Error Conditions**:
  - Handling of complex nested course structures
  - Recovery from invalid student code in playgrounds
  - Management of quiz questions with multiple correct answers
  - Fallback for browsers with disabled JavaScript or localStorage
  - Handling of very large courses with many resources

- **Required Test Coverage**:
  - 90% code coverage for core library functions
  - 100% coverage for quiz evaluation logic
  - 95% coverage for progress tracking system
  - 95% coverage for code playground integration
  - 90% coverage for resource packaging system

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Course content is properly organized in a hierarchical structure with intuitive navigation
2. Interactive quizzes provide immediate feedback and reinforce learning objectives
3. Students can track their progress through course materials across sessions
4. Code examples are runnable within the page with proper execution and output display
5. Course materials can be downloaded as complete packages for offline use
6. All interactive elements function correctly without server-side components
7. All tests pass with at least 90% code coverage
8. The course site loads and functions on standard browsers without errors

To set up your development environment:
```
uv venv
source .venv/bin/activate
```