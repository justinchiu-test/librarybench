# Language Learning Text Analysis Toolkit

A natural language processing library designed to assess text complexity, identify challenging vocabulary, and generate educational materials for language learners.

## Overview

This project provides ESL (English as Second Language) teachers with comprehensive text analysis capabilities focused on readability assessment, language proficiency mapping, vocabulary analysis, cultural reference detection, and educational exercise generation. It enables the creation of level-appropriate learning materials without requiring advanced technical expertise.

## Persona Description

Carlos develops instructional materials for non-native English speakers and needs tools to assess reading difficulty, identify challenging vocabulary, and create level-appropriate learning exercises tailored to different language proficiency levels.

## Key Requirements

1. **Readability Scoring with Granular Feedback**: Implement comprehensive text complexity analysis that breaks down readability into specific contributing factors (sentence length, vocabulary difficulty, syntactic complexity, etc.). This feature is critical for Carlos because it allows him to precisely identify which aspects of a text make it challenging for learners and target his instructional design to address specific complexity factors.

2. **Language Acquisition Level Mapping**: Develop algorithms to classify texts according to standardized language proficiency frameworks (CEFR, ACTFL, etc.) based on vocabulary, grammar, and structural features. This capability enables Carlos to efficiently match reading materials to his students' current proficiency levels, ensuring texts are challenging but accessible at each developmental stage.

3. **Vocabulary Grading**: Create tools to identify words that fall outside targeted learning levels, with automatic suggestion of level-appropriate alternatives. For Carlos, vocabulary control is essential to creating accessible materials, and automated identification of challenging words with suggested replacements dramatically speeds up his material adaptation process.

4. **Cultural Reference Detection**: Build detection mechanisms for culture-specific idioms, expressions, and references that may require additional explanation for non-native speakers. This feature helps Carlos identify content that might be linguistically appropriate but culturally opaque to his students, allowing him to provide necessary context for full comprehension.

5. **Exercise Generation**: Implement automated creation of language learning activities including cloze tests, vocabulary practice, and comprehension questions based on input texts. This capability significantly reduces Carlos's preparation time by algorithmically generating customizable practice materials directly matched to the complexity level and content of his reading texts.

## Technical Requirements

### Testability Requirements
- All text analysis algorithms must provide consistent, reproducible results
- Readability metrics must correlate with established readability frameworks
- Language level classifications must be validated against professionally-graded texts
- Vocabulary identification must match standard ESL vocabulary lists with high accuracy
- Generated exercises must meet pedagogical best practices for language acquisition

### Performance Expectations
- Process standard lesson texts (500-2000 words) in under 5 seconds
- Generate complete exercise sets for a text in under 10 seconds
- Support batch processing of curriculum-sized text collections
- Memory usage suitable for standard teacher computing equipment
- Responsive analysis for interactive text selection and modification

### Integration Points
- Standard text import formats (TXT, PDF, DOCX, HTML)
- Compatibility with common ESL vocabulary lists and frameworks
- Export capabilities for exercise generation in usable formats
- Readability scoring compatible with established educational metrics
- Mapping to international language proficiency standards (CEFR, etc.)

### Key Constraints
- Implementation using only Python standard library (no external NLP or ML dependencies)
- Algorithm design prioritizing explainability for educational contexts
- Features calibrated specifically for second language acquisition contexts
- Exercise generation meeting pedagogical best practices
- Analysis tuned for instructional rather than general-purpose text processing

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality required for this project includes:

1. **Text Complexity Analysis**
   - Multi-factor readability assessment
   - Sentence structure and length analysis
   - Discourse cohesion evaluation
   - Grammar complexity grading
   - Reading time estimation for non-native readers

2. **Proficiency Level Classification**
   - CEFR/ACTFL/other framework mapping
   - Text suitability scoring for target levels
   - Progression difficulty assessment
   - Mixed-level text segmentation
   - Calibration based on standard texts

3. **Vocabulary Analysis System**
   - Word frequency band identification
   - Academic and specialized vocabulary flagging
   - Level-appropriate alternative suggestion
   - Vocabulary burden calculation
   - Key term extraction for pre-teaching

4. **Cultural Context Processing**
   - Idiom and expression detection
   - Cultural reference identification
   - Figurative language recognition
   - Assumed knowledge assessment
   - Context dependence evaluation

5. **Exercise Generation Framework**
   - Cloze test creation with targeted gaps
   - Vocabulary practice activity generation
   - Comprehension question formulation
   - Discussion prompt creation
   - Grammar practice extraction

## Testing Requirements

### Key Functionalities to Verify
- Accurate readability assessment matching established metrics
- Correct classification of texts by language acquisition level
- Precise identification of vocabulary outside target proficiency levels
- Reliable detection of idiomatic expressions and cultural references
- Quality of automatically generated learning exercises

### Critical User Scenarios
- Analyzing a potential reading text to determine suitability for intermediate learners
- Identifying vocabulary that needs pre-teaching or glossing in an authentic text
- Creating a complete lesson plan with exercises from a selected reading passage
- Detecting cultural references that require additional explanation
- Batch processing a collection of texts to create a progressive curriculum

### Performance Benchmarks
- Complete analysis of a 1000-word text in under 3 seconds
- Vocabulary grading with 95% accuracy compared to standard ESL word lists
- CEFR level classification matching expert assessment in 85% of cases
- Cultural reference detection with precision above 80%
- Exercise generation producing pedagogically valid activities for 90% of input texts

### Edge Cases and Error Conditions
- Texts with specialized terminology or technical vocabulary
- Content with heavy use of idioms, slang, or cultural references
- Materials containing non-standard formatting or structures
- Multilingual texts or texts with code-switching
- Content with unusual discourse patterns or non-standard grammar
- Texts combining multiple difficulty levels in different sections

### Required Test Coverage Metrics
- 90% code coverage for readability analysis components
- 95% coverage for vocabulary grading functions
- 90% coverage for language level mapping
- 85% coverage for cultural reference detection
- 90% coverage for exercise generation modules

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Readability analysis provides accurate, multi-factor assessment with actionable feedback
2. Texts can be reliably mapped to standardized language proficiency frameworks
3. Vocabulary outside target proficiency levels is correctly identified with appropriate alternatives
4. Cultural references and idiomatic expressions are detected with high precision
5. Automatically generated exercises meet pedagogical standards for language instruction
6. Performance meets specified benchmarks for processing speed and accuracy
7. Analysis results demonstrate high correlation with expert ESL teacher assessment
8. The system handles a wide range of text types and complexity levels
9. Generated materials follow best practices in second language acquisition
10. The toolkit measurably reduces preparation time for creating level-appropriate materials

## Getting Started

To set up the project:

1. Create a new library project:
   ```
   uv init --lib
   ```

2. Install development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a sample script:
   ```
   uv run python script.py
   ```