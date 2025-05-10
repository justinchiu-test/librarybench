# Game Narrative and Logic Language

A domain-specific language toolkit for creating complex game narratives, quests, and character interactions.

## Overview

This project delivers a specialized domain-specific language toolkit that enables game designers and narrative writers to define complex game logic, quest lines, character interactions, and world states without requiring programming expertise. The toolkit translates these narrative and game mechanic definitions into executable game code that can drive in-game behaviors and storylines, ensuring consistency across complex narrative branches while detecting potential progression issues.

## Persona Description

Alex leads a team creating an RPG game with complex character progression and quest systems. His primary goal is to build a game logic language that allows narrative designers and game designers to create intricate quest lines and character interactions without requiring programmer intervention.

## Key Requirements

1. **Narrative branching visualization with consequence tracking**
   - Critical for Alex because RPG storylines have numerous decision points that affect future game events and character relationships, and designers need to visualize and manage this complexity.
   - The DSL must support defining branching narrative structures with decision points, conditional triggers, and consequence tracking, generating data that can represent the complete narrative tree with cause-effect relationships.

2. **Character state management with personality trait modeling**
   - Essential because RPG characters have complex states including faction relationships, personality traits, memories of player interactions, and evolving motives that influence dialogue and behavior.
   - The system must provide syntax for defining character state variables, personality models, interaction memory, and behavioral response patterns based on these factors.

3. **World state persistence with trigger-based event system**
   - Vital because open-world RPGs maintain a persistent game world where player actions have lasting consequences, requiring tracking of world state variables and conditional event triggers.
   - The DSL must enable defining world state variables, persistence rules, conditional event triggers, and causality chains that respond to changes in the game world.

4. **Economy balancing tools with progression curve analysis**
   - Necessary because RPGs contain complex economic systems involving rewards, resources, character progression, and difficulty curves that must be balanced for player satisfaction.
   - The toolkit must provide mechanisms for defining economic variables, progression curves, reward distributions, and analytics tools to model and balance these systems.

5. **Quest dependency validation preventing progression deadlocks**
   - Important because complex quest systems with interdependencies can inadvertently create progression blockers or unreachable content if not properly validated.
   - The system must analyze quest dependency structures to identify potential progression deadlocks, unreachable quest states, or conflicting quest conditions before implementation.

## Technical Requirements

- **Testability Requirements**
  - All narrative branches must be traversable in simulated gameplay scenarios
  - Character state transitions must produce consistent, predictable behaviors
  - Economic models must be testable with simulated player progression
  - Quest dependency graphs must be verified for completability
  - Event triggers must be testable in isolation and combination

- **Performance Expectations**
  - Narrative validation must complete within 5 seconds for typical story arcs
  - State transition calculations must execute within 50ms
  - The system must handle quest networks with up to 500 interconnected quests
  - Memory usage must not exceed 300MB for the toolkit core
  - The system must support concurrent simulation of up to 100 NPC behaviors

- **Integration Points**
  - Game engine scripting systems for runtime execution
  - Dialogue and conversation systems for character interactions
  - Quest tracking and journal systems for player guidance
  - Save/load systems for game state persistence
  - Game analytics platforms for progression and balance metrics

- **Key Constraints**
  - Must support hot-reloading of content for rapid iteration
  - Must handle cyclic references in relationship networks
  - Must maintain backward compatibility with existing game saves
  - Must operate efficiently within game runtime performance budgets
  - Must accommodate collaborative workflows among multiple designers

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces. The narrative visualization capabilities should generate structured data that could be visualized by external tools, not implementing the visualization itself.

## Core Functionality

The core functionality of the Game Narrative and Logic Language encompasses:

1. **Narrative Definition Language**
   - Game-specific syntax for storylines, quests, and dialogues
   - Branching narrative structures with decision points
   - Conditional content based on player choices and world state
   - Character dialogue and reaction patterns
   - Narrative tagging for theming and content classification

2. **Character State System**
   - Personality trait modeling and attribute definitions
   - Relationship network specification with dynamic adjustments
   - Memory and knowledge representation for NPCs
   - Behavioral response patterns based on state
   - Character development arcs and transformation rules

3. **World State Management**
   - Global and local state variable definition
   - Persistence rules and state change tracking
   - Event trigger conditions and execution logic
   - Time-based state evolution rules
   - State query and filtering mechanisms

4. **Economic Balancing Framework**
   - Resource type and value definitions
   - Progression curve modeling and analysis
   - Reward distribution pattern specification
   - Difficulty scaling rules and parameters
   - Economic simulation for balance testing

5. **Quest Management System**
   - Quest structure and objective definition
   - Dependency relationship specification
   - Completion condition and reward association
   - Quest state tracking and transition rules
   - Failure conditions and fallback paths

## Testing Requirements

- **Key Functionalities to Verify**
  - Narrative branch traversal and consequence propagation
  - Character state transitions and behavioral responses
  - World state persistence and event triggering
  - Economic balance across player progression curves
  - Quest dependency validation and completability

- **Critical User Scenarios**
  - Narrative designer creating a branching quest line with multiple endings
  - Character designer defining personality-driven NPC behaviors
  - World designer establishing state-changing events and triggers
  - Economy designer balancing progression curves and rewards
  - Quest designer mapping dependencies between interconnected objectives

- **Performance Benchmarks**
  - Narrative validation: < 5 seconds for 100-node story graphs
  - Character state updates: < 50ms per character update
  - World state persistence: < 100ms for full state save/load
  - Economic simulation: < 10 seconds for full progression modeling
  - Quest validation: < 3 seconds for dependency graph analysis

- **Edge Cases and Error Conditions**
  - Handling circular quest dependencies that could block progression
  - Managing conflicting character state transitions
  - Addressing unreachable narrative branches
  - Graceful degradation when state data is incomplete or corrupted
  - Handling exceptional player behavior that bypasses expected paths

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage for all modules
  - 100% coverage of quest dependency validation logic
  - Complete path coverage for all narrative branches
  - All character state transition rules must be tested
  - Full coverage of economic simulation algorithms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Game designers can define complex narrative structures without programmer intervention
2. Character behaviors consistently reflect their defined personality traits and memories
3. The system correctly tracks world state changes and triggers appropriate events
4. Economic simulations accurately predict resource distribution and progression pace
5. Quest validation identifies 100% of potential progression blockers before implementation
6. The toolkit integrates with game engine scripting systems for runtime execution
7. The test suite validates all core functionality with at least 90% coverage
8. Performance benchmarks are met under typical game design workloads

## Getting Started

To set up the development environment:

```bash
# Initialize the project
uv init --lib

# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run a specific test
uv run pytest tests/test_narrative_validator.py::test_branch_consistency

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

When implementing this project, remember to focus on creating a library that can be integrated into game development pipelines rather than a standalone application with user interfaces. All functionality should be exposed through well-defined APIs, with a clear separation between the narrative definition language and any future visualization or UI components.