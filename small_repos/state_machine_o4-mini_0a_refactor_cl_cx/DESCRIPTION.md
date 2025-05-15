# StateMachine

## Purpose and Motivation
StateMachine offers a lightweight framework for modeling finite-state machines (FSMs) in Python. It enables you to declare states, events, transitions, and guards in a clear, maintainable way. Ideal for workflows, protocol handling, or UI flow control where behavior depends on the current state and incoming events.

## Core Functionality
- Define states and named transitions with optional guard functions  
- Trigger events against a machine instance to move between states  
- Register entry/exit callbacks for specific states or global hooks  
- Query current state, available transitions, and history log  
- Support hierarchical (nested) states or parallel regions as an extension point  
- Serialise/deserialise machine definition and runtime state for persistence  

