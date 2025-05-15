# Customer Support Request Analysis Framework

A specialized natural language processing toolkit for analyzing support tickets, categorizing issues, extracting relevant information, detecting sentiment, and generating appropriate responses for customer service automation.

## Overview

This project provides customer support teams with powerful tools to analyze incoming support requests, categorize issues, extract actionable information, detect customer sentiment, and generate appropriate response templates. The framework helps support teams handle high volumes of tickets more efficiently by automating routine analysis tasks and ensuring consistent response quality.

## Persona Description

Raj develops automation for customer service teams handling high volumes of support tickets. He needs to analyze incoming requests, categorize issues, and extract actionable information to improve response efficiency.

## Key Requirements

1. **Intent Classification System**: Develop algorithms to determine the primary purpose of customer messages and categorize them into appropriate issue types, request categories, and urgency levels.
   - This feature is critical for Raj as it enables automatic ticket routing to the appropriate support teams and prioritization of urgent issues, dramatically reducing initial response time.
   - The classification must recognize multiple intents within the same message, distinguish between similar issue types, and adapt to evolving product features and common customer problems.

2. **Information Extraction Engine**: Create a framework to identify and extract key details from customer messages, including product information, error codes, action attempts, environment details, and other relevant contextual data.
   - This capability allows support agents to immediately access the critical information needed to diagnose issues without manually parsing lengthy customer messages.
   - The extraction must recognize diverse formats of product identifiers, error messages, version numbers, and other technical details even when presented in non-standard ways.

3. **Sentiment Escalation Detector**: Implement a system to identify emotionally charged messages indicating customer frustration, anger, or distress that require urgent attention and specialized handling.
   - This feature helps Raj ensure that customers experiencing significant distress receive priority attention before their frustration escalates further.
   - The detection must go beyond basic sentiment analysis to recognize emotional intensity, differentiate between frustration with the product versus the support experience, and identify specific trigger phrases indicating potential escalation risk.

4. **Response Suggestion Generator**: Build a system that creates template-based replies for common scenarios, incorporating relevant extracted information and adapting to the specific context of each customer inquiry.
   - This capability significantly improves agent efficiency by providing ready-to-use response templates that require minimal customization while still addressing the customer's specific situation.
   - The generator must select appropriate templates based on issue type, include relevant customer and product details, maintain a consistent tone, and adapt language based on customer technical proficiency.

5. **Conversation Flow Modeling**: Develop tools to track multi-message interactions throughout the resolution process, understanding the current state of each conversation and predicting next steps toward resolution.
   - This feature enables Raj to build systems that understand where each customer conversation stands in the resolution process and what actions are likely needed next.
   - The modeling must track conversation state across multiple messages, recognize when issues evolve or new issues are introduced, and identify when conversations are ready for resolution or require escalation.

## Technical Requirements

### Testability Requirements
- Intent classification must achieve measurable accuracy against human-labeled support tickets
- Information extraction must be verifiable with precision and recall metrics
- Sentiment detection must correlate with human judgment of message urgency
- Response suggestions must be evaluable for appropriateness and completeness
- Conversation flow modeling must accurately track state changes through ticket lifecycles

### Performance Expectations
- Process and analyze typical support tickets (100-500 words) in under 1 second
- Handle batches of up to 1,000 new tickets in under 5 minutes
- Generate response suggestions immediately upon ticket classification
- Maintain consistent performance regardless of ticket length or complexity
- Support concurrent analysis of multiple ongoing conversations

### Integration Points
- Accept support tickets from multiple channels (email, chat, web forms)
- Support integration with common helpdesk and CRM systems
- Enable export of analysis results in standard formats (JSON, CSV)
- Provide APIs for real-time ticket processing in support workflows
- Allow customization through configuration rather than code changes

### Key Constraints
- Implementation must use only Python standard library
- Processing must maintain customer privacy with no external API dependencies
- System must handle domain-specific terminology across different product lines
- Analysis must be effective across different customer communication styles
- Algorithms must adapt to evolving product features and support issues
- Response suggestions must be clearly marked as templates requiring human review

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system consists of five main components:

1. **Support Intent Classifier**: A framework for categorizing customer support requests. It should:
   - Identify the primary purpose of customer messages
   - Categorize requests into defined issue types and subtypes
   - Determine urgency and prioritization levels
   - Recognize multiple intents within single messages
   - Adapt to new issue categories over time

2. **Technical Detail Extractor**: A system for identifying relevant information in tickets. It should:
   - Extract product details, models, and version information
   - Identify error codes, messages, and symptoms
   - Recognize customer environment information
   - Capture previous troubleshooting steps attempted
   - Identify temporal information related to the issue

3. **Emotional Content Analyzer**: A framework for detecting customer sentiment. It should:
   - Measure overall sentiment and emotional intensity
   - Identify specific emotions (frustration, anger, satisfaction)
   - Recognize escalation indicators and trigger phrases
   - Detect sarcasm and implicit negative sentiment
   - Differentiate between product frustration and support frustration

4. **Template Response Engine**: A system for generating contextual replies. It should:
   - Select appropriate response templates based on issue type
   - Incorporate extracted customer and product information
   - Adapt language to customer technical proficiency
   - Generate step-by-step troubleshooting instructions
   - Maintain appropriate tone and consistent brand voice

5. **Conversation State Tracker**: A framework for modeling support interactions. It should:
   - Track conversation progress through resolution stages
   - Identify when new information arrives or issues evolve
   - Recognize successful resolution indicators
   - Detect stalled conversations requiring intervention
   - Model probable next steps in the resolution process

## Testing Requirements

### Key Functionalities to Verify

1. Intent Classification:
   - Test accuracy of primary intent identification
   - Verify correct categorization into issue types
   - Test detection of multiple intents in single messages
   - Validate urgency determination
   - Verify adaptation to new issue categories

2. Information Extraction:
   - Test extraction of product details in various formats
   - Verify identification of error messages and codes
   - Test recognition of environment information
   - Validate capture of previous troubleshooting attempts
   - Verify handling of ambiguous or incomplete information

3. Sentiment Detection:
   - Test identification of different emotional states
   - Verify detection of escalation indicators
   - Test measurement of emotional intensity
   - Validate correlation with human judgment
   - Verify recognition of implicit sentiment

4. Response Generation:
   - Test selection of appropriate templates
   - Verify incorporation of customer-specific details
   - Test adaptation to different technical proficiency levels
   - Validate generation of accurate troubleshooting steps
   - Verify maintenance of consistent tone

5. Conversation Tracking:
   - Test accurate state identification across message sequences
   - Verify detection of conversation progress
   - Test recognition of issue evolution
   - Validate identification of resolution readiness
   - Verify detection of stalled conversations

### Critical User Scenarios

1. Processing an initial technical support request with error codes and system details
2. Handling an escalated complaint from a frustrated customer
3. Tracking a multi-message troubleshooting conversation to resolution
4. Analyzing a complex request containing multiple separate issues
5. Processing a follow-up message with new information about an existing ticket

### Performance Benchmarks

- Classify support tickets into correct categories with at least 85% accuracy
- Extract at least 90% of critical technical details from standard format messages
- Detect high-urgency emotional content with at least 90% precision and recall
- Generate appropriate response templates for at least 80% of common scenarios
- Correctly track conversation state through resolution with at least 85% accuracy

### Edge Cases and Error Conditions

- Test with extremely brief or vague customer messages
- Verify behavior with highly technical or jargon-filled requests
- Test with messages containing mixed positive and negative sentiment
- Validate performance on non-standard communication styles
- Test with tickets containing multiple unrelated issues
- Verify handling of unusual product configurations or error scenarios
- Test with conversations that suddenly change topic or urgency

### Required Test Coverage Metrics

- Line coverage: Minimum 90%
- Branch coverage: Minimum 85%
- Function coverage: Minimum 95%
- All public APIs must have 100% test coverage
- All error handling paths must be tested
- All classification, extraction, and generation algorithms must be thoroughly tested

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

- The system correctly classifies at least 85% of support tickets into appropriate categories
- Information extraction identifies at least 90% of critical technical details in test messages
- Sentiment analysis correctly prioritizes at least 90% of high-urgency messages
- Response generation produces appropriate templates for at least 80% of common scenarios
- Conversation tracking accurately models at least 85% of multi-message support interactions

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