# Narrative Analysis and Consistency Framework

A specialized natural language processing toolkit for fiction writers to analyze character voices, track narrative elements, identify perspective shifts, and ensure thematic and stylistic consistency throughout manuscripts.

## Overview

This project provides fiction writers with sophisticated tools to analyze narrative structure, maintain consistent character voices, track point-of-view shifts, evaluate showing versus telling, analyze pacing, and monitor thematic elements throughout their manuscripts. The framework helps writers identify inconsistencies, improve stylistic elements, and ensure narrative coherence without requiring technical expertise.

## Persona Description

Priya is a novelist working on character development and narrative consistency across a series of books. She needs linguistic analysis tools to track character voices, plot elements, and thematic consistency throughout her manuscripts.

## Key Requirements

1. **Character Voice Analysis System**: Develop algorithms to measure and track distinctive speech patterns for different characters across scenes and chapters.
   - This feature is critical for Priya as it helps her maintain consistent and distinctive voices for each character throughout a novel or series, ensuring that dialogue and internal thoughts remain authentically tied to each character's established personality.
   - The system must detect subtle linguistic markers like vocabulary preferences, sentence structures, speech rhythms, and idiosyncratic expressions that define character voices.

2. **Point-of-View Detection Framework**: Create tools to identify narrative perspective shifts and analyze the consistency of viewpoint throughout different sections of a manuscript.
   - This capability allows Priya to maintain consistent narrative distance and avoid unintentional perspective shifts that can confuse readers and break immersion.
   - The detection must distinguish between different POV types (first-person, close third-person, omniscient, etc.) and identify transitions between character perspectives in multi-POV works.

3. **Show vs. Tell Analyzer**: Implement a system that highlights passages of expository "telling" that might be more effectively conveyed through "showing" with sensory details, action, or dialogue.
   - This feature helps Priya craft more engaging prose by identifying areas where direct exposition could be replaced with more immersive narrative techniques.
   - The analyzer must recognize different types of telling (character description, emotional states, background information) and suggest appropriate showing techniques for each.

4. **Narrative Pacing Visualization**: Build tools to map emotional intensity, action density, and narrative time throughout the manuscript, revealing the pacing structure of the story.
   - This capability enables Priya to see the emotional and action arcs of her story, ensuring appropriate variation and rhythm throughout the narrative.
   - The visualization must quantify factors affecting perceived pacing and present them in a way that helps identify potential problem areas (such as sagging middles or rushed climaxes).

5. **Thematic Consistency Tracker**: Develop a framework for generating and tracking symbolic language, motifs, and recurring imagery patterns throughout a manuscript.
   - This feature allows Priya to ensure that thematic elements are consistently developed and appropriately distributed throughout the narrative.
   - The tracker must identify related symbolic language, detect unintentional thematic shifts, and help maintain cohesion in the manuscript's underlying meaning structures.

## Technical Requirements

### Testability Requirements
- Character voice analysis must produce consistent, measurable linguistic profiles
- POV detection must reliably distinguish between different narrative perspectives
- Show vs. tell analysis must identify exposition patterns with quantifiable metrics
- Pacing analysis must generate reproducible visualizations with the same inputs
- Thematic tracking must detect pattern variations with statistical significance

### Performance Expectations
- Process full novel manuscripts (>100,000 words) in under 2 minutes
- Complete focused analysis of selected chapters in near real-time (< 5 seconds)
- Generate consistent results across multiple runs of the same text
- Support incremental analysis as manuscript content is revised
- Maintain acceptable performance regardless of narrative structure complexity

### Integration Points
- Accept manuscripts in standard formats (plain text, DOCX, RTF, Markdown)
- Support workable units beyond document level (scenes, chapters, character arcs)
- Provide structured export of analysis results in common formats (JSON, CSV)
- Enable integration with common writing software through file-based workflows
- Support reference manuscript comparison for series consistency

### Key Constraints
- Implementation must use only Python standard library
- All analysis must be performed locally without external service dependencies
- System must handle creative language use beyond standard grammar rules
- Processing must respect manuscript structure (chapters, scenes, etc.)
- Analysis must adapt to different fiction genres and stylistic approaches
- All components must provide meaningful feedback suitable for non-technical writers

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system consists of five main components:

1. **Character Voice Analyzer**: A framework for identifying and tracking character-specific linguistic patterns. It should:
   - Extract distinctive vocabulary, phrases, and sentence structures per character
   - Measure consistency of voice across different scenes and chapters
   - Detect dialogue attribution inconsistencies or voice "bleed" between characters
   - Track character-specific linguistic evolution throughout the narrative
   - Generate quantitative profiles of each character's speech patterns

2. **Narrative Perspective Monitor**: A system for analyzing point-of-view and narrative distance. It should:
   - Identify the prevailing POV type in each section (first person, third limited, omniscient, etc.)
   - Detect shifts between character perspectives in multi-POV works
   - Recognize unintentional POV slips or inconsistencies
   - Analyze narrative distance variations (deep internal, external observation, etc.)
   - Track sensory filter usage appropriate to the established POV

3. **Show-Don't-Tell Detector**: A framework for identifying exposition-heavy passages. It should:
   - Recognize direct exposition of character emotions, traits, or backgrounds
   - Identify instances of summarized action that could be dramatized
   - Detect "filtering" phrases that create narrative distance
   - Analyze the balance of scene vs. summary throughout the manuscript
   - Suggest opportunities for converting telling to showing based on context

4. **Pacing Analysis Engine**: A system for visualizing and analyzing narrative rhythm. It should:
   - Measure scene length, dialogue density, and action intensity
   - Track emotional intensity through sentiment analysis and emotional markers
   - Analyze temporal flow (scene time vs. narrative time)
   - Identify sections with potential pacing issues
   - Map the overall narrative arc to reveal structural patterns

5. **Thematic Element Tracker**: A framework for analyzing symbolic and thematic patterns. It should:
   - Identify recurring symbols, motifs, and imagery
   - Track thematic language across different manuscript sections
   - Generate word clouds and association networks for thematic elements
   - Detect potential unintentional thematic contradictions
   - Analyze the distribution and development of key themes throughout the work

## Testing Requirements

### Key Functionalities to Verify

1. Character Voice Analysis:
   - Test identification of character-specific linguistic markers
   - Verify consistency measurement across manuscript sections
   - Test detection of voice blending between characters
   - Validate tracking of character voice evolution
   - Verify handling of non-dialogue character expressions

2. Point-of-View Detection:
   - Test classification accuracy for different POV types
   - Verify detection of perspective shifts between characters
   - Test identification of POV inconsistencies and slips
   - Validate analysis of narrative distance variations
   - Verify handling of complex or experimental POV techniques

3. Show vs. Tell Analysis:
   - Test identification of different types of telling
   - Verify classification of showing vs. telling passages
   - Test detection of filtering phrases and distancing language
   - Validate scene vs. summary balance analysis
   - Verify context-appropriate suggestion generation

4. Pacing Visualization:
   - Test measurement of action density and intensity
   - Verify emotional arc tracking throughout manuscript
   - Test temporal flow analysis accuracy
   - Validate identification of pacing anomalies
   - Verify visualization consistency with manuscript structure

5. Thematic Tracking:
   - Test identification of symbolic language and motifs
   - Verify tracking of thematic elements across sections
   - Test detection of thematic contradictions or weakening
   - Validate thematic distribution analysis
   - Verify handling of subtle or ambiguous symbolic language

### Critical User Scenarios

1. Analyzing character dialogue consistency across a novel with multiple POV characters
2. Identifying unintentional perspective shifts in a close third-person narrative
3. Finding opportunities to convert exposition-heavy passages into scenes
4. Visualizing the pacing of a manuscript to identify structural issues
5. Tracking the development of key thematic elements across a series of novels

### Performance Benchmarks

- Process a full 100,000-word manuscript in under 2 minutes
- Complete character voice analysis for all named characters in under 30 seconds
- Identify at least 85% of POV shifts in test manuscripts
- Detect at least 80% of telling vs. showing opportunities in sample texts
- Track at least 90% of explicitly established thematic elements across the manuscript

### Edge Cases and Error Conditions

- Test with experimental narrative structures (stream of consciousness, multiple simultaneous POVs)
- Verify behavior with unreliable narrator techniques
- Test with heavily stylized or non-standard prose
- Validate performance on dialogue-heavy vs. description-heavy texts
- Test with genres having specific conventions (epistolary novels, second-person narratives)
- Verify handling of multilingual elements or constructed languages
- Test with nested narratives (stories within stories)

### Required Test Coverage Metrics

- Line coverage: Minimum 90%
- Branch coverage: Minimum 85%
- Function coverage: Minimum 95%
- All public APIs must have 100% test coverage
- All error handling paths must be tested
- All analysis algorithms must be thoroughly tested with diverse text samples

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

- Character voice analysis successfully distinguishes between at least 5 different character voices in test manuscripts
- POV detection correctly identifies at least 90% of narrative perspective types and shifts
- Show vs. tell analysis identifies at least 80% of telling passages that could be converted to showing
- Pacing visualization reveals structural patterns that match expert analysis of test manuscripts
- Thematic tracking successfully identifies and traces at least 90% of established motifs and symbols

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up your development environment:

1. Create a virtual environment using uv:
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

4. Install testing tools:
   ```
   pip install pytest pytest-json-report
   ```

5. Run tests with JSON reporting:
   ```
   pytest --json-report --json-report-file=pytest_results.json
   ```

IMPORTANT: Generating and providing the pytest_results.json file is a CRITICAL requirement for project completion. This file serves as proof that all tests pass and the implementation meets the specified requirements.