# Educational Course Site Generator

A specialized static site generator optimized for creating and organizing instructional materials in a structured, interactive format for educational purposes.

## Overview

This project provides an education-focused static site generator that enables instructors to create, organize, and publish course materials including syllabi, lecture notes, assignments, and code examples in a structured, searchable format that enhances the learning experience for students.

## Persona Description

Professor Wong develops instructional materials for computer science courses and needs to publish course syllabi, lecture notes, assignments, and code examples in an organized, searchable format for students.

## Key Requirements

1. **Hierarchical Content Organization**: Support nested structure with lessons within modules within courses.
   - Professor Wong teaches multiple courses with complex lesson structures, requiring a system that can organize content in a meaningful hierarchy that reflects the pedagogical structure of his courses.
   - This feature must support flexible nesting of content with automatic navigation generation and proper relationships between nested elements.

2. **Quiz and Exercise Generation**: Create interactive learning elements from structured content.
   - To reinforce learning concepts, Professor Wong needs to include frequent quizzes and exercises in his course materials that students can use for self-assessment.
   - The system must transform structured quiz/exercise definitions into interactive elements that provide immediate feedback without requiring server-side processing.

3. **Progress Tracking**: Allow students to mark completed sections and track their learning journey.
   - To help students manage their learning process, the site needs to track which sections they've completed and show their progress through the course materials.
   - This feature must persist progress information in the browser and provide visual indicators of completion status throughout the course.

4. **Code Playground Integration**: Embed runnable programming exercises within content.
   - As a computer science professor, practical coding exercises are essential to Professor Wong's teaching, requiring embedded environments where students can write, run, and experiment with code examples.
   - These playgrounds must support syntax highlighting, execution of code, and feedback on execution results.

5. **Downloadable Resource Packaging**: Support offline access to course materials.
   - Students often need to access materials in environments without internet connectivity, so Professor Wong needs to provide downloadable packages of course content.
   - The system should generate properly formatted offline packages (PDFs, archives) of course materials that maintain organization and include necessary resources.

## Technical Requirements

### Testability Requirements
- Content hierarchy generation must be testable with sample course structures
- Quiz/exercise functionality must verify correct behavior for different question types
- Progress tracking must validate state persistence and proper status updates
- Code playground functionality must verify code execution and result handling
- Resource packaging must validate completeness and formatting of downloadable content

### Performance Expectations
- Full course site generation should complete in under 30 seconds for a typical course (50 lessons)
- Quiz evaluation should provide immediate feedback (under 100ms)
- Code playground execution should return results in under 3 seconds for simple exercises
- Resource package generation should process a complete course in under 60 seconds

### Integration Points
- Code execution environments for different programming languages
- PDF generation libraries for downloadable resources
- Local storage mechanisms for progress tracking
- Markdown and code parsing libraries
- Archive creation utilities for downloadable packages

### Key Constraints
- Must operate without server-side processing for quiz evaluation and progress tracking
- Must generate completely static output deployable to any web hosting service
- Must support client-side only code execution for programming exercises
- Must be accessible following WCAG 2.1 AA standards for educational institutions
- Must generate offline-capable resources that maintain content relationships

## Core Functionality

The system should implement a comprehensive platform for educational content management and delivery:

1. **Course Structure Engine**
   - Define and parse hierarchical content relationships
   - Generate navigation structures reflecting course organization
   - Create proper linking between related content elements
   - Implement cross-referencing and prerequisite relationships

2. **Interactive Assessment System**
   - Parse structured quiz and exercise definitions
   - Generate client-side evaluation logic for various question types
   - Provide immediate feedback and scoring
   - Support progress tracking based on assessment completion

3. **Code Exercise Environment**
   - Implement in-browser code execution for supported languages
   - Provide syntax highlighting and basic editor features
   - Generate validation tests for programming exercises
   - Support example solutions and hints

4. **Progress Management System**
   - Store completion status for course elements
   - Generate progress visualizations (progress bars, checklists)
   - Implement persistence across sessions
   - Support resetting or transferring progress data

5. **Resource Packaging**
   - Generate PDF versions of course materials
   - Create downloadable archives with complete content
   - Maintain content relationships in offline formats
   - Optimize media resources for offline use

## Testing Requirements

### Key Functionalities to Verify
- Hierarchical course structure generation and navigation
- Interactive quiz functionality with different question types
- Progress tracking persistence and visualization
- Code playground execution and feedback
- Downloadable resource generation and completeness

### Critical User Scenarios
- Creating a multi-module course with nested lessons and topics
- Developing quizzes with various question types and automatic evaluation
- Tracking progress through a course across multiple sessions
- Creating and solving programming exercises in the code playground
- Generating and using offline resource packages

### Performance Benchmarks
- Process a complete 50-lesson course with quizzes in under 30 seconds
- Generate PDF versions of all course materials in under 60 seconds
- Execute code examples with results in under 3 seconds
- Quiz evaluation with feedback in under 100ms
- Progress updates persisted in under 50ms

### Edge Cases and Error Conditions
- Handling deeply nested or circular content relationships
- Managing browser storage limitations for progress tracking
- Graceful degradation for unsupported code execution features
- Error handling for code execution timeout or errors
- Recovery from interrupted download package generation

### Required Test Coverage Metrics
- Minimum 90% line coverage for core processing components
- 100% coverage for critical features (quiz evaluation, progress tracking)
- Integration tests for the complete content generation pipeline
- Performance tests for time-sensitive operations (code execution, quiz evaluation)

## Success Criteria

The implementation will be considered successful if it:

1. Creates properly nested course structures with intuitive navigation for at least 3 levels of hierarchy
2. Generates interactive quizzes that provide immediate feedback for at least 5 different question types
3. Tracks and persists student progress across course modules with visual indicators
4. Provides functioning code playgrounds for at least 3 programming languages commonly used in computer science education
5. Generates complete, well-formatted downloadable packages for offline access
6. Processes a typical computer science course (50 lessons, 20 quizzes, 15 code examples) in under 30 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.