# Smart City Microservices Integration Framework

## Overview
This project is a specialized event-driven microservices framework designed for smart city initiatives that integrate services across multiple municipal departments. It provides geospatial event routing, cross-department authorization, emergency broadcast capabilities, selective data persistence, and privacy controls to create an interconnected yet secure urban services infrastructure.

## Persona Description
Raj develops systems connecting various municipal services for a smart city initiative spanning transportation, utilities, and public safety. His primary goal is to implement a microservices architecture that enables different city departments to share critical information while maintaining independent operation and specialized functionality.

## Key Requirements

1. **Geospatial Event Routing Based on City Zones and Jurisdictions**
   - Implement event routing based on geographic boundaries
   - Create efficient spatial indexing for rapid event distribution
   - Support for overlapping jurisdictions with multiple responsible departments
   - Include dynamic redistricting without service disruption
   - This feature ensures that events are delivered only to departments with responsibility for specific geographic areas, optimizing system resources and respecting jurisdictional boundaries

2. **Cross-department Event Subscription with Authorization Policies**
   - Develop configurable access policies for inter-department data sharing
   - Create selective subscription based on event types and attributes
   - Support for delegated authorization with audit trails
   - Include time-bound and purpose-limited access grants
   - This feature enables controlled information sharing between departments while respecting operational boundaries and data governance requirements

3. **Emergency Broadcast Patterns with Priority Message Handling**
   - Implement emergency event prioritization and distribution
   - Create acknowledgment and escalation protocols
   - Support for resilient delivery during infrastructure disruption
   - Include fallback communication paths for critical notifications
   - This feature ensures that emergency information reaches all relevant systems with appropriate urgency, even during infrastructure challenges

4. **Long-term Data Archiving with Selective Event Persistence**
   - Develop tiered storage strategies based on data importance
   - Create data lifecycle policies with automated archiving
   - Support for efficient retrieval of historical data
   - Include compliance with municipal record retention requirements
   - This feature balances storage efficiency with the need to maintain historical smart city data for analysis, planning, and compliance purposes

5. **Public/Private Information Barriers with Citizen Privacy Controls**
   - Implement privacy-preserving data transformation pipelines
   - Create citizen consent management for personal data
   - Support for anonymization and aggregation of sensitive information
   - Include privacy impact assessments for new data integrations
   - This feature protects citizen privacy while enabling appropriate public data sharing and transparency

## Technical Requirements

### Testability Requirements
- Support for simulating multi-department interactions
- Ability to test geospatial event routing
- Testing of emergency broadcast scenarios
- Verification of privacy controls and data protection

### Performance Expectations
- Support for at least 20 integrated city departments
- Maximum 500ms latency for standard inter-department events
- Maximum 100ms latency for emergency notifications
- Support for city-scale data processing (minimum 100,000 events/hour)

### Integration Points
- Integration with departmental systems (e.g., traffic management, utility monitoring)
- Support for IoT devices and sensor networks throughout the city
- Compatibility with GIS and mapping systems
- Integration with emergency response and public safety networks

### Key Constraints
- Must comply with municipal data retention policies
- Must protect citizen privacy while enabling appropriate data sharing
- Must operate reliably in emergency situations
- Must accommodate varying technical capabilities across departments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Geospatial Event Management**
   - Geographical event routing and filtering
   - Spatial indexing and optimization
   - Jurisdiction management
   - Location-based event subscription

2. **Inter-department Communication**
   - Configurable access policies
   - Selective event subscription
   - Authorization and authentication
   - Audit logging and compliance

3. **Emergency Response System**
   - Priority-based message handling
   - Reliable emergency notification
   - Acknowledgment and escalation
   - Fallback communication paths

4. **Data Management and Retention**
   - Tiered data storage strategies
   - Automated archiving and retrieval
   - Retention policy enforcement
   - Historical data access and analysis

5. **Privacy and Public Access**
   - Privacy-preserving transformations
   - Consent management
   - Anonymization and aggregation
   - Public/private data boundaries

## Testing Requirements

### Key Functionalities that Must be Verified
- Accurate geospatial event routing
- Proper enforcement of cross-department authorization
- Reliable emergency broadcast functioning
- Correct implementation of data retention policies
- Effectiveness of privacy controls

### Critical User Scenarios
- Traffic incident affecting multiple departments
- Public utility emergency requiring coordinated response
- City-wide emergency notification and confirmation
- Historical data retrieval for urban planning
- Citizen-facing data publication with privacy protections

### Performance Benchmarks
- Route 10,000+ geospatial events per hour to correct departments
- Process emergency broadcasts within 100ms to all relevant systems
- Support 20+ city departments with their own event patterns
- Archive and retrieve data spanning at least 5 years of city operations

### Edge Cases and Error Conditions
- Partial system outages during emergency situations
- Jurisdictional boundary disputes with overlapping responsibility
- Privacy conflicts between transparency requirements and data protection
- Extreme event volumes during major city incidents
- Legacy department systems with limited integration capabilities

### Required Test Coverage Metrics
- Minimum 90% line coverage for all code
- 100% coverage of geospatial routing logic
- 100% coverage of emergency broadcast functionality
- 100% coverage of privacy control mechanisms
- 100% coverage of data archiving and retrieval

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

1. Events are correctly routed based on geospatial properties
2. Departments can securely subscribe to events from other departments
3. Emergency broadcasts are delivered with appropriate priority
4. Data is archived according to retention policies
5. Citizen privacy is protected through appropriate controls
6. Performance meets the specified benchmarks
7. All test cases pass with the required coverage

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up the development environment:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Install test dependencies
uv pip install pytest pytest-json-report

# Run tests and generate the required JSON report
pytest --json-report --json-report-file=pytest_results.json
```

CRITICAL: Generating and providing the pytest_results.json file is a mandatory requirement for project completion. This file serves as evidence that all functionality has been implemented correctly and passes all tests.