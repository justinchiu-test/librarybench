# Interactive Programming Education Platform

A specialized documentation system that combines theoretical computer science concepts with interactive code exercises to create personalized learning paths for computer science education.

## Overview

The Interactive Programming Education Platform enables computer science professors to create comprehensive instructional materials that adapt to students' learning progress. It maps concept dependencies, provides interactive exercises with automated validation, customizes learning paths, collects performance metrics, and facilitates collaborative annotations.

## Persona Description

Dr. Williams teaches programming courses and needs to create interactive textbook materials that students can explore at their own pace. He wants to combine theoretical concepts with practical, executable examples that demonstrate principles in action.

## Key Requirements

1. **Concept Dependency Mapping** - The system must create and visualize the prerequisite relationships between programming concepts, showing which topics must be mastered before others. This is critical for Dr. Williams because understanding concept dependencies allows for structured learning progressions, helping students follow logical learning paths and preventing them from tackling advanced topics before mastering fundamentals.

2. **Interactive Code Exercises** - The tool must provide executable programming challenges with automated validation and contextual hints. As a professor, Dr. Williams needs this feature to bridge theory and practice, allowing students to immediately apply new concepts, receive instant feedback, and correct misconceptions before they become entrenched.

3. **Learning Path Customization** - The system must generate personalized learning sequences based on each student's background knowledge and progress. This is essential for Dr. Williams to accommodate diverse student backgrounds and learning paces in his courses, ensuring students neither struggle with overly advanced material nor waste time on concepts they've already mastered.

4. **Anonymous Performance Metrics** - The tool must collect and aggregate student performance data while preserving individual privacy, identifying commonly misunderstood concepts. This data helps Dr. Williams identify topics that require additional explanation or alternative teaching approaches, allowing continuous improvement of course materials based on actual learning outcomes.

5. **Collaborative Annotation** - The system must enable students to share notes, questions, and insights within the documentation while maintaining academic integrity. This feature supports peer learning and community knowledge building in Dr. Williams' courses, allowing students to benefit from each other's perspectives and questions while creating a collaborative learning environment.

## Technical Requirements

### Testability Requirements
- All components must have comprehensive unit tests with minimum 90% code coverage
- Concept mapping must be verifiable with predefined knowledge graphs
- Exercise validation must be testable with correct and incorrect submissions
- Learning path generation must be verifiable with different student profiles
- Performance metrics must be testable with simulated student interactions

### Performance Expectations
- Concept dependency visualization must generate in under 3 seconds
- Code exercise validation must provide feedback in under 1 second
- Learning path customization must compute in under 500ms
- Performance metrics must aggregate data from 500+ students in under 10 seconds
- Collaborative annotations must sync between users in near real-time (< 2 seconds)

### Integration Points
- Code execution engines for multiple programming languages
- Academic content management systems
- Learning management systems (LMS)
- Automated assessment tools
- Plagiarism detection systems

### Key Constraints
- All functionality must be implementable without UI components
- Must support at least 5 programming languages (Python, Java, C++, JavaScript, SQL)
- Must handle courses with at least 100 distinct programming concepts
- Must scale to support classes with at least 500 concurrent students
- Must maintain student privacy and comply with educational data regulations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. A concept knowledge graph engine that maps dependencies between programming topics
2. An interactive code execution environment with automated validation and feedback
3. A learning path generation system that creates personalized concept sequences
4. A performance analytics engine that identifies learning patterns while preserving privacy
5. A collaborative annotation system that enables peer learning
6. An educational content management system optimized for programming instruction
7. A code plagiarism detection system that maintains academic integrity

These components should work together to create an adaptive learning environment that combines theoretical concepts with practical coding experience, personalized to each student's needs.

## Testing Requirements

The implementation must include tests for:

### Key Functionalities Verification
- Concept dependency mapping correctly identifies prerequisite relationships
- Interactive exercises properly validate student code submissions
- Learning path customization generates appropriate sequences for different profiles
- Performance metrics accurately identify commonly misunderstood concepts
- Collaborative annotation successfully synchronizes between users

### Critical User Scenarios
- A professor creates a new programming course with concept dependencies
- A student follows a personalized learning path through course material
- A teaching assistant analyzes performance data to identify struggling concepts
- Students collaboratively discuss a complex algorithm implementation
- A professor updates course material based on performance insights

### Performance Benchmarks
- Concept visualization generates within time limits for complex knowledge graphs
- Code validation responds instantly for typical student submissions
- Learning path computation performs efficiently with diverse student profiles
- Performance analytics scale appropriately with increasing student numbers
- Annotation synchronization maintains responsiveness with concurrent users

### Edge Cases and Error Handling
- Handling cyclic dependencies in concept relationships
- Processing code submissions with syntax errors or infinite loops
- Managing students with unusual learning profiles or knowledge gaps
- Dealing with boundary cases in performance aggregation
- Handling conflicting annotations or collaborative editing conflicts

### Required Test Coverage
- Minimum 90% test coverage for all components
- 100% coverage for code validation and feedback generation
- Integration tests for all external system interfaces
- Security tests for student data privacy protection

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

1. Concept dependency mapping correctly identifies at least 95% of prerequisite relationships
2. Interactive exercises provide accurate validation and helpful feedback for student submissions
3. Learning path customization generates appropriate sequences for at least 5 different student profiles
4. Performance metrics successfully identify commonly misunderstood concepts from aggregated data
5. Collaborative annotation enables effective peer learning while maintaining data integrity

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. From within the project directory, create a virtual environment:
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

4. Run tests with pytest-json-report to generate the required report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a CRITICAL requirement for project completion.