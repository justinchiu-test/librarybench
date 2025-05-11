# MedicalMind - A Knowledge Management System for Medical Students

## Overview
MedicalMind is a specialized knowledge management system designed for medical students who need to organize and connect vast amounts of information across different body systems, diseases, and treatment approaches. The system enables users to create anatomical relationships, build diagnostic frameworks, manage pharmacological information, optimize study through spaced repetition, and integrate theoretical knowledge with clinical cases.

## Persona Description
Jamal is studying medicine, absorbing vast amounts of information across different body systems, diseases, and treatment approaches. He needs to create interconnected medical knowledge that links symptoms, pathophysiology, and interventions.

## Key Requirements
1. **Anatomical relationship mapping** - Develop a comprehensive system for connecting anatomical structures with their functions and associated pathologies. This capability is critical for Jamal to understand the complex interrelationships in human anatomy, visualize how structural abnormalities lead to functional impairments, and build an integrated mental model that connects physical structures to disease processes. The system must support multi-level relationships across different body systems while maintaining biomedical accuracy.

2. **Diagnostic decision trees** - Create a framework for building and navigating diagnostic reasoning pathways that link symptoms to potential conditions with associated probabilities. This feature allows Jamal to develop clinical reasoning skills, understand the differential diagnosis process, and practice the systematic elimination approach used in clinical medicine. The system should support evidence-based probability estimates and incorporate key diagnostic criteria for various conditions.

3. **Pharmacological reference** - Implement a robust system for organizing medication information including mechanisms of action, indications, contraindications, and drug interactions. This capability helps Jamal master the extensive pharmacology knowledge required in medical education, understand the biochemical basis of drug effects, and learn to anticipate potential medication interactions. The reference system must maintain current information while supporting the theoretical understanding needed during pre-clinical years.

4. **Spaced repetition optimization** - Develop an adaptive learning system that prioritizes medical knowledge review based on forgetting curves and exam schedules. This feature is essential for Jamal to efficiently retain the massive volume of medical information, focus study time on challenging material, and prepare strategically for specific assessments in the curriculum. The system should analyze performance data to customize repetition intervals for optimal retention.

5. **Clinical case integration** - Create tools for connecting theoretical medical knowledge with patient presentations and clinical scenarios. This functionality allows Jamal to bridge the gap between classroom learning and clinical application, develop pattern recognition for disease presentations, and practice applying basic science concepts to patient care contexts. The system should support both structured case studies and personal clinical encounter notes.

## Technical Requirements
- **Testability Requirements**:
  - All components must be testable through well-defined APIs
  - Anatomical relationships must be verifiable against established medical references
  - Diagnostic algorithms must be testable with standardized case scenarios
  - Pharmacological data must be validated against authoritative sources
  - Spaced repetition algorithms must be verifiable with simulated learning patterns

- **Performance Expectations**:
  - System must efficiently handle knowledge bases with 50,000+ interconnected medical concepts
  - Anatomical relationship queries must complete in under 500ms
  - Diagnostic tree traversal must process complex symptom combinations in under 1 second
  - Full-text search across pharmacological data must return results in under 2 seconds
  - Spaced repetition scheduling must process 10,000+ knowledge items in under 3 seconds

- **Integration Points**:
  - Support for standard medical terminology (SNOMED CT, ICD-10, etc.)
  - Import capabilities for common medical reference formats
  - Export functionality for study materials and clinical notes
  - Integration with evidence-based medicine databases
  - Support for medical image annotation and reference (text-based descriptions only)

- **Key Constraints**:
  - All data must be stored locally without cloud dependencies
  - System must maintain medical accuracy while simplifying complex relationships
  - No user interface components - all functionality exposed through APIs
  - Implementation must support frequent knowledge base updates
  - System must operate efficiently with limited memory resources

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
MedicalMind needs to implement these core capabilities:

1. **Anatomical Knowledge Graph**: A comprehensive system for representing bodily structures and functions:
   - Entity representation for organs, tissues, cells, and systems
   - Relationship modeling for structural and functional connections
   - Pathological process integration linking structures to diseases
   - Multi-scale representation from molecular to organ system levels
   - Bidirectional navigation between related anatomical concepts

2. **Clinical Reasoning Engine**: A framework for diagnostic thinking:
   - Symptom-based decision tree construction
   - Bayesian probability modeling for differential diagnoses
   - Rule-in and rule-out criteria for various conditions
   - Lab value interpretation and significance assessment
   - Diagnostic pathway visualization using text-based formats

3. **Pharmacology Database**: A structured system for medication knowledge:
   - Comprehensive drug information with mechanism categorization
   - Medication classification by therapeutic category
   - Interaction detection between multiple medications
   - Side effect profiling with frequency and severity data
   - Pharmacokinetic and pharmacodynamic principle modeling

4. **Adaptive Learning System**: A sophisticated spaced repetition framework:
   - Individual forgetting curve calculation based on performance
   - Exam-aware scheduling prioritizing relevant content
   - Difficulty-based repetition interval adjustment
   - Knowledge dependency tracking for prerequisite concepts
   - Performance analytics to identify knowledge gaps

5. **Clinical Case Repository**: A system for applied medical knowledge:
   - Structured case representation with key clinical elements
   - Mapping between theoretical concepts and clinical manifestations
   - Pattern recognition support for similar case identification
   - Progressive case revelation simulating clinical discovery
   - Reflection capability for comparing approaches to similar cases

## Testing Requirements
The implementation must include comprehensive tests that verify all aspects of the system:

- **Key Functionalities to Verify**:
  - Anatomical relationship mapping correctly connects structures, functions, and pathologies
  - Diagnostic decision trees accurately guide from symptoms to potential conditions
  - Pharmacological reference properly organizes medication data and identifies interactions
  - Spaced repetition system appropriately prioritizes content based on forgetting curves and exam schedules
  - Clinical cases are effectively integrated with relevant theoretical knowledge

- **Critical User Scenarios**:
  - Exploring the anatomical relationships of the cardiovascular system and related pathologies
  - Building a diagnostic pathway for a patient presenting with specific symptoms
  - Researching a medication's mechanism, interactions, and contraindications
  - Creating a study schedule optimized for an upcoming pathology examination
  - Analyzing a clinical case and connecting its features to basic science concepts

- **Performance Benchmarks**:
  - Anatomical graph traversal must handle queries spanning multiple body systems in under 1 second
  - Diagnostic algorithms must evaluate a complex case with 20+ symptoms in under 3 seconds
  - Drug interaction checking must process regimens with 10+ medications in under 2 seconds
  - Spaced repetition scheduling must optimize 5,000+ items for a specific exam in under 5 seconds
  - Case-to-concept mapping must identify relevant theoretical connections in under 2 seconds

- **Edge Cases and Error Conditions**:
  - Handling rare anatomical variations or anomalies
  - Managing unusual symptom combinations not fitting standard diagnostic patterns
  - Processing medications with complex or poorly understood mechanisms
  - Adapting to irregular study patterns or interrupted learning sequences
  - Dealing with atypical clinical presentations of common conditions

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for diagnostic decision algorithms
  - 100% coverage for drug interaction detection
  - 95% branch coverage for spaced repetition scheduling
  - 95% coverage for anatomical relationship navigation

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

1. Medical students can map and explore anatomical relationships across body systems with associated pathologies
2. Users can build and navigate diagnostic decision trees connecting symptoms to potential conditions
3. Comprehensive pharmacological information is accessible with interaction detection capabilities
4. Study material is prioritized through spaced repetition optimized for specific exam schedules
5. Theoretical knowledge can be connected to clinical case presentations for applied learning

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