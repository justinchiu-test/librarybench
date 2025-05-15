# Financial Education and Demonstration System

## Overview
A specialized financial education tool designed for instructors teaching financial literacy to young adults. The system provides interactive demonstrations, simplified financial simulations, step-by-step educational content, assessment capabilities, and scenario-based challenges to make abstract financial concepts concrete and engaging for novice learners.

## Persona Description
Robert teaches financial literacy to young adults and needs demonstration tools that illustrate important personal finance concepts. He requires simplified examples and visualizations that make abstract financial principles concrete for novice learners.

## Key Requirements
1. **Concept demonstration mode with simplified examples and step-by-step explanations**  
   Robert needs to clearly illustrate complex financial concepts to students with limited prior knowledge. The system must provide simplified, interactive demonstrations of core financial principles (compound interest, inflation, loan amortization, etc.) with step-by-step walkthroughs that break down calculations, offer clear explanations of each component, and allow manipulation of variables to show how changes affect outcomes.

2. **Financial decision simulators showing long-term impacts of different choices**  
   To help students understand consequences of financial decisions, Robert needs simulation tools that project long-term impacts. The system should model various financial scenarios (saving vs. borrowing, renting vs. buying, investing strategies, etc.), compare different decision paths side-by-side, accelerate time to show long-term effects, and clearly illustrate trade-offs between immediate gratification and future financial health.

3. **Learning curriculum organization presenting concepts in pedagogical sequence**  
   Robert follows a structured curriculum when teaching financial literacy. The system needs to organize financial concepts in a pedagogically sound progression, track concept dependencies and prerequisites, adapt content difficulty based on learner proficiency, and provide a coherent learning pathway that builds from fundamental to advanced financial topics.

4. **Financial literacy assessment tools measuring understanding of key concepts**  
   To gauge student comprehension, Robert needs objective assessment capabilities. The system must provide concept-specific knowledge checks, scenario-based problem-solving evaluations, compare student responses against correct financial reasoning, identify specific misconceptions in student understanding, and track mastery of concepts across a financial literacy curriculum.

5. **Scenario-based challenges for students to apply financial management principles**  
   Robert wants students to practice applying financial principles to realistic situations. The system should offer scenario-based financial challenges (budgeting for first apartment, handling financial emergencies, planning major purchases, etc.), require students to make series of interconnected financial decisions, evaluate the quality of their choices, and provide constructive feedback on their financial reasoning.

## Technical Requirements
- **Testability Requirements:**
  - Financial calculations must be verified against established formulas
  - Simulation results must be reproducible with identical inputs
  - Assessment scoring algorithms must produce consistent results
  - Learning progression logic must maintain proper concept sequencing

- **Performance Expectations:**
  - Simulations must run instantly when parameters change
  - System must support at least 50 distinct financial concepts
  - Long-term financial projections (40+ years) must calculate in under 2 seconds
  - Assessment scoring must process in real-time

- **Integration Points:**
  - Extensible framework for adding new financial concepts
  - Optional export of demonstration results for classroom use
  - Assessment result aggregation and analysis
  - Curriculum customization capabilities

- **Key Constraints:**
  - Financial concepts must be simplified without sacrificing accuracy
  - Educational content must use consistent terminology and definitions
  - System must present concepts without personal financial bias
  - Explanations must be accessible to users without financial background

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement these core components:

1. **Financial Concept Demonstration Engine:**
   - Interactive financial concept models
   - Step-by-step calculation breakdowns
   - Variable manipulation capabilities
   - Simplified versions of complex financial mechanisms
   - Progressive detail levels for different learning stages

2. **Decision Impact Simulator:**
   - Long-term financial projection models
   - Multi-scenario comparison framework
   - Time acceleration for lifetime financial paths
   - Trade-off analysis between financial choices
   - Key financial metric tracking over time

3. **Curriculum Management System:**
   - Concept dependency mapping
   - Learning progression pathways
   - Proficiency-based content adaptation
   - Topic relationship visualization
   - Pedagogical sequencing controls

4. **Assessment and Evaluation Tools:**
   - Concept-specific knowledge checks
   - Financial reasoning evaluation
   - Misconception identification
   - Mastery tracking across curriculum
   - Statistical analysis of assessment results

5. **Scenario Challenge Framework:**
   - Real-world financial scenario definitions
   - Decision tree modeling for financial choices
   - Response evaluation criteria
   - Feedback generation system
   - Mistake diagnosis and remediation suggestions

## Testing Requirements
- **Key Functionalities to Verify:**
  - Accuracy of financial calculations in demonstration mode
  - Appropriate projection of long-term financial impacts in simulations
  - Correct sequencing of concepts in curriculum organization
  - Accurate assessment of financial literacy understanding
  - Proper evaluation of decisions in scenario-based challenges

- **Critical User Scenarios:**
  - Creating a compound interest demonstration with adjustable parameters
  - Comparing long-term outcomes of different student loan repayment strategies
  - Organizing a sequence of investment concepts from basic to advanced
  - Assessing student understanding of budgeting principles
  - Evaluating student decisions in a first-apartment budgeting scenario

- **Performance Benchmarks:**
  - Financial calculations must update instantly when variables change
  - Decision simulators must project and compare 5+ scenarios simultaneously
  - Curriculum organization must handle at least 100 interconnected concepts
  - Assessment tools must evaluate responses against 20+ evaluation criteria

- **Edge Cases and Error Conditions:**
  - Handling extreme values in financial calculations
  - Managing conflicting financial principles in curriculum organization
  - Processing partial or incomplete assessment responses
  - Evaluating creative but unorthodox solutions in scenario challenges
  - Adapting to learners with gaps in prerequisite knowledge

- **Required Test Coverage Metrics:**
  - Financial calculation functions: minimum 95% coverage
  - Simulation projection algorithms: minimum 90% coverage
  - Assessment scoring functions: minimum 90% coverage
  - Scenario evaluation logic: minimum 85% coverage

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
- The system effectively demonstrates financial concepts with clear step-by-step explanations
- Financial decision simulators accurately project long-term impacts of different choices
- Learning curriculum is properly organized in a pedagogically sound sequence
- Assessment tools accurately measure understanding of key financial concepts
- Scenario-based challenges provide realistic application of financial principles
- All financial calculations are accurate while remaining accessible to novice learners
- System performance meets or exceeds the specified benchmarks
- All tests pass without manual intervention

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Environment Setup
1. Set up a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.