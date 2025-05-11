# Marketing Campaign Workflow Automation Engine

## Overview
A specialized workflow automation engine designed for marketing professionals, enabling natural language workflow definition, comprehensive marketing platform integration, sophisticated audience segmentation, global campaign timing coordination, and automated performance metrics collection. This system provides reliable automation for complex marketing campaigns across multiple channels without requiring deep technical expertise.

## Persona Description
Carlos coordinates digital marketing campaigns across multiple channels and platforms. He needs to automate content publication, audience targeting, and analytics collection without deep technical expertise.

## Key Requirements
1. **Natural Language Workflow Definition**: Implement a system allowing non-technical users to describe automation needs in plain language. This feature is critical for Carlos because he and his marketing team lack programming skills but need to create sophisticated campaign workflows without developer assistance for each campaign variation.

2. **Marketing Platform Integration**: Develop connections with common advertising and content systems. Carlos requires this capability because his campaigns span multiple platforms (social media, email, web, advertising networks), and manually coordinating actions across these disparate systems is time-consuming and error-prone.

3. **Audience Segmentation Logic**: Create implementation of complex targeting rules across channels. This feature is vital for Carlos as his marketing strategy depends on delivering personalized content to precisely defined audience segments based on demographics, behavior, and engagement history across multiple channels.

4. **Campaign Timing Coordination**: Build scheduling of actions across global time zones. Carlos needs this functionality because his company markets globally, and campaign elements must be coordinated to appear at appropriate local times in different regions while maintaining overall campaign coherence.

5. **Performance Metrics Collection**: Implement automatic gathering and visualization of campaign results. This capability is essential for Carlos because measuring campaign effectiveness requires collecting and analyzing data from multiple platforms, and manual aggregation is both time-intensive and susceptible to errors.

## Technical Requirements
- **Testability Requirements**:
  - Natural language processing must be testable with diverse marketing workflow descriptions
  - Platform integrations must be testable without requiring actual marketing platform access
  - Audience segmentation logic must be verifiable with synthetic audience data
  - Timing coordination must be testable across simulated time zones
  - Metrics collection must be verifiable with mock performance data

- **Performance Expectations**:
  - Natural language workflow definition should parse and validate within 5 seconds
  - Platform integrations should handle at least 100 API requests per minute
  - Audience segmentation should process datasets of 1 million+ user profiles efficiently
  - Timing coordination should support at least 1,000 scheduled actions across 24 time zones
  - Metrics collection should aggregate data from at least 10 platforms within 10 minutes

- **Integration Points**:
  - Social media platform APIs (Facebook, Twitter, Instagram, LinkedIn, etc.)
  - Email marketing systems (Mailchimp, SendGrid, etc.)
  - Content management systems
  - Digital advertising platforms (Google Ads, Facebook Ads, etc.)
  - Customer data platforms (CDPs)
  - Analytics systems
  - Team collaboration and notification tools

- **Key Constraints**:
  - All functionality must be implemented as libraries and APIs, not as applications with UIs
  - Must respect rate limits and quotas of integrated marketing platforms
  - Must handle authentication requirements of diverse marketing systems
  - Must maintain data privacy compliance across geographic regions
  - Must operate with minimal technical knowledge requirements
  - Should be resilient to API changes in integrated platforms

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this Marketing Campaign Workflow Automation Engine centers around accessible campaign orchestration:

1. **Natural Language Parser**: A system that interprets marketing workflow descriptions in plain language and converts them into structured workflow definitions with appropriate actions and conditions.

2. **Platform Connector Framework**: Modules that establish standardized interfaces and API integration with various marketing platforms, handling authentication, rate limiting, and error recovery.

3. **Audience Segmentation Engine**: Components that define, manage, and apply complex targeting rules to audience datasets, with support for both static and dynamic segmentation criteria.

4. **Global Scheduling System**: A comprehensive scheduler that manages the timing of campaign actions across different time zones, with support for relative timing, recurring actions, and optimal engagement windows.

5. **Metrics Collection Framework**: Components that gather performance data from multiple marketing platforms, normalize metrics for comparison, and prepare data for analysis and visualization.

6. **Campaign Orchestrator**: The core engine that coordinates the execution of marketing workflows, manages cross-platform dependencies, and maintains campaign state across channels.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Accurate interpretation of natural language workflow descriptions
  - Reliable interaction with marketing platform APIs
  - Correct application of audience segmentation rules
  - Precise timing coordination across time zones
  - Comprehensive collection and normalization of performance metrics

- **Critical User Scenarios**:
  - Multi-channel campaign launch with coordinated timing
  - Audience segmentation based on complex demographic and behavioral criteria
  - Dynamic adjustment of campaign parameters based on performance metrics
  - Recovery from platform API failures during campaign execution
  - Cross-platform audience targeting with consistent messaging
  - Performance reporting aggregated across multiple channels

- **Performance Benchmarks**:
  - Natural language processing within 5 seconds for typical workflow descriptions
  - API handling at 100+ requests per minute with appropriate rate limiting
  - Audience segmentation processing 1 million+ profiles within acceptable time frames
  - Scheduling coordination for 1,000+ actions across 24 time zones
  - Metrics aggregation from 10+ platforms within 10 minutes

- **Edge Cases and Error Conditions**:
  - Ambiguous natural language instructions
  - Marketing platform API changes or failures
  - Invalid audience segmentation criteria
  - Time zone handling during daylight saving transitions
  - Missing or incomplete performance metrics
  - Rate limiting and quota exhaustion on external platforms
  - Cross-platform identity resolution conflicts
  - Regulatory compliance issues in different regions

- **Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for natural language parsing components
  - 100% coverage for platform API interaction logic
  - 100% coverage for audience segmentation rules
  - All error handling paths must be tested

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
A successful implementation of the Marketing Campaign Workflow Automation Engine will meet the following criteria:

1. Natural language workflow definition system that correctly interprets various marketing campaign descriptions, verified through tests with diverse instruction patterns.

2. Marketing platform integration that properly connects with multiple systems and handles platform-specific requirements, confirmed through tests with mock platform APIs.

3. Audience segmentation logic that correctly applies complex targeting rules, demonstrated through tests with synthetic audience data and diverse segmentation criteria.

4. Campaign timing coordination that properly schedules actions across different time zones, validated through tests with simulated global timing scenarios.

5. Performance metrics collection that accurately gathers and normalizes data from multiple sources, verified through tests with synthetic performance data.

6. Performance meeting or exceeding the specified benchmarks for processing time, throughput, and capacity.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Project Setup Instructions
To set up the development environment:

1. Create a virtual environment:
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

4. Install test dependencies:
   ```
   pip install pytest pytest-json-report
   ```

CRITICAL REMINDER: It is MANDATORY to run the tests with pytest-json-report and provide the pytest_results.json file as proof of successful implementation:
```
pytest --json-report --json-report-file=pytest_results.json
```