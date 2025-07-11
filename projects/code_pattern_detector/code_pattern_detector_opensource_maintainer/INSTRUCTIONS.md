# PyPatternGuard - Open Source Project Quality Guardian

## Overview
A community-focused code pattern detection system designed for open source maintainers managing diverse contributor bases. This implementation emphasizes automated contributor guidance, project convention learning, community pattern sharing, and multi-language support to ensure consistent quality across varied contributions.

## Persona Description
An open source project maintainer who reviews community contributions and needs to ensure consistent code quality across diverse contributors. She wants automated checks that respect project-specific conventions.

## Key Requirements

1. **Contributor-specific pattern analysis with onboarding recommendations**
   - Essential for providing personalized guidance to contributors with varying skill levels and backgrounds. Tailored recommendations help new contributors quickly adapt to project standards while respecting their existing expertise.

2. **Project convention learning from existing codebase patterns**
   - Critical for maintaining consistency without extensive manual configuration. Automatically learning from established patterns ensures that quality checks align with actual project practices rather than generic rules.

3. **Automated contributor guidelines generation based on detected patterns**
   - Vital for keeping documentation synchronized with actual code practices. Dynamic guidelines reduce maintainer workload while ensuring contributors always have current information.

4. **Community pattern library with voting and discussion features**
   - Necessary for collaborative decision-making on code standards. Community input ensures buy-in and helps evolve patterns based on collective experience and emerging best practices.

5. **Multi-language pattern detection for polyglot projects**
   - Required for modern open source projects using multiple languages. Consistent quality standards across languages prevents fragmentation and maintains project cohesion.

## Technical Requirements

- **Testability Requirements**
  - Contributor analysis must be testable with simulated contribution histories
  - Convention learning algorithms must be validated with known patterns
  - Guideline generation must produce consistent, verifiable output
  - Multi-language detection must work with test files in various languages

- **Performance Expectations**
  - First-time contributor analysis within 30 seconds
  - Convention learning from 100K LOC within 5 minutes
  - Guideline regeneration within 1 minute
  - Pattern library queries under 100ms

- **Integration Points**
  - Git history analysis for contributor patterns
  - Pull request APIs for automated feedback
  - Markdown generation for documentation
  - Database storage for community patterns
  - Language-specific parsers for polyglot support

- **Key Constraints**
  - Must respect project-specific conventions over generic rules
  - Should work with incomplete contributor information
  - Must handle projects with 100+ contributors
  - Cannot require changes to existing project structure

**IMPORTANT:** The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The open source project quality guardian must provide:

1. **Contributor Analysis Engine**
   - Historical contribution pattern analysis
   - Skill level assessment based on code quality
   - Personalized recommendation generation
   - Onboarding checklist creation

2. **Convention Learning System**
   - Pattern extraction from existing codebase
   - Statistical analysis of coding practices
   - Convention confidence scoring
   - Anomaly detection for outliers

3. **Documentation Generator**
   - Markdown-formatted guideline creation
   - Code example extraction from codebase
   - Section prioritization based on violations
   - Multi-language example support

4. **Community Pattern Platform**
   - Pattern submission and categorization
   - Voting mechanism with weighted scoring
   - Discussion thread integration
   - Pattern adoption tracking

5. **Polyglot Detection Framework**
   - Pluggable language analyzer architecture
   - Cross-language pattern correlation
   - Unified reporting across languages
   - Language-specific rule customization

## Testing Requirements

### Key Functionalities to Verify
- Accurate contributor skill assessment
- Correct convention extraction from codebases
- Quality of generated documentation
- Community pattern voting accuracy
- Multi-language detection consistency

### Critical User Scenarios
- Analyzing first-time contributor's pull request
- Learning conventions from mature project
- Regenerating guidelines after major refactor
- Community voting on new pattern proposals
- Detecting patterns across Python/JavaScript/Go

### Performance Benchmarks
- Contributor analysis under 30 seconds
- Convention learning handles 100K LOC efficiently
- Documentation generation within 1 minute
- Pattern queries return in under 100ms
- Support for projects with 500+ contributors

### Edge Cases and Error Conditions
- Handling contributors with no prior history
- Learning from inconsistent codebases
- Managing conflicting community votes
- Processing malformed code in PRs
- Dealing with rare or custom languages

### Required Test Coverage Metrics
- Minimum 85% overall code coverage
- 100% coverage for convention learning core
- All language parsers must be tested
- Community features fully covered
- Documentation generation thoroughly tested

**IMPORTANT:**
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- **REQUIRED:** Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria

The implementation successfully meets the open source maintainer's needs when:

1. **Contributor Experience**
   - New contributors receive helpful, specific guidance
   - Onboarding recommendations reduce common mistakes
   - Feedback respects contributor expertise levels
   - Review cycles become more efficient

2. **Convention Alignment**
   - Detected patterns match actual project practices
   - False positives from generic rules are minimized
   - Project-specific idioms are recognized
   - Convention evolution is tracked over time

3. **Documentation Quality**
   - Generated guidelines are clear and actionable
   - Examples come from actual project code
   - Documentation stays synchronized with practices
   - Multi-language projects have unified standards

4. **Community Engagement**
   - Pattern discussions lead to consensus
   - Voting reflects community preferences
   - Adopted patterns improve code quality
   - Contributors feel ownership of standards

**REQUIRED FOR SUCCESS:**
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the development environment:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install project in development mode
uv pip install -e .
```

**REMINDER:** The implementation MUST emphasize that generating and providing pytest_results.json is a critical requirement for project completion.